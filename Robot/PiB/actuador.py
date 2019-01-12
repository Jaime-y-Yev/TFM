import globalesPi
from time import sleep

import RPi.GPIO as GPIO


# Potenciometro
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

CLK  = 17
MISO = 27 # DOUT
MOSI = 22 # DIN
CS   = 4
potenciometro = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
difMin = 0.1 #1

# Actuador
in1= 21 #40
in2= 20 #38

GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)

GPIO.output(in1, True)
GPIO.output(in2, True)



def contraer():
	"""Contrae el actuador en pasos pequeños"""
	
	tiempoContraer = 1
	t = 0
	
	while True:
		if t <= tiempoContraer and globalesPi.problemaContraer == False:
			print("Contrayendo el actuador")
			GPIO.output(in1, True)
			GPIO.output(in2, False)
			sleep(1)
			GPIO.output(in2, True)
			t = t + 1
		else:
			break

	sleep(2)

def expandir():
	"""Expande el actuador en pasos pequeños"""

	tiempoExpandir = 1 
	t = 0
	
	while True:
		if t <= tiempoExpandir and globalesPi.problemaExpandir == False:
			print("expandiendo actuador")
			globalesPi.expandir = True
			GPIO.output(in1, False)
			GPIO.output(in2, True)
			sleep(1)
			globalesPi.expandir = False
			GPIO.output(in1, True)
			t = t + 1
		else:
			break

	sleep(2)
        

def contraerCompletamente():
	"""Contrae el actuador completamente sin utilizar incrementos"""

	print("Contrayendo el actuador completamente")
	globalesPi.contraer = True
	GPIO.output(in1, True)
	GPIO.output(in2, False)
	sleep(30)
	globalesPi.contraer = False
	GPIO.output(in2, True)

def expandirCompletamente():
	"""Expande el actuador completamente sin utilizar incrementos"""

	print("Expandiendo el actuador completamente")
	globalesPi.contraer = False
	GPIO.output(in1, False)
	GPIO.output(in2, True)
	sleep(30)
	globalesPi.contraer = True
	GPIO.output(in1, True)


def frenar():
	print("Frenando el actuador")
	GPIO.output(in1, True)
	GPIO.output(in2, True)
 

def leerPotenciometro(): 
	"""Leer continuamente el valor del potenciómetro para detectar problemas con la expansión o contracción del actuador"""

	valorOriginal = potenciometro.read_adc(1)
	print("potenciometro de actuador valor original: ",valorOriginal)
	sleep(0.5)
	potDifCandidatos = [0,0,0]
	while True:	   

		if globalesPi.expandirActuador == False:
			break
		
		valorAct = potenciometro.read_adc(1)		
		
		difPot = abs(valorAct-valorOriginal) 	# Caso real
		#difPot = 10 							# Simular casos sin problema
		#difPot = 0 							# Simular casos con problema
		print("Rotación del potenciómetro: ",difPot)
		potDifCandidatos.append(difPot)
		potDifCandidatos.pop(0)
		valorDifPromedio = sum(potDifCandidatos)/len(potDifCandidatos)
		print("Lista actual de los valores del potenciómetro: ",potDifCandidatos)
		print("Promedio de los valores del potenciómetro: ",valorDifPromedio)

					
		if valorDifPromedio <= difMin:
			print("------------------------------------------------------Problema con la penetración, piedras-------------------------------------------------")
			globalesPi.problemaExpandir = True      
			globalesPi.expandirActuador = False
			break
		
				  
		print("Valor actual del potenciómetro: ",valorAct)
		valorOriginal = valorAct
		sleep(0.5) #1
		


def actuadorTest():
	#contraerCompletamente()
	valorOriginal = potenciometro.read_adc(1)
	print("valorOriginal: ",valorOriginal)
	expandir()
	sleep(1)
	valorFinal = potenciometro.read_adc(1)
	print("valorFinal: ",valorFinal)

	contraer()
	sleep(1)

	GPIO.cleanup()

#actuadorTest()
#leerPotenciometro()
