import time
# Aquí están las definiciones del los códigos seguidas por ComandoArduino(), la función que comunica a la RPi con el Arduino
# mediante el puerto serie USB.
# 
# OJO:
#   - En el Arduino quitar todos Serial.prints() que no contengan una respuesta del Arduino a la RPi antes de utilizar esta función
#   - Cualquier modificación de las líneas demarcadas será propagada al encabezamiento en /ArduinoA/headers/comandos.h
#     debido a la función de actualizarCódigosDeComandos.py 


import serial                   # comunicación serie USB
from decimal import Decimal     # redondeo de floats 


### COMIENZO DE CÓDIGOS --- NO MODIFICAR ESTA LÍNEA ###

LEER_MODO = 10
CAMBIAR_MODO = 11
MODO_EMERGENCIA = 0
MODO_INACTIVO = 1
MODO_NAVEGACION = 2
MODO_SONDEO = 3
MODO_MANUAL = 4

CONFIRMAR_DATOS = 20

RECIBIR_DIRECCION_DISTANCIA_OBJ = 30

RECIBIR_COMANDO_MANUAL = 40

### FINAL DE CÓDIGOS --- NO MODIFICAR ESTA LÍNEA ###

# TODO: automatizar la actualización de los caracteres de inciación y terminación en comandos.h
CARACTER_DE_INICIACION = 'X'
CARACTER_DE_TERMINACION = 'x'

# Abrir la conexión serie USB con el Arduino
arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=2) 
time.sleep(2)


def comandoArduino(comando, valor1=None, valor2=None):
	"""Envía un comando y, opcionalmente, uno o dos valores, esperando en cada caso un echo del valor(es)"""    

	# Al intentar enviar la dirección y distancia al Arduino, se debe estandarizar el número de caracteres que va a recibir,
	# independientemente del número de dígitos de la dirección o distancia por lo que se rellenan con ceros cuando haga falta  
	# Simultáneamente se apunta el número de dígitos para facilitar la comprobación posterior del echo
	if comando == RECIBIR_DIRECCION_DISTANCIA_OBJ:
		
		# La dirección siempre debe tener tres dígitos (0-359 grados)
		if valor1 != None:
			# Ej:   3 --> "00"+3 --> 003
			if valor1 < 10:
				relleno1 = "00"
				numDígitos = 1
			# Ej:  23 --> "0"+23 --> 023
			elif valor1 >= 10 and valor1 < 100:
				relleno1 = "0"
				numDígitos = 2
			# Ej: 123 --> ""+123 --> 123
			elif valor1 >= 100:
				relleno1 = ""
				numDígitos = 3
			
		# La dirección siempre debe tener dos decimales (el GPS tiene una precisión de decímetros) 
		# por lo que se convierte a un float redondeado antes de rellenar con ceros
		if valor2 != None:
			# Ej: 123.456 m --> 123.45 m
			valor2 = Decimal(valor2)
			valor2 = float(round(valor2,2))

			# Ej:    4.56 --> "000"+4.56 --> 0004.56
			if valor2 < 10:
				relleno2 = "000"
			# Ej:   34.56 --> "00"+34.56 --> 0034.56
			elif valor2 >= 10 and valor2 < 100:
				relleno2 = "00"
			# Ej:  234.56 --> "0"+234.56 --> 0234.56
			elif valor2 >= 100 and valor2 < 1000:
				relleno2 = "0"
			# Ej: 1234.56 --> ""+1234.56 --> 1234.56
			elif valor2 >= 1000:
				relleno2 = ""

	# Los demás comandos no requieren relleno        
	else:
		relleno1 = ""
		relleno2 = ""
		
	# Preparar el mensaje, que incluye el comando y los dos parámetros opcionales propiamente estandarizados
	# Ej: comandoArduino(RECIBIR_DIRECCION_DISTANCIA_OBJ, 12, 123.4567) --> 
	#       mensaje = "17" + "012" + "0123.46" = "170120123.46"
	mensaje = str(comando) + relleno1 + str(valor1) + relleno2 + str(valor2) #comando=comando (ej CAMBIAR_MODO),valor1/valor2=segunda parte de comando (ej MODO_NAVEGACION)   

	# Protegerse ante las posibles excepciones IOError o SerialTimeoutException
	while True:

		try:
			#print("Comunicación serie: RPi --> ", mensaje, " --> Arduino")
			
			# Escribir los caracteres del mensaje al búfer
			for caracter in mensaje:
				arduino.write(caracter.encode('utf-8'))
			
			# Esperar a que se envíen todos los bytes del mensaje, paralizando la función hasta que queden cero bytes en el búfer de salida
			while True:
				if arduino.out_waiting == 0:
					break
			
			# Leer la respuesta del Arduino para confirmar que no ha habido problemas de comuniación
			respuesta = str(arduino.readline())
			
			#print("after respuesta = ", respuesta)

			# Esperar a que se reciban todos los bytes de la respuesta, paralizando la función hasta que queden cero bytes en el búfer de entrada
			while True:
				if arduino.in_waiting == 0:
					break

			#print("after while")

			
			# El Arduino devuelve una respuesta de la forma b'xyz', así que quitar b' del principio y ' del final
			respuesta = respuesta[2:len(respuesta)-5]   
			
			#print("Comunicación serie: RPi <-- ", respuesta, " <-- Arduino")
			
			# Se debe recibir la respuesta propiamente iniciada y terminada
			if respuesta[0] == CARACTER_DE_INICIACION and respuesta[len(respuesta)-1] == CARACTER_DE_TERMINACION:
				
				# Acceder al contenido de la respuesta entre los caracteres de iniciación y de terminación
				respuesta = respuesta[1:len(respuesta)-1]
				#print("respuesta:",respuesta)
				
				#print("comando:",comando)

				# La lectura del modo debe responderse con uno de los cinco modos
				if comando == LEER_MODO:
					
					# Convertir el modo de caracter a un entero
					modo = int(respuesta)          
					
					# Si se ha recibido uno de los cinco modos, devolverlo
					if modo == MODO_EMERGENCIA or modo == MODO_INACTIVO or modo == MODO_NAVEGACION or modo == MODO_SONDEO or modo == MODO_MANUAL:
						print("«---------- Modo de Arduino es ", modo)
						return modo
					else:
						print("Comunicación serie: Error al leer el modo del Arduino")
				
				# El cambio de modo debe responderse con el nuevo modo
				elif comando == CAMBIAR_MODO:
					
					# Convertir el modo de caracter a un entero
					modo = int(respuesta)

					# Si se ha recibido el modo que se envíó, devolverlo
					if modo == valor1:
						print("«----------Arduino ha cambiado modo a ", modo)
						return modo
					else:
						print("Comunicación serie: Error al cambiar el modo del Arduino")
				
				# La confirmación de llegada debe responderse con su estado (0 ó 1)
				elif comando == CONFIRMAR_DATOS:



					# Convertir la llegada de caracter a un entero   
					llegada = int(respuesta[0])
					casoNavegacion = int(respuesta[1])
					direccionAct = int(respuesta[2:])
					
					#print("llegada = ", llegada)
					#print("casoNavegacion = ", casoNavegacion)
					#print("direccionAct = ", direccionAct)

					
					# Si se ha recibido el estado de la llegada, devolverlo
					if (llegada == 0 or llegada == 1) and (0 <= casoNavegacion and casoNavegacion <= 9) and (0 <= direccionAct and direccionAct <= 359):

						#if llegada == 0:
							#print("Comunicación serie: Arduino NO HA LLEGADO todavía al objetivo actual")
						#elif llegada == 1:
							#print("Comunicación serie: Arduino HA LLEGADO al objetivo actual")
						
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

						return llegada, casoNavegacion, direccionAct
					else:
						print("Comunicación serie: Error al leer los datos del Arduino")
				
				# El envío de la dirección y distancia debe responderse con éstos mismos valores
				elif comando == RECIBIR_DIRECCION_DISTANCIA_OBJ:
					
					# Convertir a sus tipos respectivos   
					dirección = int(respuesta[:numDígitos])
					distancia = float(respuesta[numDígitos:])

					# Si se ha recibido la direccción y distancia enviada, devolverlas
					if dirección == valor1 and distancia == valor2:

						print("«---------- El Arduino ha recibido la dirección ", dirección, " y la distancia ", distancia)
						return dirección, distancia
					else:
						print("Comunicación serie: Error al leer la dirección y distancia del Arduino")
						
				# El envío de un comando manual debe responderse con dicho comando
				elif comando == RECIBIR_COMANDO_MANUAL:

					# La respuesta ya tiene el formato deseado
					return respuesta
					
			
			# Notificar de una respuesta incompleta o corrupta
			else:
				print("Comunicación serie: Error en la estructura de la respuesta de Arduino")

		# Reintentar el envío del mensaje al Arduino y la lectura de su respuesta
		except:
			print("Comunicación serie: Excepción en comando de Arduino. Reintentando...")

        
# Función para pruebas y depuración
def testComandos():
    
    while True:
           
        modoCambiado = comandoArduino(CAMBIAR_MODO, MODO_NAVEGACION)
        print("modoCambiado = " + str(modoCambiado))
        
        print()
                        
        modoLeído = comandoArduino(LEER_MODO)
        print("modoLeído = " + str(modoLeído))
        
        print()

        if modoLeído == MODO_NAVEGACION:
            
            llegada, casoNavegacion, direccionAct = comandoArduino(CONFIRMAR_DATOS)
            print("llegada = " + str(llegada))
            print("casoNavegacion = " + str(casoNavegacion))
            print("direccionAct = " + str(direccionAct))

            
            print()

            direcciónObj, distanciaObj = comandoArduino(RECIBIR_DIRECCION_DISTANCIA_OBJ, 123, 4567.89299999999)
            print("direccionObj recibida = " + str(direcciónObj))
            print("distanciaObj recibida = " + str(distanciaObj))
        
        elif modoLeído == MODO_MANUAL:
            
            comandoManual = comandoArduino(RECIBIR_COMANDO_MANUAL, "ar")
            print("comandoManual = ", comandoManual)
            
            time.sleep(3)
            
            comandoManual = comandoArduino(RECIBIR_COMANDO_MANUAL, "pp")
            print("comandoManual = " + str(comandoManual))
            
            time.sleep(1)

            
        
        print()
        print()


#testComandos()
