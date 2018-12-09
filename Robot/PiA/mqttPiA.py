import paho.mqtt.client as mqtt  
import time
import json
import globalesPiA
from comandosParaArduinoA import *


#broker_address="iot.eclipse.org" # Broker MQTT gratis 
#broker_address='test.mosquitto.org'
#broker_address='192.168.1.128' #PiA
broker_address='192.168.43.25' #Jaime phonem



 

# Se utiliza MQTT para mandar coordAct, modo, trayectoria y información(estados) 
def pubMQTT(topic, mensaje): 

    #def on_connect(client, userdata, flags, rc): # definir la acción que hacer al conectar al broker. En este caso es imprimir el mensaje abajo
        #print("Pub MQTT conectado al topic " + topic + " con código ", rc) 

    pub = mqtt.Client()                           # definir el cliente
    #pub.on_connect = on_connect                  # definir que funcion ejecutar al conectar    
    pub.connect(broker_address, 1883, 60)         # indicar cómo conectar
    pub.loop_start()                              # empezar el bucle      
    print("»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»»» PiA pub al topic ", topic + "/ el mensaje ", mensaje)
    pub.publish(topic + "/", str(mensaje))        # publicar el mensaje a un topic indicado en la llamada de la fucnión     
    pub.disconnect()                              # desconectar    
    pub.loop_stop()                               # parar el bucle para poder salir de la función y no bloquear el hilo                      

#Se utiliza MQTT para recibir comandos de modo, coordObj, y geometría
def subMQTT(topic):

	def on_connect(client, userdata, flags, rc):  # definir la acción que hacer al conectar al broker. En este caso es imprimir el mensaje abajo        
		#print("Sub MQTT conectado al topic " + topic + " con código ", rc)
		sub.subscribe(topic + "/")          # subscribir a un topic indicado por "topic", un parametro de la función

	def on_message(client, userdata, message):    # definir la acción que hacer al rebir el mensaje de broker. En este caso es decodificar el mensaje y guardarlo en un variable global 

		mensaje = message.payload.decode("utf-8") # decodificar mensaje json
		print("«««««««««««««««««««««««««««««««««««««««««««««««« PiA sub mensaje: ", mensaje)

		mensaje2 = json.loads(mensaje)
		# Desconectar del broker al recibir señal de matar        
		if "matar" in mensaje2:
			sub.disconnect()
		else:


			# Recibir el mensaje mqtt del servidor con los comandos de modos
			if topic == "control/ServidorRobot":
				control = json.loads(mensaje)
				
				# Si el mensaje contiene modo, guardar al variable global y cambiar el modo de sistema
				if "modo" in mensaje:                 
					globalesPiA.modo = int(control["modo"])

					# Cambiar una marca que permite recibir geometría en hilo de navegar para no conjelar el hilo
					if globalesPiA.modo == MODO_NAVEGACION:
						globalesPiA.permitirSubCoordObj = True 
					else:
						globalesPiA.permitirSubCoordObj = False

					if globalesPiA.modo == MODO_SONDEO:
						pubMQTT("resultados", json.dumps({"coordObjMedicion":globalesPiA.coordObj}))
						
				# Si el mensaje contiene marchaParo, guardar al variable global y empezar navegar()        
				elif "marchaParo" in mensaje:           
					globalesPiA.marchaOparo = int(control["marchaParo"])
				elif "navManual" in mensaje:
					globalesPiA.permitirComandoManual= True

					if int(control["navManual"]) == 0:
						globalesPiA.comandoManual = "pf"
					elif int(control["navManual"]) == 1:
						globalesPiA.comandoManual = "ar"
					elif int(control["navManual"]) == 2:
						globalesPiA.comandoManual = "ai"
					elif int(control["navManual"]) == 3:
						globalesPiA.comandoManual = "ad"
					elif int(control["navManual"]) == 4:
						globalesPiA.comandoManual = "rr"
					elif int(control["navManual"]) == 5:
						globalesPiA.comandoManual = "ri"
					elif int(control["navManual"]) == 6:
						globalesPiA.comandoManual = "rd"
					elif int(control["navManual"]) == 7:
						globalesPiA.comandoManual = "gi"
					elif int(control["navManual"]) == 8:
						globalesPiA.comandoManual = "gd"
				elif "reintentoSondeo" in mensaje:
					globalesPiA.reintentoSondeo = int(control["reintentoSondeo"])
				elif "antena" in mensaje:
					globalesPiA.antena = int(control["antena"])
					print("Antena: ",int(control["antena"]))
					globalesPiA.estadoPiA = "Antena " + str(globalesPiA.antena)


			
			# Recibir el mensaje mqtt del servidor con la información de coordObj, geometria, y idSesion
			if topic == "navegación/coordObj_geometría":
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
	  


	sub = mqtt.Client()                               # definir el cliente que envíe y recibe del Servidor
	sub.on_connect = on_connect                       # definir que función ejecutar al conectar
	sub.on_message = on_message                       # definir que función ejecutar al recibir el mensaje del broker
	sub.connect(broker_address, 1883, 60)             # indicar cómo conectar
	sub.loop_forever()                                # crear un bucle infinito para recibir mensajes


def subMQTTZ(topic):

	def on_connect(client, userdata, flags, rc):  # definir la acción que hacer al conectar al broker. En este caso es imprimir el mensaje abajo        
		#print("Sub MQTT conectado al topic " + topic + " con código ", rc)
		sub.subscribe(topic)          # subscribir a un topic indicado por "topic", un parametro de la función

	def on_message(client, userdata, message):    # definir la acción que hacer al rebir el mensaje de broker. En este caso es decodificar el mensaje y guardarlo en un variable global 

		mensaje = message.payload.decode("utf-8") # decodificar mensaje json
		#print("sub mensaje: ", mensaje)
		
		mensajeJSON = json.loads(mensaje) 

		lon = float(mensajeJSON["lng"])
		lat = float(mensajeJSON["lat"])
		coordActCan = [float(lon),float(lat)]
		
		globalesPiA.coordActCandidato = coordActCan

		
		sub.disconnect()

		

			

	sub = mqtt.Client()                               # definir el cliente que envíe y recibe del Servidor
	sub.on_connect = on_connect                       # definir que función ejecutar al conectar
	sub.on_message = on_message                       # definir que función ejecutar al recibir el mensaje del broker
	sub.connect(broker_address, 1883, 60)             # indicar cómo conectar
	sub.loop_forever()                




#subMQTTZ("navegacion/coordAct/")


