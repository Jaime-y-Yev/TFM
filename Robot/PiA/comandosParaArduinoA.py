import time
import serial
from decimal import Decimal

# OJO! Quitar todos Serial.prints de Arduino antes de utilizar esta función

### COMIENZO DE CODIGOS --- NO MODIFICAR ESTA LINEA ###

LEER_MODO = 10
CAMBIAR_MODO = 11
MODO_EMERGENCIA = 0
MODO_INACTIVO = 1
MODO_NAVEGACION = 2
MODO_SONDEO = 3

CONFIRMAR_LLEGADA = 17

RECIBIR_DIRECCION_DISTANCIA_OBJ = 20

### FINAL DE CODIGOS --- NO MODIFICAR ESTA LINEA ###


arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=2) # Iniciar conexión serial
time.sleep(2)
##arduino.close()



# Envia un comando y opcionalmente uno o dos valores, esperando en cada caso un echo del valor(es)
## Una respuesta puede tener una combinación de dirección y distancia (ej. 17.89, 1 grado y 7.89 metros) que es necesario correctamente parsear
def comandoArduino(comando, valor1=None, valor2=None):
    
    if comando == RECIBIR_DIRECCION_DISTANCIA_OBJ:
        
        if valor1 != None:
            if valor1 < 10:
                leading1 = "00"
                numDigitos = 1
            elif valor1 >= 10 and valor1 < 100:
                leading1 = "0"
                numDigitos = 2
            elif valor1 >= 100:
                leading1 = ""
                numDigitos = 3
            

        if valor2 != None:
            valor2 = Decimal(valor2)
            valor2 = float(round(valor2,2))
##            print("Type valor2: ",type(valor2))

            if valor2 < 10:
                leading2 = "000"
            elif valor2 >= 10 and valor2 < 100:
                leading2 = "00"
            elif valor2 >= 100 and valor2 < 1000:
                leading2 = "0"
            elif valor2 >= 1000:
                leading2 = ""
        
    else:
        leading1 = ""
        leading2 = ""
        
    

    mensaje = str(comando) + leading1 + str(valor1) + leading2 + str(valor2) #comando=comando (ej CAMBIAR_MODO),valor1/valor2=segunda parte de comando (ej MODO_NAVEGACION)   

    while True:

        try:
##            time.sleep(1)
            
##            while True:
##
##                time.sleep(2)
##                
####                if arduino.in_waiting() == 0:
####                    print("Input buffer is empty")
####                else:
####                    print("Input buffer is not empty yet")
####                
####                if arduino.out_waiting() == 0:
####                    print("Output buffer is empty")
####                else:
####                    print("Output buffer is not empty yet")
##                
##                if arduino.in_waiting == 0 and arduino.out_waiting == 0:
##                    print("Input and output buffers are empty. Proceeding to write.")
##                    break
##                else:
##                    print("Input or output buffers are not empty yet. Waiting...")
                
            
            #arduino.reset_input_buffer()
            #time.sleep(1)
##
            #arduino.reset_output_buffer()
            #time.sleep(1)

            print("Writing mensaje: ", mensaje)
            
            for caracter in mensaje:
                arduino.write(caracter.encode('utf-8'))
            
            while True:
                if arduino.out_waiting == 0:
                    break
            
            respuesta = str(arduino.readline())
            
            
            while True:
                if arduino.in_waiting == 0:
                    break            

            
            print("Read respuesta: ", respuesta)

            respuesta = respuesta[2:len(respuesta)-5]
            
            print("Stripped respuesta: ", respuesta)
            
            if respuesta[0] == 'X' and respuesta[len(respuesta)-1] == 'x':
                #print("Éxito en la estructura de la respuesta de Arduino")
                
                contenido = respuesta[1:len(respuesta)-1]
                print("Arduino ha devuelto el contenido: ", contenido)
                
                if comando == LEER_MODO:
                    
                    contenido = int(contenido)
                    
                    if contenido == MODO_EMERGENCIA or contenido == MODO_INACTIVO or contenido == MODO_NAVEGACION or contenido == MODO_SONDEO:
                        #print("Modo del Arduino = ", contenido)
                        return contenido
##                        break
                    else:
                        print("Error al leer el modo del Arduino")
                
                elif comando == CAMBIAR_MODO:
                    
                    contenido = int(contenido)
                    #print("contenido ", type(contenido))
                    #print("valor1 ",type(valor1))
                    if contenido == valor1:
                        #print("Modo del Arduino = ", contenido)
                        return contenido
##                        break
                    else:
                        print("Error al cambiar el modo del Arduino")
                
                elif comando == CONFIRMAR_LLEGADA:
                                        
                    contenido = int(contenido)
                    
                    if contenido == 0 or contenido == 1:
                        print("Llegada del Arduino = ", contenido)
                        return contenido
##                        break
                    else:
                        print("Error al leer la llegada del Arduino")
                
                elif comando == RECIBIR_DIRECCION_DISTANCIA_OBJ:
                    
                    contenido1 = int(contenido[:numDigitos])
                    contenido2 = float(contenido[numDigitos:])
                    #print("Contenido 1 Dir del Arduino = ", type(contenido1), " y contenido 2 dist del Arduino = ", type(contenido2))
                    #print("Valor1 Dir del Arduino = ", type(valor1), " y Valor2 dist del Arduino = ", type(valor2))
                    #print("Contenido 1 Dir del Arduino = ", contenido1, " y contenido 2 dist del Arduino = ", contenido2)
                    #print("Valor1 Dir del Arduino = ", valor1, " y Valor2 dist del Arduino = ", valor2)


                    if int(contenido1) == int(valor1) and contenido2 == valor2:
                        #print("Before break Contenido 1 Dir del Arduino = ", type(contenido1), " y before break contenido 2 dist del Arduino = ", type(contenido2))

                        return int(contenido1), contenido2
##                        break
                    else:
                        print("Error al leer la dirección y distancia del Arduino")
            
            else:
                print("Error en la estructura de la respuesta de Arduino")


        except:
            print("Excepción en comando de Arduino. Reintentando...")
##            arduino.reset_input_buffer()
##            arduino.reset_output_buffer()


        

def testComandos():
    
    while True:
           
        modoCambiado = comandoArduino(CAMBIAR_MODO, MODO_NAVEGACION)
        print("modoCambiado = " + str(modoCambiado))
        
        #time.sleep(1)
        
        modoLeido = comandoArduino(LEER_MODO)
        print("modoLeido = " + str(modoLeido))
        
        if modoLeido == MODO_NAVEGACION:
            
            llegada = comandoArduino(CONFIRMAR_LLEGADA)
            print("llegada = " + str(llegada))

            direccionObj, distanciaObj = comandoArduino(RECIBIR_DIRECCION_DISTANCIA_OBJ, 123, 4567.89299999999)
            print("direccionObj recibida = " + str(direccionObj))
            print("distanciaObj recibida = " + str(distanciaObj))
        
        print()

#testComandos()