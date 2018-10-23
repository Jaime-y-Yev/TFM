// DEFINICIONES LAS VARIABLES UTILIZADO EN ARDUINOA-------------------------------------------------------------------------------------------------------------------

// Demonstración
int imprimir = 0; // 0 = no imprimir cuando hay comunicación activa con PiA; 1 = imprimir distancias y variables dentro de ArduinoA cuando no hay comunicación con PiA
int imprimir_nav = 0;

// Comandos de RPi
#include "headers/comandos.h"
#define LONGITUD_MENSAJE 20
char mensaje[LONGITUD_MENSAJE];
int comando;

// Modo de operación
int modo = MODO_INACTIVO;         // empezar en modo de parada
int *modoPuntero = &modo;

// Controlador de motores
#include <SoftwareSerial.h>
#include "RoboClaw.h"
#define DIRECCION_MEMORIA_RC 0x80
#define V_LENTA 30 //30
#define V_NORMAL 40 //50
#define V_RAPIDA 50 //80
#define PORCENTAJE 0.6
SoftwareSerial serial(10, 11);    // 10 to S2 and 11 to S1
RoboClaw rc(&serial, 10000);

// Magnetometro
#include <Wire.h>
#include <Adafruit_LSM303.h>
#define ANGULO_DEC 0.011635528
Adafruit_LSM303 lsm;

// Direcciones
#define IZQUIERDA 'I'
#define DERECHA 'D'
#define RECTA 'R'
#define PARAR 'P'
#define ATRAS 'A'
#define ATRAS_IZQUIERDA 'i'
#define ATRAS_DERECHA 'd'
#define DESP_ADELANTE 0
#define DESP_ATRAS 1
#define DESP_GIRO 2
#define TOL_DIRECCION 10
#define TOL_SONAR 0.1            // tolerancia grados a girar
int direccionObj = 0;
int *direccionObjPuntero = &direccionObj;
int direccionAct = 0;
int *direccionActPuntero = &direccionAct;
int errorDireccion = 0; 
int *errorDireccionPuntero = &errorDireccion;

// Sonar
#define TRIGFI 2
#define ECHOFI 3
#define TRIGFD 8
#define ECHOFD 9
#define TRIGA 4
#define ECHOA 5
#define TRIGI 6
#define ECHOI 7
#define TRIGD 12 
#define ECHOD 13
#define M_SONARFI 0.0177
#define B_SONARFI -0.8338
#define M_SONARFD 0.0178
#define B_SONARFD -0.3905
#define M_SONARA 0.0178
#define B_SONARA -0.9843
#define M_SONARI 0.0177
#define B_SONARI -0.3467
#define M_SONARD 0.0177 
#define B_SONARD -0.0027 

float distanciaSonarFI = 0.0;
float *distanciaSonarFIPuntero = &distanciaSonarFI;
float distanciaSonarFD = 0.0;
float *distanciaSonarFDPuntero = &distanciaSonarFD;
float distanciaSonarA = 0.0; 
float *distanciaSonarAPuntero = &distanciaSonarA;
float distanciaSonarI = 0.0; 
float *distanciaSonarIPuntero = &distanciaSonarI;  
float distanciaSonarD = 0.0; 
float *distanciaSonarDPuntero = &distanciaSonarD;

//---- Distancias cuando el robot está entre filas
#define DISTANCIA_FILA 0.25                  // (en campo = 0.5) distancia que determina si estás en una fila o no
#define TOL_DISTANCIA 0.25                   // tolerancia de distancia para el modo entre filas

// Distancias de evitación de obstáculos
#define DISTANCIA_GIRO_MIN 0.25              // !distancia min para girar 
#define DISTANCIA_GRANDE 1                   //(en campo = 10) 
#define DISTANCIA_CORTA 0.4                  //(en campo = 3)
#define DISTANCIA_OBSTACULO 0.2              //(en campo = 1)   el robot intenta a evitar el obstáculo a esta distancia
#define DISTANCIA_PARADA 0.1                 //(en campo = 0.2) el robot para completamente a esta distancia de un obstáculo 

#define RATIO_ENCODER_DISTANCIA 0.00594

float distanciaObj = 0;                      // distancia recibida de Pi
float *distanciaObjPuntero = &distanciaObj; 
float distanciaAct = 0;                      // distancia desplazada por el robot según los encoders
float *distanciaActPuntero = &distanciaAct;
int llegada = 1;                             // llegada = 1, Arduino listo para recibir comandos; llegada = 0, Arduino NO listo para recibit comandos
int *llegadaPuntero = &llegada;


void setup()
{
  // Inicializar los sensores y comunicaciones serie
  Serial.begin(115200);
  lsm.begin();
  rc.begin(38400);

  pinMode(TRIGFI, OUTPUT);
  pinMode(ECHOFI, INPUT);
  pinMode(TRIGFD, OUTPUT);
  pinMode(ECHOFD, INPUT);
  pinMode(TRIGA, OUTPUT);
  pinMode(ECHOA, INPUT);
  pinMode(TRIGI, OUTPUT);
  pinMode(ECHOI, INPUT);
  pinMode(TRIGD, OUTPUT);
  pinMode(ECHOD, INPUT);
}

void loop()
{


  COMUNICACIÓN CON PiA PARA NAVEGAR-------------------------------------------------------------------------------------------------------------------------
 
  
  delay(300); // esperar un poco para iniciar la comunicación serie sin errores
  
  // Recibir mensajes de PiA, decodificarlos, y hacer una conversión a forma útil----------------------------------
  if (Serial.available())
  {
    int i;
    for (i = 0; Serial.available(); i++)          // si hay una conexión con PiA, empieza a recibir mensajes
      mensaje[i] = Serial.read();                 // guarda el mensaje caracter por caracter
    mensaje[i] = '\0';                            // convierte mensaje a string
  }
  else
     memset(mensaje, 0, sizeof(mensaje));         // vaciar el mensaje (reinicializarlo a todo 0's) 
  
  comando = (int)convertirAfloat(mensaje, 1, 0);  // conversión del mensaje de string a float
  
  // Mandar mensajes a PiA ------------------------------------------------------------------------------------------
  
  // ArduinoA informa PiA de su modo 
  if (comando == LEER_MODO)
  {
    String respuesta = 'X' + String(modo) + 'x';  // eco el comando a PiA con caracteres de inciación y terminación
    Serial.println(respuesta);
    Serial.flush();
  }  
  
  // Cambiar el modo de Arduino
  if (comando == CAMBIAR_MODO)
  {
     *modoPuntero = mensaje[2] - '0';         
     String respuesta = 'X' + String(modo) + 'x';  // eco el comando a PiA con caracteres de inciación y terminación
     Serial.println(respuesta);
     Serial.flush();
  }   

  // Modo Inactivo y Modo Emergencia:---------------------------------------------------------------------------------
  if (modo == MODO_INACTIVO || modo == MODO_EMERGENCIA)
  {
    parar();                                  // el robot siempre para
    llegada = 1;                              // el robot está listo para recibir comandos de dirección y distancia
    rc.ResetEncoders(DIRECCION_MEMORIA_RC);   // reseteo de los encoders
    *direccionObjPuntero = 0;                 // reseteo de variable dirección
    *distanciaObjPuntero = 0.00;              // reseteo de variable distancia
  }
  
  // Modo Navegacición------------------------------------------------------------------------------------------------
  else if (modo == MODO_NAVEGACION)
  {
    // Mandar el estado de variable llegada a PiA. En PiA este variable = llegadaArduinoA
    if (comando == CONFIRMAR_LLEGADA)           
    {
      String respuesta = 'X' + String(llegada) + 'x'; 
      Serial.println(respuesta);
      Serial.flush();
    }
    // Recibir dirección y distancia comandos si llegada = 1
    else if (comando == RECIBIR_DIRECCION_DISTANCIA_OBJ)
    {
      rc.ResetEncoders(DIRECCION_MEMORIA_RC);                             // resetear encoders

      *direccionObjPuntero = (int)convertirAfloat(mensaje, 2, 2);         // recibir dirección y guardarla en variable global
      *distanciaObjPuntero = convertirAfloat(mensaje, 6, 5);              // recibir distancia y guardarla en variable global
 
      String direccionYdistanciaObj = String(direccionObj) + String(distanciaObj); // eco la dirección y distancia a PiA para asegurar que han sido envidados correctamente
      String respuesta = 'X' + String(direccionYdistanciaObj) + 'x';
      Serial.println(respuesta);
      Serial.flush();
      
      llegada = 0;                                                         // resetear llegada a 0 para no recibir nuevos comandos mientras el desplazamiento
    }


    LEER SENSORES PARA DESPLAZAR SEGÚN DIRECCIÓNES DE PiA--------------------------------------------------------------------------------------------------------------

    
    // Leer sonar FI, FD, I, D, A-----------------------------------------------------------------------------------
    leerSonars();                                                          
    if (imprimir ==1)
    {
      Serial.print("distanciaSonarFI MAIN= ");  Serial.println(distanciaSonarFI);
      Serial.print("distanciaSonarFD MAIN = ");  Serial.println(distanciaSonarFD);
      Serial.print("distanciaSonarI = ");  Serial.println(distanciaSonarI);
      Serial.print("distanciaSonarD = ");  Serial.println(distanciaSonarD);
      Serial.print("distanciaSonarA = ");  Serial.println(distanciaSonarA);
      Serial.println();
    }
    
    // Leer magnetometro---------------------------------------------------------------------------------------------
    leerMagnetometro();                                                      
    if (imprimir ==1)
    {
      Serial.println(direccionAct);
    }

    // Calcular cuanto hirar sabiendo la dirección corriente y dirección obj------------------------------------------
    char giro = calcularGiro();                                              
    if (imprimir ==1)
    {
      Serial.print("giro = ");  Serial.println(giro);
      Serial.print("direccionObj = ");  Serial.println(direccionObj);
      Serial.print("direccionAct = ");  Serial.println(direccionAct);
      Serial.println();
    }

    // Leer encoder y calcular distancia viajada multiplicando este numero por un ratio para convertir a metros------
    calcularDistanciaAct(distanciaActPuntero);    
    if (imprimir_nav ==1)
    {
      Serial.print("distanciaAct = ");  Serial.println(distanciaAct);
      Serial.print("distanciaObj = ");  Serial.println(distanciaObj);
    }

    // Calcular distancia a desplazar---------------------------------------------------------------------------------
    float distAdesplazar = distanciaObj - distanciaAct;
     if (imprimir_nav ==1)
    {
      Serial.print("distAdesplazar = ");  Serial.println(distAdesplazar);
    }
    if (distAdesplazar <= 0.2)   // al desplazar la distancia necesaria, cambiar llegada a 1 para obtener nuevos comandos y para corregir su posición
    {
      llegada = 1;             
      parar();      
      if (imprimir_nav ==1)
      {
        Serial.println("arrived");
      }

    // Mover el robot teniendo en cuenta distancia, dirección, y obstáculos--------------------------------------------
    else
      moverRobot(distanciaSonarIPuntero,distanciaSonarDPuntero,distanciaSonarFIPuntero,distanciaSonarFDPuntero,distanciaSonarAPuntero,giro,distAdesplazar,errorDireccionPuntero, modoPuntero, imprimir_nav);
  }
 }
}


//  if (mensaje[0] == 'p')
//    parar();    
//  else if (mensaje[0] == 'a' && mensaje[1] == 'r')
//    avanzarRecto(V_LENTA);
//  else if (mensaje[0] == 'a' && mensaje[1] == 'i')
//    avanzarIzquierda(V_LENTA);
//  else if (mensaje[0] == 'a' && mensaje[1] == 'd')
//    avanzarDerecha(V_LENTA);
//  else if (mensaje[0] == 'r' && mensaje[1] == 'r')
//    retrocederRecto(V_LENTA);
//  else if (mensaje[0] == 'r' && mensaje[1] == 'i')
//    retrocederIzquierda(V_LENTA);
//  else if (mensaje[0] == 'r' && mensaje[1] == 'd')
//    retrocederDerecha(V_LENTA);
//  else if (mensaje[0] == 'g' && mensaje[1] == 'i')
//    giroIzquierda(V_LENTA);
//  else if (mensaje[0] == 'g' && mensaje[1] == 'd')
//    giroDerecha(V_LENTA);
//  else if (mensaje[0] == 'z' && mensaje[1] == 'e')
//    rc.ResetEncoders(DIRECCION_MEMORIA_RC);
    

// Convertir array a float
float convertirAfloat(char mensaje[], int numDigitos, int comienzoMensaje)
{
  int i;
  char vector[LONGITUD_MENSAJE];   // crear un array con la longitúd del mensaje

  // En un bucle, añadir el mensaje en el array
  for (i = 0; i <= numDigitos; i++) 
    vector[i] = mensaje[i + comienzoMensaje];
  vector[i] = '\0';                // utilizar el cáracter de terminación saber donde termina el mensaje

  return atof(vector);             // devolver el mensaje en formato float
}



