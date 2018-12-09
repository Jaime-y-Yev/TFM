// Depuración
#define IMPRIMIR  false
#define IMPRIMIR_MAG false
#define IMPRIMIR_SONARS false
#define IMPRIMIR_MOTORES false
#define IMPRIMIR_NAV false

// Comandos de RPi
#include "headers/comandos.h"
#define LONGITUD_MENSAJE 20
char mensaje[LONGITUD_MENSAJE];
int comando;

// Modo de operación
int modo = MODO_INACTIVO;// empezar en modo de parada
//int modo = MODO_MANUAL;
int *modoPuntero = &modo;
int casoNavegacion = 0;
int *casoNavegacionPuntero = &casoNavegacion;

// Controlador de motores
#include <SoftwareSerial.h>
SoftwareSerial serial(2, 3);    // 2(was 10) to S2 and 3 (was 11) to S1
#include "RoboClaw.h"
RoboClaw rc(&serial, 10000);
#define DIRECCION_MEMORIA_RC 0x80

// Magnetómetro
#include <Wire.h>
#include <Adafruit_LSM303.h>
Adafruit_LSM303 lsm;
#define ANGULO_DEC 0.011635528

// Parámetros de movimiento
int velocidad;
#define VEL_LENTA 1400  
#define VEL_NORMAL 1700 
#define VEL_RAPIDA 2000 
#define VEL_PORCENTAJE 0.2 
#define ACELERACION 1000

int giro;
#define GIRO_IZQUIERDA 'I'
#define GIRO_DERECHA 'D'
#define GIRO_RECTO 'R'
#define GIRO_ATRAS 'A'
//int memoriaGIRO[20];  // TODO: CREATE LINKED LIST

int desp; 
int *despPuntero = &desp;
#define DESP_POSITIVO 0
#define DESP_NEGATIVO 1
#define DESP_GIRO 2

int direccionAct = 0;
int *direccionActPuntero = &direccionAct;
int direccionObj = 0; //205 simu just Arduino                        // CAMBIAR EN SIMULACIÓN------------------------------------------------------------
int *direccionObjPuntero = &direccionObj;
#define TOL_DIRECCION 7
//int errorDireccion = 0; 
//int *errorDireccionPuntero = &errorDireccion;

// Sonar
#include <math.h>

float distanciaSonarFI = 0.0;
float *distanciaSonarFIPuntero = &distanciaSonarFI;
#define TRIG_FI 4
#define ECHO_FI 5
#define M_FI 0.0177
#define B_FI -0.8338

float distanciaSonarFD = 0.0;
float *distanciaSonarFDPuntero = &distanciaSonarFD;
#define TRIG_FD 6
#define ECHO_FD 7
#define M_FD 0.0178
#define B_FD -0.3905

float distanciaSonarI1 = 0.0; 
float *distanciaSonarI1Puntero = &distanciaSonarI1;
#define TRIG_I1 8
#define ECHO_I1 9
#define M_I1 0.0177
#define B_I1 -0.3467

float distanciaSonarI2 = 0.0; 
float *distanciaSonarI2Puntero = &distanciaSonarI2; 
#define TRIG_I2 10
#define ECHO_I2 11
#define M_I2 0.0177
#define B_I2 -0.3467

float distanciaSonarD1 = 0.0; 
float *distanciaSonarD1Puntero = &distanciaSonarD1;
#define TRIG_D1 12
#define ECHO_D1 13
#define M_D1 0.0177 
#define B_D1 -0.0027 

float distanciaSonarD2 = 0.0; 
float *distanciaSonarD2Puntero = &distanciaSonarD2;
#define TRIG_D2 14 
#define ECHO_D2 15
#define M_D2 0.0177 
#define B_D2 -0.0027 

float distanciaSonarA = 0.0; 
float *distanciaSonarAPuntero = &distanciaSonarA;
#define TRIG_A 16
#define ECHO_A 17
#define M_A 0.0178
#define B_A -0.9843

//---- Distancias cuando el robot está entre filas utilizando sensor D1 y F1
#define DISTANCIA_FILA 0.95                 // (en campo = 0.5) distanciaPerpendicular a fila que determina si estás en una fila o no. DistanciaFilaDiagonal = distanciaPerpendicular/cos(45)
#define TOL_ENTREFILAS 0.05

// Distancias de evitación de obstáculos con sensores FI FD
#define DISTANCIA_GIRO_MIN 0.5              //0.5 // !distancia min para girar 
#define DISTANCIA_GRANDE 10                //2.0//(en campo = 10) /////////////////////////////////
#define DISTANCIA_CORTA 0.4                //1.0//(en campo = 3)
#define DISTANCIA_OBSTACULO 0.25             //0.4//(en campo = 1)   el robot intenta a evitar el obstáculo a esta distancia
#define DISTANCIA_PARADA 0.15                //0.2//(en campo = 0.2) el robot para completamente a esta distancia de un obstáculo 

#define DISTANCIA_LADO_SEGURO 0.225 
#define DISTANCIA_LADO_DIAGONAL_SEGURO 0.19

#define RATIO_DIST_ENCODER_1 0.00918
#define RATIO_DIST_ENCODER_2 0.00914

float distanciaObj = 0; // 1.5 simu just Arduino                     // distancia recibida de Pi ------------------------------------------------------------------------------
float *distanciaObjPuntero = &distanciaObj; 
float distanciaAct = 0.01;                      // distancia desplazada por el robot según los encoders
float *distanciaActPuntero = &distanciaAct;
#define TOL_DISTANCIA 0.2            // tolerancia grados a girar
int llegada = 1;      // 0 simu just Arduino                       // llegada = 1, Arduino listo para recibir comandos; llegada = 0, Arduino NO listo para recibit comandos
int *llegadaPuntero = &llegada;


void setup()
{
  // Inicializar los sensores y comunicaciones serie
  Serial.begin(115200);
  
  lsm.begin();
  
  rc.begin(38400);
  rc.ResetEncoders(DIRECCION_MEMORIA_RC); 
  
  pinMode(TRIG_FI, OUTPUT);
  pinMode(ECHO_FI, INPUT);
  pinMode(TRIG_FD, OUTPUT);
  pinMode(ECHO_FD, INPUT);
  pinMode(TRIG_A, OUTPUT);
  pinMode(ECHO_A, INPUT);
  pinMode(TRIG_I1, OUTPUT);
  pinMode(ECHO_I1, INPUT);
  pinMode(TRIG_I2, OUTPUT);
  pinMode(ECHO_I2, INPUT);
  pinMode(TRIG_D1, OUTPUT);
  pinMode(ECHO_D1, INPUT);
  pinMode(TRIG_D2, OUTPUT);
  pinMode(ECHO_D2, INPUT);
}

void loop()
{
  if (IMPRIMIR) {Serial.print(F("-------  MAIN LOOP ---------")); Serial.print(F(" MODO = ")); Serial.println(modo);}

  //COMUNICACIÓN CON PiA PARA NAVEGAR-------------------------------------------------------------------------------------------------------------------------
  erroresMotor();

  //leerVelocidad();  
  // Sonars
  leerSonars();
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
  {
     memset(mensaje, '\0', sizeof(mensaje));         // vaciar el mensaje (reinicializarlo a todo 0's) 
     memset(comando, '\0', sizeof(comando));         // vaciar el comando (reinicializarlo a todo 0's) 
  }
  
  comando = (int)convertirAfloat(mensaje, 1, 0);  // conversión del mensaje de string a float
  
  // Responder a comandos de PiA ------------------------------------------------------------------------------------------
      // Mandar el estado de variable llegada a PiA. En PiA este variable = llegadaArduinoA
  if (comando == CONFIRMAR_DATOS)           
  {
    String respuesta = 'X' + String(llegada) + String(casoNavegacion) + String(direccionAct) + 'x'; 
    Serial.println(respuesta);
    Serial.flush();
  }
  // ArduinoA informa PiA de su modo 
  if (comando == LEER_MODO)
  {
    String respuesta = 'X' + String(modo) + 'x';  // eco el comando a PiA con caracteres de inciación y terminación
    Serial.println(respuesta);
    Serial.flush();
  }   
  // Cambiar el modo de Arduino
  else if (comando == CAMBIAR_MODO)
  {
     *modoPuntero = mensaje[2] - '0';         
     String respuesta = 'X' + String(modo) + 'x';  // eco el comando a PiA con caracteres de inciación y terminación
     Serial.println(respuesta);
     Serial.flush();
  }   

  // Modo Inactivo y Modo Emergencia:---------------------------------------------------------------------------------
  if (modo == MODO_EMERGENCIA)
  {
    if (IMPRIMIR) Serial.println(F("Modo EMEREGNCIA"));
    parar();                                  // el robot siempre para
    llegada = 0;                              // el robot NO está listo para recibir comandos de dirección y distancia
    rc.ResetEncoders(DIRECCION_MEMORIA_RC);   // reseteo de los encoders
    *direccionObjPuntero = 0;                 // reseteo de variable dirección
    *distanciaObjPuntero = 0.00;              // reseteo de variable distancia
    *casoNavegacionPuntero = 9;             
  }
  else if (modo == MODO_INACTIVO)
  {
    if (IMPRIMIR) Serial.println(F("Modo INACTIVO "));
    parar();                                  // el robot siempre para
    llegada = 1;                              // el robot está listo para recibir comandos de dirección y distancia
    rc.ResetEncoders(DIRECCION_MEMORIA_RC);   // reseteo de los encoders
    *direccionObjPuntero = 0;                 // reseteo de variable dirección
    *distanciaObjPuntero = 0.00;              // reseteo de variable distancia
    *casoNavegacionPuntero = 9;             
  }
  
  // Modo Navegacición------------------------------------------------------------------------------------------------
  else if (modo == MODO_NAVEGACION || modo == MODO_SONDEO)
  {
   // Recibir dirección y distancia
   if (comando == RECIBIR_DIRECCION_DISTANCIA_OBJ)
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

 

    // Magnetómetro
    leerMagnetometro();                                                      
    if (IMPRIMIR) {Serial.print(F("direccionObj = ")); Serial.print(direccionObj); Serial.print(F(" direccionAct = ")); Serial.println(direccionAct);}

    // Calcular cuanto girar sabiendo la dirección corriente y dirección obj------------------------------------------
    giro = calcularGiro();                                              
    if (IMPRIMIR) {Serial.print(F("giroMAIN = "));  Serial.print((char)giro); Serial.print(F("  direccionObj = "));  Serial.print(direccionObj); Serial.print(F("  direccionAct = "));  Serial.println(direccionAct); Serial.println();}

    // Leer encoder y calcular distancia viajada multiplicando este numero por un ratio para convertir a metros------
    calcularDistanciaAct();    
    if (IMPRIMIR) {Serial.print(F("distanciaObj = "));  Serial.println(distanciaObj); Serial.print(F("distanciaAct = "));  Serial.println(distanciaAct);}

    // Calcular distancia a desplazar---------------------------------------------------------------------------------
    float distAdesplazar = distanciaObj - distanciaAct;
    if (IMPRIMIR) {Serial.print(F("distAdesplazar = "));  Serial.println(distAdesplazar);}
    
    if (distAdesplazar <= 0.00 || (distanciaAct > 0.7&&distanciaAct <= 1.0))   // al desplazar la distancia necesaria, cambiar llegada a 1 para obtener nuevos comandos y para corregir su posición
    {
      if (IMPRIMIR) Serial.println(F("-------------------------ARRIVED ------------------------------"));
      llegada = 1;             
      pararadaSuave();
      rc.ResetEncoders(DIRECCION_MEMORIA_RC);   // reseteo de los encoders .....
      *direccionObjPuntero = 0;                 // reseteo de variable dirección/....
      *distanciaObjPuntero = 0.00;              // reseteo de variable distancia....
      //*modoPuntero = MODO_INACTIVO; //////// TESTING 
    }
    // Mover el robot teniendo en cuenta distancia, dirección, y obstáculos--------------------------------------------
    if (distAdesplazar > 0.00 && llegada == 0)
    {
      navegacionAutomatica(giro, distAdesplazar, modoPuntero, casoNavegacionPuntero, despPuntero);
    }
  }
  else if (modo == MODO_MANUAL)
  {
    if (distanciaSonarFI <= DISTANCIA_PARADA || distanciaSonarFD <= DISTANCIA_PARADA)
      parada(); 
    if (comando == RECIBIR_COMANDO_MANUAL)
      navegacionManual(mensaje); 
  }
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
