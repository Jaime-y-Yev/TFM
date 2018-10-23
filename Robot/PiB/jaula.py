import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

servoPin = 12
GPIO.setup(servoPin, GPIO.OUT)
servoPWM = GPIO.PWM(servoPin, 50)
servoPWM.start(0)
angleIn = 55
angleOut = 133
ultimoAngulo = angleIn
##def setAngle(angle):
##    duty = angle/18 + 2
##    GPIO.output(servoPin, True)
##    servoPWM.ChangeDutyCycle(duty)
##    sleep(3)
##    GPIO.output(servoPin, False)
##    servoPWM.ChangeDutyCycle(0)
##
##def revelar():
##    print("revelando jaula")
##    setAngle(angleOut)
##
##
##def retraer():
##    print("retrayendo jaula")
##    setAngle(angleIn)

def revelar():

    print("revelando jaula")
    GPIO.output(servoPin, True)

    for angulo in range(ultimoAngulo, angleOut):
        duty = angulo/18 + 2
        servoPWM.ChangeDutyCycle(duty)
        sleep(0.05)

    GPIO.output(servoPin, False)
    servoPWM.ChangeDutyCycle(0)
    global ultimoAngulo
    ultimoAngulo = angleOut
##    sleep(3)



def retraer():
    
    print("retrayendo jaula")
    GPIO.output(servoPin, True)

    for angulo in range(ultimoAngulo, angleIn, -1):
        duty = angulo/18 + 2
        servoPWM.ChangeDutyCycle(duty)
        sleep(0.05)

    GPIO.output(servoPin, False)
    servoPWM.ChangeDutyCycle(0)
##    sleep(3)
    global ultimoAngulo
    ultimoAngulo = angleIn
    
#revelar()
#retraer()
#GPIO.cleanup()