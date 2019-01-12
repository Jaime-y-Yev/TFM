import csv
import globalesPi


def guardarMed(nombre,medicionesDict,sustancia=None):
	fields = [sustancia,medicionesDict["Temperatura"],medicionesDict["Humedad"],medicionesDict["EC"],medicionesDict["Salinidad"],medicionesDict["SDT"],medicionesDict["Epsilon"]]
	
	with open(nombre,"a") as f:
		writer = csv.writer(f)
		writer.writerow(fields)
		print("Guardando mediciones: ",fields)
		
#guardarMed("Test",medicionesDict,"aire")
