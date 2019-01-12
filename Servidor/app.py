# Librerías de Flask y funciones relacionadas 
from flask import Flask, flash, redirect, render_template, request, session, jsonify
# from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

# Crear la aplicación de Flask
app = Flask(__name__)

# Configurar Flask para asegurarse de que los templates se vuelven a cargar automáticamente
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configurar la sesión de Flask para utilizar el sistema de archivos en lugar de las cookies
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
app.config['MQTT_BROKER_URL'] = 'localhost' #Self
#app.config['MQTT_BROKER_URL'] = '192.168.1.128' #piA
#app.config['MQTT_BROKER_URL'] = '192.168.43.25' #móvil
#app.config['MQTT_BROKER_URL'] = '192.168.1.135' #piB
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False


# Modo de operación y estados
EMERGENCIA = 0
INACTIVO = 1
NAVEGACIÓN = 2
SONDEO = 3
modo = INACTIVO
estadoPiA = "Apagado"
estadoArduinoA = "Apagado"
estadoPiB = "Apagado"
estadoArduinoB = "Apagado" 


# Comunicación MQTT 
clienteMQTT = Mqtt(app)                 # se subscribe y publica a los distintos topics para recibir y enviar control y datos al robot

topics = ['RobotServidor/modo/leer',            # recibe a peticiones de actualización de modo por parte del robot 
          'RobotServidor/modo/escribir',        # recibe el modo actual del robot    
          'RobotServidor/estado/PiA',           # espera a actualizaciones sobre el estado de PiA
          'RobotServidor/estado/ArduinoA',      #   "    "        "          "   "    "    "  ArduinoA
          'RobotServidor/estado/PiB',           #   "    "        "          "   "    "    "  PiB
          'RobotServidor/estado/ArduinoB',      #   "    "        "          "   "    "    "  ArduinoB
          'RobotServidor/coordAct',             # espera a actualizaciones sobre la posición actual del robot
          'RobotServidor/trayectoria',          # espera a la trayectoria generada por PiA
          'RobotServidor/resultados/fotos/I',   # recibe fotos de la vegetación al lado izquierdo del robot para mostrar en /controlRobot
          'RobotServidor/resultados/fotos/D',   #   "      "   "  "      "      "   "   derecho    "    "    "      "    "          " 
          'RobotServidor/resultados/medidas'    # almacena los resultados en la base de datos
         ]                                

# Variables globales modificadas vía MQTT (y /controlRobot) y recogidas en distintos routes de Flask
coordAct = [0,0]                        # modificada en el topic: 'navegación/coordAct/'
trayectoria = [[0,0], [0,0], [0,0]]     # modificada en el topic: 'navegación/trayectoria/'
idSesion = 0                            # modificada por el POST de /controlRobot

# Subscribirse a todos los topics
@clienteMQTT.on_connect()
def handle_connect(client, userdata, flags, rc):
    """Subscribirse a todos los topics de MQTT"""

    for topic in topics:
        clienteMQTT.subscribe(topic)
        
import base64
from time import sleep
# Procesar datos recibidos por MQTT
@clienteMQTT.on_message()
def handle_mqtt_message(client, userdata, message):
    """Procesar el mensaje MQTT dependiendo del topic"""
    
    # Parsear el mensaje entre el topic y el payload
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    topic = data["topic"]
    payload = data["payload"]   

    global modo   # necesario sólo para el topic 'control/RobotServidor/modo/'
    
    #print("Servidor: ", topic," <---<---<--- ", payload, " <---<---<--- Robot")

    # Actualizar el modo del robot si se recibe una petición
    if topic == 'RobotServidor/modo/leer':
        sleep(5)
        clienteMQTT.publish("ServidorRobot/modoA", modo, qos=1)
        clienteMQTT.publish("ServidorRobot/modoB", modo, qos=1)
        print("Servidor: ServidorRobot/modo --->--->---> ", modo, " --->--->---> Robot")

    # Cambiar el modo del sistema al modo recibido del robot
    elif topic == 'RobotServidor/modo/escribir':
        
        if modo != EMERGENCIA:
            modo = int(payload)
            
        clienteMQTT.publish("ServidorRobot/modoA", modo, qos=1)
        clienteMQTT.publish("ServidorRobot/modoB", modo, qos=1)
        print("Servidor: ServidorRobot/modo --->--->---> ", modo, " --->--->---> Robot")

    # Modificar la variable global coordAct para recogerla en /_rp
    elif topic == 'RobotServidor/coordAct':
        global coordAct
        coordAct = ast.literal_eval(payload)
        print("El servidor ha recibido la coordenada actual del robot: ", coordAct)

    # Modificar la variable global trayectoria para recogerla en /_rc
    elif topic == 'RobotServidor/trayectoria':
        global trayectoria 
        payload = json.loads(data["payload"])    
        trayectoria = payload["trayectoria"]
        print("El servidor ha recibido la trayectoria generada por el robot: ", trayectoria)

    # Actualizar el estado de PiA para reflejarlo en /controlRobot
    elif topic == 'RobotServidor/estado/PiA':
        global estadoPiA  
        estadoPiA = payload
        print("El servidor ha recibido el estado de PiA: ", estadoPiA)

    # Actualizar el estado de ArduinoA para reflejarlo en /controlRobot
    elif topic == 'RobotServidor/estado/ArduinoA':
        global estadoArduinoA  
        estadoArduinoA = payload
        print("El servidor ha recibido el estado de ArduinoA: ", estadoArduinoA)
    
    # Actualizar el estado de PiB para reflejarlo en /controlRobot
    elif topic == 'RobotServidor/estado/PiB':
        global estadoPiB  
        estadoPiB = payload
        print("El servidor ha recibido el estado de PiB: ", estadoPiB)

    # Actualizar el estado de ArduinoB para reflejarlo en /controlRobot
    elif topic == 'RobotServidor/estado/ArduinoB':
        global estadoArduinoB 
        estadoArduinoB = payload
        print("El servidor ha recibido el estado de ArduinoB: ", estadoArduinoB)
    
    elif topic == 'RobotServidor/resultados/medidas':
        payload = json.loads(data["payload"])

        coordObj = str(payload["coordObj"]) 
        temperatura = payload["Temperatura"]
        humedad = payload["Humedad"]
        ec = payload["EC"]
        salinidad = payload["Salinidad"]
        sdt = payload["SDT"]
        epsilon = payload["Epsilon"]
        idSesion = payload["idSesión"]        
        verdeI = payload["verdeI"]        
        verdeD = payload["verdeD"]        

        print("El servidor ha recibido las medidas del robot")

        # Abrir la conexión con la base de datos SQL
        con = sqlite3.connect('tfm.db')     
        db = con.cursor()                   

        # Añadir los resultados junto con su coordObj a la base de datos
        db.execute('INSERT INTO resultados ("idSesión","coordObj","Temperatura","Humedad","EC","Salinidad","SDT","Epsilon","verdeI","verdeD") VALUES (?,?,?,?,?,?,?,?,?,?)', (idSesion,coordObj, temperatura,humedad,ec,salinidad,sdt,epsilon,verdeI,verdeD,))

        # Cerrar la conexión con la base de datos
        con.commit()
        con.close()
        

    elif topic == 'RobotServidor/resultados/fotos/I':
        print("fotoI recibida")
        foto = message.payload.decode('ascii')

        imgdata = base64.b64decode(foto)

        with open('static/fotoI.jpg', 'wb') as f:
            f.write(imgdata)
            print("saved fotoI")
    
    elif topic == 'RobotServidor/resultados/fotos/D':
        print("fotoD recibida")
        foto = message.payload.decode('ascii')

        imgdata = base64.b64decode(foto)

        with open('static/fotoD.jpg', 'wb') as f:
            f.write(imgdata)
            print("saved fotoD")
            
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
    elif level == MQTT_LOG_DEBUG:
       print('MQTT LogDebug: {}'.format(buf))
    
    


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
        # Nota: es simplemente un ejemplo de validación de datos en el servidor, aunque en realidad se haría en el lado del cliente
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



nombresParcelas = ""
@app.route("/")     # este endpoint sólo al método GET
@login_required
def index():
    """Página Inicial"""

    # Servir la página inicial index.html
    return render_template("index.html")



@app.route('/crearParcela', methods=['GET', 'POST']) 
@login_required
def crearParcela():
    """Obtener la geometría de una parcela (polígono y línea) para guíar la navegación del robot"""

    # Mostrar la página de creación de parcelas
    if request.method == 'GET':

        # Enviar un JSON con las coordenadas del centro del mapa
        # Nota: Idealmente serían valores dinámicos (eg. la granja del usuario)
        puntoCentro = json.dumps({"xCentro": -3.69, "yCentro": 40.410})

        # Enviar las coordenadas para centrar el mapa de crearParcela.html
        return render_template("crearParcela.html", puntoCentro=puntoCentro)

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



def calcularPoliCentro(geomCoords):
    """Calcular el punto central de una parcela según la línea"""

    # Extraer el polígono (contorno) de la parcela
    geomCoords = ast.literal_eval(geomCoords)
    poli = str(geomCoords['poli']) 
    poli = poli.replace('[','').split('],')
    [map(int, s.replace(']','').split(',')) for s in poli]
    poli[len(poli)-1] = poli[len(poli)-1].replace(']]','')
    
    # Convertir las coordenadas de texto a números
    poliWeb = []
    for coord in poli:
        coord = coord.split(', ')
        coordLon = float(coord[0])
        coordLat = float(coord[1])
        
        poliWeb.append([coordLon, coordLat])

    # Extraer la línea (hilera) de la parcela
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
    
    # Devolver las coordenadas del contro y las del punto centro
    return poliWeb, puntoCentro



@app.route('/verParcela', methods=['GET', 'POST']) 
@login_required
def verParcela():
    """Ver una parcela y elegir unas coordendas objetivo"""
   
    # Mostrar la parcela elegida en index.html, centrándola en el mapa 
    if request.method == 'GET':

        # Abrir la conexión con la base de datos SQL
        con = sqlite3.connect('tfm.db')
        db = con.cursor()
        
        # Adquirir lista de todas las parcelas de este usuario
        db.execute("SELECT nombreParcela FROM parcelas WHERE usuario=?", (session["usuario"],))
        nombresParcelas = db.fetchall()
        
        # Obtener el nombre de la parcela elegida en el respectivo menú desplegable de index.html para mostarla en verParcela.html
        nombreParcela = request.args.get('nombreParcela')
    
        if nombreParcela == None:
            db.execute("SELECT nombreParcela FROM parcelas WHERE usuario=?", (session["usuario"],))
            nombreParcela = db.fetchall()
            nombreParcela = nombreParcela[0][0]
        
        # Obtener la geometría de la parcela elegida para centrar el mapa de verParcela.html en esa parcela
        db.execute("SELECT idParcela, geometría FROM parcelas WHERE usuario=? AND nombreParcela=?", (session["usuario"],nombreParcela,))
        id_geometría = db.fetchall()

        # Extraer la sesión 
        idUsuarioParcela = id_geometría[0][0]

        # Hallar todas las sesiones asociadas a este usuario
        db.execute("SELECT idSesión FROM objetivos WHERE idUsuarioParcela=?", (idUsuarioParcela,))
        idsesiones = db.fetchall()

        # Convertir de [(),(), ...] a [, , ...]
        idList = []
        for ids in idsesiones:
            idList.append(ids[0])

        # Extraer las coordenadas de la línea de esa parcela
        geomCoords = id_geometría[0][1]

        # Hallar el contorno y punto centro de la parcela        
        poli, puntoCentro = calcularPoliCentro(geomCoords)

        # Hallar todos los resultados asociados a todas las sesiones
        todosResultados = []
        for ids in idList:
            db.execute("SELECT coordObj,Temperatura,Humedad,EC,Salinidad,SDT,Epsilon,tiempo FROM resultados WHERE idSesión=?", (ids,))   
            resultados = db.fetchall()

            todosResultados = todosResultados + resultados

        # Hallar las fechas de las sesiones y filtrar los resultados mostrados si lo indica /verParcela        
        fechas = []
        resultadosFiltrados = []
        for resultado in todosResultados:
            fechaTiempo = datetime.strptime(resultado[7], '%Y-%m-%d %H:%M:%S')
            fecha = str(fechaTiempo.date())

            if fecha not in fechas:
                fechas.append(fecha)

            if fecha == request.args.get("menuFechas"):
                resultadosFiltrados.append(resultado)

        # Enviar el nombre de la parcela y su punto medio (para centrar el mapa) a verParcela.html
        return render_template("verParcela.html", nombresParcelas=nombresParcelas, nombreParcela=nombreParcela, puntoCentro=puntoCentro, poli=poli, resultados=resultadosFiltrados, fechas=fechas)

 
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

import csv  
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase


@app.route('/mandarResultados', methods=['POST']) 
def mandarResultados():
    resultados = request.json 

    # Abrir la conexión con la base de datos SQL
    con = sqlite3.connect('tfm.db')
    db = con.cursor()

    # Obtener el correo del usuario actual
    db.execute("SELECT email FROM clientes WHERE usuario=?", (session["usuario"],))
    correo = db.fetchall()[0][0]

    # Cerrar la conexión con la base de datos
    con.commit()
    con.close()

    # Guardar los datos en un archivo csv    
    with open("resultados.csv", "w") as f:
        writer = csv.writer(f)
        fields = ["coordObj","temp","hum","ec","sal","sdt","epsilon","tiempo"]
        writer.writerow(fields)
        for fila in resultados:  
            fields = [fila["coordObj"],float(fila["temp"]),float(fila["hum"]),float(fila["ec"]),float(fila["sal"]),float(fila["sdt"]),float(fila["epsilon"]),fila["tiempo"]]
            writer.writerow(fields)
    
    # Mandar el archivo csv por correo
    msg = MIMEMultipart() # Escribe la información que he dado antes en campos correspondientes
    msg["From"] = "KYevheniya@gmail.com"
    msg["To"] = "KYevheniya@gmail.com"
    msg["Subject"] = "Resultados Robot Agricola"
    msg.preamble = "File attached"

    ctype, encoding = mimetypes.guess_type("resultados.csv") # Preparación para mandar el correo
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    fp = open("resultados.csv", "rb")
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(attachment) 
    attachment.add_header("Content-Disposition", "attachment", filename="resultados.csv") # Se utiliza 3 headers que incluye el archivo csv
    msg.attach(attachment)

    server = smtplib.SMTP("smtp.gmail.com","587") # Usamos el servidor de google. Sólo funciona con el puerto 587
    server.ehlo()
    server.starttls()
    server.login("KYevheniya@gmail.com","Yevheniya110562894") # Hace un login con mi información
    server.sendmail("KYevheniya@gmail.com", "KYevheniya@gmail.com", msg.as_string()) # Envia el correo
    server.quit()
  
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/controlRobot', methods=['GET', 'POST']) 
def controlRobot():
    """Asignar una coordObj al robot y aprobar la trayectoria que éste genera a partir de dicha coordObj"""

    # Mostrar la parcela y coordObj seleccionada en index.html
    if request.method == 'GET':
        
        # Obtener los datos de la sesión elegida en el menú desplegable de index.html
        sesionElegida = request.args.get('sesión')

        # Abrir la conexión con la base de datos SQL
        con = sqlite3.connect('tfm.db')
        db = con.cursor()

        # Adquirir lista de todas las sesiones pendientes, independientemente del usuario
        db.execute("SELECT tiempoEjecución, idSesión, coordObjs FROM objetivos WHERE estado=? ORDER BY tiempoEjecución ASC;", ('Pendiente',))
        sesionesPendientes = db.fetchall()
        
        if sesionElegida == None:
            db.execute("SELECT idParcela FROM parcelas WHERE usuario=?", (session["usuario"],))
            idParcela = db.fetchall()
            idParcela = idParcela[0][0]

            db.execute("SELECT idSesión FROM objetivos WHERE idUsuarioParcela=?", (idParcela,))
            idSesión = db.fetchall()
            idSesión = idSesión[0][0]

            db.execute("SELECT coordObjs FROM objetivos WHERE idSesión=?", (idSesión,))
            coordObjs = db.fetchall()
            coordObjs = coordObjs[0][0]
        else:
            print("sesionElegida = ", sesionElegida)
            tiempoId_coordObjs = sesionElegida.split(", '")
            idSesión = sesionElegida.split(', ')[1]      
            coordObjs = tiempoId_coordObjs[1]
            coordObjs = coordObjs[:len(coordObjs)-2]

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

        # Extraer las coordenadas de la parcela
        geomCoords = geometría[0][0]
        poli, puntoCentro = calcularPoliCentro(geomCoords)
       
        # Mostrar coordObjs en controlRobot.html (y no olvidar a qué sesión pertenecen)
        return render_template("controlRobot.html", sesionesPendientes=sesionesPendientes, coordObjs=coordObjs, idSesión=idSesión, puntoCentro=puntoCentro, poli=poli)


    # Enviar las señales de control de controlRobot.html a PiA
    elif request.method == 'POST':
        
        # Recibir el JSON de controlRobot.html
        controlWeb = request.json

        # La mayoría de los comandos se envían a sus respectivos topics sin procesar nada
        if "topic" in controlWeb:
            topic = controlWeb["topic"]
            mensaje = controlWeb["mensaje"]

            if topic == "ServidorRobot/modo":
                if modo != EMERGENCIA:
                    clienteMQTT.publish("ServidorRobot/modoA", mensaje)
                    clienteMQTT.publish("ServidorRobot/modoB", mensaje)
            else:
                clienteMQTT.publish(topic, mensaje)


        # Al enviar una coordObj hay que enviar también la geometría de la parcela
        elif "coordObj" in controlWeb:

            # Extraer del Ajax la sesión y la coordenada objetivo 
            global idSesion
            idSesion = controlWeb["idSesión"]        # Modificar la variable global idSesión para recogerla en el elif del POST de /controlRobot (justo más abajo)
            coordObj = controlWeb["coordObj"]        # Enviar a PiA
            
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
            clienteMQTT.publish("ServidorRobot/coordObj_geometría", str(coordObj_geometria_idSesion))
       

        # Responder al Ajax de controlRobot.html que se ha recibido correctamente
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


# Actualizar controlRobot.html con el modo y los estados del recibidos del robot vía MQTT
@app.route('/_actualizarControlRobot')
def actualizarControlRobot():
    return jsonify(modo=modo, estadoPiA=estadoPiA, estadoArduinoA=estadoArduinoA, estadoPiB=estadoPiB, estadoArduinoB=estadoArduinoB, trayectoria=trayectoria, latr=coordAct[1], lonr=coordAct[0])



@app.route("/logout")
def logout():
    """Cerrar la sesión del usuario actual"""

    # Borrar los datos de la sesión anterior
    session.clear()     

    # Redirigir a la página de inicio
    return redirect("/")
