import moverCamara
import fotos
import subprocess

import globalesPi

from time import sleep

def tomarFotos():
	"""Tomar una foto a cada lado del robot"""
	
	moverCamara.girarCentroIzquierda()
	sleep(1)
	
	fotoI = fotos.tomarFoto('I')
	print("Foto de la izquierda guardada en: ", fotoI)
	verdeI = subprocess.check_output('/home/pi/TFM/Robot/PiB/fotos ' + fotoI, shell=True)
	verdeI = verdeI.decode("utf-8")
	print("Analizada la cantidad de verde al lado izquierdo en el índice VARI = ", verdeI)	
	
	moverCamara.girarIzquierdaDerecha()
	sleep(1)
	
	fotoD = fotos.tomarFoto('D')	
	print("Foto de la derecha guardada en: ", fotoI)
	verdeD = subprocess.check_output('/home/pi/TFM/Robot/PiB/fotos ' + fotoD, shell=True)
	verdeD = verdeD.decode("utf-8")
	print("Analizada la cantidad de verde al lado derecho en el índice VARI = ", verdeI)	

	moverCamara.girarDerechaCentro()
	sleep(1)

	verdesDict = {"verdeI": verdeI, "verdeD": verdeD}

	return verdesDict, fotoI, fotoD
	

#tomarFotos()

import os
import signal

def mostrarVideo():
	"""Stream el video captado por la cámara en la página [IP_DE_PIB]:8090"""
	
	os.environ["LD_LIBRARY_PATH"] = "/home/pi/Downloads/mjpg-streamer-master/mjpg-streamer-experimental"
	videoProceso = subprocess.Popen('./start.sh', cwd='/home/pi/Downloads/mjpg-streamer-master/mjpg-streamer-experimental', preexec_fn=os.setsid)
	
	while True:
		
		if globalesPi.modo != globalesPi.MODO_MANUAL:
			grupoProcesos = os.getpgid(videoProceso.pid)
			os.killpg(grupoProcesos, signal.SIGTERM)
			break

	
#mostrarVideo()
