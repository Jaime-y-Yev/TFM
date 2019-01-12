import sys
sys.path.insert(0, '/home/pi/TFM/Robot')
from comandosParaArduino import *

# GENERAL
modo = MODO_INACTIVO #MODO_INACTIVO, MODO_EMERGENCIA, MODO_SONDEO, MODO_NAVEGACION, MODO_MANUAL 

# MODO_SONDEO
permitirMovimientoJaula = False
permitirMovimientoActuador = False

expandirActuador = False
contraerActuador = False
problemaExpandir = False
problemaContraer = False

ultimoPulsoAA = 1200
ultimoPulsoID = 1200

coordObj= [0,0]

matarPotenciometro = False 

comandoCamara = 0

sondeoTerminado = 0 

idSesion = None

# ESTADOS PiB y ArduinoB
estadoPiB = "Arrancando..."
estadoArduinoB = "Arrancando..."
