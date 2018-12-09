import actuador
import jaula
import sensor
from time import sleep

from comandosParaArduinoB import *
import globalesPiB

import RPi.GPIO as GPIO

def sondear():
	errores = []
	jaula.revelar()     # mover la jaula para revelar el sensor/actuador
	sleep(1)

	actuador.expandir() # activar y expandir el actuador para insertar el sensor en el suelo 
	if globalesPiB.problemaExpandir == False:
		
		# MEDICIÓN POR SENSOR
		sensor.hacerMediciones()
	   
	actuador.contraer() # contraer el actuador    
	if globalesPiB.problemaContraer == False:
		sleep(1)        
		jaula.retraer()     # mover la jaula hacia la posición inicial

	#Si ocurren problemas
	if globalesPiB.problemaContraer == True:
		#PUB UNABLE TO CONTRACT
		errores.append(1)
		globalesPiB.modo = MODO_EMERGENCIA        
			  
	if globalesPiB.problemaExpandir == True:
		sleep(1)
		if globalesPiB.intentoSondear <= 3: 
			contraerCompletamente()
			#PUB MOVE 10 CM FOREWARD
			pubMQTT("control/ServidorRobot",json.dumps({"reintentoSondeo":1}))
			errores.append(2)
			
		elif globalesPiB.intentoSondear > 3:
			errores.append(3)
			#PUB UNABLE TO TAKE MEASUREMENT, NEXT COORDOBJ
			globalesPiB.modo = MODO_INACTIVO
	# Reseteo de variables 
	globalesPiB.problemaExpandir = False
	globalesPiB.problemaContraer = False

	##    GPIO.cleanup()

	return errores

##sondear()
