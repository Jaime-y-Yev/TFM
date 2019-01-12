import pygame
import pygame.camera

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
