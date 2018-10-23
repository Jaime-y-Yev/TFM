import paho.mqtt.client as mqtt  
import time
import json
import globalesPiB



def pubSyncModo(): 

    def on_connectpub(client, userdata, flags, rc): 
        m = "Connected flags: " + str(flags) + " result code: " + str(rc) + " client1_id: " + str(client)
        print(m)

  
    #broker_address="127.0.0.1" # Una opción del broker es elegir un IP. En este caso Raspberry Pi IP address 
    broker_address="iot.eclipse.org"

    pub = mqtt.Client() 

    pub.on_connect = on_connectpub 

    pub.connect(broker_address, 1883, 60) 


    pub.loop_start()    

    peticiónModo = {"modo?": 1}

    json_string = json.dumps(peticiónModo) # Convertir en formato json
    pub.publish("/syncModo/",str(json_string)) # Publicamos json bajo de un topic basado en key. 
    print("pubModo: ", json_string)
    pub.disconnect()    
    pub.loop_stop()


def pubModo(): 

    def on_connectpub(client, userdata, flags, rc): 
        m = "Connected flags: " + str(flags) + " result code: " + str(rc) + " client1_id: " + str(client)
        print(m)

  
    #broker_address="127.0.0.1" # Una opción del broker es elegir un IP. En este caso Raspberry Pi IP address 
    broker_address="iot.eclipse.org"

    pub = mqtt.Client() 

    pub.on_connect = on_connectpub 

    pub.connect(broker_address, 1883, 60) 


    pub.loop_start()    

    modo = {"modo": globalesPiB.modo}

    json_string = json.dumps(modo) # Convertir en formato json
    pub.publish("/modo/",str(json_string)) # Publicamos json bajo de un topic basado en key. 
    print("pubModo: ", json_string)
    pub.disconnect()    
    pub.loop_stop()


def subControl():
    
    # Se recibe un mensaje cuando se conecta a broker 
    def on_connectsub(client, userdata, flags, rc):
        print("subControl connected with result code ", rc)

        # Subscibir en on_connect() signifíca que  se se pierde la conexión, los subscriciones van a ser renovados
        sub.subscribe("/control/#")


    # Se crea una función para hacer algo cada vez que recibimos un mensaje
    def on_messagesub(client1, userdata, message):
        control = message.payload.decode("utf-8") # Decodificar mensaje json
        control = json.loads(control)
        print("Subbed MQTT control = ", control)
         
        if "modo" in control:
            
            globalesPiB.modo = int(control["modo"])
            
            if globalesPiB.modo == globalesPiB.SONDEO:
                permitirMovimientoJaula = True
                permitirMovimientoActuador = False
            else:
                permitirMovimientoJaula = False
                permitirMovimientoActuador = False

    sub = mqtt.Client() # Se crea un cliente (como en el caso del publisher). En este caso es un subscriber.

    # Asociar las funciones
    sub.on_connect = on_connectsub 
    sub.on_message = on_messagesub
    
    #broker_address="127.0.0.1"
    broker_address="iot.eclipse.org"

    sub.connect(broker_address, 1883, 60) # Conectar el cliente con el broker (usar IP del broker)

    sub.loop_forever() # Crear un bucle infinito para recibir mensajes


def pubTest(): 

    def on_connectpub(client, userdata, flags, rc): 
        m = "Connected flags: " + str(flags) + " result code: " + str(rc) + " client1_id: " + str(client)
        print(m)

  
    #broker_address="127.0.0.1" # Una opción del broker es elegir un IP. En este caso Raspberry Pi IP address 
    broker_address="iot.eclipse.org"

    pub = mqtt.Client() 

    pub.on_connect = on_connectpub 

    pub.connect(broker_address, 1883, 60) 


    pub.loop_start()    

##    peticiónModo = {"modo?": 1}
##
##    json_string = json.dumps(peticiónModo) # Convertir en formato json
##    pub.publish("/modo/", 1) # Publicamos json bajo de un topic basado en key. 
##    time.sleep(1)
    pub.publish("/control/instrucción/modo/", 2) # Publicamos json bajo de un topic basado en key. 

##    print("pubModo: ", json_string)
    pub.disconnect()    
    pub.loop_stop()

pubTest()