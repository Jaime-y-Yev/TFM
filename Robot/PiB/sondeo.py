import actuador
import jaula
import sensor
from time import sleep

import sys
sys.path.insert(0, '/home/pi/TFM/Robot')
from comandosParaArduino import *

import globalesPi

import RPi.GPIO as GPIO	

def sondear(coordObj):
	"""Ejecutar un ciclo de sondeo utilizando el movimiento de la jaula, actuador y la sonda"""
	
	# Mover la jaula para revelar el sensor/actuador
	jaula.revelar()     
	
	# Por seguridad, mantener control sobre las etapas del actuador
	globalesPi.expandirActuador = True 
	globalesPi.contraerActuador = False
	
	# Activar y expandir el actuador para insertar el sensor en el suelo
	actuador.expandir() 	
	globalesPi.expandirActuador = False 

	# Si surge un problema de expansión, el actuador se contrae, la jaula se retrae, y se informa del hecho
	if globalesPi.problemaExpandir == True:
		actuador.contraer()

		jaula.retraer()

		globalesPi.expandirActuador = False
		globalesPi.contraerActuador = True
		return		
	# Si no surge un problema de expansión, el sensor hace mediciones
	medicionesDict = sensor.hacerMediciones(coordObj)
	medicionesDict["idSesión"] = globalesPi.idSesion
	
	# Por seguridad, mantener control sobre las etapas del actuador
	globalesPi.expandirActuador = False
	globalesPi.contraerActuador = True
	
	# Contraer el actuador
	actuador.contraer()  

	# Mover la jaula a su posición original
	jaula.retraer()

	return medicionesDict
