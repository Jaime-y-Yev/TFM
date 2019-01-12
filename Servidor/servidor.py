from time import sleep      # para ralentizar el checkeo de la variable matarHilos

# Librerías para la ejecución de programas de Windows mediante Python
import os
import subprocess


def arrancarServidor():
    """Arrancar los procesos que constituyen el servidor """

    print("Arrancando el servidor -----------------------------------------------")           

    print("Arrancando el broker de MQTT Mosquitto")  
    mosquitto = subprocess.Popen('c:/"Program Files"/mosquitto/mosquitto.exe', shell=True) 
    #mosquitto = subprocess.Popen(['powershell.exe','c:/"Program Files"/mosquitto/mosquitto.exe'])             
    sleep(1)

    print("Arrancando la base de datos de SQLite3")  
    phpLiteAdmin = subprocess.Popen('c:/MAMP/bin/php/php7.2.1/php.exe -S 0.0.0.0:90', shell=True, cwd='c:/MAMP/bin/phpliteAdmin')  # phpLiteAdmin: administrador de SQLite3 
    sleep(1)

    print("Arrancando la webapp de Flask")
    os.environ["FLASK_DEBUG"] = "False"                                              # no arrancar en modo de depuración
    flask = subprocess.Popen('flask run --host=0.0.0.0 --port=8080 --no-reload')     # arrancar la app de Flask
    sleep(1)

    return mosquitto, phpLiteAdmin, flask

def apagarServidor(mosquitto, phpLiteAdmin, flask):
    """Apagar los procesos del servidor"""

    print("Apagando el servidor -----------------------------------------------")

    print("Apagando la webapp de Flask")
    subprocess.Popen("taskkill /F /T /PID %i"%flask.pid)
    sleep(1)

    print("Apagando la base de datos de SQLite3")
    subprocess.Popen("taskkill /F /T /PID %i"%phpLiteAdmin.pid)
    sleep(1)

    print("Apagando el broker de MQTT Mosquitto")  
    subprocess.Popen("taskkill /F /T /PID %i"%mosquitto.pid)
    sleep(1)



# Arrancar el servidor por lo menos una vez
mosquitto, phpLiteAdmin, flask = arrancarServidor()

# Esperar a la señal introducida por el usuario mediante el teclado para matar o reiniciar los procesos
while True:

    comando = input()       

    if comando == 'm' or comando == 'r':

        if comando == 'r':
            print("Reiniciando el servidor -----------------------------------------------")

        apagarServidor(mosquitto, phpLiteAdmin, flask)
        sleep(1)

        if comando == 'r':

            mosquitto, phpLiteAdmin, flask = arrancarServidor()

            comando = ''

        elif comando == 'm':
            break

print("Servidor apagado -----------------------------------------------")
