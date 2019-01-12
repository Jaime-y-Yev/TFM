import paho.mqtt.client as mqtt  
import time
import json
import globalesPi

import sys
sys.path.insert(0, '/home/pi/TFM/Robot')
from comandosParaArduino import *

import base64


broker_address = '192.168.1.132' 	# servidor conectado a wifi
#broker_address = '192.168.43.198'	# servidor conectado a datos
broker_port = 1883
broker_timeout = 60

 
def pubMQTT(topic, mensaje,retainMess=False):
	"""Publica mensajes mediante MQTT""" 

	pub = mqtt.Client()                           
	pub.connect(broker_address, broker_port, broker_timeout)         
	pub.loop_start()                                    
	print("--->--->--->--->--->--->--->--->--->--->--->---> Pi pub al topic ", topic, " el mensaje ", mensaje)

	if topic == "RobotServidor/resultados/fotos/I" or topic == "RobotServidor/resultados/fotos/D":
		f = open(mensaje, 'rb')
		fileContent = f.read()
		byteArr = bytes(fileContent)
		result = base64.b64encode(byteArr)
		pub.publish(topic, result, 0)
		print("Foto publicada al servidor")	
	else:	
		pub.publish(topic, str(mensaje), retain=retainMess)            

	pub.disconnect()                                  
	pub.loop_stop()                                    
    
               

def subMQTT(topics):
	"""Se subscribe a mensajes mediante MQTT""" 

	def on_connect(client, userdata, flags, rc):  # notificar que se ha conectado al topic        
		print("Sub MQTT conectado al topic " + str(topics))
		sub.subscribe(topics)

	def on_message(client, userdata, message):    # dependiendo del topic, procesar el mensaje de forma distinta 

		mensaje = message.payload.decode("utf-8") 
		print("<---<---<---<---<---<---<---<---<---<---<---<--- Pi sub en topic ",message.topic ," el mensaje ", mensaje)

		if mensaje == '{"matar": "m"}':
			sub.disconnect()

		if message.topic == "ServidorRobot/modoA":		# cambia el modo de PiA

			if globalesPi.modo != MODO_EMERGENCIA and not (globalesPi.modo == MODO_SONDEO and int(mensaje) == MODO_NAVEGACION):
				globalesPi.modo = int(mensaje)

			if globalesPi.modo == MODO_NAVEGACION:
				globalesPi.permitirSubCoordObj = True 
		
		if message.topic == "ServidorRobot/modoB":		# cambia el modo de PiB
			
			if globalesPi.modo != MODO_EMERGENCIA and not (globalesPi.modo == MODO_SONDEO and int(mensaje) == MODO_NAVEGACION):
				globalesPi.modo = int(mensaje)
		
		if message.topic == "ServidorRobot/marchaParo":		# señal de marcha o paro que inicia o detiene la navegación
			globalesPi.marchaOparo = int(mensaje)

		if message.topic == "ServidorRobot/antena":			# cambia la antena utilizada en la navegación (RTKlib o móvil)
			globalesPi.antena = int(mensaje)
			globalesPi.estadoPiA = "Cambiado a antena " + str(globalesPi.antena)
			
		if message.topic == "movilRobot/coordAct":			# recibe coordAct del móvil

			mensajeJSON = json.loads(mensaje) 

			lon = float(mensajeJSON["lng"])
			lat = float(mensajeJSON["lat"])
			coordActCan = [lon,lat]
			
			globalesPi.coordActCandidato = coordActCan		# guardar en la lista de candidatos de coordAct

		if message.topic == "ServidorRobot/coordObj_geometría":		# recibir coordObj y el contorno de la parcela

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
  
		if message.topic == "ServidorRobot/navManual":		# recibir los comandos de la navegación manual para mover los motores (PiA)
			globalesPi.permitirComandoManual = True
			globalesPi.comandoManual = mensaje

		if message.topic == "RobotRobot/sondeoTerminado":	# recibir el estado de sondeo de PiB
			globalesPi.sondeoTerminado = int(mensaje)
			
		if message.topic == "ServidorRobot/moverCamara":	# recibir los comandos de la navegación manual para mover la cámara (PiB)
			globalesPi.comandoCamara = int(mensaje)
			
		if message.topic == "RobotRobot/coordObj":			# recibir coordObj de PiA para asignarla a las medidas recogidas por PiB
			coordObj_idSesion = json.loads(mensaje)
			globalesPi.coordObj = coordObj_idSesion["coordObj"]
			globalesPi.idSesion = coordObj_idSesion["idSesion"]
		
		sub.disconnect()
	

	sub = mqtt.Client()                               # definir el cliente que envía y recibe del Servidor
	sub.on_connect = on_connect                       # definir que función ejecutar al conectar
	sub.on_message = on_message                       # definir que función ejecutar al recibir el mensaje del broker
	sub.connect(broker_address, broker_port, broker_timeout)             # indicar cómo conectar
	sub.loop_forever()                                # crear un bucle infinito para recibir mensajes
