import os
import time
import pexpect

# Inicar el proceso de RTKLIB 
procesoRTK = pexpect.spawn('/home/pi/RTKLIB-rtklib_2.4.3/app/rtkrcv/gcc/rtkrcv')

# Continuar el arranco del servidor RTKLIB automaticamente
def iniciarRTK():
    procesoRTK.expect('rtkrcv> ')
    procesoRTK.sendline('load /home/pi/TFM/Robot/PiA/rtkrcv.conf')
    procesoRTK.sendline('\r\n')
    
    procesoRTK.sendline('start')
    procesoRTK.sendline('\r\n')
    
    procesoRTK.sendline('y')
    procesoRTK.sendline('\r\n')
    
# Reiniciar el servidor RTKLIB automaticamente                 
def reiniciarRTK():
    procesoRTK.sendline('restart')
    procesoRTK.sendline('\r\n')
    
    procesoRTK.sendline('y')
    procesoRTK.sendline('\r\n')
    
# Apagar el servidor RTKLIB seguramente                
def finalizarRTK():
    procesoRTK.sendline('shutdown')
    procesoRTK.sendline('\r\n')

# Leer solución actual del GPS de un archivo y devolver coordAct
def obtenerCoordAct():
    
    archivoSalidaRTK = '/home/pi/output.data'
    tamanoArchivoPrev = 0
    tamanoArchivo = os.path.getsize(archivoSalidaRTK)
    coordAct = [0,0]
           
    if tamanoArchivo > tamanoArchivoPrev:
        
        salidaRTK = open(archivoSalidaRTK, 'rb')
                    
        # Buscar la linea que tiene un fix
        salidaRTK.seek(-74,2)
        fix = salidaRTK.read(1)
        fix = fix.decode('utf-8')
        
        # Si la racio utilizado es aceptable (hay un fix), guardar el resultado       
        if fix == str(1):
            # Guardar latitud
            salidaRTK.seek(-115,2)
            latAct = salidaRTK.read(12)
            latAct = latAct.decode('utf-8')
            
            # Guardar longitud
            salidaRTK.seek(-100,2)
            lonAct = salidaRTK.read(12)
            lonAct = lonAct.decode('utf-8')
            
            #coordAct = [float(latAct), float(lonAct)]
            coordAct = [float(lonAct), float(latAct)]
        
        # Si no hay un resultado aceptable, devolver el mensaje informativo
        else:           
            coordAct = 'obteniendo una solucion...'                          
                    
        tamanoArchivoPrev = tamanoArchivo
    
    tamanoArchivo = os.path.getsize(archivoSalidaRTK)
        
    return coordAct


            
##obtenerCoordAct()
