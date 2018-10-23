from time import sleep
import RPi.GPIO as GPIO



# Define GPIO signals to use
# Physical pins 40(in1),38(in2)
# GPIO21,GPIO20

in1=40
in2=38

GPIO.setmode(GPIO.BOARD)

GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)

def contraer():
    print("contrayendo actuador")
    GPIO.output(in1, True)
    GPIO.output(in2, False)
##    sleep(30)
    sleep(2)
    GPIO.output(in2, True)
    

def expandir():
    print("expandiendo actuador")
    GPIO.output(in1, False)
    GPIO.output(in2, True)
##    sleep(35)
    sleep(2)
    GPIO.output(in1, True)

def contraerCompletamente():
    print("contrayendo actuador")
    GPIO.output(in1, True)
    GPIO.output(in2, False)
    sleep(30)
    #sleep(2)
    GPIO.output(in2, True)


def frenar():
    print("frenando")
    GPIO.output(in1, True)
    GPIO.output(in2, True)
   

def actuadorTest():
    expandir()
    sleep(1)
    contraer()
    sleep(1)
    
    GPIO.cleanup()


##actuadorTest()
#frenar()
##contraerCompletamente()