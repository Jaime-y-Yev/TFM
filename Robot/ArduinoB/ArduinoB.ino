/*
  Este Arduino se dedica sólo a conectar o desconectar la batería principal (o la pared) dependiendo del comando 
  que le llegue del mando de infrarojos. Controla la fuente mediante un relé que abre o cierra el circuito de la batería,
  los motores, y el actuador lineal.
*/

//#include "comandos.h"

// Modos
//int modo = MODO_INACTIVO;
//int *modoPuntero = &modo;

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

// Interrupcion proveniente de PiB
//#define PIN_INTERRUPCION 2
#define PIN_INTERRUPCION1 2
#define PIN_INTERRUPCION2 3

#define RELE 7     // pin del trigger del relé

// Arrancar el control IR y el relé
void setup()
{
  Serial.begin(9600);

  // IR
  irrecv.enableIRIn();        // arrancar el IR
  irrecv.blink13(true);       // parpadear LED_BUILTIN al recibir un valor IR (ayuda a depurar)

  // Interrupcion
  //pinMode(PIN_INTERRUPCION, INPUT_PULLUP);
  //attachInterrupt(digitalPinToInterrupt(PIN_INTERRUPCION), alternarRele, RISING);

  /*
  pinMode(PIN_INTERRUPCION1, INPUT_PULLUP); 
  pinMode(PIN_INTERRUPCION2, INPUT_PULLUP);
  digitalWrite(PIN_INTERRUPCION1, HIGH); // Enable pullup on digital pin 2, interrupt pin 0
  digitalWrite(PIN_INTERRUPCION2, HIGH); // Enable pullup on digital pin 2, interrupt pin 0
  attachInterrupt(digitalPinToInterrupt(PIN_INTERRUPCION1), desconectarBateria, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_INTERRUPCION2), conectarBateria, RISING);
  */

  // Relé
  pinMode(RELE, OUTPUT);      // el Arduino envía una señal de trigger al relé
  digitalWrite(RELE, LOW);    // asegurarse de empezar con la batería desconectada
}

// Conectar o desconectar la batería según el comando IR que llegue
void loop()
{
  delay(300);

  DHT.read11(PIN_DHT11);

  Serial.print("temperatura = "); Serial.println(DHT.temperature);
  Serial.print("humedad = "); Serial.println(DHT.humidity);

  if (DHT.temperature >= 400 || DHT.humidity >= 800)
  {
    Serial.println("Exceeded temp or humidity limit");
    desconectarBateria();
    //*modoPuntero = MODO_EMERGENCIA;
  }

  long nivelBateria = medirBateriaSeguridad();
  Serial.print("nivelBateria = "); Serial.println(nivelBateria, DEC); 
  
  if (nivelBateria <= 4700)
  {
    Serial.println("Battery low");
    desconectarBateria();
    //*modoPuntero = MODO_EMERGENCIA; 
  }

  // Si llega cualquier comando IR, desconectar o conectar la bateria dependiendo de su estado actual
  if (irrecv.decode(&results))    
  {   
    digitalWrite(RELE, !bitRead(PORTD, RELE));   // escribir el valor opuesto al estado actual del pin    
    delay(200);   // evitar doble recepcion del comando IR 

    irrecv.resume();              // preparase para recibir el siguiente valor
  }
}

void desconectarBateria(void)
{
  digitalWrite(RELE, LOW);
}

void conectarBateria(void)
{
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
