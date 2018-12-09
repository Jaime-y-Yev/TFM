#!/usr/bin/env python
import minimalmodbus
from time import sleep

minimalmodbus.BAUDRATE = 9600
minimalmodbus.TIMEOUT = 0.1
# port name, slave address (in decimal)
instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
instrument.debug = True

import json

def hacerMediciones():
    #Register number, number of decimals, function code
        
    temperatura = instrument.read_register(0,2) # Temperatura (c)
    print (temperatura)
    
    sleep(0.5)
    
    vwc= instrument.read_register(1,2) # Volumetric water content (%)
    print (vwc)
    
    sleep(0.5)
    
    ec= instrument.read_register(2) # EC (0-20000)
    print (ec)
    
    sleep(0.5)

    salinity= instrument.read_register(3) # Salinity (0-20000 mg/L)
    print (salinity)
    
    sleep(0.5)

    tds = instrument.read_register(4) # Total dissolved solids (0-20000 mg/L)
    print (tds)
    
    sleep(0.5)
    
    epsilon = instrument.read_register(5,2) # Dielectric constant (0-20000 mg/L)
    print (epsilon)
    
    #mqttPub('/RobotServidor/resultados', json.dumps({"coordObj": globalesPiB.coordObjMedicion, "temp": temp, ..., "epsilon": epsilon}))	TODOTODOTODOTODOTODO


#hacerMediciones()
