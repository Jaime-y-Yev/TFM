import globalesPiB
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
difMin = 25

# Actuador

# Define GPIO signals to use
# Physical pins 40(in1),38(in2)
# GPIO21,GPIO20
#GPIO.setmode(GPIO.BOARD)

in1= 21 #40
in2= 20 #38

GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)

GPIO.output(in1, True)
GPIO.output(in2, True)



def contraer():
    tiempoContraer = 2
##    print("contrayendo actuador")
##    GPIO.output(in1, True)
##    GPIO.output(in2, False)
####    sleep(30)
##    sleep(2)
##    GPIO.output(in2, True)
    t = 0
    while True:
        if t <= tiempoContraer and globalesPiB.problemaContraer == False:
            print("contrayendo actuador")
            GPIO.output(in1, True)
            GPIO.output(in2, False)
        ##    sleep(30)
            sleep(1)
            GPIO.output(in2, True)
            t = t + 1
        else:
            break

def expandir():
    tiempoExpandir = 2
##    print("expandiendo actuador")
##    globalesPiB.expandir = True
##    GPIO.output(in1, False)
##    GPIO.output(in2, True)
####    sleep(35)
##    sleep(2)
##    globalesPiB.expandir = False
##    GPIO.output(in1, True)
    t = 0
    while True:
        if t <= tiempoExpandir and globalesPiB.problemaExpandir == False:
            print("expandiendo actuador")
            globalesPiB.expandir = True
            GPIO.output(in1, False)
            GPIO.output(in2, True)
        ##    sleep(35)
            sleep(1)
            globalesPiB.expandir = False
            GPIO.output(in1, True)
            t = t + 1
        else:
            break
        

def contraerCompletamente():
    print("contrayendo actuador completamente")
    globalesPiB.contraer = True
    GPIO.output(in1, True)
    GPIO.output(in2, False)
    sleep(30)
    #sleep(2)
    globalesPiB.contraer = False
    GPIO.output(in2, True)

def expandirCompletamente():
    print("expandiendo actuador completamente")
    globalesPiB.contraer = False
    GPIO.output(in1, False)
    GPIO.output(in2, True)
    sleep(30)
    globalesPiB.contraer = True
    GPIO.output(in1, True)


def frenar():
    print("frenando")
    GPIO.output(in1, True)
    GPIO.output(in2, True)
   

def leerPotenciometro(): 

	valorOriginal = potenciometro.read_adc(1)
	print(valorOriginal)
	sleep(0.5)

	while True:
		
		if globalesPiB.matarPotenciometro == True:
			break
			   
		valorAct = potenciometro.read_adc(1)
		if globalesPiB.expandirActuador == True:
			if (valorAct-valorOriginal)< difMin:
				globalesPiB.intentoSondear += 1
				globalesPiB.problemaExpandir = True      

		elif globalesPiB.contraerActuador == True:
			if (valorOriginal-valorAct)< difMin:
				globalesPiB.problemaContraer = True  
		print(valorAct)
		valorOriginal = valorAct
		sleep(0.5) 


def actuadorTest():
    #leerPotenciometro()
    expandir()
    sleep(1)
    #leerPotenciometro()
    contraer()
    sleep(1)
    #leerPotenciometro()
    
    GPIO.cleanup()

#actuadorTest()

#expandirCompletamente()
#expandir()
#contraerCompletamente()
#frenar()
##contraerCompletamente()
