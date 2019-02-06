import RPi.GPIO as GPIO
from time import sleep


GPIO.setmode(GPIO.BCM)
servoPin = 18

# Preparar el pwm del servo
GPIO.setup(servoPin, GPIO.OUT)
servoPWM = GPIO.PWM(servoPin, 50)
servoPWM.start(0)

# Angulos que el servo tiene que girar para desplazar la jaula
angleIn = 20 
angleOut = 100  

def setAngle(angle):
    duty = angle/18 + 2
    GPIO.output(servoPin, True)
    servoPWM.ChangeDutyCycle(duty)
    sleep(3)
    GPIO.output(servoPin, False)
    servoPWM.ChangeDutyCycle(0)

#~ def revelar():
    #~ print("revelando jaula")
    #~ setAngle(angleOut)


#~ def retraer():
    #~ print("retrayendo jaula")
    #~ setAngle(angleIn)

def revelar():
	"""Mover la jaula sobre el agujero para poder expandir el actuador"""

	print("Revelando la jaula")
	GPIO.output(servoPin, True)

	# Utilizar pequeños incrementos para reducir la velocidad de la jaula
	for angulo in range(angleIn, angleOut, 3):
		duty = angulo/18 + 2
		servoPWM.ChangeDutyCycle(duty)
		sleep(0.08)

	GPIO.output(servoPin, False)
	servoPWM.ChangeDutyCycle(0)
	sleep(2)



def retraer():
	"""Mover la jaula a su posición original"""

	print("Retrayendo la jaula")
	GPIO.output(servoPin, True)

	# Utilizar pequeños incrementos para reducir la velocidad de la jaula
	for angulo in range(angleOut, angleIn, -3):
		duty = angulo/18 + 2
		servoPWM.ChangeDutyCycle(duty)
		sleep(0.08)

	GPIO.output(servoPin, False)
	servoPWM.ChangeDutyCycle(0)
	sleep(2)

def testJaula():   
    revelar()
    retraer()
    GPIO.cleanup()

#testJaula()

# Para acoplar el servo en la posición correcta:
# con el servo desacoplado, girar a 90 grados
#setAngle(90)
# Tirar de jaula hacia atrás lo más posible
# Acoplar servo
# 20 debería retraer, y 100 revelar

