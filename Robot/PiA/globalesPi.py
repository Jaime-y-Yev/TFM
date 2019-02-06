import sys
sys.path.insert(0, '/home/pi/TFM/Robot')
from comandosParaArduino import *

#GENERAL
modo = MODO_INACTIVO #MODO_INACTIVO, MODO_EMERGENCIA, MODO_SONDEO, MODO_NAVEGACION, MODO_MANUAL
resetearArduino = True
tiempoInicio = 0.0

#MODO_NAVEGACION
coordAct = [0,0]
coordActCandidato = [-3.6923941969462253, 40.40798485276355] #Atocha1
antena = 0

coordObj = [0,0]
geometria =  {"coordObj": [0, 0], "geometria": "[0,0][1,1]"}

permitirSubCoordObj = True
marchaParo = 0

llegadaArduino = 0

idSesion = 0

# MODO_MANUAL
comandoManual = 0
permitirCambioModoManual = True
permitirComandoManual = True

# MODO_SONDEO
direccionObjUltima = 0
reintentoSondeo = 0
sondeoTerminado = 0
robotDesplazando = False

#ESTADOS PiA y ArduinoA 
estadoPiA = "Arrancando..."
estadoArduinoA = "Arrancando..."


## -------------------------------------------------------------DEPURACION DE NAVEGAR() en PiA
## globalesPiA.modo = 2
## globalesPiA.marchaParo = 1
## globalesPiA.permitirSubCoordObj == False
## trayectoria = [[0,0],[0,1],[1,1],[1,0]]
## globalesPiA.coordObj = [1,0]
## globalesPiA.coordAct = [0,0]
## print("!!!!!!!!!!!navegando")       
## navegar(trayectoria, globalesPiA.coordObj)
## -------------------------------------------------------------  

