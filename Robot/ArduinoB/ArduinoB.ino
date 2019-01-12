/*
  Este Arduino se dedica sólo a conectar o desconectar la batería principal (o la pared) dependiendo del comando 
  que le llegue del mando de infrarojos. Controla la fuente mediante un relé que abre o cierra el circuito de la batería,
  los motores, y el actuador lineal.
*/

// Comandos de RPi
#include "headers/comandos.h"
char mensaje[20];
int comando;

// Modos
int modo = MODO_INACTIVO;
int *modoPuntero = &modo;

// Control remoto IR
#include <IRremote.h>
#define RECV_PIN 5              // pin del receptor IR
IRrecv irrecv(RECV_PIN);        // objeto IR
decode_results results;         // almacena resultados
//#define DESCONECTAR 0xFF6897    // botón "0" 
//#define CONECTAR 0xFF30CF       // botón "1"

// Sensor de temperatura y humedad
#include <dht.h>
dht DHT;
#define PIN_DHT11 A0
int temperatura;
int humedad;

// Interrupcion proveniente de PiB
#define PIN_INTERRUPCION_DESCONECT 2
#define PIN_INTERRUPCION_CONECT 3

#define RELE 7     // pin del trigger del relé

// Arrancar el control IR y el relé
void setup()
{
  Serial.begin(115200);

  // IR
  irrecv.enableIRIn();        // arrancar el IR
  irrecv.blink13(true);       // parpadear LED_BUILTIN al recibir un valor IR (ayuda a depurar)

  // Interrupcion
  pinMode(PIN_INTERRUPCION_DESCONECT, INPUT_PULLUP); 
  pinMode(PIN_INTERRUPCION_CONECT, INPUT_PULLUP);
  digitalWrite(PIN_INTERRUPCION_DESCONECT, LOW); // Habilitar el pullup en el pin digital 2
  digitalWrite(PIN_INTERRUPCION_CONECT, LOW); // Habilitar el pullup en el pin digital 3
  attachInterrupt(digitalPinToInterrupt(PIN_INTERRUPCION_DESCONECT), desconectarBateria, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_INTERRUPCION_CONECT), conectarBateria, RISING);

  // Relé
  pinMode(RELE, OUTPUT);      // el Arduino envía una señal de trigger al relé
  digitalWrite(RELE, LOW);    // asegurarse de empezar con la batería desconectada

  DHT.read11(PIN_DHT11);
  temperatura = DHT.temperature;
  humedad = DHT.humidity;
}


// Conectar o desconectar la batería según el comando IR que llegue
void loop()
{
  delay(300);
  
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
  
  
  DHT.read11(PIN_DHT11);

  temperatura = 0.3*temperatura + 0.7*DHT.temperature;
  humedad = 0.3*humedad + 0.7*DHT.humidity;

  //Serial.print("temperatura = "); Serial.println(DHT.temperature);
  //Serial.print("humedad = "); Serial.println(DHT.humidity);

  if (temperatura >= 45 || humedad >= 60)
  {
    //Serial.println("Exceeded temp or humidity limit");
    desconectarBateria();
    *modoPuntero = MODO_EMERGENCIA;
  }

  long nivelBateria = medirBateriaSeguridad();
  //Serial.print("nivelBateria = "); Serial.println(nivelBateria, DEC); 
  
  if (nivelBateria <= 4700)
  {
    //Serial.println("Battery low");
    desconectarBateria();
    *modoPuntero = MODO_EMERGENCIA; 
  }

  // Si llega cualquier comando IR, desconectar o conectar la bateria dependiendo de su estado actual
  if (irrecv.decode(&results))    
  {
    //Serial.print("results.value = "); Serial.println(results.value);   
    digitalWrite(RELE, !bitRead(PORTD, RELE));   // escribir el valor opuesto al estado actual del pin    
    delay(200);   // evitar doble recepcion del comando IR 

    irrecv.resume();              // preparase para recibir el siguiente valor
  }
}

void desconectarBateria(void)
{
  //Serial.println("Desconectando batería");
  digitalWrite(RELE, LOW);
}

void conectarBateria(void)
{
  //Serial.println("Conectando batería");
  digitalWrite(RELE, HIGH);
}

long medirBateriaSeguridad() 
{
  // Read 1.1V reference against AVcc
  // set the reference to Vcc and the measurement to the internal 1.1V reference
  #if defined(__AVR_ATmega32U4__) || defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__)
    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  #elif defined (__AVR_ATtiny24__) || defined(__AVR_ATtiny44__) || defined(__AVR_ATtiny84__)
    ADMUX = _BV(MUX5) | _BV(MUX0);
  #elif defined (__AVR_ATtiny25__) || defined(__AVR_ATtiny45__) || defined(__AVR_ATtiny85__)
    ADMUX = _BV(MUX3) | _BV(MUX2);
  #else
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  #endif  

  delay(2); // Wait for Vref to settle
  ADCSRA |= _BV(ADSC); // Start conversion
  while (bit_is_set(ADCSRA,ADSC)); // measuring

  uint8_t low  = ADCL; // must read ADCL first - it then locks ADCH  
  uint8_t high = ADCH; // unlocks both

  long result = (high<<8) | low;

  result = 1125300L / result; // Calculate Vcc (in mV); 1125300 = 1.1*1023*1000
  return result; // Vcc in millivolts
}

// Convertir array a float
float convertirAfloat(char mensaje[], int numDigitos, int comienzoMensaje)
{
  int i;
  char vector[20];   // crear un array con la longitúd del mensaje

  // En un bucle, añadir el mensaje en el array
  for (i = 0; i <= numDigitos; i++) 
    vector[i] = mensaje[i + comienzoMensaje];
  vector[i] = '\0';                // utilizar el cáracter de terminación saber donde termina el mensaje

  return atof(vector);             // devolver el mensaje en formato float
}
