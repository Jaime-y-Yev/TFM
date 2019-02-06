import subprocess
from time import sleep
import globalesPi


import pigpio

print("Matando el proceso de pigpiod")
subprocess.Popen(['sudo', 'killall', 'pigpiod'], shell=False)
	
sleep(1)

print("Reiniciando el proceso de pigpiod")
subprocess.Popen(['sudo', 'pigpiod'], shell=False)
sleep(1)

# Dependiendo del servo (de giro horizontal y de giro vertical), los límites de movimiento son distintos
pinServoID = 19
pinServoAA = 26

pulsoLimiteDerecha = 600;
pulsoLimiteIzquierda = 2000;
pulsoCentroID = 1300

pulsoLimiteArriba = 1700
pulsoLimiteAbajo = 2400
pulsoCentroAA = 2000


pi = pigpio.pi()

if not pi.connected:
    print("Pigpio no conectado")

def moverServo(pinServo, posicion):
	
	if pinServo == pinServoID:
		servoUtilizado = "ID"
		limiteMin = pulsoLimiteDerecha
		limiteMax = pulsoLimiteIzquierda
	elif pinServo == pinServoAA:
		servoUtilizado = "AA"		
		limiteMin = pulsoLimiteArriba
		limiteMax = pulsoLimiteAbajo
		
	print("Moviendo el servo ", servoUtilizado)

	# Vigilar que el servo no sobrepasa sus límites
	if (posicion < limiteMin or posicion > limiteMax):		
		print("La cámara esta en un extremo")
		return
		
	pi.set_servo_pulsewidth(pinServo, posicion)



def posicionInicial():
	moverServo(pinServoID, pulsoCentroID)
	moverServo(pinServoAA, pulsoCentroAA)

posicionInicial()

def girarCentroIzquierda():
	moverServo(pinServoID, pulsoLimiteIzquierda)
	

def girarIzquierdaDerecha():
	moverServo(pinServoID, pulsoLimiteDerecha)


def girarDerechaCentro():
	moverServo(pinServoID, pulsoCentroID)
	
	
		
def moverServoWeb(key):

	if key not in [1,2,3,4]:
		return

	if key == 1 or key == 2:
		pinServo = pinServoAA
	elif key == 3 or key == 4:
		pinServo = pinServoID	
		
	if key == 1 or key == 4:   
		incDec =-1
	elif key == 2 or key == 3:   
		incDec = 1
	   
	pos = pi.get_servo_pulsewidth(pinServo) + incDec*20 

	moverServo(pinServo, pos)
      
	

def testGiroCompleto(): 
	girarCentroIzquierda()
	sleep(1)
	girarIzquierdaDerecha()
	sleep(1)
	girarDerechaCentro()

#testGiroCompleto()

def testServoWeb(): 

	while True:
		
		key = int(input())
		
		moverServoWeb(key)

#testServoWeb()

