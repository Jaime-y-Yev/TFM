# Librería de hilos y códigos de cada hilo
import threading
hiloFlaskID = 1             
hiloPhpLiteAdminID = 2      


matarHilos = 'o'            # señal que mata a los hilos
from time import sleep      # para ralentizar el checkeo de la variable matarHilos

def matarHilo(proceso):
    """Espera a la señal para matar el proceso"""

    while True:

        sleep(0.5)

        if matarHilos == 'm':
            subprocess.Popen("taskkill /F /T /PID %i"%proceso.pid)
            break


# Librerías para la ejecución de programas de Windows mediante Python
import os
import subprocess





class Hilo(threading.Thread):
    
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):

        print("Comenzando hilo ", end='')           

        # Hilo de Flask que arranca la aplicación y espera a la señal que lo mata
        if self.threadID == hiloFlaskID: 
            print("Flask")

            os.environ["FLASK_DEBUG"] = "False" # No arrancar en modo de depuración
            # Arrancar el proceso Flask mediante PowerShell
            flaskProceso = subprocess.Popen('powershell.exe flask run --host=0.0.0.0 --port=8080 --no-reload') # make debug false
            #flaskProceso = subprocess.Popen(['powershell.exe','python','app.py'], cwd='c:/users/y/documents/trabajofinmaster/tfm/servidor')

            matarHilo(flaskProceso)             # esperar a la señal para matar al proceso de Flask
            
            print("Terminando hilo Flask")


        # Hilo del administrador de SQLite llamado phpLiteAdmin (no es imprescindible para el funcionamiento del servidor, pero ayuda a visualizar la base de datos) 
        elif self.threadID == hiloPhpLiteAdminID:
            print("phpLiteAdmin")  

            # Arrancar el proceso de phpLiteAdmin mediante PowerShell
            phpLiteAdminProceso = subprocess.Popen(['powershell.exe','c:/MAMP/bin/php/php7.2.1/php.exe', '-S 0.0.0.0:90'], cwd='c:/MAMP/bin/phpliteAdmin')
            
            matarHilo(phpLiteAdminProceso)      # esperar a la señal para matar al proceso de phpLiteAdmin

            print("Terminando hilo phpLiteAdmin")

          

# Hilo princiapl que arranca los demás hilos
print("Comenzando hilo Principal")           

# Crear cada hilo
hiloFlask = Hilo(hiloFlaskID)
hiloPhpLiteAdmin = Hilo(hiloPhpLiteAdminID)

# Iniciar cada hilo
hiloFlask.start() 
hiloPhpLiteAdmin.start()


# Esperar a la señal introducida por el usuario mediante el teclado para matar a los hilos
while True:

    sleep(0.5)

    matarHilos = input()        # recibir una señal del teclado

    # Si se ha recibido la señal de terminación, propagarla al resto de hilos y matar el hilo principal
    if matarHilos == 'm':
        break

print("Terminando hilo Principal")
