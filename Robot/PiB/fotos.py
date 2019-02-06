import pygame
import pygame.camera
import time

pygame.init()
pygame.camera.init()

import datetime

camara = pygame.camera.Camera("/dev/video0", (640,480))

def tomarFoto(lado):
	"""Tomar una foto con la webcam"""
	
	camara.start()		

	foto = camara.get_image()	# tomar la foto

	carpetaFotos = '/home/pi/TFM/Robot/PiB/Fotos/'					# guardar en la carpeta de fotos
	timeStamp = str(datetime.datetime.now())						# el nombre de la foto contiene la hora y fecha
	nombreFoto = carpetaFotos + timeStamp + '_' + lado + '.bmp'		# añadir al nombre de la foto el lado en el que se tomó
	nombreFoto = nombreFoto.replace(' ','_')

	pygame.image.save(foto, nombreFoto)

	camara.stop()

	return nombreFoto


#tomarFoto('T')

def tomarMuchasFotos(calidad, repeticiones):
	for i in range(repeticiones):
		tomarFoto(calidad + str(i))
		time.sleep(0.5)

#tomarMuchasFotos('Normal', 20)

from os import listdir, fsencode, fsdecode
import subprocess 


def analizarMuchasFotos(carpeta):

	carpetaBase = '/home/pi/TFM/Robot/PiB/Fotos/Calibración/'
	directory = fsencode(carpetaBase + carpeta)

	for file in listdir(directory):
		filename = fsdecode(file)
		#print('filename = ', filename)
		
		verdeI = subprocess.check_output('/home/pi/TFM/Robot/PiB/fotos ' + carpetaBase + carpeta + '/' + filename, shell=True)
		verdeI = verdeI.decode("utf-8")
		print(verdeI)
		
		time.sleep(0.5)

#analizarMuchasFotos('Malas')
