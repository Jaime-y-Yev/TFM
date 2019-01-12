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
		if posicion < limiteMin:
			if pinServo == pinServoAA:
				globalesPi.ultimoPulsoAA = limiteMin
			elif pinServo == pinServoID:
				globalesPi.ultimoPulsoID = limiteMin
		elif posicion > limiteMax:
			if pinServo == pinServoAA:
				globalesPi.ultimoPulsoAA = limiteMax
			elif pinServo == pinServoID:
				globalesPi.ultimoPulsoID = limiteMax
			
		print("La cámara esta en un extremo")
		
	else:
		pi.set_servo_pulsewidth(pinServo, posicion)

resolucionGiro = 100
tiempoEntreGiro = 0.0625

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
    
	if key == 1 or key == 2:
		
		if key == 1:   
			globalesPi.ultimoPulsoAA -= 20
		elif key == 2:   
			globalesPi.ultimoPulsoAA += 20
		
		moverServo(pinServoAA, globalesPi.ultimoPulsoAA)

	elif key == 3 or key == 4:
		
		if key == 3:   
			globalesPi.ultimoPulsoID += 20
		elif key == 4:   
			globalesPi.ultimoPulsoID -= 20
		
		moverServo(pinServoID, globalesPi.ultimoPulsoID)


def testGiroCompleto(): 
	girarCentroIzquierda()
	sleep(1)
	girarIzquierdaDerecha()
	sleep(1)
	girarDerechaCentro()

#testGiroCompleto()


