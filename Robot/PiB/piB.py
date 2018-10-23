import threading
hiloMatarID = 0
hiloEstadosID = 1
hiloControlID = 2
hiloModoSyncID = 3
hiloSondeoID = 4
matarHilos = 'o'


import json
import time

import globalesPiB

from mqttPiB import pubMQTT, subMQTT

from comandosParaArduinoB import *

from time import sleep

# Sondeo
##import RPi.GPIO as GPIO
import actuador
import jaula
#from actuador import *
#from jaula import *


class Hilo(threading.Thread):
    
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        
    def run(self):
        
        print("Comenzando hilo ", end='')
            
        # Se mata los procesos facilmente con un hilo adicional----------------------------------   
        if self.threadID == hiloMatarID:
            print("Matar")
 
            while True:
                global matarHilos
                matarHilos = input() # utilizar la entrada de teclado             
                if matarHilos == 'm': 
                    break

            print("Terminando hilo Matar")
       
        # Mandar estados de PiB y ArduinoB a Servidor----------------------------------------
        elif self.threadID == hiloEstadosID:
            print("Estado")
            
            # iniciar el variable local con un valor imposible para ejecutar el proceso la primera vez
            estadoPiB = 0
            estadoArduinoB= 0
            while True:

                if estadoPiB != globalesPiB.estadoPiB:# solo mandar estados de PiB cuando había un cambio en PiB
                    pubMQTT("control/estadoPiB",json.dumps(globalesPiB.estadoPiB)) # mandar información del PiB a Servidor
                    estadoPiB = globalesPiB.estadoPiB # actualizar el variable local para poder reinicar el proceso
                    print(globalesPiB.estadoPiB)
                    
                if estadoArduinoB != globalesPiB.estadoArduinoB:# solo mandar estados de ArduinoA cuando había un cambio en ArduinoB
                    pubMQTT("control/estadoArduinoB",json.dumps(globalesPiB.estadoArduinoB)) # mandar infromación de ArduinoB a Servidor
                    estadoArduinoB = globalesPiB.estadoArduinoB # actualizar el variable local para poder reinicar el proceso
                    print(globalesPiB.estadoArduinoB)

                # Mater hilos seguramente utilizando la entrada de "m" en terminal 
                if matarHilos == 'm':
                    break           
            
            print("Terminando hilo Control")
       
        # Recibir comandos del Servidor-------------------------------------------------------- 
        elif self.threadID == hiloControlID:
            print("Control") 
            
            while True:
                
                # Utilizar MQTT para recibir cambios de modo o marchaParo estados
                subMQTT("control/ServidorRobot")  
        
                # Mater hilos seguramente utilizando la entrada de "m" en terminal 
                if matarHilos == 'm':
                    pubMQTT("control/ServidorRobot", "m")
                    break          
            
            print("Terminando hilo Control")
        
        # Sincronizar modos del Arduino, PiB y Servidor---------------------------------------
        elif self.threadID == hiloModoSyncID:
            print("ModoSync")
            
            modo = 9 # iniciar el variable local con un valor imposible para entrar sincronización
            while True:
                
                # Utilizar el cambio de modos para sincronizar el modo de ArduinoA
                if modo != globalesPiB.modo: 
                    
                    # Informar el usuario sobre el cambio de los modos
                    globalesPiB.estadoPiB = "Cambio de modos detectado. Cambiando modo de PiB..."
                    
                    modo = globalesPiB.modo # guardar el modo corriente en un variable, para poder hacer el flanco otra vez
                    globalesPiB.estadoPiB = "modoPiB: " + str(modo)
                    
                    # Se utiliza MQTT para publicar el modo sincronizado a Servidor
                    pubMQTT("control/RobotServidor/modo", globalesPiB.modo)

                
                # Mater hilos seguramente utilizando la entrada de "m" en terminal 
                if matarHilos == 'm':
                    break
                
            print("Terminando hilo modo")
        
        
        # Calcular trayectoria y ejecutar navegación del robot
        elif self.threadID == hiloSondeoID:#-------------------------------------------------------------
            print("Sondeo")
            actuador.frenar()
            
            while True:
                sleep(1)
                print("In Hilo Sondeo globalesPiB.modo =", globalesPiB.modo)
                
                # Sólo activar la jaula y actuador en el modo de sondeo 
                if globalesPiB.modo == MODO_SONDEO:
                    
                    print("Sondeo iniciado")
                                                             
                    jaula.revelar()     # mover la jaula para revelar el sensor/actuador
                    sleep(1)
                    
                    actuador.expandir() # activar y expandir el atuador para insertar el sensor en el suelo 
                    
                    sleep(5)            # simula tiempo de sondeo
                    
                    actuador.contraer() # contraer el actuador
                    sleep(1)
                    
                    jaula.retraer()     # mover la jaula hacia la posición inicial
                    
                    globalesPiB.modo = MODO_INACTIVO 

                if matarHilos == 'm':   
                    jaula.servoPWM.stop()
                    GPIO.cleanup()    
                    break
                
            print("Terminando hilo Sondeo")  
                                

# Hilo principal que arranca los demás hilos
print("Comenzando hilo Principal")           

# Al encender Pi, actualizar su modo según el servidor enviando
# Sincronizar modos antes de empezar hilos
pubMQTT("control/RobotServidor/syncModo", 1) 

# Crear cada hilo
hiloMatar = Hilo(hiloMatarID)
hiloEstados = Hilo(hiloEstadosID)
hiloControl = Hilo(hiloControlID)
hiloModoSync = Hilo(hiloModoSyncID)
hiloSondeo = Hilo(hiloSondeoID)

# Iniciar cada hilo
hiloMatar.start()
sleep(0.25)
hiloEstados.start()
sleep(0.25)
hiloControl.start()
sleep(0.25)
hiloModoSync.start()
sleep(0.25)
hiloSondeo.start()


        

