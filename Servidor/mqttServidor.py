import paho.mqtt.client as mqtt  
import time
import json


def pubMQTT(topic, value): 

    def on_connectpub(client, userdata, flags, rc): # Mensaje que recibe publisher al conectar
        m = "Connected flags: " + str(flags) + " result code: " + str(rc) + " client1_id: " + str(client)
        print(m)
  
    #broker_address="127.0.0.1" # Una opción del broker es elegir un IP. En este caso Raspberry Pi IP address 
    broker_address="iot.eclipse.org" # Una opción del broker es elegir un IP. En este caso Raspberry Pi IP address 

    pub = mqtt.Client() # Crear publisher

    pub.on_connect = on_connectpub # Asociar functiones al conectar

    pub.connect(broker_address, 1883, 60) # Conectar publisher al broker. Usar 1883- el puerto automatico.


    pub.loop_start()    # Empezar Bucle
    pub.publish(topic, value) # Publicamos json bajo de un topic baado en key. 
           
    pub.disconnect()    
    pub.loop_stop()

