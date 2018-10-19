# Copia los códigos de los comandos de RPi para Arduino (comandosParaArduino.py) al encabezamiento del Arduino (comandos.h)
# No es una función crítica del proyecto, es simplemente una herramienta de utilidad para asegurar que RPi y Arduino están de acuerdo

# Copiar las constantes de comandosParaArduino.py a comandos.h
def actualizarEncabezamientoArduino(archivoPi, archivoArduino):
    
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
archivoPiA = '/home/pi/Desktop/piA/comandosParaArduinoA.py'
archivoArduinoA = '/home/pi/Desktop/arduinoA/headers/comandos.h'

actualizarEncabezamientoArduino(archivoPiA,archivoArduinoA)


# TODO: automatizar la compilación y la subida de comandos.h al Arduino
