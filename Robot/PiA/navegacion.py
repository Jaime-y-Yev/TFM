import math
import time


import globalesPiA


from comandosParaArduinoA import *

# Decide cual de los puntos intermedios de la trayectoria es el coordObj corriente hasta llegar al último punto 
def siguientePunto(puntosIntermedios):
    
    # Cada llamada aumentar el contador global que decide que es el punto objetivo corriente de la lista de puntos en trayectoria
    global iDeTrayectoria
    iDeTrayectoria += 1 # el contador empieza en iDeTrayectoria = 1 (incluye el coordAct donde empieza el robot)   
    print("Hay "+str(len(puntosIntermedios)) + "puntosIntermedios en la trayectoria") 

    # Si al aumentar el contador, el valor de contador es más que la cantidad de puntos en la trayectoria => ya hemos llegado
    if len(puntosIntermedios) < (iDeTrayectoria-1): 
        print("Llegado a coorObj final, el punto "+str(iDeTrayectoria) + " de trayectoria" )
        return 1, 'fin'
    
    # Si todavía se puede ir al próximo punto
    else: 
        print("Seteando un nuevo punto via: " + str(puntosIntermedios[iDeTrayectoria-1])) 
        puntoIntermedioActual = puntosIntermedios[iDeTrayectoria-1] # se asigna el próximo punto objetivo  
        return 0, puntoIntermedioActual # nuevo pùnto intermedio

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
    return direccionObj

# Se calcula la distancia entre coordAct y coordObj teniendo en cuenta que el planeta es redonda
def distancia(coordAct, coordObj):
    
    # Se descompone las coordenadas para obtener valores individuales
    latObj =float(coordObj[0])
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
    
    # distanciaObj = d km for MINISIMULACION
    distanciaObj = d *1000  #in meters


    return distanciaObj

# Se inicializa la tolerancia de distancia
distanciaTol = 2 # was 0.01

def navegar(trayectoria, coordObj):
		
	# Actualizar el variable global de estados
	globalesPiA.estadoPiA = "Navegar() ejecutando..."

	global iDeTrayectoria
	iDeTrayectoria = 1
	global llegada
	llegada = 0    

	# Cambiar modo de Arduino a MODO_NAVEGACION
	modoDeArduino = comandoArduino(CAMBIAR_MODO, MODO_NAVEGACION)  # envia comando para cambiar modo de Arduino y recibe confirmacion del Arduino

	# Se informa el usuario sobre los estados de PiA y Arduino
	globalesPiA.estadoArduinoA = "En navegación, modo de Arduino: " + str(modoDeArduino) 
	globalesPiA.estadoPiA = "En navegación, modo de PiA: " + str(globalesPiA.modo)

	coordObj = globalesPiA.coordAct  # guardar el valor corriente de coordAct en una copia de coordObj local empieza el proceso de navegación maś tarde

	# SIMULACIÓN-------------------------------------------------

	simulación = 0    
	if simulación == 1:          # Simulación de navegar() sólo
		lasttime = time.clock() 
		j = 0                    

	if simulación == 2:
		j = 0                    # Simulación ArduinoA y navegar()
		
	# -------------------------------------------------------------------
	while True:
		# Copia local del algunos variables para calcular direccion y distancia para evitar que cualquier cambio afecte cálculo actual    
		
		modo = globalesPiA.modo
		marchaOparo = globalesPiA.marchaOparo
		
		# En caso de emrgencia, cambiar el modo del ArduinoA a MODO_EMERGENCIA
		if modo == MODO_EMERGENCIA:
			globalesPiA.estadoPiA = "Durante navegación, modo cambiado a emergencia" # informar el usuario sobre la emergencia
			comandoArduino(CAMBIAR_MODO, MODO_EMERGENCIA)
			break
		
		# Si el modo de PiA cambia, desactivamos el ArduinoA y se sale de navegar()
		if modo != MODO_NAVEGACION or marchaOparo == 0:
			globalesPiA.estadoPiA = "Durante navegación, modo cambiado..."
			comandoArduino(CAMBIAR_MODO, MODO_INACTIVO)
			break        
		
		# Se continúa la navegación sólo si no hay cambio desde MODO_NAVEGACION y si marchaOparo todavía es igual a 1
		if modo == MODO_NAVEGACION and marchaOparo == 1 and globalesPiA.coordAct != 'obteniendo una solucion...':
			
			
			coordAct = globalesPiA.coordAct 

			print("..                                                                                                                                        en navegar()..")
			
			# Simulación ---------------------------------------------------- 
			
			if simulación == 1:
				llegadaArduino = 1
				if time.clock()-lasttime > 5 and j< len(trayectoria): 
					coordAct = trayectoria[j]                           
					globalesPiA.coordAct = trayectoria[j] 
					j += 1 
					lasttime = time.clock()
			if simulación == 2:
				llegadaArduino = comandoArduino(CONFIRMAR_DATOS)
				
			# -----------------------------------------------------------------
			
			# Se confirma que el Arduino está listo para navegar o si el Arduino ha desplazado la distancia correcta para recibir un nuevo objetivo
			if simulación == 0:
				llegadaArduino, casoNavegacion, direccionAct = comandoArduino(CONFIRMAR_DATOS)
				print("«----------llegada Arduino: ", llegadaArduino)
				print("«----------casoNavegacion Arduino: ", casoNavegacion)
				print("«----------direccionAct Arduino: ", direccionAct)
			globalesPiA.estadoArduinoA = "llegadaArduino = " + str(llegadaArduino) # informar el usuario sobre el estado de ArduinoA
			globalesPiA.estadoArduinoA = "ArduinoA listo para recibir comandos"
			
			# Sólo ejecutar los próximos pasos si el Arduino está listo para recibir los comandos
			if llegadaArduino == 1:                                                     
				# Simulación ArduinoA y navegar()---------------------------------- 
				
				if simulación == 2:
					coordAct = trayectoria[j] 
					globalesPiA.coordAct = trayectoria[j]
				
				# -----------------------------------------------------------------
				
				# Primero: aseguramos que ya no estamos en nuestro coordObj final
				últimoPuntoTrayectoria =  trayectoria[len(trayectoria)-1]
				distanciaObj = distancia(coordAct, últimoPuntoTrayectoria) # antes de iniciar el cálculo, asegurarse de no haber llegado ya al objetivo (ej. si ha ocurrido un reset durante la navegación)          
				print("distanciaObj a ULTIMO PUNTO: "+ str(distanciaObj))     

				if distanciaObj <= distanciaTol:  # comprobar si el robot ha llegado al ÚLTIMO punto de trayectoria              
					print("coordAct antes de llegar: "+ str(coordAct))     
					print("coordObj antes de llegar: "+ str(coordObj))     
					globalesPiA.estadoPiA = "Navegación finalizada"        # informar el usuario sobre la llegada finalizada
					globalesPiA.estadoArduinoPiA = "Navegación finalizada"

					# Cambiar el modo de Arduino a inactivo después de la llegada exitosa
					respuesta = comandoArduino(CAMBIAR_MODO, MODO_INACTIVO)
					break
				
				# Segundo: si no estámos en nuestro coordObj final empezamos la navegación a ith punto de la trayectoria
				elif distanciaObj > distanciaTol:
											
					# Se recalcula la distancia entre coordAct y coordObj pero este vez coordObj no es el punto final de la trayectoria, sino la siguinete punto
					distanciaObj = distancia(coordAct, coordObj)         # la primera vez, coordAct=coordObj => SIEMPRE cumple este condición. Sirve para iniciar el bucle
					
					# Asigna el proximo punto de la trayectoria a nuestro coordObj se hemos llegado al punto previo
					if distanciaObj <= distanciaTol: 
						llegada, coordObj = siguientePunto(trayectoria)  # al llegar al último punto de trayectoria, llegada=1. En otros casos, llegada=0
					
					print("llegada PiA: ", llegada)
					
					# Si pasa cuando la distancia entre final punto objetivo y actual todavía es > distancia Tol -> avería
					if llegada == 1:
						globalesPiA.estadoPiA = "Error en navegación, cambiando a MODO_EMERGENCIA..."
						globalesPiA.modo = MODO_EMERGENCIA
						break
					
					# Casi siempre estamos en este caso. No cogemos siguiente punto de trayectoria. Recalculamos distancia y dirección
					elif llegada == 0:     
						
						# Se llama las funciones que calculan dirección y distancia entre le punto corriente y el próximo punto via de la trayectoria
						#print("BEFORE DIRECCION COORDACT: ",coordAct)
						#print("BEFORE DIRECCION COORDOBJ: ", coordObj)
						direccionObj = direccion(coordAct, coordObj)
						globalesPiA.direccionObjUltima = direccionObj
						distanciaObj = distancia(coordAct, coordObj)
				
						print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
						print( "----------»Mandamos al ArduinoA direccionObj: "+ str(direccionObj)) # informar el usuario sobre la manda de dirección y distancia
						print( "----------»Mandamos al ArduinoA distanciaObj: "+ str(distanciaObj)) # informar el usuario sobre la manda de dirección y distancia
						print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
						

						globalesPiA.estadoPiA = "Mandamos al ArduinoA direccionObj: "+ str(direccionObj) # informar el usuario sobre la manda de dirección y distancia
						globalesPiA.estadoPiA = "Mandamos al ArduinoA distanciaObj: "+ str(distanciaObj)

						# Se manda la direccionObj y distanciaObj al ArduinoA               
						direccionObj, distanciaObj = comandoArduino(RECIBIR_DIRECCION_DISTANCIA_OBJ, int(direccionObj), distanciaObj)
						
						# Simulación ArduinoA y navegar()------------------------------
						
						if simulación == 2:
							j += 1 
						
						# -------------------------------------------------------------
			
			# El robot está desplazando hacia la coordenada asignada           
			elif llegadaArduino == 0:
				globalesPiA.estadoArduinoA = "ArduinoA navegando..." # informar el usuario sobre el estado de ArduinoA

				time.sleep(5) # no molestar el ArduinoA cuando está desplazando hacía el punto via asignado
					

#----------------------------------------------------------------------------------------------------------------
def moverReintentoSondeo():
	while True:
		llegadaArduino = comandoArduino(CONFIRMAR_DATOS)
		print("«----------llegada Arduino: ", type(llegadaArduino))
		if llegadaArduino == 1:
			direccionObj = globalesPiA.direccionObjUltima
			distanciaObj = 0.1
			direccionObj, distanciaObj = comandoArduino(RECIBIR_DIRECCION_DISTANCIA_OBJ, int(direccionObj), distanciaObj)	
			globalesPiA.reintentoSondeo = 0
			break

def navegarSimu():
        
    # Actualizar el variable global de estados
    globalesPiA.estadoPiA = "Navegar() ejecutando..."
    
    #global iDeTrayectoria
    #iDeTrayectoria = 1
    global llegada
    llegada = 0    
    
    # Cambiar modo de Arduino a MODO_NAVEGACION
    modoDeArduino = comandoArduino(CAMBIAR_MODO, MODO_NAVEGACION)  # envia comando para cambiar modo de Arduino y recibe confirmacion del Arduino
    
    # Se informa el usuario sobre los estados de PiA y Arduino
    globalesPiA.estadoArduinoA = "En navegación, modo de Arduino: " + str(modoDeArduino) 
    globalesPiA.estadoPiA = "En navegación, modo de PiA: " + str(globalesPiA.modo)

    #coordObj = globalesPiA.coordAct  # guardar el valor corriente de coordAct en una copia de coordObj local empieza el proceso de navegación maś tarde
    
    # SIMULACIÓN-------------------------------------------------
    
    simulación = 0    
    if simulación == 1:          # Simulación de navegar() sólo
        lasttime = time.clock() 
        j = 0                    
 
    if simulación == 2:
        j = 0                    # Simulación ArduinoA y navegar()
        
    # -------------------------------------------------------------------
    while True:
        # Copia local del algunos variables para calcular direccion y distancia para evitar que cualquier cambio afecte cálculo actual    
        #coordAct = globalesPiA.coordAct 
        modo = MODO_NAVEGACION
        marchaOparo = 1
        
        # En caso de emrgencia, cambiar el modo del ArduinoA a MODO_EMERGENCIA
        if modo == MODO_EMERGENCIA:
            globalesPiA.estadoPiA = "Durante navegación, modo cambiado a emergencia" # informar el usuario sobre la emergencia
            comandoArduino(CAMBIAR_MODO, MODO_EMERGENCIA)
            break
        
        # Si el modo de PiA cambia, desactivamos el ArduinoA y se sale de navegar()
        if modo != MODO_NAVEGACION or marchaOparo == 0:
            globalesPiA.estadoPiA = "Durante navegación, modo cambiado..."
            comandoArduino(CAMBIAR_MODO, MODO_INACTIVO)
            break        
        
        # Se continúa la navegación sólo si no hay cambio desde MODO_NAVEGACION y si marchaOparo todavía es igual a 1
        if modo == MODO_NAVEGACION and marchaOparo == 1:                                 
            
            # Simulación ---------------------------------------------------- 
            
            if simulación == 1:
                llegadaArduino = 1
                if time.clock()-lasttime > 5 and j< len(trayectoria): 
                    coordAct = trayectoria[j]                           
                    globalesPiA.coordAct = trayectoria[j] 
                    j += 1 
                    lasttime = time.clock()
            if simulación == 2:
                llegadaArduino = comandoArduino(CONFIRMAR_DATOS)
                
            # -----------------------------------------------------------------
            
            # Se confirma que el Arduino está listo para navegar o si el Arduino ha desplazado la distancia correcta para recibir un nuevo objetivo
            if simulación == 0:
                llegadaArduino = comandoArduino(CONFIRMAR_DATOS)
                print("llegada Arduino: ", type(llegadaArduino))

            globalesPiA.estadoArduinoA = "llegadaArduino = " + str(llegadaArduino) # informar el usuario sobre el estado de ArduinoA
            globalesPiA.estadoArduinoA = "ArduinoA listo para recibir comandos"
            
            # Sólo ejecutar los próximos pasos si el Arduino está listo para recibir los comandos
            if llegadaArduino == 1:                                                     
                
                # Simulación ArduinoA y navegar()---------------------------------- 
                
                if simulación == 2:
                    coordAct = trayectoria[j] 
                    globalesPiA.coordAct = trayectoria[j]
                
                # -----------------------------------------------------------------
                
                # Primero: aseguramos que ya no estamos en nuestro coordObj final
                #últimoPuntoTrayectoria =  trayectoria[len(trayectoria)-1]
                #distanciaObj = distancia(coordAct, últimoPuntoTrayectoria) # antes de iniciar el cálculo, asegurarse de no haber llegado ya al objetivo (ej. si ha ocurrido un reset durante la navegación)          
                
                
                #if distanciaObj <= distanciaTol:  # comprobar si el robot ha llegado al ÚLTIMO punto de trayectoria              
                    #print("coordAct antes de llegar: "+ str(coordAct))     
                    #print("coordObj antes de llegar: "+ str(coordObj))     
                    #globalesPiA.estadoPiA = "Navegación finalizada"        # informar el usuario sobre la llegada finalizada
                    #globalesPiA.estadoArduinoPiA = "Navegación finalizada"

                    # Cambiar el modo de Arduino a inactivo después de la llegada exitosa
                    #respuesta = comandoArduino(CAMBIAR_MODO, MODO_INACTIVO)
                    #break
                
                # Segundo: si no estámos en nuestro coordObj final empezamos la navegación a ith punto de la trayectoria
                #elif distanciaObj > distanciaTol:
                                            
                    
                    # Casi siempre estamos en este caso. No cogemos siguiente punto de trayectoria. Recalculamos distancia y dirección
                #elif llegada == 0:
                    
##                if simulación == 3:
##                    comandoArduino(CAMBIAR_MODO, MODO_INACTIVO)
##                    #break
##                    direccionObj = 0
##                    distanciaObj = 0
                if simulación == 0:
                    direccionObj = 0
                    distanciaObj = 2
                    simulación = 3
                   
                    
                    globalesPiA.estadoPiA = "Mandamos al ArduinoA direccionObj: "+ str(direccionObj) # informar el usuario sobre la manda de dirección y distancia
                    globalesPiA.estadoPiA = "Mandamos al ArduinoA distanciaObj: "+ str(distanciaObj)

                    # Se manda la direccionObj y distanciaObj al ArduinoA               
                    direccionObj, distanciaObj = comandoArduino(RECIBIR_DIRECCION_DISTANCIA_OBJ, int(direccionObj), distanciaObj)
                    
                    # Simulación ArduinoA y navegar()------------------------------
                    
                    if simulación == 2:
                        j += 1 
                    
                        # -------------------------------------------------------------
            
            # El robot está desplazando hacia la coordenada asignada           
            elif llegadaArduino == 0:
                globalesPiA.estadoArduinoA = "ArduinoA navegando..." # informar el usuario sobre el estado de ArduinoA

                time.sleep(5) # no molestar el ArduinoA cuando está desplazando hacía el punto via asignado
                    
#navegar()
