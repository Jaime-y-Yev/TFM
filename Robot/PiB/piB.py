import threading
hiloMatarID = 0
hiloEstadosID = 1
hiloControlID = 2
hiloModoSyncID = 3
hiloPotenciometroID = 4
hiloSondeoID = 5
hiloCamaraID = 6
matarHilos = 'o'


import json
import time

import globalesPiB

from mqttPiB import pubMQTT, subMQTT


from comandosParaArduinoB import *
from time import sleep

# Sondeo
import RPi.GPIO as GPIO
from sondeo import sondear
import os
import subprocess
pigpioProceso = subprocess.Popen(['sudo', 'pigpiod'], shell=False)
from camara import tomarFotos

##from actuador import leerPotenciometro as actuador_leerPotenciometro
##from jaula import servoPWM as jaula_servoPWM
import actuador
import jaula
#from actuador import *
#from jaula import *

import bateria

import moverCamara


class Hilo(threading.Thread):

	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID
		
	def run(self):
		
		print("Comenzando hilo ", end='')
			
		# Se mata los procesos facilmente con un hilo adicional----------------------------------   
		if self.threadID == hiloMatarID:
			print("Matar")

			while True:
				global matarHilos
				matarHilos = input() # utilizar la entrada de teclado             
				if matarHilos == 'm':
					globalesPiB.matarPotenciometro = True
					pubMQTT('RobotServidor/coordObjMedicion', json.dumps({"matar": "m"}))
					pubMQTT('control/ServidorRobot', json.dumps({"matar": "m"}))
					#pigpioProceso.kill()
					pigpioKillProceso = subprocess.Popen(['sudo', 'killall', 'pigpiod'], shell=False)
					os.system("sudo kill %d"%(pigpioProceso.pid))
					break

			print("Terminando hilo Matar")
	   
		# Mandar estados de PiB y ArduinoB a Servidor----------------------------------------
		elif self.threadID == hiloEstadosID:
			print("Estado")
			
			# iniciar el variable local con un valor imposible para ejecutar el proceso la primera vez
			estadoPiB = 0
			estadoArduinoB= 0
			while True:

				if estadoPiB != globalesPiB.estadoPiB:# solo mandar estados de PiB cuando había un cambio en PiB
					pubMQTT("control/estadoPiB",json.dumps(globalesPiB.estadoPiB)) # mandar información del PiB a Servidor
					estadoPiB = globalesPiB.estadoPiB # actualizar el variable local para poder reinicar el proceso
					print(globalesPiB.estadoPiB)
					
				if estadoArduinoB != globalesPiB.estadoArduinoB:# solo mandar estados de ArduinoA cuando había un cambio en ArduinoB
					pubMQTT("control/estadoArduinoB",json.dumps(globalesPiB.estadoArduinoB)) # mandar infromación de ArduinoB a Servidor
					estadoArduinoB = globalesPiB.estadoArduinoB # actualizar el variable local para poder reinicar el proceso
					print(globalesPiB.estadoArduinoB)

				# Mater hilos seguramente utilizando la entrada de "m" en terminal 
				if matarHilos == 'm':
					break           
			
			print("Terminando hilo Control")
	   
		# Recibir comandos del Servidor-------------------------------------------------------- 
		elif self.threadID == hiloControlID:
			print("Control") 

			while True:
				
				# Utilizar MQTT para recibir cambios de modo o marchaParo estados
				subMQTT("control/ServidorRobot")  
		
				# Mater hilos seguramente utilizando la entrada de "m" en terminal 
				if matarHilos == 'm':
					pubMQTT("control/ServidorRobot", "m")
					break          
			
			print("Terminando hilo Control")
		
		# Sincronizar modos del Arduino, PiB y Servidor---------------------------------------
		elif self.threadID == hiloModoSyncID:
			print("ModoSync")
			
			modo = globalesPiB.modo
			#modo = 9 # iniciar el variable local con un valor imposible para entrar sincronización
			while True:
				
				# Utilizar el cambio de modos para sincronizar el modo de ArduinoA
				if modo != globalesPiB.modo: 
					
					# Informar el usuario sobre el cambio de los modos
					globalesPiB.estadoPiB = "Cambio de modos detectado. Cambiando modo de PiB..."
					
					modo = globalesPiB.modo # guardar el modo corriente en un variable, para poder hacer el flanco otra vez
					globalesPiB.estadoPiB = "modoPiB: " + str(modo)
					
					# Se utiliza MQTT para publicar el modo sincronizado a Servidor
					pubMQTT("control/RobotServidor/modo", globalesPiB.modo)
					
					if globalesPiB.modo == MODO_EMERGENCIA:
						bateria.desconectar()
					else:
						bateria.conectar()

				
				# Mater hilos seguramente utilizando la entrada de "m" en terminal 
				if matarHilos == 'm':
					break
				
			print("Terminando hilo modo")
		
		# Potenciometro---------------------------------------
		elif self.threadID == hiloPotenciometroID:
			print("Potenciometro")
				
			actuador.leerPotenciometro()
							
			# Mater hilos seguramente utilizando la entrada de "m" en terminal 
			#if matarHilos == 'm':
			#	break
			
			print("Terminando hilo potenciometro")
		
		elif self.threadID == hiloSondeoID:#-------------------------------------------------------------
			print("Sondeo")
					
			while True:
				sleep(1)
				print("In Hilo Sondeo globalesPiB.modo =", globalesPiB.modo)
				
				# Sólo activar la jaula y actuador en el modo de sondeo 
				if globalesPiB.modo == MODO_SONDEO:
					
					print("Sondeo iniciado")
					
					subMQTT('RobotServidor/coordObjMedicion') # need globalesPiB.coordObj
					
					sondear()
					
					tomarFotos()
										
					globalesPiB.modo = MODO_INACTIVO 

				if matarHilos == 'm':   
					jaula.servoPWM.stop()
	##                    GPIO.cleanup()    
					break
				
			print("Terminando hilo Sondeo")  
		
		elif self.threadID == hiloCamaraID:#-------------------------------------------------------------
			print("Camara")
			
			while True:
										
				if (globalesPiB.modo == MODO_MANUAL):
					moverCamara.moverServoWeb(globalesPiB.comandoCamara)

				if matarHilos == 'm':   
					break
				
			print("Terminando hilo Sondeo")  
								
	

# Hilo principal que arranca los demás hilos
print("Comenzando hilo Principal")           

# Al encender Pi, actualizar su modo según el servidor enviando
# Sincronizar modos antes de empezar hilos
pubMQTT("control/RobotServidor/syncModo", 1)   

# Crear cada hilo
hiloMatar = Hilo(hiloMatarID)
hiloEstados = Hilo(hiloEstadosID)
hiloControl = Hilo(hiloControlID)
hiloModoSync = Hilo(hiloModoSyncID)
hiloPotenciometro = Hilo(hiloPotenciometroID)
hiloSondeo = Hilo(hiloSondeoID)
hiloCamara = Hilo(hiloCamaraID)

# Iniciar cada hilo
hiloMatar.start()
sleep(0.25)
hiloEstados.start()
sleep(0.25)
hiloControl.start()
sleep(0.25)
hiloModoSync.start()
sleep(0.25)
hiloPotenciometro.start()
sleep(0.25)
hiloSondeo.start()
sleep(0.25)
hiloCamara.start()

        

