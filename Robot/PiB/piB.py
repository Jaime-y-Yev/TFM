import threading
hiloMatarID = 0
hiloEstadosID = 1
hiloControlID = 2
hiloModoSyncID = 3
hiloPotenciometroID = 4
hiloSondeoID = 5
hiloCamaraID = 6
hiloVideoID = 7
matarHilos = 'o'


import json
from time import sleep, monotonic
import globalesPi

import sys
sys.path.insert(0, '/home/pi/TFM/Robot')
from comandosParaArduino import *
from mqttPi import pubMQTT, subMQTT

import RPi.GPIO as GPIO
from sondeo import sondear
import subprocess

import actuador
import jaula

import bateria

import camara
import moverCamara

class Hilo(threading.Thread):

	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
		
	def run(self):
		
		print("Comenzando hilo ", end='')
			
		# Matar el resto de hilos------------------------------------------------------------------   
		if self.threadID == hiloMatarID:
			print("Matar")

			while True:
				global matarHilos
				matarHilos = input() # utilizar la entrada de teclado             
				if matarHilos == 'm':
					globalesPi.expandirActuador = False
					pubMQTT('ServidorRobot/modoB', json.dumps({"matar": "m"}))
					pubMQTT('ServidorRobot/moverCamara', json.dumps({"matar": "m"}))
					pubMQTT('RobotRobot/coordObj', json.dumps({"matar": "m"}))
					break

			print("Terminando hilo Matar")
	   
		# Mandar estados de PiB y ArduinoB a Servidor-----------------------------------------------
		elif self.threadID == hiloEstadosID:
			print("Estado")
			
			# Iniciar la variable local con un texto vacio para ejecutar el proceso la primera vez
			estadoPiB = 0
			estadoArduinoB= 0
			while True:

				if estadoPiB != globalesPi.estadoPiB:									 # solo mandar estados de PiB cuando había un cambio en PiB
					pubMQTT("RobotServidor/estado/PiB",globalesPi.estadoPiB) 			 # mandar información del PiB a Servidor
					estadoPiB = globalesPi.estadoPiB 									 # actualizar la variable local para poder reinicar el proceso
					
				if estadoArduinoB != globalesPi.estadoArduinoB:							 		   # solo mandar estados de ArduinoA cuando había un cambio en ArduinoB
					pubMQTT("RobotServidor/estado/ArduinoB",globalesPi.estadoArduinoB) 			   # mandar infromación de ArduinoB a Servidor
					estadoArduinoB = globalesPi.estadoArduinoB 									   # actualizar la variable local para poder reinicar el proceso

				# Matar este hilo
				if matarHilos == 'm':
					break           
			
			print("Terminando hilo Estados")
	   
		# Recibir comandos del Servidor---------------------------------------------------------------
		elif self.threadID == hiloControlID:
			print("Control") 

			while True:
							
				# Utilizar MQTT para recibir cambios de modo o comandos para mover la camara manualmente
				subMQTT([("ServidorRobot/modoB",1),("ServidorRobot/moverCamara",1)])
		
				# Matar este hilo 
				if matarHilos == 'm':
					break          
			
			print("Terminando hilo Control")
		
		# Sincronizar modos del Arduino, PiB y Servidor-----------------------------------------------
		elif self.threadID == hiloModoSyncID:
			print("ModoSync")
			
			# Iniciar el reloj y asignar la frecuencia de vigilación del Arduino
			tiempoInicial = monotonic()
			intervaloVigilarArduino = 10
				
			modo = globalesPi.modo
			while True:
				
				if monotonic() - tiempoInicial >= intervaloVigilarArduino:
					vigilarModoArduino()
					tiempoInicial = monotonic()
																
				if modo != globalesPi.modo: 
					# Informar el usuario sobre el cambio de los modos					
					modo = globalesPi.modo # guardar el modo actual en una variable, para poder hacer el flanco otra vez
					globalesPi.estadoPiB = "Cambiando modo a "  + str(globalesPi.modo)
					
					# Se utiliza MQTT para publicar el modo sincronizado a Servidor
					pubMQTT("RobotServidor/modo/escribir", globalesPi.modo)
					
					# Desconectar la batería si hay una emergencia					
					if globalesPi.modo == MODO_EMERGENCIA:
						bateria.desconectar()
					else:
						bateria.conectar()
				
				# Matar este hilo 
				if matarHilos == 'm':
					break
				
			print("Terminando hilo ModoSync")
		
		# Potenciometro-------------------------------------------------------------------------------
		elif self.threadID == hiloPotenciometroID:
			print("Potenciometro")
			
			while True:
							
				if globalesPi.expandirActuador == True:
					actuador.leerPotenciometro()
				
				# Matar este hilo 
				if matarHilos == 'm':
					break				
			
			print("Terminando hilo Potenciometro")
		
		# Ejecutar sondeo, iniciado por PiA------------------------------------------------------------
		elif self.threadID == hiloSondeoID:
			print("Sondeo")
					
			while True:
				sleep(1)
				
				# Sólo activar la jaula y actuador en el modo de sondeo 
				if globalesPi.modo == MODO_SONDEO:
					
					print("Sondeo iniciado")
					
					globalesPi.sondeoTerminado = 0

					# Conjelar el hilo hasta obtener coordObj de PiA
					subMQTT(('RobotRobot/coordObj',2)) 
					
					sleep(1)
					
					resultadosSondeoDict = sondear(globalesPi.coordObj) # revelar la jaula, obtener mediciones del sensor, retraer la jaula

					# Si hay un problema con la expansión del actuador, notificar piA (que reinicia el proceso si reintentoSondeo < 2)					
					if globalesPi.problemaExpandir == True:
						globalesPi.sondeoTerminado = 2
						pubMQTT('RobotRobot/sondeoTerminado', 2,retainMess=False)
						globalesPi.problemaExpandir = False
					
					# Si no hay un problema con la expansión, tomar las fotos
					elif globalesPi.problemaExpandir == False:
												
						sleep(1)

						# Informar PiA que el sondeo se realizó con éxito
						globalesPi.sondeoTerminado = 1
						pubMQTT('RobotRobot/sondeoTerminado', 1,retainMess=False)
						
						# Tomar las fotos y hacer un análisis de la cantidád de verde
						verdesDict, fotoI, fotoD = camara.tomarFotos()

						# Añadir los resultados de las fotos a los resultados de sondeo
						resultadosSondeoDict.update(verdesDict)


						# Mandar los resultados al servidor
						globalesPi.estadoPiB = "Mandando resultados al servidor"
						print("Mandando resultados al servidor: ", resultadosSondeoDict)
						pubMQTT('RobotServidor/resultados/medidas', json.dumps(resultadosSondeoDict))
						sleep(1)

						pubMQTT('RobotServidor/resultados/fotos/I', fotoI)
						sleep(1)
						
						pubMQTT('RobotServidor/resultados/fotos/D', fotoD)
						sleep(1)
						
						# Cambiar modo de PiB a MODO_INACTIVO 
						globalesPi.modo = MODO_INACTIVO
								
				# Matar este hilo 
				if matarHilos == 'm':
					jaula.servoPWM.stop()
					break
				
			print("Terminando hilo Sondeo")  
		
		# Hilo que ejecuta el movimiento de la cámara durante la navegación manual ----------------------
		elif self.threadID == hiloCamaraID:
			print("Camara")
			
			while True:
										
				if (globalesPi.modo == MODO_MANUAL):
					moverCamara.moverServoWeb(globalesPi.comandoCamara)
				
				# Matar este hilo 
				if matarHilos == 'm':   
					break
				
			print("Terminando hilo Camara")  
		
		# Transmite en vivo el video durante la navegación manual  --------------------------------------
		elif self.threadID == hiloVideoID:
			print("Video")
			
			while True:
										
				if (globalesPi.modo == MODO_MANUAL):
					camara.mostrarVideo()
				
				# Matar este hilo 
				if matarHilos == 'm':   
					break
				
			print("Terminando hilo Video") 
								


# Hilo principal que arranca los demás hilos
print("Comenzando hilo Principal")           

# Crear los hilos
hiloMatar = Hilo(hiloMatarID)
hiloEstados = Hilo(hiloEstadosID)
hiloControl = Hilo(hiloControlID)
hiloModoSync = Hilo(hiloModoSyncID)
hiloPotenciometro = Hilo(hiloPotenciometroID)
hiloSondeo = Hilo(hiloSondeoID)
hiloCamara = Hilo(hiloCamaraID)
hiloVideo = Hilo(hiloVideoID)

# Empezar los hilos
hiloMatar.start()
sleep(0.25)
hiloEstados.start()
sleep(0.25)
hiloControl.start()
sleep(0.25)
hiloModoSync.start()
sleep(0.25)

# Al encender Pi, actualizar su modo según el modo general del sistema
pubMQTT("RobotServidor/modo/leer",1) 

hiloPotenciometro.start()
sleep(0.25)
hiloSondeo.start()
sleep(0.25)
hiloCamara.start()
sleep(0.25)
hiloVideo.start()


