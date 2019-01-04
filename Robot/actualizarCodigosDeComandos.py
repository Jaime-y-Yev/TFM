# Copia los códigos de los comandos de RPi para Arduino (comandosParaArduino.py) al encabezamiento del Arduino (comandos.h)
# No es una función crítica del proyecto, es simplemente una herramienta de utilidad para asegurar que RPi y Arduino están de acuerdo

# Copiar las constantes de comandosParaArduino.py a comandos.h
def actualizarEncabezamientoArduino(archivoPi, archivoArduino):
    print("Actualizando encabezamiento del Arduino")
    
    # Leer de comandosParaArduino.py
    comandosPi = open(archivoPi,'r')

    # Escribir en comandos.h
    comandosArduino = open(archivoArduino,'w')

    # No empezar a copiar líneas de un archivo a otro hasta indicarlo
    copiar = False

    # Copiar las líneas de comandosParaArduino.py sólo en la sección delineada
    for línea in comandosPi:
               
        # Dejar de copiar al llegar al final de la sección permitida
        if línea == '### FINAL DE CÓDIGOS --- NO MODIFICAR ESTA LÍNEA ###\n':
            break
    
        # Copiar mientras siga permitido, ignorando las líneas en blanco
        if copiar == True and línea != '\n':

            # Ej: del el archivo .py de RPi al archivo .h de Arduino
            #            "LEER_MODO = 10" --> "#define LEER_MODO 10"
            comandosArduino.write('#define ')
            línea = línea.replace(" = "," ")
            comandosArduino.write(línea)
        
        # Empezar a copiar al llegar al principio de la sección permitida 
        if línea == '### COMIENZO DE CÓDIGOS --- NO MODIFICAR ESTA LÍNEA ###\n':
            copiar = True
        
    # Cerrar los dos archivos
    comandosPi.close()
    comandosArduino.close()


# Esta función actualiza el archivo comandos.h de Arduino pero no lo compila ni sube al Arduino
archivoPiA = '/home/pi/TFM/Robot/comandosParaArduino.py'
archivoArduinoA = '/home/pi/TFM/Robot/ArduinoA/headers/comandos.h'

#actualizarEncabezamientoArduino(archivoPiA,archivoArduinoA)


import subprocess
from time import sleep


def compilarSubirArduino():
	#print("Compilando el Arduino")
	#procesoCompilacion = subprocess.Popen('arduino-cli compile -b arduino:avr:uno /home/pi/TFM/Robot/ArduinoA', shell = True)
	#sleep(15)
	#procesoCompilacion.kill()

	#print("Subiendo el Arduino")
	#procesoSubida = subprocess.Popen('arduino-cli upload -b arduino:avr:uno /home/pi/TFM/Robot/ArduinoA -p /dev/ttyACM0', shell = True)
	#sleep(10)
	#procesoSubida.kill()
	
	resultadoCompilacion = ""
	while resultadoCompilacion != "bytes":
		print("\nCompiling Arduino")
		resultadoCompilacion = subprocess.check_output(['arduino-cli', 'compile', '-b', 'arduino:avr:uno', '/home/pi/TFM/Robot/ArduinoA'], shell = False)
		print("resultadoCompilacion = ", resultadoCompilacion)
		print()
		resultadoCompilacion = resultadoCompilacion[-7:-2]
		resultadoCompilacion = resultadoCompilacion.decode()
		print("resultadoCompilacion = ", resultadoCompilacion)

		if resultadoCompilacion == "bytes":
			print("Compiled successfully")
		else:
			print("Problem while compiling, retrying...")


	resultadoSubida = "blahblah"
	while resultadoSubida != "":
		
		print("\nUploading Arduino")
		resultadoSubida = subprocess.check_output(['arduino-cli', 'upload', '-b', 'arduino:avr:uno', '/home/pi/TFM/Robot/ArduinoA', '-p', '/dev/ttyACM0'], shell = False)
		print("resultadoSubida = ", resultadoSubida)
		print()
		resultadoSubida = resultadoSubida.decode()
		print("resultadoSubida = ", resultadoSubida)

		if resultadoSubida == "":
			print("Uploaded successfully")
		else:
			print("Problem while uploading, retrying...")
	
	sleep(2)

#compilarSubirArduino()
