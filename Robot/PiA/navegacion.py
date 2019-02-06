import math
from time import sleep,clock

import sys
sys.path.insert(0, '/home/pi/TFM/Robot/PiA')
import globalesPi

sys.path.insert(0, '/home/pi/TFM/Robot')
from actualizarCodigosDeComandos import *
from comandosParaArduino import *


# Decide cuál de los puntos intermedios de la trayectoria es el coordObj corriente hasta llegar al último punto 
def siguientePunto(puntosIntermedios):
    
    # Cada llamada aumentar el contador global que decide que es el punto objetivo actual de la lista de puntos en trayectoria
    global iDeTrayectoria
    iDeTrayectoria += 1 # el contador empieza en iDeTrayectoria = 1 (incluye el coordAct donde empieza el robot)
    print("---------------------------------------------------------------------------------------------------------------------------------")   
    print("Hay "+str(len(puntosIntermedios)) + "puntosIntermedios en la trayectoria") 
    print("---------------------------------------------------------------------------------------------------------------------------------")


    # Si al aumentar el contador, el valor de contador es más que la cantidad de puntos en la trayectoria => ya hemos llegado
    if len(puntosIntermedios) < (iDeTrayectoria-1): 
        print("Llegado a coorObj final, el punto "+str(iDeTrayectoria) + " de trayectoria" )
        return 1, 'fin'
    
    # Si todavía se puede ir al próximo punto
    else: 
        print("Seteando un nuevo punto via: " + str(puntosIntermedios[iDeTrayectoria-1])) 
        puntoIntermedioActual = puntosIntermedios[iDeTrayectoria-1] 	# se asigna el próximo punto objetivo  
        return 0, puntoIntermedioActual 								# nuevo pùnto intermedio

# Se calcula la dirección entre coordAct y coordObj utilizando ecuación conocida
def direccion(coordAct, coordObj): 
    
    # Se descompone las coordenadas para obtener valores individuales
    lonObj = coordObj[0]
    latObj = coordObj[1]
    lonAct = coordAct[0]
    latAct = coordAct[1]
    
    # Se convierte los valores a radianes
    latAct = math.radians(latAct)
    latObj = math.radians(latObj)
    lonAct = math.radians(lonAct)
    lonObj = math.radians(lonObj)

    # Se sigue la ecuación de conversión
    difLong = lonObj - lonAct

    m = math.sin(difLong)*math.cos(latObj)    
    g0 = math.sin(latAct)*math.cos(latObj)*math.cos(difLong)
    g = math.cos(latAct)*math.sin(latObj)-g0
    h = math.atan2(m,g)
    
    # Se convierte el valor en grados para poder utilizarlo en ArduinoA
    h = math.degrees(h) 
    direccionObj = (h + 360) % 360 # para obtener el valor entre 0 y 360 grados
    return int(direccionObj)

# Se calcula la distancia entre coordAct y coordObj teniendo en cuenta que el planeta es redonda
def distancia(coordAct, coordObj):
    
	# Se descompone las coordenadas para obtener valores individuales
	try:
		latObj =float(coordObj[0])
	except:
		return 0.0

	lonObj =float(coordObj[1])
	latAct =float(coordAct[0])
	lonAct =float(coordAct[1])

	radio = 6371 # km

	# Se halla la diferencia entre valores lat y lon en radianes
	dlat = math.radians(latObj-latAct)
	dlon = math.radians(lonObj-lonAct)

	# Se utiliza una ecuación para have la conversión a distancia
	a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(latAct)) \
		* math.cos(math.radians(latObj)) * math.sin(dlon/2) * math.sin(dlon/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = radio * c # tenemos en cuenta el radio del planeta

	# distanciaObj = d km para simulación sin GPS
	distanciaObj = d *1000  #en metros
	distanciaObj = round(distanciaObj,2)
	return distanciaObj
    
# Se calcula el promedio de la lista de coordAct recibidos del móvil
def promedio(coordActCandidatos):
	
	# Se inicializa las listas de latitudes y longitudes
	lats = []
	lons = []
	
	# Separa los latitudes y longitudes de los coordAct del móvil
	for coordActCandidato in coordActCandidatos:
		lats.append(coordActCandidato[0])
		lons.append(coordActCandidato[1])    
	
	# Se calcula el promedio de latitudes y longitudes 
	coordActLat = sum(lats)/len(coordActCandidatos)
	coordActLon = sum(lons)/len(coordActCandidatos)
	
	# Devuelve un coordAct que es el promedio de las coordenadas de la lista inicial
	coordAct = [coordActLat,coordActLon]
	return coordAct

# Se inicializa la tolerancia de distancia (ej. llegar a 0.8m del objetivo signifíca llegar exitosamente)
distanciaTol = 1.5 # 

# La función principal de navegción autonoma que manda comandos de distancia y dirección al ArduinoA
def navegar(trayectoria, coordObj):
	
	print("Navegar empezando----------------------------------------------------------------------------------------------------------------------")	
	
	# Actualizar el variable global de estados
	globalesPi.estadoPiA = "Navegando..."

	# Inicializar la posición inicial en la lista de coordenadas en la trayectoria calculada
	global iDeTrayectoria
	iDeTrayectoria = 1
	
	# Inicializa la variable de llegada a 0 
	global llegada
	llegada = 0    
	
	vigilarModoArduino()

	coordObj = globalesPi.coordAct  # guardar el valor actual de coordAct en una copia de coordObj local para empezar el proceso de navegación maś tarde

	# SIMULACIÓN---------------------------------------------------------
	simulación = 2   
	if simulación == 1:          # Simulación de navegar() sólo
		lasttime = clock() 
		j = 0                    
	elif simulación == 2:
		j = 0                    # Simulación ArduinoA y navegar()
	# -------------------------------------------------------------------
	while True:
		
		# Copia local del algunos variables para calcular direccion y distancia para evitar que cualquier cambio afecte cálculo actual    
		modo = globalesPi.modo
		marchaParo = globalesPi.marchaParo
		
		# En el caso de emrgencia, cambiar el modo del ArduinoA a MODO_EMERGENCIA
		if modo == MODO_EMERGENCIA:
			globalesPi.estadoPiA = "Durante navegación, modo cambiado a emergencia" # informar el usuario sobre la emergencia
			comandoArduino(CAMBIAR_MODO, MODO_EMERGENCIA)
			break
		
		# Si el modo de PiA cambia, desactivamos el ArduinoA y se sale de navegar()
		if modo != MODO_NAVEGACION or marchaParo == False:
			globalesPi.estadoPiA = "Durante navegación, modo cambiado..."
			comandoArduino(CAMBIAR_MODO, MODO_INACTIVO)
			break        
		
		# Se continúa la navegación sólo si no hay cambio desde MODO_NAVEGACION y si marchaParo todavía es igual a 1
		if modo == MODO_NAVEGACION and marchaParo == True and globalesPi.coordAct != 'obteniendo una solucion...':
			
			while globalesPi.coordAct == 'obteniendo una solucion...':
				print("En navegación, esperando una solución")
				
			coordAct = globalesPi.coordAct 

			print("..............................................................................................................................................en navegar()..")
			
			# Simulación ---------------------------------------------------- 
			if simulación == 1:
				if clock()-lasttime > 5 and j< len(trayectoria): 
					coordAct = trayectoria[j]                           
					globalesPi.coordAct = trayectoria[j] 
					j += 1 
					lasttime = clock()
			elif simulación == 2:
				casoNavegacion, direccionAct = comandoArduino(CONFIRMAR_DATOS)
				coordAct = trayectoria[j] 
				globalesPi.coordAct = trayectoria[j]
			# --------------------------------------------------------------- 				
			
			# Para calibrar magnetómetro y depurar casos de navegación del Arduino
			if simulación == 0:				
				casoNavegacion, direccionAct = comandoArduino(CONFIRMAR_DATOS)
				
				print("---------------------------------------------------------------------------------------------------------")
				print("!!!!!«----------casoNavegacion Arduino: ", casoNavegacion)
				print("«!!!!!----------direccionAct Arduino: ", direccionAct)
				print("---------------------------------------------------------------------------------------------------------")
			
			
			# Primero: aseguramos que ya no estamos en nuestro coordObj final
			últimoPuntoTrayectoria =  trayectoria[len(trayectoria)-1]
			distanciaObj = distancia(coordAct, últimoPuntoTrayectoria)  # antes de iniciar el cálculo, asegurarse de no haber llegado ya al objetivo (ej. si ha ocurrido un reset durante la navegación)          
			print("distanciaObj a ULTIMO PUNTO: "+ str(distanciaObj))     

			if distanciaObj <= distanciaTol:  							# comprobar si el robot ha llegado al ÚLTIMO punto de trayectoria                  
				globalesPi.estadoPiA = "Navegación finalizada"          # informar el usuario sobre la llegada finalizada
				globalesPi.estadoArduinoA = "Navegación finalizada"
				print("---------------------------------------------------------------------------------------------------------")
				print("-----------------------------------------Navegación finalizada-------------------------------------------")
				print("---------------------------------------------------------------------------------------------------------")

				# Cambiar el modo de Arduino a inactivo después de la llegada exitosa
				comandoArduino(CAMBIAR_MODO, MODO_INACTIVO)
				break
			
			# Segundo: si no estámos en nuestro coordObj final empezamos la navegación a ith punto de la trayectoria
			elif distanciaObj > distanciaTol:
										
				# Se recalcula la distancia entre coordAct y coordObj pero este vez coordObj no es el punto final de la trayectoria, sino la siguinete punto
				distanciaObj = distancia(coordAct, coordObj)         # la primera vez, coordAct=coordObj => SIEMPRE cumple este condición. Sirve para iniciar el bucle
				
				# Asigna el proximo punto de la trayectoria a nuestro coordObj se hemos llegado al punto previo
				if distanciaObj <= distanciaTol: 
					llegada, coordObj = siguientePunto(trayectoria)  # al llegar al último punto de trayectoria, llegada=1. En otros casos, llegada=0
									
				# Si pasa cuando la distancia entre final punto objetivo y actual todavía es > distancia Tol -> avería
				if llegada == 1:
					globalesPi.estadoPiA = "Error en navegación, cambiando a MODO_EMERGENCIA..."
					globalesPi.modo = MODO_EMERGENCIA
					break
				
				# Casi siempre estamos en este caso. No cogemos siguiente punto de trayectoria. Recalculamos distancia y dirección
				elif llegada == 0:     
											
					# Se llama las funciones que calculan dirección y distancia entre le punto corriente y el próximo punto via de la trayectoria
					direccionObj = direccion(coordAct, coordObj)
					globalesPi.direccionObjUltima = direccionObj
					distanciaObj = distancia(coordAct, coordObj)
					
					globalesPi.estadoArduinoA = "ArduinoA navegando..." # informar el usuario sobre el estado de ArduinoA
						
					# Se manda la direccionObj y distanciaObj al ArduinoA               
					direcciónObj = comandoArduino(RECIBIR_DIRECCION_OBJ, direccionObj)
					distanciaObj = comandoArduino(RECIBIR_DISTANCIA_OBJ, distanciaObj)
					
					print("---------------------------------------------------------------------------------------------------------------------------------")
					print("----------»Mandamos al ArduinoA direccionObj: "+ str(direccionObj)) # informar el usuario sobre la manda de dirección y distancia
					print("----------»Mandamos al ArduinoA distanciaObj: "+ str(distanciaObj)) # informar el usuario sobre la manda de dirección y distancia
					print("---------------------------------------------------------------------------------------------------------------------------------")

					
					# Simulación ArduinoA y navegar()------------------------------
					if simulación == 2:
						j += 1 
					# -------------------------------------------------------------
			sleep(3)
		

# Si hay un problema con el sondeo, mover el robot unos centímetros para sondear otra vez 
def moverReintentoSondeo():
	
		print("Moviendo unos centimetros...")
		sleep(1)
		
		# Asegurar que el sondeo no puede ocurrir cuando el robot está moviendo
		globalesPi.robotDesplazando = True
		
		# Asegurar que ArduinoA es en mismo modo que PiA
		vigilarModoArduino()
		
		# Obtener estatus del ArduinoA, su propio caso de navegación, y su dirección actual
		casoNavegacion, direccionAct = comandoArduino(CONFIRMAR_DATOS)
		
		# Si el ArduinoA está listo para recibir instrucciones de navegación
		direcciónObj = comandoArduino(RECIBIR_DIRECCION_OBJ, globalesPi.direccionObjUltima)
		distanciaObj = comandoArduino(RECIBIR_DISTANCIA_OBJ, 0.1)
		globalesPi.robotDesplazando = False


