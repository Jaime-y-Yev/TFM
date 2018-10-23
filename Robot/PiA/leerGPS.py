import os
import time
import pexpect


procesoRTK = pexpect.spawn('/home/pi/RTKLIB-rtklib_2.4.3/app/rtkrcv/gcc/rtkrcv')


def iniciarRTK():
    procesoRTK.expect('rtkrcv> ')
    procesoRTK.sendline('load /home/pi/RTKLIB-rtklib_2.4.3/app/rtkrcv/gcc/rtkrcv.conf')
    procesoRTK.sendline('\r\n')
    
    procesoRTK.sendline('start')
    procesoRTK.sendline('\r\n')
    
    procesoRTK.sendline('y')
    procesoRTK.sendline('\r\n')
    
                
def reiniciarRTK():
    procesoRTK.sendline('restart')
    procesoRTK.sendline('\r\n')
    
    procesoRTK.sendline('y')
    procesoRTK.sendline('\r\n')
    

def finalizarRTK():
    procesoRTK.sendline('shutdown')
    procesoRTK.sendline('\r\n')


def obtenerCoordAct():
    
    #archivoSalidaRTK = '/home/pi/Desktop/piA/output.txt'
    archivoSalidaRTK = '/home/pi/output.data'
    tamanoArchivoPrev = 0
    tamanoArchivo = os.path.getsize(archivoSalidaRTK)
    
    #coordAct = [0,0]
           
    if tamanoArchivo > tamanoArchivoPrev:
        
        salidaRTK = open(archivoSalidaRTK, 'rb')
                    
        # Get ratio
        salidaRTK.seek(-74,2)
        fix = salidaRTK.read(1)
        fix = fix.decode('utf-8')
        
##        print(fix)
        
        if fix == str(1):

            # Get latitude
            salidaRTK.seek(-115,2)
            latAct = salidaRTK.read(12)
            latAct = latAct.decode('utf-8')
            
            # Get longitude
            salidaRTK.seek(-100,2)
            lonAct = salidaRTK.read(12)
            lonAct = lonAct.decode('utf-8')
            
            coordAct = [float(latAct), float(lonAct)]
        
        else:
            
            coordAct = 'obteniendo una solucion...'
                          
                    
        tamanoArchivoPrev = tamanoArchivo
    
    tamanoArchivo = os.path.getsize(archivoSalidaRTK)
    
    
    return coordAct


            
##obtenerCoordAct()