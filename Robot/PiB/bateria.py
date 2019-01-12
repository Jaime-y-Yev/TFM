import RPi.GPIO as GPIO
from time import sleep


GPIO.setmode(GPIO.BCM)
pinInterrupción1 = 24
pinInterrupción2 = 23

GPIO.setup(pinInterrupción1, GPIO.OUT)
GPIO.setup(pinInterrupción2, GPIO.OUT)


def desconectar():
	"""Causar una interrupción en uno de los pines de ArduinoB para desconectar la batería"""

	GPIO.output(pinInterrupción1, True)
	sleep(0.5)
	GPIO.output(pinInterrupción1, False)
	sleep(0.2)

def conectar():
	"""Causar una interrupción en uno de los pines de ArduinoB para conectar la batería"""

	GPIO.output(pinInterrupción2, True)
	sleep(0.5)
	GPIO.output(pinInterrupción2, False)
	sleep(0.2)


def testRele():
	desconectar()
	sleep(1)
	conectar()
	sleep(1)

	while True:
		inp = input()
		if inp == 'm':
			break 

	desconectar()
	sleep(2)


	GPIO.cleanup() 
	sleep(1) 
    
 

#testRele()
#desconectar()
#conectar()
