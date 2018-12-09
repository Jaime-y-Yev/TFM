from comandosParaArduinoA import *

permitirSubCoordObj = True

modo = MODO_INACTIVO  # MODO_EMERGENCIA, MODO_SONDEO, MODO_FOTO, MODO_NAVEGACION

coordAct = [0,0]

# -------------------------------------------------------------DEPURACION DE NAVEGAR() y TRAYECTORIA()
#coordAct = [-3.68714675591591, 40.412042323101566]         # punto dentro
#coordAct = [-3.679261062066962, 40.41304368157035]          # punto dentro abajo der
#coordAct = [-3.6846041679382324, 40.413315296173096]        # punto dentro abajo izq     
#coordAct = [-3.680655809445034, 40.42041081522803]         # punto dentro
#coordAct = [-3.686617651240814, 40.416741534846125]        # punto dentro arriba izq
#coordAct = [-3.6896322691664865, 40.41846174279818]        # punto fuera
#coordAct = [-3.685636480970593, 40.43005615696222]         # punto fuera
#coordAct = [-3.67573842760479,40.42724150717895]           # punto fuera
#coordAct = [-3.6942145228385920,40.409135073423386]
coordActCandidato = [-3.6923941969462253, 40.40798485276355] #Atocha1
#coordActHallado = False  add if needed
antena = 1
marchaOparo = 0

coordObj = [0,0]

geometria =  {"coordObj": [0, 0], "geometria": "[0,0][1,1]"}

idSesion = 0

llegadaArduino = 0

estadoPiA = 0
estadoArduinoA = 0

marcaDistDir = 0
marcaLeerModoArduino = 0
marcaComBloc = 0

comandoManual = 0

permitirCambioModoManual = True
permitirComandoManual = True

# MODO_SONDEO
direccionObjUltima = 0
reintentoSondeo = 0



## -------------------------------------------------------------DEPURACION DE NAVEGAR() en PiA
## globalesPiA.modo = 2
## globalesPiA.marchaOparo = 1
## globalesPiA.permitirSubCoordObj == False
## trayectoria = [[0,0],[0,1],[1,1],[1,0]]
## globalesPiA.coordObj = [1,0]
## globalesPiA.coordAct = [0,0]
## print("!!!!!!!!!!!navegando")       
## navegar(trayectoria, globalesPiA.coordObj)
## -------------------------------------------------------------  
