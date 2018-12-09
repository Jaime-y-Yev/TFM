import moverCamara
import fotos
import subprocess

import globalesPiB

from time import sleep

def tomarFotos():
	
	moverCamara.girarCentroIzquierda()
	sleep(1)
	
	nombreFoto = fotos.tomarFoto('I')
	sleep(0.5)
	#subprocess.Popen(['/home/pi/TFM/Robot/PiB/fotos', nombreFoto], shell=False)
	verde = subprocess.check_output('/home/pi/TFM/Robot/PiB/fotos ' + nombreFoto, shell=True)
	verde = verde.decode("utf-8")
	print("In tomarFotos() verde = ", verde)
	
	#mqttPub('/RobotServidor/resultados', json.dumps({"coordObj": globalesPiB.coordObjMedicion, "verdeIzq": verde})) 	TODOTODOTODOTODOTODO
	
	#pubMQTTF('/RobotServidor/fotos', nombreFoto) 	TODOTODOTODOTODOTODO
	
	
	moverCamara.girarIzquierdaDerecha()
	sleep(1)
	
	nombreFoto = fotos.tomarFoto('D')	
	sleep(0.5)

	#subprocess.Popen(['/home/pi/TFM/Robot/PiB/fotos', nombreFoto], shell=False)
	verde = subprocess.check_output('/home/pi/TFM/Robot/PiB/fotos ' + nombreFoto, shell=True)
	verde = verde.decode("utf-8")
	
	#mqttPub('/RobotServidor/resultados', json.dumps({"coordObj": globalesPiB.coordObjMedicion, "verdeDcha": verde})) 	TODOTODOTODOTODOTODO
	


	
	moverCamara.girarDerechaCentro()
	sleep(1)





#tomarFotos()
