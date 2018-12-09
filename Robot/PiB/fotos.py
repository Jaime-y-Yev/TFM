import pygame
import pygame.camera

pygame.init()
pygame.camera.init()
#print(pygame.camera.list_cameras())

import datetime


camara = pygame.camera.Camera("/dev/video0", (640,480))

def tomarFoto(lado):

	camara.start()

	foto = camara.get_image()

	carpetaFotos = '/home/pi/TFM/Robot/PiB/Fotos/'
	timeStamp = str(datetime.datetime.now())
	nombreFoto = carpetaFotos + timeStamp + '_' + lado + '.bmp'
	nombreFoto = nombreFoto.replace(' ','_')

	pygame.image.save(foto, nombreFoto)

	camara.stop()

	return nombreFoto


#tomarFoto('T')
