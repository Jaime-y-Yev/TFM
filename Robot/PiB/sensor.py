#!/usr/bin/env python
import minimalmodbus
from time import sleep

from guardarMediciones import guardarMed

# Definir los parámetros del sensor
minimalmodbus.BAUDRATE = 9600
minimalmodbus.TIMEOUT = 0.2 
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # (puerto, dirección del esclavo)
instrument.debug = True

def hacerMediciones(coordObj=None,sustancia=None):
	"""Medir las distintas propiedades del suelo"""

	# Indicar textura de tierra 0=mineral,1=arena,2=arcilla,3=turba
	if sustancia == "mineral":
		instrument.write_register(32,0)  	# número del registro, textura
	elif sustancia	== "arena":
		instrument.write_register(32,1) 
	elif sustancia	== "arcilla":
		instrument.write_register(32,2) 
	elif sustancia	== "turba":
		instrument.write_register(32,3)	
	else:
		instrument.write_register(32,0) 		
	
	sleep(0.5)
	
	texturaTierra = instrument.read_register(32) # Leer registro para comprobar textura de tierra
	print ("Analizando tierra de textura: ", texturaTierra)
	
	# Hacer mediciones
	temperatura = instrument.read_register(0,2) # Temperatura (c)
	print ("Temperatura: ",temperatura)
	#print (type(temperatura))

	sleep(0.5)

	humedad = instrument.read_register(1,2) 	# Humedad (%)
	print ("Humedad: ", humedad)
	#print (type(humedad))

	sleep(0.5)

	ec= instrument.read_register(2) 			# EC (0-20000)
	print ("EC: ", ec)
	#print (type(ec))

	sleep(0.5)

	salinidad= instrument.read_register(3) 		# Salinidad (0-20000 mg/L)
	print ("Salinidad: ", salinidad)
	#print (type(salinidad))

	sleep(0.5)

	sdt= instrument.read_register(4) 			# Sólidos disueltos totales (0-20000 mg/L)
	print ("SDT: ", sdt)
	#print (type(sdt))

	sleep(0.5)

	epsilon = instrument.read_register(5,2) 	# Constante dieléctrica (0-20000 mg/L)
	print ("Epsilon: ", epsilon)
	#print (type(epsilon))

	sleep(0.5)

	medicionesDict = {"coordObj": coordObj, "Temperatura": temperatura, "Humedad": humedad, "EC": ec, "Salinidad": salinidad, "SDT": sdt, "Epsilon": epsilon}

	#guardarMed("CompilacionDatos",medicionesDict,sustancia) # Opcional, si quiero guardar las medidas
	
	sleep(3)
	
	return medicionesDict


#hacerMediciones(sustancia="aire")

def compilarDatos(cantidad,sustancia):
	for i in range(cantidad):
		hacerMediciones(sustancia=sustancia)
		sleep(1)
#compilarDatos(100,"turba") # 230ml of water. note last two measurements are 6.5 and 8g salt. also remove last 3 measurements from turba
