import RPi.GPIO as GPIO
from time import sleep

##GPIO.setmode(GPIO.BOARD)
##pinInterrupción = 18

GPIO.setmode(GPIO.BCM)
##pinInterrupción = 24
pinInterrupción1 = 24
pinInterrupción2 = 23

#GPIO.setup(pinInterrupción, GPIO.OUT)
GPIO.setup(pinInterrupción1, GPIO.OUT)
GPIO.setup(pinInterrupción2, GPIO.OUT)


#def pulsoInterrupción(tiempoPulso):
#    GPIO.output(pinInterrupción, False)
#    sleep(0.2)
#    GPIO.output(pinInterrupción, True)
#    sleep(tiempoPulso)
#	GPIO.output(pinInterrupción, False)

def desconectar():
    #pulsoInterrupción(0.25)
    GPIO.output(pinInterrupción1, True)
    sleep(0.5)
    GPIO.output(pinInterrupción1, False)
    sleep(0.2)

def conectar():
    #pulsoInterrupción(1.25)
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


	
