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
int modo = MODO_NAVEGACION;         // empezar en modo de parada
int *modoPuntero = &modo;
_Bool navegacionManual = true;

// Controlador de motores
#include <SoftwareSerial.h>
#include "RoboClaw.h"
#define DIRECCION_MEMORIA_RC 0x80
#define V_LENTA 30 //30
#define V_NORMAL 50 //50
#define V_RAPIDA 60 //80
#define PORCENTAJE 0.6 // 0.6
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
#define TOL_DIRECCION 7 ///////
#define TOL_SONAR 0.2            // tolerancia grados a girar
int direccionObj = 205;            // CAMBIAR EN SIMULACIÓN------------------------------------------------------------
int *direccionObjPuntero = &direccionObj;

int direccionPreobstaculo= 205; ////////////////////////////////////
int *direccionPreobstaculoPuntero = &direccionPreobstaculo;
char giroPreobstaculo; /////////////////////////////////////////
char *giroPreobstaculoPuntero = &giroPreobstaculo;
// TODO CREATE LINKED LIST
int memoriaGIRO[20];

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
#define DISTANCIA_GIRO_MIN 0.5              //0.5 // !distancia min para girar 
#define DISTANCIA_GRANDE 10                //2.0//(en campo = 10) /////////////////////////////////
#define DISTANCIA_CORTA 0.5                //1.0//(en campo = 3)
#define DISTANCIA_OBSTACULO 0.2             //0.4//(en campo = 1)   el robot intenta a evitar el obstáculo a esta distancia
#define DISTANCIA_PARADA 0.10                //0.2//(en campo = 0.2) el robot para completamente a esta distancia de un obstáculo 

#define RATIO_DIST_ENCODER_1 0.00918
#define RATIO_DIST_ENCODER_2 0.00914

float distanciaObj = 3;                      // distancia recibida de Pi ------------------------------------------------------------------------------
float *distanciaObjPuntero = &distanciaObj; 
float distanciaAct = 0;                      // distancia desplazada por el robot según los encoders
float *distanciaActPuntero = &distanciaAct;
int llegada = 0;                             // llegada = 1, Arduino listo para recibir comandos; llegada = 0, Arduino NO listo para recibit comandos
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
  delay(500); // for prints
}

void loop()
{
  //COMUNICACIÓN CON PiA PARA NAVEGAR-------------------------------------------------------------------------------------------------------------------------

  erroresMotor();
  
  delay(200); // esperar un poco para iniciar la comunicación serie sin errores
  
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
  if (modo == MODO_NAVEGACION) ////// WAS ELSE IF
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


    // LEER SENSORES PARA DESPLAZAR SEGÚN DIRECCIÓNES DE PiA--------------------------------------------------------------------------------------------------------------

    
    // Leer sonar FI, FD, I, D, A-----------------------------------------------------------------------------------
    leerSonars();                                                          
    if (imprimir ==1)
    {
      Serial.print("distanciaSonarFI = ");  Serial.println(distanciaSonarFI);
      Serial.print("distanciaSonarFD = ");  Serial.println(distanciaSonarFD);
      Serial.print("distanciaSonarI = ");  Serial.println(distanciaSonarI);
      Serial.print("distanciaSonarD = ");  Serial.println(distanciaSonarD);
      Serial.print("distanciaSonarA = ");  Serial.println(distanciaSonarA);
      Serial.println();
    }
//    if (distanciaSonarFI <= 0.4 || distanciaSonarFD <= 0.4) ////////////////////////////////////////
//    {
//      parar();
//      modo = MODO_INACTIVO;
//    }
//     Leer magnetometro---------------------------------------------------------------------------------------------
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
   
    // char giro = RECTA; ///////////////////////////////////////////////added for test to go straight

    // Leer encoder y calcular distancia viajada multiplicando este numero por un ratio para convertir a metros------
    calcularDistanciaAct(distanciaActPuntero);    
    
    if (imprimir_nav ==1)
    {
      //Serial.print("distanciaAct = ");  Serial.println(distanciaAct);
      //Serial.print("distanciaObj = ");  Serial.println(distanciaObj);
    }

    // Calcular distancia a desplazar---------------------------------------------------------------------------------
    float distAdesplazar = distanciaObj - distanciaAct;
    
    if (imprimir_nav ==1)
    {
      Serial.print("distAdesplazar = ");  Serial.println(distAdesplazar);
    }
    if (navegacionManual == false)
    {
      if (distAdesplazar <= 0.00)   // al desplazar la distancia necesaria, cambiar llegada a 1 para obtener nuevos comandos y para corregir su posición
      {
        llegada = 1;             
        parar();    
        modo = MODO_INACTIVO; //////// TESTING 
        if (imprimir_nav ==1)
        {
          Serial.println("arrived");
        }
      }
      // Mover el robot teniendo en cuenta distancia, dirección, y obstáculos--------------------------------------------
      if (distAdesplazar > 0.00)
      {
        moverRobot(giro, distAdesplazar,errorDireccionPuntero);
//        moverRobot(distanciaSonarIPuntero,distanciaSonarDPuntero,distanciaSonarFIPuntero,distanciaSonarFDPuntero,distanciaSonarAPuntero,giro,distAdesplazar,errorDireccionPuntero, modoPuntero);
      }
    }
    else if (navegacionManual == true)
    {
      navManual(mensaje); 
    }
  }
}

void navManual(char mensaje[])
{
    if (mensaje[0] == 'p')
      parar();    
    else if (mensaje[0] == 'a' && mensaje[1] == 'r')
      avanzarRecto(V_LENTA);
    else if (mensaje[0] == 'a' && mensaje[1] == 'i')
      avanzarIzquierda(V_LENTA);
    else if (mensaje[0] == 'a' && mensaje[1] == 'd')
      avanzarDerecha(V_LENTA);
    else if (mensaje[0] == 'r' && mensaje[1] == 'r')
      retrocederRecto(V_LENTA);
    else if (mensaje[0] == 'r' && mensaje[1] == 'i')
      retrocederIzquierda(V_LENTA);
    else if (mensaje[0] == 'r' && mensaje[1] == 'd')
      retrocederDerecha(V_LENTA);
    else if (mensaje[0] == 'g' && mensaje[1] == 'i')
      giroIzquierda(V_NORMAL);
    else if (mensaje[0] == 'g' && mensaje[1] == 'd')
      giroDerecha(V_NORMAL);
    else if (mensaje[0] == 'z' && mensaje[1] == 'e')
      rc.ResetEncoders(DIRECCION_MEMORIA_RC);
}

    

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

void erroresMotor(void)
{
  Serial.println("erroresMotor()");
  _Bool valid;
  uint16_t estado = rc.ReadError(DIRECCION_MEMORIA_RC, &valid);
  _Bool error = false;

  Serial.print("estado & 0x0000 = ");  Serial.println(estado & 0x0000);
  Serial.print("error = ");  Serial.println(error);

  if (!(estado & 0x0000)) Serial.println("RC Normal");
  if (estado & 0x0001) {Serial.println("RC Error: Sobrecorriente M1"); error = true;} 
  if (estado & 0x0002) {Serial.println("RC Error: Sobrecorriente M2"); error = true;} 
  if (estado & 0x0004) {Serial.println("RC Error: E-stop"); error = true;} 
  if (estado & 0x0008) {Serial.println("RC Error: temperatura"); error = true;} 
  if (estado & 0x0010) {Serial.println("RC Error: temperatura 2"); error = true;} 
  if (estado & 0x0020) {Serial.println("RC Error: Batería principal alta"); error = true;} 
  if (estado & 0x0040) {Serial.println("RC Error: Batería lógica alta"); error = true;} 
  if (estado & 0x0080) {Serial.println("RC Error: Batería lógica baja"); error = true;} 
  if (estado & 0x0100) {Serial.println("RC Error: M1 driver"); error = true;} 
  if (estado & 0x0200) {Serial.println("RC Error: M2 driver"); error = true;} 
  if (estado & 0x0400) {Serial.println("RC Aviso: Batería principal alta"); error = true;} 
  if (estado & 0x0800) {Serial.println("RC Aviso: Batería principal baja"); error = true;} 
  if (estado & 0x1000) {Serial.println("RC Aviso: temperatura M1"); error = true;} 
  if (estado & 0x2000) {Serial.println("RC Aviso: temperatura M2"); error = true;} 
  //if (estado & 0x4000) Serial.println("RC M1 Home"); 
  //if (estado & 0x8000) Serial.println("RC M2 Home");

  if (error) *modoPuntero = MODO_EMERGENCIA;
}
