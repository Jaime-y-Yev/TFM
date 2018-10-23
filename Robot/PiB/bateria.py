import RPi.GPIO as GPIO
from time import sleep

pinInterrupción = 18

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pinInterrupción, GPIO.OUT)

def pulsoInterrupción(tiempoPulso):
    GPIO.output(pinInterrupción, False)
    sleep(0.2)
    GPIO.output(pinInterrupción, True)
    sleep(tiempoPulso)
    GPIO.output(pinInterrupción, False)

def desconectar():
    pulsoInterrupción(0.25)    

def conectar():
    pulsoInterrupción(1.25)

##while True:
##    sleep(1)
##    desconectar()
##    sleep(1)
##    conectar()

##desconectar()
##sleep(1)
conectar()
sleep(1)
desconectar()
sleep(1)


GPIO.cleanup()    

