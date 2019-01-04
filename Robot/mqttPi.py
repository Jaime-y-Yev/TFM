import paho.mqtt.client as mqtt  
import time
import json
import globalesPiA

import sys
sys.path.insert(0, '/home/pi/TFM/Robot')
from comandosParaArduino import *

broker_address = '192.168.1.132' #laptop
#broker_address = '192.168.1.128' #piA
#broker_address = '192.168.1.135' #piB
#broker_address = '192.168.43.25'
broker_port = 1883
broker_timeout = 60

 

# Se utiliza MQTT para mandar coordAct, modo, trayectoria y información(estados) 
def pubMQTT(topic, mensaje,retainMess=False): 

    def on_connect(client, userdata, flags, rc): # definir la acción que hacer al conectar al broker. En este caso es imprimir el mensaje abajo
        print("Pub MQTT conectado al topic " + topic + " con código ", rc) 

    pub = mqtt.Client()                           # definir el cliente
    pub.on_connect = on_connect                  # definir que funcion ejecutar al conectar    
    pub.connect(broker_address, broker_port, broker_timeout)         # indicar cómo conectar
    pub.loop_start()                              # empezar el bucle      
    print("»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»» PiA pub al topic ", topic, " el mensaje ", mensaje)
    pub.publish(topic, str(mensaje), retain=retainMess)        # publicar el mensaje a un topic indicado en la llamada de la fucnión     
    pub.disconnect()                              # desconectar    
    pub.loop_stop()                               # parar el bucle para poder salir de la función y no bloquear el hilo                      

#Se utiliza MQTT para recibir comandos de modo, coordObj, y geometría
def subMQTT(topics):

	def on_connect(client, userdata, flags, rc):  # definir la acción que hacer al conectar al broker. En este caso es imprimir el mensaje abajo        
		print("Sub MQTT conectado al topic " + str(topics) + " con código ", rc)
		sub.subscribe(topics)

	def on_message(client, userdata, message):    # definir la acción que hacer al rebir el mensaje de broker. En este caso es decodificar el mensaje y guardarlo en un variable global 

		mensaje = message.payload.decode("utf-8") # decodificar mensaje json
		print("«««««««««««««««««««««««««««««««««««««««««««««««« PiA sub en topic: ",message.topic ," mensaje ", mensaje)

		if message.topic == "ServidorRobot/modo":
			print("recibiendo modo")

			#if globalesPiA.modo != MODO_EMERGENCIA and (int(mensaje) != MODO_NAVEGACION and globalesPiA.modo != MODO_SONDEO):
			if globalesPiA.modo != MODO_EMERGENCIA and not (globalesPiA.modo == MODO_SONDEO and int(mensaje) == MODO_NAVEGACION):
				globalesPiA.modo = int(mensaje)

			if globalesPiA.modo == MODO_NAVEGACION:
				globalesPiA.permitirSubCoordObj = True 
			
			
			sub.disconnect()
		
		if message.topic == "ServidorRobot/marchaParo":
			globalesPiA.marchaOparo = int(mensaje)
			sub.disconnect()

		if message.topic == "ServidorRobot/antena":
			globalesPiA.antena = int(mensaje)
			globalesPiA.estadoPiA = "Antena " + str(globalesPiA.antena)
			print("globalesPiA.antena ", globalesPiA.antena)
			sub.disconnect()

		
		if message.topic == "movilRobot/coordAct":

			mensajeJSON = json.loads(mensaje) 

			lon = float(mensajeJSON["lng"])
			lat = float(mensajeJSON["lat"])
			coordActCan = [float(lon),float(lat)]
			
			globalesPiA.coordActCandidato = coordActCan
			
			sub.disconnect()

		if message.topic == "ServidorRobot/coordObj_geometría":

			coordObj_geometria = json.loads(mensaje)

			# Formatear el mensaje mqtt para obtener poli y linea en formato útil para la función trayectoria() y navegar()
			coordObj = coordObj_geometria["coordObj"]
			idSesion = coordObj_geometria["idSesion"]
			geometria = coordObj_geometria["geometria"]
			geometria = eval(geometria)                     # hacer una conversión entre los lists de string a formato dict
			geomLinea = json.loads(str(geometria["línea"]))
			geomPoli = json.loads(str(geometria["poli"]))
			geomPoli = geomPoli[:len(geomPoli)-1]
			geometria = {"linea":geomLinea,"poli":geomPoli}

			# Guardar los variables a globalesPiA 
			globalesPiA.coordObj = coordObj 
			globalesPiA.geometria = geometria
			globalesPiA.idSesion = idSesion
			sub.disconnect()
  
		if message.topic == "ServidorRobot/navManual":
			globalesPiA.permitirComandoManual= True
			globalesPiA.comandoManual = mensaje


		if message.topic == "RobotRobot/sondeoTerminado":
			globalesPiA.sondeoTerminado = int(mensaje)
			print("He recibido sondeTerminado en mqtt")
			sub.disconnect()

		if message.topic == "RobotServidor/resultados/medidas":
			resultados = json.loads(mensaje)
			sub.disconnect()
	

	sub = mqtt.Client()                               # definir el cliente que envíe y recibe del Servidor
	sub.on_connect = on_connect                       # definir que función ejecutar al conectar
	sub.on_message = on_message                       # definir que función ejecutar al recibir el mensaje del broker
	sub.connect(broker_address, broker_port, broker_timeout)             # indicar cómo conectar
	sub.loop_forever()                                # crear un bucle infinito para recibir mensajes
