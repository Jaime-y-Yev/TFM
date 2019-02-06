from time import sleep
# Aquí están las definiciones del los códigos seguidas por ComandoArduino(), la función que comunica a la RPi con el Arduino
# mediante el puerto serie USB.
# 
# OJO:
#   - En el Arduino quitar todos Serial.prints() que no contengan una respuesta del Arduino a la RPi antes de utilizar esta función
#   - Cualquier modificación de las líneas demarcadas será propagada al encabezamiento en /ArduinoA/headers/comandos.h
#     debido a la función de actualizarCódigosDeComandos.py 

import serial                   # comunicación serie USB
from decimal import Decimal     # redondeo de floats 

from actualizarCodigosDeComandos import *

### COMIENZO DE CÓDIGOS --- NO MODIFICAR ESTA LÍNEA ###

LEER_MODO = 10
CAMBIAR_MODO = 11
MODO_EMERGENCIA = 0
MODO_INACTIVO = 1
MODO_NAVEGACION = 2
MODO_SONDEO = 3
MODO_MANUAL = 4

CONFIRMAR_DATOS = 20

RECIBIR_DIRECCION_OBJ = 30
RECIBIR_DISTANCIA_OBJ = 31


RECIBIR_COMANDO_MANUAL = 40

### FINAL DE CÓDIGOS --- NO MODIFICAR ESTA LÍNEA ###

import sys
sys.path.insert(0, '/home/pi/TFM/Robot/PiA')
import globalesPi


numExcepciones = 0

# Abrir la conexión serie USB con el Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=2, parity=serial.PARITY_EVEN) 
sleep(3)


def comandoArduino(comando, valor=None):
	"""Envía un comando y, opcionalmente, uno o dos valores, esperando en cada caso un echo del valor(es)"""    

	# El mensaje incluye el comando y, opcionalmente, un valor 
	mensaje = str(comando) + str(valor) 

	# Protegerse ante las posibles excepciones IOError o SerialTimeoutException
	global numExcepciones
	while True:

		try:
			sleep(1)

			print("Comunicación serie: RPi --> ", mensaje, " --> Arduino")
			
			# Escribir los caracteres del mensaje al búfer
			arduino.write(mensaje.encode('utf-8'))
			#for caracter in mensaje:
			#	arduino.write(caracter.encode('utf-8'))
			
			# Esperar a que se envíen todos los bytes del mensaje, paralizando la función hasta que queden cero bytes en el búfer de salida
			#while True:
				#if arduino.out_waiting == 0:
					#break
			
			# Leer la respuesta del Arduino para confirmar que no ha habido problemas de comuniación
			respuesta = arduino.readline()		
			respuesta = respuesta.decode('utf-8')
						
			# Esperar a que se reciban todos los bytes de la respuesta, paralizando la función hasta que queden cero bytes en el búfer de entrada
			#while True:
				#if arduino.in_waiting == 0:
					#break
					
			print("Comunicación serie: RPi <-- ", respuesta, " <-- Arduino")
			
			# La lectura del modo debe responderse con uno de los cinco modos
			if comando == LEER_MODO:
				
				# Convertir el modo de caracter a un entero
				modo = int(respuesta)   
				
				# Si se ha recibido uno de los cinco modos, devolverlo
				if modo == MODO_EMERGENCIA or modo == MODO_INACTIVO or modo == MODO_NAVEGACION or modo == MODO_SONDEO or modo == MODO_MANUAL:
					globalesPi.estadoArduinoA = "Modo: " + str(modo) 
					print("«---------- El modo actual del Arduino es ", modo)
					numExcepciones = 0
					return modo
				else:
					print("Comunicación serie: Error al leer el modo del Arduino")
			
			# El cambio de modo debe responderse con el nuevo modo
			elif comando == CAMBIAR_MODO:
				
				# Convertir el modo de caracter a un entero
				modo = int(respuesta)

				# Si se ha recibido el modo que se envíó, devolverlo
				if modo == valor:
					globalesPi.estadoArduinoA = "Cambiando modo a " + str(modo) 
					print("«---------- El Arduino ha cambiado su modo a ", modo)
					numExcepciones = 0
					return modo
				else:
					print("Comunicación serie: Error al cambiar el modo del Arduino")
			
			# La confirmación de llegada debe responderse con el caso de navegación del Arduino, y su dirección actual
			elif comando == CONFIRMAR_DATOS:

				# Dividir la respuesta en los parámetros deseados   
				casoNavegacion = int(respuesta[0])
				direccionAct = int(respuesta[1:])
									
				# Devolver el estado de la llegadalo, el caso de navegación, y la dirección actual
				if (0 <= casoNavegacion and casoNavegacion <= 9) and (0 <= direccionAct and direccionAct <= 359):
					
					if casoNavegacion == 0:
						casoNavegacion = "Caso navegación: desconocido"
					elif casoNavegacion == 1:
						casoNavegacion = "Caso navegación: obstáculo de frente demasiado cerca, parando"
					elif casoNavegacion == 2:
						casoNavegacion = "Caso navegación: obstáculo de lado demasiado cerca, desviando"
					elif casoNavegacion == 3:
						casoNavegacion = "Caso navegación: obstáculo de frente con espacio, retrocediendo"
					elif casoNavegacion == 4:
						casoNavegacion = "Caso navegación: evitando obstáculo"
					elif casoNavegacion == 5:
						casoNavegacion = "Caso navegación: obstáculo no muy lejos"
					elif casoNavegacion == 6:
						casoNavegacion = "Caso navegación: obstáculo muy lejos"
					elif casoNavegacion == 7:
						casoNavegacion = "Caso navegación: entre filas"
					elif casoNavegacion == 9:
						casoNavegacion = "Caso navegación: no navegando"

					numExcepciones = 0
					return casoNavegacion, direccionAct
				else:
					print("Comunicación serie: Error al leer los datos del Arduino")
			
			# El envío de la dirección y distancia debe responderse con éstos mismos valores
			elif comando == RECIBIR_DIRECCION_OBJ:
				
				# Convertir a sus tipos respectivos   
				dirección = int(respuesta)
				
				# Si se ha recibido la direccción y distancia enviada, devolverlas
				if dirección == valor:

					print("«---------- El Arduino ha recibido la dirección ", dirección)
					numExcepciones = 0
					return dirección
				else:
					print("Comunicación serie: Error al leer la dirección del Arduino")

			elif comando == RECIBIR_DISTANCIA_OBJ:
				
				# Convertir a sus tipos respectivos   
				distancia = float(respuesta)

				# Si se ha recibido la direccción y distancia enviada, devolverlas
				if distancia == valor:

					print("«---------- El Arduino ha recibido la distancia ", distancia)
					numExcepciones = 0
					return distancia
				else:
					print("Comunicación serie: Error al leer la distancia del Arduino")

					
			# El envío de un comando manual debe responderse con dicho comando
			elif comando == RECIBIR_COMANDO_MANUAL:

				# La respuesta ya tiene el formato deseado
				numExcepciones = 0
				return respuesta
				
		# Reintentar el envío del mensaje al Arduino y la lectura de su respuesta
		except:
			print("Comunicación serie: Excepción en comando de Arduino. Reintentando...")
			numExcepciones += 1
			
			print("numExcepciones = ", numExcepciones)
			
			if numExcepciones >= 15:
				numExcepciones = 0
				subirArduino()
				vigilarModoArduino()
				break
				
			sleep(1)
			
def vigilarModoArduino():
	"""Asegurarse de que los modos de la RPi y el Arduino están sincronizados, y que el Arduino no tiene una emergencia"""
	 
	sleep(1)
	modoArduino = comandoArduino(LEER_MODO)

	if modoArduino == MODO_EMERGENCIA:
		globalesPi.modo = MODO_EMERGENCIA
	sleep(1)
	
	if modoArduino != globalesPi.modo:
		comandoArduino(CAMBIAR_MODO, globalesPi.modo)	

        
def testComandos(): # depuración
    
	while True:
		   
		modoLeído = comandoArduino(LEER_MODO)
		print("modoLeído = " + str(modoLeído))

		print()

		modoCambiado = comandoArduino(CAMBIAR_MODO, MODO_NAVEGACION)
		print("modoCambiado = " + str(modoCambiado))
		
		print()

		if modoLeído == MODO_NAVEGACION:
			
			casoNavegacion, direccionAct = comandoArduino(CONFIRMAR_DATOS)
			print("casoNavegacion = " + str(casoNavegacion))
			print("direccionAct = " + str(direccionAct))
			
			print()

			direcciónObj = comandoArduino(RECIBIR_DIRECCION_OBJ, 20)
			print("direccionObj = " + str(direcciónObj))
		
			distanciaObj = comandoArduino(RECIBIR_DISTANCIA_OBJ, 2.00)
			print("distanciaObj = " + str(distanciaObj))
		
		elif modoLeído == MODO_MANUAL:
			
			comandoManual = comandoArduino(RECIBIR_COMANDO_MANUAL, "ar")
			print("comandoManual = ", comandoManual)
						
			comandoManual = comandoArduino(RECIBIR_COMANDO_MANUAL, "pp")
			print("comandoManual = " + str(comandoManual))
						
		
		print()
		print()


#testComandos()
