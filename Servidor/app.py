# Librerías de Flask y funciones relacionadas 
from flask import Flask, flash, redirect, render_template, request, session, jsonify
# from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

# Crear la aplicación de Flask
app = Flask(__name__)

# Configurar Flask para asegurarse de que los templates se vuelven a cargar automáticamente
app.config["TEMPLATES_AUTO_RELOAD"] = True
#app.config["TEMPLATES_AUTO_RELOAD"] = False


# Configure la sesión de Flask para utilizar el sistema de archivos en lugar de las cookies
from flask_session import Session
from tempfile import mkdtemp
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Librería de SQL
import sqlite3

# Librerías para el manejo de objetos JSON
import json
import ast

# Librería para convertir entre formatos de tiempo en /verParcela
from datetime import datetime


# Asegurarse de que las respuestas no se guardan
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Crear un decorador de funciones que exija que el usuario esté validado
from functools import wraps
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("idUsuario") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Librería y configuración MQTT
from flask_mqtt import Mqtt
#app.config['MQTT_BROKER_URL'] = 'iot.eclipse.org'
#app.config['MQTT_BROKER_URL'] = 'test.mosquitto.org' 
#app.config['MQTT_BROKER_URL'] = '192.168.1.128' #piA
app.config['MQTT_BROKER_URL'] = '192.168.43.25' #Jaime phone



app.config['MQTT_BROKER_PORT'] = 1883
#app.config['MQTT_BROKER_URL'] = 'localhost'm
#memoryviewm
#m
#app.config['MQTT_BROKER_PORT'] = 80
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False


# Modos de operación
EMERGENCIA = 0
INACTIVO = 1
NAVEGACIÓN = 2
SONDEO = 3
modo = INACTIVO
estadoPiA = "testEstadoPiA"
estadoArduinoA = "testEstadoArduinoA"
estadoPiB = "testEstadoPiB"
estadoArduinoB = "testEstadoArduinoB" 


# Comunicación MQTT 
clienteMQTT = Mqtt(app)         # se subscribe y publica a los distintos topics para recibir y enviar control y datos al robot
topics = ['control/RobotServidor/syncModo/',    # espera a peticiones de actualización de modo por parte del robot 
          'control/RobotServidor/modo/',        # actualiza el modo del robot
          'control/estadoPiA/',                 # espera a actualizaciones sobre el estado de PiA
          'control/estadoArduinoA/',            #   "    "        "          "   "    "    "  ArduinoA
          'control/estadoPiB/',                 #   "    "        "          "   "    "    "  PiB
          'control/estadoArduinoB/',            #   "    "        "          "   "    "    "  ArduinoB
          'navegación/coordAct/',               # espera a actualizaciones sobre la posición actual del robot
          'navegación/trayectoria/',             # espera a la trayectoria generada por PiA
          'RobotServidor/resultados/fotos/'
         ]                                

# Variables globales modificadas vía MQTT (y /controlRobot) y recogidas en distintos routes de Flask
coordAct = [0,0]                        # modificada en el topic: 'navegación/coordAct/'
trayectoria = [[0,0], [0,0], [0,0]]     # modificada en el topic: 'navegación/trayectoria/'
idSesion = 0                            # modificada por el POST de /controlRobot

# Funciones ejecutadas al conectarse al bróker MQTT y al recibir los distintos mensajes
@clienteMQTT.on_connect()
def handle_connect(client, userdata, flags, rc):
    """Subscribirse a todos los topics de MQTT"""
    for topic in topics:
        clienteMQTT.subscribe(topic)
        
import base64
from time import sleep
@clienteMQTT.on_message()
def handle_mqtt_message(client, userdata, message):
    """Procesar el mensaje MQTT dependiendo del topic"""
    
    topic2 = message.topic
    if topic2 != 'RobotServidor/resultados/fotos/': 
        # Parsear el mensaje entre el topic y el payload
        data = dict(
            topic=message.topic,
            payload=message.payload.decode()
        )
        topic = data["topic"]
        payload = json.loads(data["payload"])   

        global modo   # necesario sólo para el topic 'control/RobotServidor/modo/'
        
        print("subbed")

        # Actualizar el modo del robot si se recibe una petición
        if topic == 'control/RobotServidor/syncModo/':

            if payload == 1: 
                print("El servidor ha recibido de parte del robot una petición de actualización de modo")
                sleep(2)
                modoJSON = json.dumps({"modo": str(modo)})
                clienteMQTT.publish("control/ServidorRobot/", modoJSON)
        
        # Cambiar el modo del sistema al modo recibido del robot
        elif topic == 'control/RobotServidor/modo/':
            modo = payload
            print("El robot ha indicado que su modo es: ", modo, ". Actualizando el modo en el servidor...")
            modoJSON = json.dumps({"modo": str(modo)})
            clienteMQTT.publish('control/ServidorRobot/', modoJSON)



        # Modificar la variable global coordAct para recogerla en /_rp
        elif topic == 'navegación/coordAct/':
            global coordAct
            coordAct = payload
            print("El servidor ha recibido la posición actual del robot: ", coordAct)

        # Modificar la variable global trayectoria para recogerla en /_rc
        elif topic == 'navegación/trayectoria/':
            global trayectoria  
            trayectoria = payload["trayectoria"]
            print("El servidor ha recibido la trayectoria generada por el robot: ", trayectoria)

        # Actualizar el estado de PiA para reflejarlo en /controlRobot
        elif topic == 'control/estadoPiA/':
            global estadoPiA  
            estadoPiA = payload
            print("El servidor ha recibido el estado de PiA: ", estadoPiA)

        # Actualizar el estado de ArduinoA para reflejarlo en /controlRobot
        elif topic == 'control/estadoArduinoA/':
            global estadoArduinoA  
            estadoArduinoA = payload
            print("El servidor ha recibido el estado de ArduinoA: ", estadoArduinoA)
        
        # Actualizar el estado de PiB para reflejarlo en /controlRobot
        elif topic == 'control/estadoPiB/':
            global estadoPiB  
            estadoPiB = payload
            print("El servidor ha recibido el estado de PiB: ", estadoPiB)

        # Actualizar el estado de ArduinoB para reflejarlo en /controlRobot
        elif topic == 'control/estadoArduinoB/':
            global estadoArduinoB 
            estadoArduinoB = payload
            print("El servidor ha recibido el estado de ArduinoB: ", estadoArduinoB)

    elif topic2 == 'RobotServidor/resultados/fotos/':
        print("foto recibida")
        foto = message.payload.decode('ascii')

        imgdata = base64.b64decode(foto)

        with open('output.jpg', 'wb') as f:
            f.write(imgdata)
            print("saved foto")
            
# Log de MQTT
MQTT_LOG_INFO = 0x01
MQTT_LOG_NOTICE	= 0x02
MQTT_LOG_WARNING = 0x04
MQTT_LOG_ERR = 0x08
MQTT_LOG_DEBUG = 0x10
@clienteMQTT.on_log()
def handle_logging(client, userdata, level, buf):
    if level == MQTT_LOG_INFO:
        print('MQTT Log Info: {}'.format(buf))
    elif level == MQTT_LOG_NOTICE:
        print('MQTT Log Notice: {}'.format(buf))
    elif level == MQTT_LOG_WARNING:
        print('MQTT Log Warning: {}'.format(buf))
    elif level == MQTT_LOG_ERR:
        print('MQTT Log Error: {}'.format(buf))
    #elif level == MQTT_LOG_DEBUG:
    #   print('MQTT LogDebug: {}'.format(buf))
    
    


############################################### Aquí empiezan las definiciones de los endpoints/routes de Flask ###############################################

@app.route("/crearUsuario", methods=["GET", "POST"])
def crearUsuario():
    """Crear un usuario nuevo"""

    # Borrar los datos de la sesión anterior
    session.clear()     

    # Mostrar la página de creación de usuarios
    if request.method == "GET":
        return render_template("crearUsuario.html")

    # Procesar los datos del nuevo usuario introducidos en crearUsuario.html
    elif request.method == "POST":

        # Abrir la conexión con la base de datos SQL
        con = sqlite3.connect('tfm.db')     
        db = con.cursor()                   

        # Recoger el nombre, la contraseña, y el correo del usuario introducidos en el formulario de crearUsuario.html
        usuarioDeseado = request.form.get("usuario")
        contraseña = request.form.get("contraseña")
        correo = request.form.get("email")

        # Asegurarse de que no existe el usuario elegido
        db.execute("SELECT usuario FROM clientes WHERE usuario=?", (usuarioDeseado,))   
        usuariosExistentes = db.fetchall()
        if len(usuariosExistentes) != 0:
            return "Ya existe el usuario"

        # Encriptar la contraseña del usuario
        contraseñaEncriptada = generate_password_hash(contraseña)   

        # Añadir este nuevo usuario a la base de datos
        db.execute('INSERT INTO clientes ("idUsuario","usuario","contraseña","email") VALUES (NULL,?,?,?)', (usuarioDeseado, contraseñaEncriptada, correo,))

        # Cerrar la conexión con la base de datos
        con.commit()
        con.close()

        # Redirigir a la página de inicio
        return redirect("/")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Entrar a la cuenta del usuario"""

    # Borrar los datos de la sesión anterior
    session.clear()     

    # Mostrar la página de login
    if request.method == "GET":
        return render_template("login.html")

    # Establecer la sesión actual del usuario introducido en login.html
    elif request.method == "POST":

        # Abrir la conexión con la base de datos SQL
        con = sqlite3.connect('tfm.db')
        db = con.cursor()

        # Recoger el nombre y la contraseña introducidos en el formulario de login.html
        usuario = request.form.get("usuario")
        contraseñaIntroducida = request.form.get("contraseña")

        # Asegurarse de que existe el usuario elegido y la contraseña es correcta
        db.execute("SELECT usuario,contraseña,idUsuario FROM clientes WHERE usuario=?", (usuario,))   # query database for desired username
        usuarios_contraseñas = db.fetchall()

        # Cerrar la conexión con la base de datos
        con.close()

        # Asegurarse de que existe el usuario
        if len(usuarios_contraseñas) == 0:
            return "No existe el usuario"

        # Extraer la contraseña asociada a este usuario en la base de datos
        contraseñaAlmacenada = usuarios_contraseñas[0][1]

        # Asegurarse de que la contraseña es correcta
        if not check_password_hash(contraseñaAlmacenada, contraseñaIntroducida):
            return "La contraseña no es correcta"

        # Almacenar los datos de la sesión en la variable global de Flask (un diccionario llamado "session")
        session["idUsuario"] = usuarios_contraseñas[0][2]
        session["usuario"] = usuarios_contraseñas[0][0]

        # Redirigir a la página de inicio
        return redirect("/")



@app.route("/")     # este endpoint sólo al método GET
@login_required
def index():
    """Panel de control del usuario"""

    # Abrir la conexión con la base de datos SQL
    con = sqlite3.connect('tfm.db')
    db = con.cursor()

    # Adquirir lista de todas las parcelas de este usuario
    db.execute("SELECT nombreParcela FROM parcelas WHERE usuario=?", (session["usuario"],))
    nombresParcelas = db.fetchall()

    # Adquirir lista de todas las sesiones pendientes, independientemente del usuario
    db.execute("SELECT tiempoEjecución, idSesión, coordObjs FROM objetivos WHERE estado=? ORDER BY tiempoEjecución ASC;", ('Pendiente',))
    sesionesPendientes = db.fetchall()

    # Cerrar la conexión con la base de datos
    con.close()

    # Pasar la lista de parcelas y de las sesiones pendientes a sus respectivos menúes desplegables de index.html
    return render_template("index.html", nombresParcelas=nombresParcelas, sesionesPendientes=sesionesPendientes)



@app.route('/crearParcela', methods=['GET', 'POST']) 
@login_required
def crearParcela():
    """Obtener la geometría de una parcela (polígono y línea) para guíar la navegación del robot"""

    # Mostrar la página de creación de parcelas
    if request.method == 'GET':
        return render_template("crearParcela.html")

    # Almacenar la geometría de la nueva parcela en la base de datos
    elif request.method == 'POST':
        
        # Recibir el JSON de Ajax de crearParcela.html y extraer el nombre de la parcela y su geometría (polígono y línea)
        geometríaDeAjax = request.json
        nombreParcela = geometríaDeAjax['nombreParcela']
        poli = str(geometríaDeAjax['poli'])     # poli = [[[],[], ..., []]] así que convertirlo a string para poder quitarle los corchetes del principio y el final
        poli = poli[1:len(poli)-1]              # poli =  [[],[], ..., []]
        línea = geometríaDeAjax['linea']

        # Formar un JSON con la geometría para enviar a la base de datos
        geometría = str({"poli": poli, "línea": línea})

        # Abrir la conexión con la base de datos SQL
        con = sqlite3.connect('tfm.db')
        db = con.cursor()
        
        # Almacenar la geometría de esta parcela y asociarla al usuario y al nombre de la parcela
        db.execute('INSERT INTO parcelas ("usuario","nombreParcela","geometría") VALUES (?,?,?)', (session["usuario"],nombreParcela,geometría,))

        # Cerrar la conexión con la base de datos
        con.commit()
        con.close()

        # Responder al Ajax de crearParcela.html que se ha recibido y almacenado correctamente el nombre de la parcela y su geometría
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    

@app.route('/verParcela', methods=['GET', 'POST']) 
@login_required
def verParcela():
    """Ver una parcela y elegir unas coordendas objetivo"""

    # Mostrar la parcela elegida en index.html, centrándola en el mapa 
    if request.method == 'GET':

        # Abrir la conexión con la base de datos SQL
        con = sqlite3.connect('tfm.db')
        db = con.cursor()
        
        # Obtener el nombre de la parcela elegida en el respectivo menú desplegable de index.html para mostarla en verParcela.html
        nombreParcela = request.args.get('nombreParcela')

        # Obtener la geometría de la parcela elegida para centrar el mapa de verParcela.html en esa parcela
        db.execute("SELECT geometría FROM parcelas WHERE usuario=? AND nombreParcela=?", (session["usuario"],nombreParcela,))
        geometría = db.fetchall()

        # Cerrar la conexión con la base de datos
        con.close()

        # Extraer las coordenadas de la línea de esa parcela
        geomCoords = geometría[0][0]
        print("geomCoords = ", geomCoords)
        
        geomCoords = ast.literal_eval(geomCoords)
        poli = str(geomCoords['poli']) 
        poli = poli.replace('[','').split('],')
        [map(int, s.replace(']','').split(',')) for s in poli]
        
        print("poli = ", poli)
        print("type poli = ", type(poli))
        poli[len(poli)-1] = poli[len(poli)-1].replace(']]','')
        print("poli = ", poli)
        print("type poli = ", type(poli))

        poliWeb = []
        for coord in poli:
            coord = coord.split(', ')
            print("coord = ", coord)
            print("type coord = ", type(coord))
 
            coordLon = float(coord[0])
            coordLat = float(coord[1])
            print("coordLon = ", coordLon)
            print("type coordLon = ", type(coordLon))
            print("coordLat = ", coordLat)
            print("type coordLat = ", type(coordLat))

            poliWeb.append([coordLon, coordLat])

        línea = str(geomCoords['línea']) 
        línea = línea.replace('[','').split('],')
        [map(int, s.replace(']','').split(',')) for s in línea]

        # Calcular el punto medio de la línea para centrar el mapa
        punto1 = línea[0]
        punto2 = línea[1]
        punto2 = punto2[1:len(punto2)-2]

        x1, y1 = punto1.split(',')      # extraer las coordenadas del primer punto de la línea
        x2, y2 = punto2.split(',')      # extraer las coordenadas del segundo punto de la línea

        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)     

        xCentro = (x1+x2)/2        # calcular el valor medio de la coordenada x
        yCentro = (y1+y2)/2        # calcular el valor medio de la coordenada y

        puntoCentro = json.dumps({"xCentro": xCentro, "yCentro": yCentro})  # crear un JSON con estos valores
        
        # Enviar el nombre de la parcela y su punto medio (para centrar el mapa) a verParcela.html
        return render_template("verParcela.html", nombreParcela=nombreParcela, puntoCentro=puntoCentro, poli=poliWeb)

 
    # Almacenar unas nuevas coordObjs en la base de datos, asociándolas al usuario y parcela correspondientes
    elif request.method == 'POST':
        
        # Recibir JSON de Ajax de verParcela.html y extraer la fecha de ejecución, el nombre de la parcela, y las coordenadas objetivo elegidas
        coordObjsDeAjax = request.json      # !!!!!! CHANGE NAME TO COORD_TIEMPO_ETC
        tiempoEjecución = coordObjsDeAjax[0]
        tiempoEjecución = datetime.strptime(tiempoEjecución, '%Y-%m-%d %H:%M:%S')
        nombreParcela = coordObjsDeAjax[1]
        coordObjs = coordObjsDeAjax[2:]

        # Abrir la conexión con la base de datos SQL
        con = sqlite3.connect('tfm.db')
        db = con.cursor()

        # Obtener el id de la parcela actual
        db.execute("SELECT idParcela FROM parcelas WHERE usuario=? AND nombreParcela=?", (session["usuario"],nombreParcela,))
        idUsuarioParcela = db.fetchall()[0][0]

        # Almacenar la sesión, es decir, las coordenadas objetivo y su tiempo de ejecución y asociarla idUsuarioParcela (el usuario y la parcela actual) 
        db.execute('INSERT INTO objetivos ("coordObjs","tiempoEjecución","idUsuarioParcela") VALUES (?,?,?)', (str(coordObjs),tiempoEjecución,int(idUsuarioParcela),))

        # Cerrar la conexión con la base de datos
        con.commit()
        con.close()

        # Responder al Ajax de verParcela.html que se ha recibido y almacenado correctamente la sesión
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    


@app.route('/controlRobot', methods=['GET', 'POST']) 
def controlRobot():
    """Asignar una coordObj al robot y aprobar la trayectoria que éste genera a partir de dicha coordObj"""

    # Mostrar la parcela y coordObj seleccionada en index.html
    if request.method == 'GET':
        
        # Obtener los datos de la sesión elegida en el menú desplegable de index.html
        sesionElegida = request.args.get('sesión')
        print("sesionElegida = ", sesionElegida)
        tiempoId_coordObjs = sesionElegida.split(", '")
        idSesión = sesionElegida.split(', ')[1]      
        coordObjs = tiempoId_coordObjs[1]
        coordObjs = coordObjs[:len(coordObjs)-2]

        # Abrir la conexión con la base de datos SQL
        con = sqlite3.connect('tfm.db')
        db = con.cursor()
        
        # Obtener la geometría de la parcela elegida para centrar el mapa de verParcela.html en esa parcela
        db.execute("SELECT idUsuarioParcela FROM objetivos WHERE idSesión=?", (idSesión,))
        idUsuarioParcela = db.fetchall()

        # Extraer las coordenadas de la línea de esa parcela
        idParcela = idUsuarioParcela[0][0]
        print("idParcela = ", idParcela)
        
        # Obtener la geometría de la parcela elegida para centrar el mapa de verParcela.html en esa parcela
        db.execute("SELECT geometría FROM parcelas WHERE idParcela=?", (idParcela,))
        geometría = db.fetchall()

        # Cerrar la conexión con la base de datos
        con.close()

        # Extraer las coordenadas de la línea de esa parcela
        geomCoords = geometría[0][0]
        print("geomCoords = ", geomCoords)
        
        geomCoords = ast.literal_eval(geomCoords)
        poli = str(geomCoords['poli']) 
        poli = poli.replace('[','').split('],')
        [map(int, s.replace(']','').split(',')) for s in poli]
        
        print("poli = ", poli)
        print("type poli = ", type(poli))
        poli[len(poli)-1] = poli[len(poli)-1].replace(']]','')
        print("poli = ", poli)
        print("type poli = ", type(poli))

        poliWeb = []
        for coord in poli:
            coord = coord.split(', ')
            print("coord = ", coord)
            print("type coord = ", type(coord))
 
            coordLon = float(coord[0])
            coordLat = float(coord[1])
            print("coordLon = ", coordLon)
            print("type coordLon = ", type(coordLon))
            print("coordLat = ", coordLat)
            print("type coordLat = ", type(coordLat))

            poliWeb.append([coordLon, coordLat])

        línea = str(geomCoords['línea']) 
        línea = línea.replace('[','').split('],')
        [map(int, s.replace(']','').split(',')) for s in línea]

        # Calcular el punto medio de la línea para centrar el mapa
        punto1 = línea[0]
        punto2 = línea[1]
        punto2 = punto2[1:len(punto2)-2]

        x1, y1 = punto1.split(',')      # extraer las coordenadas del primer punto de la línea
        x2, y2 = punto2.split(',')      # extraer las coordenadas del segundo punto de la línea

        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)     

        xCentro = (x1+x2)/2        # calcular el valor medio de la coordenada x
        yCentro = (y1+y2)/2        # calcular el valor medio de la coordenada y

        puntoCentro = json.dumps({"xCentro": xCentro, "yCentro": yCentro})  # crear un JSON con estos valores
        
        # Mostrar coordObjs en controlRobot.html (y no olvidar a qué sesión pertenecen)
        return render_template("controlRobot.html", coordObjs=coordObjs, idSesión=idSesión, puntoCentro=puntoCentro, poli=poliWeb)


    # Enviar la geometría de la parcela a PiA o la señal de Marcha/Paro desde controlRobot.html
    elif request.method == 'POST':
        
        # Recibir JSON de Ajax de controlRobot.html (puede ser una coordenada objetivo o una señal de Marcha/Paro)
        coordObj_o_control_DeAjax = request.json
        
        # En caso de recibir un cambio de modo, enviarlo a PiA para prepararlo para navegar
        if "modo" in coordObj_o_control_DeAjax:

            # Extraer del Ajax el modo
            modo = coordObj_o_control_DeAjax["modo"]

            # Enviar el JSON a PiA
            modoJSON = json.dumps({"modo": str(modo)})
            clienteMQTT.publish("control/ServidorRobot/", modoJSON)


        # En caso de recibir una coordenada objetivo, enviarla a PiA junto con la geometría de la parcela correspondiente
        elif "coordObj" in coordObj_o_control_DeAjax:

            # Extraer del Ajax la sesión y la coordenada objetivo 
            global idSesion
            idSesion = coordObj_o_control_DeAjax["idSesión"]        # Modificar la variable global idSesión para recogerla en el elif del POST de /controlRobot (justo más abajo)
            coordObj = coordObj_o_control_DeAjax["coordObj"]        # Enviar a PiA
            
            # Abrir la conexión con la base de datos SQL
            con = sqlite3.connect('tfm.db')
            db = con.cursor()

            # Identificar el usuario y la parcela correspondientes a este objetivo
            db.execute("SELECT idUsuarioParcela FROM objetivos WHERE idSesión=?", (idSesion,))
            idUsuarioParcela = db.fetchall()
            idUsuarioParcela = idUsuarioParcela[0][0]

            # Hallar la geometría de la parcela identificada en el paso anterior
            db.execute("SELECT geometría FROM parcelas WHERE idParcela=?", (idUsuarioParcela,))
            geometria = db.fetchall()
            geometria = geometria[0][0]
            
            # Cerrar la conexión con la base de datos
            con.close()

            # Enviar un JSON a PiA con la coordenada objetivo y la geometría de la parcela para generar una trayectoria
            coordObj_geometria_idSesion = json.dumps({"coordObj": coordObj, "geometria": geometria, "idSesion": idSesion})
            clienteMQTT.publish("navegación/coordObj_geometría/", str(coordObj_geometria_idSesion))

        # En caso de recibir una señal de Marcha/Paro, enviarla a PiA para navegar la trayectoria
        elif "marchaOparo" in coordObj_o_control_DeAjax:

            # Extraer del Ajax la señal de Marcha/Paro 
            marchaOparo = coordObj_o_control_DeAjax["marchaOparo"]

            # Enviar el JSON a PiA
            marchaParoJSON = json.dumps({"marchaParo": str(marchaOparo)})
            clienteMQTT.publish("control/ServidorRobot/", str(marchaParoJSON))

            # Abrir la conexión con la base de datos SQL
            con = sqlite3.connect('tfm.db')     
            db = con.cursor()       

            # Ya que el usuario ha aprobado la trayectoria, actualizar la sesión en la base de datos
            db.execute("UPDATE objetivos SET trayectorias=? WHERE idSesión=?", (str(trayectoria),idSesion,))
            
            # Cerrar la conexión con la base de datos
            con.commit()
            con.close()

        # En caso de recibir una señal de mover la cámara, enviarla a PiA para mover la cámara manualmente
        elif "moverCamara" in coordObj_o_control_DeAjax:

            # Extraer del Ajax la dirección de navegación
            moverCamaraManual = coordObj_o_control_DeAjax["moverCamara"]

            # Enviar el JSON a PiA
            moverCamaraManualJSON = json.dumps({"moverCamara": str(moverCamaraManual)})
            clienteMQTT.publish("control/ServidorRobot/", str(moverCamaraManualJSON))


        # En caso de recibir una señal de navegación manual, enviarla a PiA para navegar manualmente
        elif "navManual" in coordObj_o_control_DeAjax:

            # Extraer del Ajax la dirección de navegación
            direcciónManual = coordObj_o_control_DeAjax["navManual"]

            # Enviar el JSON a PiA
            direcciónManualJSON = json.dumps({"navManual": str(direcciónManual)})
            clienteMQTT.publish("control/ServidorRobot/", str(direcciónManualJSON))

        # En caso de recibir una señal de navegación manual, enviarla a PiA para navegar manualmente
        elif "antena" in coordObj_o_control_DeAjax:

            # Extraer del Ajax la dirección de navegación
            antena = coordObj_o_control_DeAjax["antena"]

            # Enviar el JSON a PiA
            antenaJSON = json.dumps({"antena": str(antena)})
            clienteMQTT.publish("control/ServidorRobot/", str(antenaJSON))


        # Responder al Ajax de controlRobot.html que se ha recibido la coordenada objetivo o la trayectoria generada por PiA
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


# Actualizar controlRobot.html con la trayectoria recibida del robot vía MQTT
@app.route('/_cr') 
def cr():
    return jsonify(trayectoria=trayectoria)

# Actualizar controlRobot.html con la posición actual recibida del robot vía MQTT
@app.route('/_pr')
def rp():
    rlat = coordAct[1]
    rlon = coordAct[0]
    return jsonify(latr=rlat, lonr=rlon)

# Actualizar controlRobot.html con el modo y los estados del recibidos del robot vía MQTT
@app.route('/_md')
def md():
    return jsonify(modo=modo, estadoPiA=estadoPiA, estadoArduinoA=estadoArduinoA, estadoPiB=estadoPiB, estadoArduinoB=estadoArduinoB)


# TODO: imitar lo que se ha hecho para /history en /resultados 
#@app.route("/history")
#@login_required
#def history():
#    """Show history of transactions"""

#    transactions = db.execute("SELECT * FROM transactions WHERE username = :username ORDER BY time", username=session["username"])

#    return render_template("history.html", table=transactions)



@app.route("/logout")
def logout():
    """Cerrar la sesión del usuario actual"""

    # Borrar los datos de la sesión anterior
    session.clear()     

    # Redirigir a la página de inicio
    return redirect("/")
