import paho.mqtt.client as mqtt  
import time
import json
import globalesPiB
#from comandosParaBrduinoB import *

#import camara
#import moverCamara
#import pigpioServo

#broker_address="iot.eclipse.org" # Broker MQTT gratis 
broker_address="192.168.1.128" # Broker MQTT gratis 

# Se utiliza MQTT para mandar coordAct, modo, trayectoria y información(estados) 
def pubMQTT(topic, mensaje): 

    #def on_connect(client, userdata, flags, rc): # definir la acción que hacer al conectar al broker. En este caso es imprimir el mensaje abajo
        #print("Pub MQTT conectado al topic " + topic + " con código ", rc) 

    pub = mqtt.Client()                           # definir el cliente
    #pub.on_connect = on_connect                  # definir que funcion ejecutar al conectar    
    pub.connect(broker_address, 1883, 60)         # indicar cómo conectar
    pub.loop_start()                              # empezar el bucle      
    pub.publish(topic + "/", str(mensaje))        # publicar el mensaje a un topic indicado en la llamada de la fucnión     
    print("pub MQTT: ",mensaje, " to topic ", topic)
    pub.disconnect()                              # desconectar    
    pub.loop_stop()                               # parar el bucle para poder salir de la función y no bloquear el hilo  
    

import base64

def pubMQTTF(topic):

	def on_publish(mosq, userdata, mid):
		mosq.disconnect()

	client = mqtt.Client()                           # definir el cliente

	client.on_publish = on_publish

	client.connect(broker_address, 1883, 60)

	f = open('2018-12-06_17:28:27.435776_T.jpg', 'rb')
	fileContent = f.read()
	byteArr = bytes(fileContent)
	result = base64.b64encode(byteArr)
	#client.publish(topic + "/", byteArr, 0)
	client.publish(topic + "/", result, 0)
	print("published foto")

	client.loop_forever()                    

#Se utiliza MQTT para recibir comandos de modo, coordObj, y geometría
def subMQTT(topic):

	def on_connect(client, userdata, flags, rc):  # definir la acción que hacer al conectar al broker. En este caso es imprimir el mensaje abajo        
		print("Sub MQTT conectado al topic " + topic + " con código ", rc)
		sub.subscribe(topic + "/")          # subscribir a un topic indicado por "topic", un parametro de la función

	def on_message(client, userdata, message):    # definir la acción que hacer al rebir el mensaje de broker. En este caso es decodificar el mensaje y guardarlo en un variable global 
		
		mensaje = message.payload.decode("utf-8") # decodificar mensaje json
		print("sub mensaje: ", mensaje)
		
		# Desconectar del broker al recibir señal de matar        
		if mensaje == "m":
			sub.disconnect()

		# Recibir el mensaje mqtt del servidor con los comandos de modos
		if topic == "control/ServidorRobot":
			print("in topic")           

			
			control = json.loads(mensaje)
			print("after loads control = ",control)           
			# Si el mensaje contiene modo, guardar al variable global y cambiar el modo de sistema
			if "modo" in control:
			
				globalesPiB.modo = int(control["modo"])
				
				if globalesPiB.modo == globalesPiB.SONDEO:
					permitirMovimientoJaula = True
					permitirMovimientoActuador = False
				else:
					permitirMovimientoJaula = False
					permitirMovimientoActuador = False
			
			elif "moverCamara" in control:
				print("in elif moverCamara in control")
				#moverCamara.moverServoWeb(int(control["moverCamara"]))
				globalesPiB.comandoCamara = int(control["moverCamara"])
				
				
			elif "coordObjMedicion" in control:
				globales.coordObjMedicion = control["coordObjMedicion"]
				
		print("before disconnect")           
		sub.disconnect()

 

                
	sub = mqtt.Client()                               # definir el cliente que envíe y recibe del Servidor
	sub.on_connect = on_connect                       # definir que función ejecutar al conectar
	sub.on_message = on_message                       # definir que función ejecutar al recibir el mensaje del broker
	sub.connect(broker_address, 1883, 60)             # indicar cómo conectar
	sub.loop_forever()                                # crear un bucle infinito para recibir mensajes


#pubMQTTF('RobotServidor/resultados/fotos')
