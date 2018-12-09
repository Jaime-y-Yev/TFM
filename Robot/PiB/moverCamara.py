import pigpio
#import subprocess
#pigpioProceso = subprocess.Popen(['sudo', 'pigpiod'], shell=False)

from time import sleep
import globalesPiB


pinServoID = 19
pinServoAA = 26

pulsoLimiteDerecha = 600;
pulsoLimiteIzquierda = 2000;
pulsoCentroID = 1300

pulsoLimiteArriba = 1700
pulsoLimiteAbajo = 2400
pulsoCentroAA = 2000

resolucion = 100

pi = pigpio.pi()

if not pi.connected:
    print("not connected")

def moverServo(pinServo, posicion):
	print("so fluffy...what a cat", pinServo)
	
	if pinServo == pinServoID:
		limiteMin = pulsoLimiteDerecha
		limiteMax = pulsoLimiteIzquierda
	elif pinServo == pinServoAA:
		limiteMin = pulsoLimiteArriba
		limiteMax = pulsoLimiteAbajo

	if (posicion < limiteMin or posicion > limiteMax):
		if posicion < limiteMin:
			if pinServo == pinServoAA:
				globalesPiB.ultimoPulsoAA = limiteMin
			elif pinServo == pinServoID:
				globalesPiB.ultimoPulsoID = limiteMin
		elif posicion > limiteMax:
			if pinServo == pinServoAA:
				globalesPiB.ultimoPulsoAA = limiteMax
			elif pinServo == pinServoID:
				globalesPiB.ultimoPulsoID = limiteMax
			
		print("La camara esta en un extremo")
		
	else:
		pi.set_servo_pulsewidth(pinServo, posicion)

resolucionGiro = 100
tiempoEntreGiro = 0.0625


def girarCentroIzquierda():
	
	for i in range(pulsoCentroID, pulsoLimiteIzquierda, resolucionGiro):
		moverServo(pinServoID, i)
		sleep(tiempoEntreGiro)


def girarIzquierdaDerecha():
	
	for i in range(pulsoLimiteIzquierda, pulsoLimiteDerecha, -resolucionGiro):
		moverServo(pinServoID, i)
		sleep(tiempoEntreGiro)

def girarDerechaCentro():
	
	for i in range(pulsoLimiteDerecha, pulsoCentroID, resolucionGiro):
		moverServo(pinServoID, i)
		sleep(tiempoEntreGiro)
	
def moverServoWeb(key):
    
	if key == 1 or key == 2:
		
		if key == 1:   
			globalesPiB.ultimoPulsoAA -= 20
		elif key == 2:   
			globalesPiB.ultimoPulsoAA += 20
		
		moverServo(pinServoAA, globalesPiB.ultimoPulsoAA)

	elif key == 3 or key == 4:
		
		if key == 3:   
			globalesPiB.ultimoPulsoID += 20
		elif key == 4:   
			globalesPiB.ultimoPulsoID -= 20
		
		moverServo(pinServoID, globalesPiB.ultimoPulsoID)


def testGiroCompleto(): 
	girarCentroIzquierda()
	girarIzquierdaDerecha()
	girarDerechaCentro()





