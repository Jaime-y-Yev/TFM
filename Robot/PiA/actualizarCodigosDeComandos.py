# Copia los códigos de los comandos de piA para ArduinoA (comandosParaArduino.py) al header del ArduinoA (comandos.h)

def actualizarH():
    carpetaPi = '/home/pi/Desktop/piA/comandosParaArduinoA.py'
    comandosPi = open(carpetaPi,'r')

    carpetaArduino = '/home/pi/Desktop/arduinoA/headers/comandos.h'
    comandosArduino = open(carpetaArduino,'w')

    copiar = False
    
    for linea in comandosPi:
               
        if linea == '### FINAL DE CODIGOS --- NO MODIFICAR ESTA LINEA ###\n':
            break
    
        if copiar == True and linea != '\n':
            comandosArduino.write('#define ')
            linea = linea.replace(" = "," ")
            comandosArduino.write(linea)
        
        if linea == '### COMIENZO DE CODIGOS --- NO MODIFICAR ESTA LINEA ###\n':
            copiar = True
        


    comandosArduino.close()



actualizarH() # don't forget to re-upload into Arduino!!!

##time.sleep(1)
##
##procesoArduino = subprocess.run(['arduino', '--upload', '/home/pi/Desktop/arduinoA/arduinoA.ino'])
##
##time.sleep(20)
##
##procesoArduino.kill()
