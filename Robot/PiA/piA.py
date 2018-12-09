import threading
hiloMatarID = 0
hiloRTKID = 1
hiloCoordActID = 9
hiloNavegarID = 2
hiloControlID = 3
hiloModoSyncID = 4
hiloEstadosID = 5
hiloArduinoID = 6
matarHilos = 'o'


import json
import time

from comandosParaArduinoA import *

from leerGPS import *

from navegacion import navegar,direccion,distancia

import globalesPiA

from mqttPiA import pubMQTT, subMQTT, subMQTTZ

from trayectoria import crearTrayectoria

compileUploadArduino = True
if compileUploadArduino:
	import actualizarCodigosDeComandos


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
					pubMQTT("control/ServidorRobot", json.dumps({"matar": "m"}))
					pubMQTT("navegación/coordObj_geometría", json.dumps({"matar": "m"}))
					break

			print("Terminando hilo Matar")

		# Mandar estados de PiA y ArduinoA a Servidor----------------------------------------
		elif self.threadID == hiloEstadosID:
			print("Estados")
			
			# iniciar el variable local con un valor imposible para ejecutar el proceso la primera vez
			estadoPiA = 0
			estadoArduinoA = 0
			while True:

				if estadoPiA != globalesPiA.estadoPiA:# solo mandar estados de PiA cuando había un cambio en PiA
					pubMQTT("control/estadoPiA",json.dumps(globalesPiA.estadoPiA)) # mandar información del PiA a Servidor
					estadoPiA = globalesPiA.estadoPiA # actualizar el variable local para poder reinicar el proceso
					print(globalesPiA.estadoPiA)

				if estadoArduinoA != globalesPiA.estadoArduinoA:# solo mandar estados de ArduinoA cuando había un cambio en ArduinoA
					pubMQTT("control/estadoArduinoA",json.dumps(globalesPiA.estadoArduinoA)) # mandar infromación de ArduinoA a Servidor
					estadoArduinoA = globalesPiA.estadoArduinoA # actualizar el variable local para poder reinicar el proceso
					print(globalesPiA.estadoArduinoA)

				# Mater hilos seguramente utilizando la entrada de "m" en terminal 
				if matarHilos == 'm':
					break           
			
			print("Terminando hilo Estados")

		# Recibir comandos del Servidor-------------------------------------------------------- 
		elif self.threadID == hiloControlID:
			print("Control") 

			while True:

				# Utilizar MQTT para recibir cambios de modo o marchaParo estados
				subMQTT("control/ServidorRobot")  

				# Mater hilos seguramente utilizando la entrada de "m" en terminal 
				if matarHilos == 'm':
					break
			
			print("Terminando hilo Control")

		# Sincronizar modos del Arduino, PiA y Servidor---------------------------------------
		elif self.threadID == hiloModoSyncID:
			print("ModoSync")
			
			modo = globalesPiA.modo # iniciar el variable local con un valor imposible para entrar sincronización
			while True:
				
				# Utilizar el cambio de modos para sincronizar el modo de ArduinoA
				
				if modo != globalesPiA.modo: 
					
					# Informar el usuario sobre el cambio de los modos
					globalesPiA.estadoPiA = "Cambio de modos detectado. Cambiando modo de PiA..."
					
					modo = globalesPiA.modo # guardar el modo corriente en un variable, para poder hacer el flanco otra vez
					globalesPiA.estadoPiA = "modoPiA: " + str(modo)
					print("PiA cambiando su modo...")
					if modo == MODO_MANUAL:
						globalesPiA.permitirCambioModoManual = True
						pubMQTT("navegación/coordObj_geometría",json.dumps({"matar": "m"}))
					# Se utiliza MQTT para publicar el modo sincronizado a Servidor
					pubMQTT("control/RobotServidor/modo", globalesPiA.modo)

				# Si hay asincronización, hacer un reset de modos
				if globalesPiA.modo == MODO_NAVEGACION and globalesPiA.permitirSubCoordObj == True and globalesPiA.marchaOparo == 1:
					globalesPiA.estadoPiA = "Asincronización detectada, reseteando modos..." 
					
					globalesPiA.modo = MODO_INACTIVO
					globalesPiA.permitirSubCoordObj = True
					globalesPiA.marchaOparo = 0
				

				
				# Mater hilos seguramente utilizando la entrada de "m" en terminal 
				if matarHilos == 'm':
					break
				
			print("Terminando hilo modoSync")
		
			   
		# Se obtien coordenadas actuales (coordAct) del robot-----------------------------------------
		elif self.threadID == hiloRTKID:
			print("RTK")
			
			
			#Inicializar RTKLIB que se utiliza en el próximo paso
			iniciarRTK()
			
			# Utilizar RASPIGNSS con RTKLIB para obtener y filtrar coordenadas actuales
			tiempoInicio = time.clock()
			while True:                
				time.sleep(0.5) #was 0.5
				
				coordActGPS = obtenerCoordAct() # leer la posición actual del robot
				#print("CoordAct Intermediate: " + str(coordActGPS))		
								
				
				
				#Si el GPS no puede obtener la posición dentro de cierto tiempo, se lo reinicia 
				if (str(coordActGPS) == 'obteniendo una solucion...' and (time.clock() - tiempoInicio) > 90): # reiniciar RTKLIB si gps no encuentra los satélites
			
					#globalesPiA.estadoPiA = "Reiniciando RTKLIB" # informar el usuario sobre el reinicio de RTKLIB
					
					reiniciarRTK() 
				   
					time.sleep(3)# dar tiempo a GPS para reiniciar correctamente 

					tiempoInicio = time.clock()
					
					print("Reiniciando RTK")
				
				if globalesPiA.antena == 0:
					# Se guarda la coordinada actual en un variable global sin preocuparnos sobre existencia de una solución
					globalesPiA.coordAct = coordActGPS
				
				# Una comprobación final de la coordenada
				if ((coordActGPS != 'obteniendo una solucion...')) :
																				
					pubMQTT("navegación/coordAct",json.dumps(globalesPiA.coordAct))

				# Mater hilos seguramente utilizando la entrada de "m" en terminal 
				if matarHilos == 'm':
					break
			
			#Apagar RTK seguramente antes de ternimar el hilo RTK
			finalizarRTK()           
			for i in range(20):
				print(procesoRTK.readline())            
			procesoRTK.close()                                      
			
			print("Terminando hilo RTK")
		
		
		elif self.threadID == hiloCoordActID:
			print("CoordAct")
			
			coordActCandidatos = [[0,0],[0,0],[0,0]]	
			distanciaEntreCandidatos = [1000,1000,1000]
				
			while True:
				#Rellenar lista de candidatos	
					
				subMQTTZ("navegacion/coordAct/")
				coordActCandidatos.append(globalesPiA.coordActCandidato) 
				coordActCandidatos.pop(0)
				for i in range (len(coordActCandidatos)):
					if i < (len(coordActCandidatos)-1):
						distanciaEntreCandidatos[i] = distancia(coordActCandidatos[i], coordActCandidatos[i+1])
					elif i == (len(coordActCandidatos)-1):
						distanciaEntreCandidatos[i] = distancia(coordActCandidatos[i], coordActCandidatos[0])
				#print("distanciaEntreCandidatos list: ", distanciaEntreCandidatos)
				
				if globalesPiA.antena == 1:
					if max(distanciaEntreCandidatos) <= 5:
						#globalesPiA.coordAct = promedio(coordActCandidatos) # create coordinate averaging function
						globalesPiA.coordAct = coordActCandidatos[2]
					else:
						globalesPiA.coordAct = 'obteniendo una solucion...'
						#print("globalesPiA.coordAct (final!!): ", globalesPiA.coordAct)

								
				
				if globalesPiA.coordAct != 'obteniendo una solucion...':
					#print("Sending to server from antena 1:", globalesPiA.coordAct)
					pubMQTT("navegación/coordAct",json.dumps(globalesPiA.coordAct))

				# Mater hilos seguramente utilizando la entrada de "m" en terminal 
				if matarHilos == 'm':
					break


			print("Terminando hilo CoordAct")

		
		# Calcular trayectoria y ejecutar navegación del robot
		elif self.threadID == hiloNavegarID:#-------------------------------------------------------------
			print("Navegar")      
					 
			contadorVigilarArduino = 4000
			while True:
				
				if contadorVigilarArduino >=1000:
					contadorVigilarArduino = 0 
					if globalesPiA.modo == MODO_EMERGENCIA:
						comandoArduino(CAMBIAR_MODO, MODO_EMERGENCIA)	
					modoArduino = comandoArduino(LEER_MODO)
					if modoArduino == MODO_EMERGENCIA:
						#print("Arduino EMERGENCIA")
						globalesPiA.modo = MODO_EMERGENCIA
						pubMQTT("navegación/coordObj_geometría", json.dumps({"matar": "m"}))

				contadorVigilarArduino += 1 
				
				if globalesPiA.modo == MODO_NAVEGACION: # sólo ejecutar los próximos pasos si ArduinoA está listo para recibir comandos y si estamos en MODO_NAVEGACION
					

					
					# Primero: obtenemos la información necesaria para poder ejecutar navegar()
					if globalesPiA.marchaOparo == 0 and globalesPiA.permitirSubCoordObj == True:
						print("Before Sub")
						# Utilizar MQTT para sub coordObj y geometria del Servidor         
						subMQTT("navegación/coordObj_geometría")
						globalesPiA.estadoPiA = "Geometria recibida del Servidor... "

						# No calcular una trayectoria hasta recibir una solución adecuada del GPS
						while True:
							if globalesPiA.coordAct == 'obteniendo una solucion...' and globalesPiA.modo == MODO_NAVEGACION:
								globalesPiA.estadoPiA = "Esperando solución para calcular trayectoria"
								print("in While true")
								time.sleep(1)
							else:
								print("in Else")
								break
													
						if globalesPiA.modo == MODO_NAVEGACION:
							# Se construye la trayectoria utilizando la geometria y coordObj
							trayectoria = crearTrayectoria(globalesPiA.coordAct, globalesPiA.coordObj, globalesPiA.geometria)
							globalesPiA.estadoPiA = "Trayectoria calculada con éxito!"
							
							# Utiliza MQTT para publicar trayectoria al Servidor
							trayectoriaPub = json.dumps({"trayectoria": trayectoria, "idSesion": globalesPiA.idSesion}) # se construye trayectoriPub en el formato dict
							globalesPiA.estadoPiA = "Mandando trayectoria al Servidor..."
							pubMQTT("navegación/trayectoria",trayectoriaPub)

							# Se cambia permitirSubCoordObj a False para evitar llamada de sub_coordObj_geometria() otra vez
							globalesPiA.permitirSubCoordObj = False                                 
					
					
					# Segundo: utilizamos la información en el paso previo para ejecutar navegar()
					elif globalesPiA.marchaOparo == 1 and globalesPiA.permitirSubCoordObj == False:
						globalesPiA.estadoPiA = "En Marcha, Navegando..."
						
						# La funcion principal de navegación 
						navegar(trayectoria, globalesPiA.coordObj)
						
											
						# Se resetea algunos variables para poder reiniciar el proceso cuando termine sondeo
						globalesPiA.marchaOparo = 0
						globalesPiA.permitirSubCoordObj = True
						
						#globalesPiA.modo = MODO_SONDEO
				
				elif globalesPiA.modo == MODO_MANUAL:
					#subMQTT("control/ServidorRobot")
					#print ("AFTER WHILE...IN MANUAL MODE")
					
					if globalesPiA.permitirCambioModoManual == True:
						comandoArduino(CAMBIAR_MODO, MODO_MANUAL)
						globalesPiA.permitirCambioModoManual= False
					if globalesPiA.permitirComandoManual== True:
						comandoArduino(RECIBIR_COMANDO_MANUAL, globalesPiA.comandoManual) # mandar comando de navegacion al arduino
						globalesPiA.permitirComandoManual= False
						
				elif globalesPiA.modo == MODO_SONDEO:
				
					comandoArduino(CAMBIAR_MODO, MODO_SONDEO)
					if globalesPiA.reintentoSondeo == 1:
						moverReintentoSondeo()
				 
				
				# Mater hilos seguramente utilizando la entrada de "m" en terminal 
				if matarHilos == 'm':
					break
				
			print("Terminando hilo Navegar")

# Sincronizar modos antes de empezar hilos
pubMQTT("control/RobotServidor/syncModo", 1)

# Crear los hilos
hiloMuerte = Hilo(hiloMatarID)      # mata otros hilos
hiloControl = Hilo(hiloControlID)   # recibe comandos de control del Servidor
hiloModoSync = Hilo(hiloModoSyncID) # sincroniza modos
hiloRTK = Hilo(hiloRTKID)           # obtiene posición actual del robot
hiloCoordAct = Hilo(hiloCoordActID)           # obtiene posición actual del robot
hiloNavegar = Hilo(hiloNavegarID)   # construye trayectoria y hace navegación
hiloEstados = Hilo(hiloEstadosID)

# Empezar los hilos
hiloMuerte.start()
time.sleep(0.25)
hiloEstados.start()
time.sleep(0.25)
hiloControl.start()
time.sleep(0.25)
hiloModoSync.start()
time.sleep(0.25)

hiloRTK.start()
time.sleep(0.25)
hiloCoordAct.start()
time.sleep(0.25)

hiloNavegar.start()


