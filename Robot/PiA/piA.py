import threading
hiloMatarID = 0
hiloRTKID = 1
hiloNavegarID = 2
hiloControlID = 3
hiloModoSyncID = 4
hiloEstadosID = 5
hiloArduinoID = 6
hiloMovilID = 7
hiloSondeoID = 8
matarHilos = 'o'


import json
from time import sleep,clock,monotonic

import sys
sys.path.insert(0, '/home/pi/TFM/Robot')
from comandosParaArduino import *
from mqttPi import pubMQTT, subMQTT

from guardarPosicion import guardarCoordAct

from leerGPS import *

from navegacion import navegar,direccion,distancia, moverReintentoSondeo, promedio

import globalesPi

from trayectoria import crearTrayectoria

from actualizarCodigosDeComandos import *

# Recompilar el ArduinoA al arrancar PiA para evitar problemas con la comunicación serie
if globalesPi.resetearArduino:
	actualizarEncabezamientoArduino(archivoPi,archivoArduinoA)
	compilarSubirArduino()
	globalesPi.resetearArduino = False


class Hilo(threading.Thread):
    
	def __init__(self, threadID):
		threading.Thread.__init__(self)
		self.threadID = threadID

	def run(self):

		print("Comenzando hilo ", end='')

		# Matar el resto de hilos-----------------------------------------------------------  
		if self.threadID == hiloMatarID:
			print("Matar")

			while True:
				
				global matarHilos
				matarHilos = input() # utilizar la entrada de teclado para matar los hilos            

				if matarHilos == 'm': 
					pubMQTT("ServidorRobot/modoA", json.dumps({"matar": "m"}))
					pubMQTT("ServidorRobot/marchaParo", json.dumps({"matar": "m"}))
					pubMQTT("ServidorRobot/antena", json.dumps({"matar": "m"}))
					pubMQTT("movilRobot/coordAct", json.dumps({"matar": "m"}))
					pubMQTT("ServidorRobot/coordObj_geometría", json.dumps({"matar": "m"}))
					pubMQTT("RobotRobot/sondeoTerminado", json.dumps({"matar": "m"}))
					pubMQTT("RobotServidor/resultados/medidas", json.dumps({"matar": "m"}))
					pubMQTT("RobotRobot/coordObj", json.dumps({"matar": "m"}))
					break

			print("Terminando hilo Matar")

		# Mandar estados de PiA y ArduinoA a Servidor----------------------------------------
		elif self.threadID == hiloEstadosID:
			print("Estados")
			
			# Iniciar la variable local con un texto vacio para ejecutar el proceso la primera vez
			estadoPiA = ""
			estadoArduinoA = ""
			while True:
				
				if estadoPiA != globalesPi.estadoPiA:						 # solo mandar estados de PiA cuando había un cambio en PiA
					pubMQTT("RobotServidor/estado/PiA",globalesPi.estadoPiA) # mandar información del PiA a Servidor
					estadoPiA = globalesPi.estadoPiA 						 # actualizar la variable local para poder reinicar el proceso
					print(globalesPi.estadoPiA)

				if estadoArduinoA != globalesPi.estadoArduinoA:				 			# solo mandar estados de ArduinoA cuando había un cambio en ArduinoA
					pubMQTT("RobotServidor/estado/ArduinoA",globalesPi.estadoArduinoA)  # mandar infromación de ArduinoA a Servidor
					estadoArduinoA = globalesPi.estadoArduinoA 						    # actualizar la variable local para poder reinicar el proceso
					print(globalesPi.estadoArduinoA)

				# Matar este hilo  
				if matarHilos == 'm':
					break           
			
			print("Terminando hilo Estados")

		# Recibir comandos del Servidor-------------------------------------------------------- 
		elif self.threadID == hiloControlID:
			print("Control") 

			while True:

				# Utilizar MQTT para recibir cambios de modo, marchaParo, o de antena o comandos para mover el robot manualmente 
				subMQTT([("ServidorRobot/modoA",1),("ServidorRobot/marchaParo",1),("ServidorRobot/antena",1),("ServidorRobot/navManual",1)])  
				
				# Matar este hilo  
				if matarHilos == 'm':
					break
			
			print("Terminando hilo Control")

		# Sincronizar modos del PiA y Servidor------------------------------------------------
		elif self.threadID == hiloModoSyncID:
			print("ModoSync")
			
			modo = globalesPi.modo # iniciar la variable local con un valor inicial para entrar sincronización
			while True:
				
				if modo != globalesPi.modo: 										
					# Informar el usuario sobre el cambio de los modos
					modo = globalesPi.modo # guardar el modo actual en una variable, para poder detectar el flanco otra vez
					globalesPi.estadoPiA = "Cambiando modo a " + str(globalesPi.modo)
					
					if modo == MODO_MANUAL:
						globalesPi.permitirCambioModoManual = True
				
					# Se utiliza MQTT para publicar el modo sincronizado a Servidor
					pubMQTT("RobotServidor/modo/escribir", globalesPi.modo)

				# Si hay asincronización, hacer un reset de modos
				if globalesPi.modo == MODO_NAVEGACION and globalesPi.permitirSubCoordObj == True and globalesPi.marchaParo == True:
					globalesPi.estadoPiA = "Asincronización detectada, reseteando modos..." 
					
					globalesPi.modo = MODO_INACTIVO
					globalesPi.permitirSubCoordObj = True
					globalesPi.marchaParo = False
				
				# Matar este hilo  
				if matarHilos == 'm':
					break
				
			print("Terminando hilo modoSync")
		
			   
		# Se obtiene coordenadas actuales (coordAct) del robot-----------------------------------------
		elif self.threadID == hiloRTKID:
			print("RTK")
			
			#Inicializar reloj para hacer mediciones
			globalesPi.tiempoInicio = monotonic()
			
			#Inicializar RTKLIB que se utiliza en el próximo paso
			iniciarRTK()
			
			# Utilizar RASPIGNSS con RTKLIB para obtener y filtrar coordenadas actuales
			tiempoInicio = clock()
			while True:                
				
				sleep(0.3) 
				
				coordActGPS = obtenerCoordAct() # leer la posición actual del robot				
				
				# Si el GPS no puede obtener la posición dentro de cierto tiempo, se reinicia 
				if (str(coordActGPS) == 'obteniendo una solucion...' and (clock() - tiempoInicio) > 90): # reiniciar RTKLIB si el gps no encuentra los satélites			
					reiniciarRTK() 				   
					sleep(3)                          # dar tiempo a GPS para reiniciar correctamente 
					tiempoInicio = clock()					
					print("Reiniciando RTK")
				
				if globalesPi.antena == 0: 
					globalesPi.coordAct = coordActGPS  # se guarda la coordinada actual en un variable global sin preocuparnos sobre existencia de una solución
								
				# Una comprobación final de la coordenada
				if coordActGPS != 'obteniendo una solucion...':																				
					pubMQTT("RobotServidor/coordAct", globalesPi.coordAct)
					#guardarCoordAct("RTKTrayectorias0601",coordActGPS)

				# Matar este hilo  
				if matarHilos == 'm':
					break
			
			# Apagar RTK de forma segura antes de terminar el hilo RTK
			finalizarRTK()           
			for i in range(20):
				print(procesoRTK.readline())            
			procesoRTK.close()                                      
			
			print("Terminando hilo RTK")
		
		# Utilizar un móvil para obtener coordenadas actuales ----------------------------------------
		elif self.threadID == hiloMovilID:
			print("Móvil")
			
			# Inicializar las listas asociadas con la filtración de coordenadas recibidas por el móvil
			coordActCandidatos = [[0,0],[0,0],[0,0]]	
			distanciaEntreCandidatos = [1000,1000,1000]
				
			while True:
				
				# Rellenar la lista de candidatos				
				subMQTT(("movilRobot/coordAct",1))
				coordActCandidatos.append(globalesPi.coordActCandidato) 
				coordActCandidatos.pop(0)
				for i in range (len(coordActCandidatos)):
					if i < (len(coordActCandidatos)-1):
						distanciaEntreCandidatos[i] = distancia(coordActCandidatos[i], coordActCandidatos[i+1])
					elif i == (len(coordActCandidatos)-1):
						distanciaEntreCandidatos[i] = distancia(coordActCandidatos[i], coordActCandidatos[0])				
				
				# Filtrar la lista de los candidatos
				if globalesPi.antena == 1:
					# No devolver un coordAct hasta que el promedio de la distancia entre los candidatos sea menor que 5 m
					if max(distanciaEntreCandidatos) <= 5: 
						coordActMovil = promedio(coordActCandidatos)
						globalesPi.coordAct = coordActMovil 
					
					# Si el promedio de la distancia entre los candidatos es mayor que 5 m, devolver un mensaje informativo
					else:
						globalesPi.coordAct = 'obteniendo una solucion...'
					
				#guardarCoordAct("Movil",coordActMovil)
				
				# Mandar el coordAct válido
				if globalesPi.coordAct != 'obteniendo una solucion...':
					pubMQTT("RobotServidor/coordAct", globalesPi.coordAct)

				# Matar este hilo  
				if matarHilos == 'm':
					break

			print("Terminando hilo Móvil")

		
		# Calcular trayectoria y ejecutar navegación del robot ---------------------------------------
		elif self.threadID == hiloNavegarID:
			print("Navegar")      
			
			# Inicializar el reloj y asignar la frecuencia de vigilación del Arduino
			tiempoInicial = monotonic()
			intervaloVigilarArduino = 10		 
			while True:
				
				# Leer el modo actual del ArduinoA y sincronizarlo con PiA, vigilando cualquier emergencia
				if monotonic()-tiempoInicial >= intervaloVigilarArduino and globalesPi.robotDesplazando == False:
					vigilarModoArduino()
					tiempoInicial = monotonic()
								
				if globalesPi.modo == MODO_NAVEGACION: # sólo ejecutar los próximos pasos si ArduinoA está listo para recibir comandos y si estamos en MODO_NAVEGACION
					
					# Primero: obtenemos la información necesaria para poder ejecutar navegar()
					if globalesPi.marchaParo == False and globalesPi.permitirSubCoordObj == True:
						
						# Utilizar MQTT para recibir coordObj y geometria del Servidor         
						subMQTT(("ServidorRobot/coordObj_geometría",2))
						globalesPi.estadoPiA = "coordObj recibida del Servidor... "

						# No calcular una trayectoria hasta recibir una solución adecuada del GPS
						while True:
							print("Esperando una solución")
							if (globalesPi.coordAct == "obteniendo una solucion..." and globalesPi.modo == MODO_NAVEGACION) or (globalesPi.coordAct == [0,0] and globalesPi.modo == MODO_NAVEGACION):
								globalesPi.estadoPiA = "Esperando solución para calcular trayectoria"
								print("Esperando una solución")
								sleep(1)
							else:
								break
													
						if globalesPi.modo == MODO_NAVEGACION:
							# Se construye la trayectoria utilizando la geometria y coordObj
							trayectoria = crearTrayectoria(globalesPi.coordAct, globalesPi.coordObj, globalesPi.geometria)
							globalesPi.estadoPiA = "Trayectoria calculada con éxito!"
							
							# Utiliza MQTT para publicar trayectoria al Servidor
							trayectoriaPub = json.dumps({"trayectoria": trayectoria, "idSesion": globalesPi.idSesion}) # se construye trayectoriPub en el formato dict
							globalesPi.estadoPiA = "Mandando trayectoria al Servidor..."
							pubMQTT("RobotServidor/trayectoria",trayectoriaPub)

							# Se cambia permitirSubCoordObj a False para evitar llamada de sub_coordObj_geometria() otra vez
							globalesPi.permitirSubCoordObj = False                                 
												
					# Segundo: utilizamos la información en el paso previo para ejecutar navegar()
					elif globalesPi.marchaParo == 1 and globalesPi.permitirSubCoordObj == False:
						globalesPi.estadoPiA = "En Marcha, Navegando..."
						
						# La función principal de navegación 
						globalesPi.robotDesplazando = True
						navegar(trayectoria, globalesPi.coordObj)
						globalesPi.robotDesplazando = False
											
						# Se resetea algunas variables para poder reiniciar el proceso cuando termine sondeo
						globalesPi.marchaParo = False
						globalesPi.permitirSubCoordObj = True
						print("cambiando a modo a MODO_SONDEO")
						globalesPi.modo = MODO_SONDEO
						
						globalesPi.sondeoTerminado = 0 						
				
				# En modo manual, el robot recibe los comandos de navegación desde la página web
				elif globalesPi.modo == MODO_MANUAL:	
					
					# Primero: cambiar el modo de Arduino a MODO_MANUAL				
					if globalesPi.permitirCambioModoManual == True:
						comandoArduino(CAMBIAR_MODO, MODO_MANUAL)
						globalesPi.permitirCambioModoManual = False
					
					# Segundo:  Se mandar comandos de navegación al ArduinoA
					if globalesPi.permitirComandoManual == True:
						comandoArduino(RECIBIR_COMANDO_MANUAL, globalesPi.comandoManual) 
						globalesPi.permitirComandoManual = False										
				
				# Matar este hilo  
				if matarHilos == 'm':
					break
				
			print("Terminando hilo Navegar")
		
		# Iniciar el sondeo ejecutado por PiB
		elif self.threadID == hiloSondeoID:#-------------------------------------------------------------
			print("Sondeo") 
			
			while True:

				if globalesPi.modo == MODO_SONDEO:
					
					# Sondeo no empezado, mandando coordObj y esperando a empezar el sondeo
					if globalesPi.sondeoTerminado == 0 and globalesPi.robotDesplazando == False: 
						sleep(5)
						globalesPi.estadoPiA = "Esperando a empezar el sondeo..."
						pubMQTT("RobotRobot/coordObj", json.dumps({"coordObj": globalesPi.coordObj, "idSesion": globalesPi.idSesion}))
						subMQTT(("RobotRobot/sondeoTerminado",1))

					# Sondeo terminado, reiniciar variables y cambiar el modo a MODO_INACTIVO
					if globalesPi.sondeoTerminado == 1: # Sondeo sin error
						globalesPi.estadoPiA = "Sondeo terminado sin error..."
						globalesPi.sondeoTerminado = 0
						globalesPi.modo = MODO_INACTIVO
						globalesPi.reintentoSondeo = 0
					
					# Sondeo no terminado por problema de expansión del actuador, mover el robot para intentar de nuevo						
					elif globalesPi.sondeoTerminado == 2 and globalesPi.reintentoSondeo < 2: 
						globalesPi.estadoPiA = "Sondeo terminado con error de expansión..."
						
						# Mover el robot unos centímetros
						moverReintentoSondeo()
						
						# Contar el número de reintentos
						globalesPi.reintentoSondeo += 1
						globalesPi.sondeoTerminado = 0
						globalesPi.estadoPiA = "Número de reintentos: " + str(globalesPi.reintentoSondeo)
					
					# Sondeo no terminado por problema de llegar al ḿaximo numero de reintentos, cambiar modo a MODO_INACTIVO 						
					elif globalesPi.sondeoTerminado == 2 and globalesPi.reintentoSondeo == 2: 
						pubMQTT("RobotServidor/resultados/medidas",json.dumps({"coordObj": globalesPi.coordObj,"problema": 2 }))
						print("Problema con sondeo, intentos=max , modo inactivo...")
						globalesPi.modo = MODO_INACTIVO
						sleep(5)
						globalesPi.reintentoSondeo = 0	
						globalesPi.sondeoTerminado = 0
					
					# Sondeo no terminado por problema con contracción, cambiar modo a MODO_EMERGENCIA 				
					elif globalesPi.sondeoTerminado == 3: 
						pubMQTT("RobotServidor/resultados/medidas",json.dumps({"coordObj": globalesPi.coordObj,"problema": 3 }))
						globalesPi.modo = MODO_EMERGENCIA
				
				# Matar este hilo  
				if matarHilos == 'm':
					break
				
			print("Terminando hilo Sondeo")					

				 
# Crear los hilos
hiloMuerte = Hilo(hiloMatarID)      
hiloEstados = Hilo(hiloEstadosID)
hiloControl = Hilo(hiloControlID)   
hiloModoSync = Hilo(hiloModoSyncID) 
hiloRTK = Hilo(hiloRTKID)           
hiloMovil = Hilo(hiloMovilID)           
hiloNavegar = Hilo(hiloNavegarID)   
hiloSondeo = Hilo(hiloSondeoID)

# Empezar los hilos
hiloMuerte.start()
sleep(0.25)
hiloEstados.start()
sleep(0.25)
hiloControl.start()
sleep(0.25)
hiloModoSync.start()
sleep(0.25)

# Al encender Pi, actualizar su modo según el modo general del sistema
pubMQTT("RobotServidor/modo/leer", 1)

#hiloRTK.start()
#sleep(0.25)
hiloMovil.start()
sleep(0.25)
hiloNavegar.start()
sleep(0.25)
hiloSondeo.start()


