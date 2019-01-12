import math

# Hallar pendiente de una linea
def pendiente(linea): # linea = [[x1,y1],[x2,y2]]
    
    # Extraer los puntos individuales de "linea"
    x1 = linea[0][0]
    y1 = linea[0][1]
    x2 = linea[1][0]
    y2 = linea[1][1]
    
    # Utilizar los puntos extraidos en el paso previo para calcular el pendiente
    pendiente = (y2 - y1)/(x2 - x1)
    
    return pendiente

# Hallar la intersección con el eje y
def yint(punto, pendiente):
	
	# Extraer las coordenadas individuales del "punto"
	x = punto[0]
	y = punto[1]

	# Utilizar los puntos extraidos en el paso previo para calcular la intersección
	yinter = y - pendiente*x # y1 = mx1 + b => b = y1-mx1 

	return yinter

# Averiguar si c esta enre a y b donde a y b son los puntos de contorno y c es una intersección 
def entrePuntos(a,b,c):
    
    tol = 0.25 # tolerancia
    
    # Extraer las coordenadas individuales de "a", "b" y "c" 
    ax = a[0]
    ay = a[1]
    bx = b[0]
    by = b[1]
    cx = c[0]
    cy = c[1]
    
    # Hallar producto vectorial entre los puntos
    productoVect = (cy - ay) * (bx - ax) - (cx - ax) * (by - ay)

    # Si el producto vecotorial es más que una tolerancia, predefinida, punto c no está entre puntos a y b
    if abs(productoVect) > tol:
        return False
    
    # Si el producto escalar es menos que 0, punto c no está entre puntos a y b
    productoEsc = (cx - ax) * (bx - ax) + (cy - ay)*(by - ay)
    if productoEsc < 0:
        return False
    
    # Si la distancia cuadrada es menos que el producto escalar, punto c no está entre puntos a y b
    distanciaCuad = (bx - ax)*(bx - ax) + (by - ay)*(by - ay)
    if productoEsc > distanciaCuad:
        return False
    
    # Si ningunos de los casos anteriores pasan, punto c está entre puntos a y b
    return True

# Hallar ecuaciones de todas lineas de polígono (contorno) 
def crearPoliEc(geometría):
    
    # Extraer los puntos de polígono de la geometría recibida
    poligono = geometría['poli'] 
    
    # Crear lista de las lineas de polígono con sus pendientes y intersecciones con eje y
    poliEc = [] 
    
    # Extraer segmentos separados del polígono
    for i in range(len(poligono)): 
        if i == (len(poligono)-1):
            segmentoPoli = poligono[i],poligono[0]            # extraer el último segmento sin dar errores
        else:
            segmentoPoli= poligono[i],poligono[i+1]           # extraer todos salvo el último
   
       
        segmentoPoliPendiente = pendiente(segmentoPoli)       # hallar pendiente de ith linea de poligono
        
        punto = segmentoPoli[1]
        segmentoPoliYint = yint(punto,segmentoPoliPendiente)  # hallar y int de ith linea de poligono
        
        # Añadir la pendiente, intersección con eje y, las coordenadas de la línea a una lista
        poliEc = poliEc + [(segmentoPoliPendiente,segmentoPoliYint,segmentoPoli[0],segmentoPoli[1])] 
        print("Lista de pendiente,Yint,puntos de segmento de cada parte del polígono: ",poliEc)
        
    return poliEc

# Hallar intersecciones entre lineas que pasan por el punto objetivo y/o punto actual
def interseccionesValidas(lineaEc,poliEc):
    
	pendiente1 = lineaEc[0]                                    # pendiente de nuestra linea que pasa por el objetivo
	yint1 = lineaEc[1]                                         # yint de nuestra linea que pasa por el objetivo

	interseccionesValid = []                                   # crear una lista de intersecciones vacia

	# Pasar por cada linea del contorno hallando intersecciones y verificando si son válidas
	for i in range (len(poliEc)):
		
		pendiente2 = poliEc[i][0]                              # pendiente de ith ecuacion en el polígono
		yint2 = poliEc[i][1]                                   # yint de ith ecuacion en el polígono
		
		x = (yint1 - yint2) / (pendiente2 - pendiente1)        # calcular la intersección (x,y)
		y = pendiente2 * x + yint2
		

		# Decidir si es una interseccion válida. Los limites son las coordenadas (extremos) del contorno
		limitex1 = poliEc[i][2][0]
		limitex2 = poliEc[i][3][0]
		limitey1 = poliEc[i][2][1]
		limitey2 = poliEc[i][3][1]
		
		if (limitex1 <= x <=  limitex2 or limitex2 <= x <=  limitex1) and (limitey1 <= y <=  limitey2 or limitey2 <= y <=  limitey1):
			interseccionesValid = interseccionesValid + [[x,y]]  # añadir a la lista sólo intersecciones válidas
		print("Intersecciones válidas entre línea que pasa por coordObj y el polígono: ", interseccionesValidas)
	return interseccionesValid


# Poner puntos de los extremos del polígono y las intersecciones en orden. Extremos del polígono + intersecciones válidas = puntos via
def crearPuntosIntermedios(geometría,poliEc,coordAct,coordObj):
    
    # Decidir si una interseccion es entre dos extremos de una linea del contorno, y ponerlo en orden con otras
    def hallarPuntosIntermedios(intersecciones, contorno, tipo):
        
        # Inicializar las variables necesarias para pasar por las líneas del contorno y crear una nueva lista llena de puntos Intermedios en orden
        counter = 0
        i = 0
        puntosIntermedios = []
        puntosIntermedios = contorno.copy()

        for j in range(len(contorno)):
            
            # Elegir dos puntos siguientes del contorno
            a = contorno[j]
            
            if j == (len(contorno)-1):
                b = contorno[0] 
            else: 
                b = contorno[j+1]
           
            c = intersecciones[i]
            
            # Ejecutar la función que decide si punto c es entre a y b
            entre = entrePuntos(a,b,c) 
            
            # Añádir a la lista nueva de los puntosIntermedios = puntos via
            if entre == True:  
                counter += 1
                x = intersecciones[i] 
                puntosIntermedios.insert(j+counter,x)
                intersecciones[i].append(tipo)            # utilizado más tarde. Tipo signifíca el tipo de punto (actual o objetivo) por que pasa la intersección originalmente
     
                i += 1
                
                if i == len(intersecciones):              # al terminar poniendo todas intersecciones en la nueva lista, se sale del bucle
                    break
        return puntosIntermedios
    
    # Se obtiene la información de geometria de las líneas que pasan por el punto objetivo y actual para obtener sus intersecciones con el contorno:

    # Hallar pendiente de linea 0  
    linea = geometría['linea']
    pendienteOriginal = pendiente(linea)

    # Crear linea pasando por nuestro objetivo
    lineaObjYint = yint(coordObj,pendienteOriginal)
    lineaObjEc = (pendienteOriginal,lineaObjYint)
    
    # Crear linea pasando por nuestro punto actual
    lineaActYint = yint(coordAct, pendienteOriginal)
    lineaActEc = (pendienteOriginal, lineaActYint)
  
    # Hallar intersecciones y guardarlas en la lista si están dentro de los rangos       
    interseccionesObj = interseccionesValidas(lineaObjEc,poliEc)
    interseccionesAct = interseccionesValidas(lineaActEc,poliEc)

   # Se determina el caso en que estámos:
    if len(interseccionesAct) != 0 and len(interseccionesObj) != 0:  # Existen intersecciones válidas que pasan por coordAct y coordObj
        print("Intersecciones de coordAct and coordObj encontrados")
        puntosIntermedios = hallarPuntosIntermedios(interseccionesObj, geometría['poli'], 'O')
        puntosIntermedios = hallarPuntosIntermedios(interseccionesAct, puntosIntermedios, 'A')
        
    if len(interseccionesAct) == 0 and len(interseccionesObj) == 0: # No existen intersecciones válidas
        print("Intersecciones de coordAct and coordObj NO encontrados")

        puntosIntermedios = [] # No existen puntos intermedios. Sólo existe el contorno
    
    if len(interseccionesAct) != 0 and len(interseccionesObj) == 0: # Sólo existe intersecciones que pasan por coordAct
        print("Intersecciones de coordAct encontrados")

        puntosIntermedios = hallarPuntosIntermedios(interseccionesAct, geometría['poli'], 'A')
    
    if len(interseccionesAct) == 0 and len(interseccionesObj) != 0: # Sólo existe intersecciones que pasan por coordObj
        print("Intersecciones de coordObj encontrados")

        puntosIntermedios = hallarPuntosIntermedios(interseccionesObj, geometría['poli'], 'O')
    
    print("Intersecciones y puntos del contorno puestos en orden consecutivo: ",puntosIntermedios)
    return puntosIntermedios

# Probar todas las posibles rotaciones de la lista de puntos intermedios para calcular la trayectoria con la menor distancia total
def construirTrayectoria(puntosIntermedios, coordAct, coordObj):   

	print("Construyendo trayectoria con coordAct = ", coordAct ," y coordObj = ",coordObj)

	from navegacion import distancia 

	# Hallar distancia entre un punto de puntos intermedios y la proxima de la lista
	def distanciaTotal(lista, indexPuntoObj):
		d = 0
		for i in range(indexPuntoObj):
			d = d + distancia(lista[i],lista[i+1])
		
		return d

	# Hallar punto más cercana si no existe intersecciones que pasan por coordAct y/o coordObj o ningún de ellos
	def sustituirPuntoFaltado(puntoA,puntoB,coordObj_o_Act):
			
		# Hallar distancias entre puntos intermedios y coordAct y/o coordObj (el punto que NO tiene intersecciones con el contorno)
		distancias = []
		for coord in puntosIntermedios:
			dist = distancia(coordObj_o_Act,coord)
			distancias.append([dist,coord]) # No olvidar escribir el punto que da la distancia, no sólo la distancia

		# En la lista de distancias elegir la distancia más pequeña y asignar ella a puntoA que falta
		minimum = distancias[0][0]
		puntoA = distancias[0][1]

		for i in range(len(distancias)-1):
			if distancias[i][0] < minimum:
				minimum = distancias[i][0]
				puntoA = distancias[i][1]

		return puntoA    


	# Iniciar algunas variables utilizadas en el próximo paso
	counterA = 0
	counterO = 0
	actA = 0
	actB = 0
	objA = 0
	objB = 0

	# Asignar un lado A o B a los puntos intermedios (intersecciones que pasan por coordAct y coordObj)
	for punto in puntosIntermedios:
		if len(punto) == 3:
			if punto[2] == "A":
				if counterA == 0:
					actA = punto
					counterA = 1
				elif counterA == 1:
					actB = punto
			if punto[2] == "O":
				if counterO == 0:
					objA = punto    
					counterO = 1
				elif counterO == 1:
					objB = punto
	 
	# Si no hay intersecciones que pasan por coordAct o coordObj, llamar una función que encuentra un punto más cercano que se puede utilizar como parte de la trayectoria
	if actA == 0 and actB == 0:
		actA = sustituirPuntoFaltado(actA,actB,coordAct)  # llamamos la función con los puntos que NO tenemos (actA y/o actB en este caso)
		actB = actA
	if objA == 0 and objB == 0:
		objA = sustituirPuntoFaltado(objA,objB,coordObj) # llamamos la función con los puntos que NO tenemos (objA y/o objB en este caso)
		objB = objA
		
	print("actA final = ", actA)
	print("actB final = ", actB)
	print("objA final = ", objA)
	print("objB final = ", objB)

	# -----Rotar la lista de puntosIntermedios, creando trayectorias posibles, y elegir más eficiente-----   

	# --Crear listas de punto actual a objetivo en ordenen horario:--

	# Obtener la posición de actA y actB (las intersecciónes la línea que pasa por coordAct con el contorno) en la lista en orden horario
	indexActA = puntosIntermedios.index(actA)
	indexActB = puntosIntermedios.index(actB)    

	# Rotar la lista para empezar la trayectoria de actA 
	aHorario = puntosIntermedios[indexActA:] + puntosIntermedios[:indexActA]    
	# Obtener la posición de objA y objB (las intersecciónes la línea que pasa por coordObj con el contorno) en la lista en orden horario que empieza en actA
	indexObjA = aHorario.index(objA)
	indexObjB = aHorario.index(objB)
	# Opción 0: Se sale por lado A de la línea que pasa por coordAct y se llega a lado A de coordObj
	distancia0 = distanciaTotal(aHorario,indexObjA) + distancia(coordAct,actA) + distancia(coordObj,objA)
	# Opción 1: Se sale por lado B de la línea que pasa por coordAct y se llega a lado B de coordObj
	distancia1 = distanciaTotal(aHorario,indexObjB) + distancia(coordAct,actA) + distancia(coordObj,objB)

	# Rotar la lista para empezar la trayectoria de actB
	bHorario = puntosIntermedios[indexActB:] + puntosIntermedios[:indexActB]    
	# Obtener la posición de objA y objB (las intersecciónes la línea que pasa por coordObj con el contorno) en la lista en orden horario que empieza en actB
	indexObjA = bHorario.index(objA)
	indexObjB = bHorario.index(objB)
	# Opción 2: Se sale por lado B de la línea que pasa por coordAct y se llega a lado A de coordObj
	distancia2 = distanciaTotal(bHorario,indexObjA) + distancia(coordAct,actB) + distancia(coordObj,objA)
	# Opción 3: Se sale por lado B de la línea que pasa por coordAct y se llega a lado B de coordObj
	distancia3 = distanciaTotal(bHorario,indexObjB) + distancia(coordAct,actB) + distancia(coordObj,objB)

	# --Crear listas de punto actual a objetivo en ordenen antihorario:--

	puntosIntermediosR = puntosIntermedios.copy()
	puntosIntermediosR.reverse()

	# Obtener la posición de actA y actB (las intersecciónes la línea que pasa por coordAct con el contorno) en la lista en order antihorario
	indexActA = puntosIntermediosR.index(actA)
	indexActB = puntosIntermediosR.index(actB)

	# Rotar la lista para empezar la trayectoria de actA 
	aAntiHorario = puntosIntermediosR[indexActA:] + puntosIntermediosR[:indexActA]   
	# Obtener la posición de objA y objB en la lista en orden ANTIHORARIO que empieza en actA
	indexObjA = aAntiHorario.index(objA)
	indexObjB = aAntiHorario.index(objB)    
	# Opción 4: Se sale por lado A de la línea que pasa por coordAct y se llega a lado A de coordObj
	distancia4 = distanciaTotal(aAntiHorario,indexObjA) + distancia(coordAct,actA) + distancia(coordObj,objA)
	# Opción 5: Se sale por lado A de la línea que pasa por coordAct y se llega a lado B de coordObj
	distancia5 = distanciaTotal(aAntiHorario,indexObjB) + distancia(coordAct,actA) + distancia(coordObj,objB)

	# Rotar la lista para empezar la trayectoria de actB 
	bAntiHorario = puntosIntermediosR[indexActB:] + puntosIntermediosR[:indexActB]
	# Obtener la posición de objA y objB en la lista en orden ANTIHORARIO que empieza en actB
	indexObjA = bAntiHorario.index(objA)
	indexObjB = bAntiHorario.index(objB)
	# Opción 6: Se sale por lado B de la línea que pasa por coordAct y se llega a lado A de coordObj
	distancia6 = distanciaTotal(bAntiHorario,indexObjA) + distancia(coordAct,actB) + distancia(coordObj,objA)
	# Opción 7: Se sale por lado B de la línea que pasa por coordAct y se llega a lado B de coordObj
	distancia7 = distanciaTotal(bAntiHorario,indexObjB) + distancia(coordAct,actB) + distancia(coordObj,objB)

	# Crear lista de distancias totales da las trayectorias posibles
	distancias = [distancia0, distancia1, distancia2, distancia3, distancia4, distancia5, distancia6, distancia7]

	for i in range(len(distancias)-1):
		print("Distancia total a viajar de la opción ", i, ": ", distancias[i], " m")
	 
	distanciaMin = min(distancias)             # hallar distancia mínima en la lista de distancias totales de cada trayectoria posible
	indiceMin = distancias.index(distanciaMin) # hallar la posición de esta distancia en a lista

	# Dependiendo de la trayectoria maś eficiente, se elige el lado del campo que el robot tiene que entrar para llegar a coordObj 
	if indiceMin == 0 or indiceMin == 1: 
		if indiceMin == 0:                     # Opción 0: salimos por lado A de coordAct y llegamos a lado A a coordObj en orden HORARIO
			indiceFin = aHorario.index(objA)
		elif indiceMin == 1:                   # Opción 1: salimos por lado B de coordAct y llegamos a lado B a coordObj en orden HORARIO
			indiceFin = aHorario.index(objB)
		trayectoria = aHorario[:indiceFin+1]
	elif indiceMin == 2 or indiceMin == 3:     
		if indiceMin == 2:                     # Opción 2: salimos por lado B de coordAct y llegamos a lado A a coordObj en orden HORARIO
			indiceFin = bHorario.index(objA)
		elif indiceMin == 3:                   # Opción 3: salimos por lado B de coordAct y llegamos a lado B a coordObj en orden HORARIO
			indiceFin = bHorario.index(objB)
		trayectoria = bHorario[:indiceFin+1]
	elif indiceMin == 4 or indiceMin == 5:
		if indiceMin == 4:                     # Opción 4: salimos por lado A de coordAct y llegamos a lado A a coordObj en orden ANTIHORARIO
			indiceFin = aAntiHorario.index(objA)
		elif indiceMin == 5:                   # Opción 5: salimos por lado A de coordAct y llegamos a lado B a coordObj en orden ANTIHORARIO
			indiceFin = aAntiHorario.index(objB)
		trayectoria = aAntiHorario[:indiceFin+1]
	elif indiceMin == 6 or indiceMin == 7:
		if indiceMin == 6:                     # Opción 6: salimos por lado B de coordAct y llegamos a lado A a coordObj en orden ANTIHORARIO
			indiceFin = bAntiHorario.index(objA)
		elif indiceMin == 7:                   # Opción 7: salimos por lado B de coordAct y llegamos a lado B a coordObj en orden ANTIHORARIO
			indiceFin = bAntiHorario.index(objB)
		trayectoria = bAntiHorario[:indiceFin+1]
		
	trayectoria = [coordAct] + trayectoria    # Se añade el punto actual (coordAct) al inicio de nuestra trayecotria para mostrarla bien en la página web
	trayectoria.append(coordObj)

	return trayectoria

# Devuelve la trayectoria que el robot utilizará para su navegación
def crearTrayectoria(coordAct, coordObj, geometría):                               # devuelve la trayectoria óptima (menor distancia total) entre coordAct y coordObj
	print("---------------------------------------------------------------------------------------------------------")
	print("Calculando trayectoria... ")
	print("---------------------------------------------------------------------------------------------------------")
	poliEc = crearPoliEc(geometría)                                                # halla las ecuaciones de los segmentos del polígono

	puntosIntermedios = crearPuntosIntermedios(geometría,poliEc,coordAct,coordObj) # organiza los puntos consecutivos

	if len(puntosIntermedios) != 0:
		trayectoria = construirTrayectoria(puntosIntermedios, coordAct, coordObj)  # calcula la trayectoria optima desde coordAct
	else:
		trayectoria = [coordAct, coordObj]
		print("---------------------------------------------------------------------------------------------------------")
		print("Trayectoria: ", trayectoria)
		print("---------------------------------------------------------------------------------------------------------")


	return trayectoria




