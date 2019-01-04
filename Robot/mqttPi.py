import paho.mqtt.client as mqtt  
import time
import json
import globalesPi

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
    print("»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»» Pi pub al topic ", topic, " el mensaje ", mensaje)
    pub.publish(topic, str(mensaje), retain=retainMess)        # publicar el mensaje a un topic indicado en la llamada de la fucnión     
    pub.disconnect()                              # desconectar    
    pub.loop_stop()                               # parar el bucle para poder salir de la función y no bloquear el hilo     
    

import base64

def pubMQTTF(topic, mensaje):

	def on_publish(mosq, userdata, mid):
		mosq.disconnect()

	client = mqtt.Client()                           # definir el cliente

	client.on_publish = on_publish

	client.connect(broker_address, 1883, 60)

	f = open(mensaje, 'rb')
	fileContent = f.read()
	byteArr = bytes(fileContent)
	result = base64.b64encode(byteArr)
	#client.publish(topic, byteArr, 0)
	client.publish(topic, result, 0)
	print("published foto")

	client.loop_forever()                  

#Se utiliza MQTT para recibir comandos de modo, coordObj, y geometría
def subMQTT(topics):

	def on_connect(client, userdata, flags, rc):  # definir la acción que hacer al conectar al broker. En este caso es imprimir el mensaje abajo        
		print("Sub MQTT conectado al topic " + str(topics) + " con código ", rc)
		sub.subscribe(topics)

	def on_message(client, userdata, message):    # definir la acción que hacer al rebir el mensaje de broker. En este caso es decodificar el mensaje y guardarlo en un variable global 

		mensaje = message.payload.decode("utf-8") # decodificar mensaje json
		print("«««««««««««««««««««««««««««««««««««««««««««««««« PiA sub en topic: ",message.topic ," mensaje ", mensaje)

		if message.topic == "ServidorRobot/modoA":
			print("recibiendo modo")

			if globalesPi.modo != MODO_EMERGENCIA and not (globalesPi.modo == MODO_SONDEO and int(mensaje) == MODO_NAVEGACION):
				globalesPi.modo = int(mensaje)

			if globalesPi.modo == MODO_NAVEGACION:
				globalesPi.permitirSubCoordObj = True 
			
			
			sub.disconnect()
		
		if message.topic == "ServidorRobot/modoB":
			
			if globalesPi.modo != MODO_EMERGENCIA and not (globalesPi.modo == MODO_SONDEO and int(mensaje) == MODO_NAVEGACION):
				globalesPi.modo = int(mensaje)
			
			sub.disconnect()
		
		if message.topic == "ServidorRobot/marchaParo":
			globalesPi.marchaOparo = int(mensaje)
			sub.disconnect()

		if message.topic == "ServidorRobot/antena":
			globalesPi.antena = int(mensaje)
			globalesPi.estadoPiA = "Antena " + str(globalesPi.antena)
			print("globalesPi.antena ", globalesPi.antena)
			sub.disconnect()

		
		if message.topic == "movilRobot/coordAct":

			mensajeJSON = json.loads(mensaje) 

			lon = float(mensajeJSON["lng"])
			lat = float(mensajeJSON["lat"])
			coordActCan = [float(lon),float(lat)]
			
			globalesPi.coordActCandidato = coordActCan
			
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

			# Guardar los variables a globalesPi
			globalesPi.coordObj = coordObj 
			globalesPi.geometria = geometria
			globalesPi.idSesion = idSesion
			sub.disconnect()
  
		if message.topic == "ServidorRobot/navManual":
			globalesPi.permitirComandoManual= True
			globalesPi.comandoManual = mensaje


		if message.topic == "RobotRobot/sondeoTerminado":
			globalesPi.sondeoTerminado = int(mensaje)
			print("He recibido sondeTerminado en mqtt")
			sub.disconnect()

		if message.topic == "RobotServidor/resultados/medidas":
			resultados = json.loads(mensaje)
			sub.disconnect()
				
			
		if message.topic == "ServidorRobot/moverCamara":
			print("in sub moverCamara ")
			#moverCamara.moverServoWeb(int(control["moverCamara"]))
			globalesPi.comandoCamara = int(mensaje)
			sub.disconnect()
			
		if message.topic == "RobotRobot/coordObj":
			coordObj_idSesion = json.loads(mensaje)
			globalesPi.coordObj = coordObj_idSesion["coordObj"]
			globalesPi.idSesion = coordObj_idSesion["idSesion"]
			sub.disconnect()
	

	sub = mqtt.Client()                               # definir el cliente que envíe y recibe del Servidor
	sub.on_connect = on_connect                       # definir que función ejecutar al conectar
	sub.on_message = on_message                       # definir que función ejecutar al recibir el mensaje del broker
	sub.connect(broker_address, broker_port, broker_timeout)             # indicar cómo conectar
	sub.loop_forever()                                # crear un bucle infinito para recibir mensajes
