import csv
import time
import globalesPi
def guardarCoordAct(nombre, coordAct):
	#lon = coordAct.split(",")[0]
	#lon = lon.replace('"[',"")
	lon = coordAct[0]
	#lat = coordAct.split(",")[1]
	#lat = lon.replace(']"',"")
	lat = coordAct[1]

	tiempo = time.strftime("%H,%M,%S", time.gmtime())
	h, m, s = tiempo.split(',')
	elapsed = time.monotonic()-globalesPi.tiempoInicio
	
	fields=[lon,lat,h,m,s,elapsed]
	with open(nombre, 'a') as f:
		writer = csv.writer(f)
		writer.writerow(fields)
		print("Guardando coordAct: ",coordAct)
    
def test():
	globalesPi.tiempoInicio =time.monotonic()

	while True:
		guardarCoordAct("File1")
		time.sleep(2)

#test()
