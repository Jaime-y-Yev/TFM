/*
  Este Arduino se dedica sólo a conectar o desconectar la batería principal (o la pared) dependiendo del comando 
  que le llegue del mando de infrarojos. Controla la fuente mediante un relé que abre o cierra el circuito de la batería,
  los motores, y el actuador lineal.
*/

#include <IRremote.h>

// Control remoto IR
#define RECV_PIN 5              // pin del receptor IR
IRrecv irrecv(RECV_PIN);        // objeto IR
decode_results results;         // almacena resultados
unsigned long key_value = 0;    // valor recibido
#define DESCONECTAR 0xFF6897    // botón "0" 
#define CONECTAR 0xFF30CF       // botón "1"

#define RELE 7     // pin del trigger del relé

// Arrancar el control IR y el relé
void setup()
{
  Serial.begin(9600);

  // IR
  irrecv.enableIRIn();        // arrancar el IR
  irrecv.blink13(true);       // parpadear LED_BUILTIN al recibir un valor IR (ayuda a depurar)

  // Relé
  pinMode(RELE, OUTPUT);      // el Arduino envía una señal de trigger al relé
  digitalWrite(RELE, LOW);    // asegurarse de empezar con la batería desconectada
}

// Conectar o desconectar la batería según el comando IR que llegue
void loop()
{
  if (irrecv.decode(&results))    // si llega un valor por IR
  {
    if (results.value == 0XFFFFFFFF) results.value = key_value;     // para evitar repetición del valor
  
    switch(results.value)     // valor recibido por el IR
    {
      // Desconectar la batería
      case DESCONECTAR:                    
        Serial.println("0");
        digitalWrite(RELE, LOW);   
        break;
      
      // Conectar la batería  
      case CONECTAR:
        Serial.println("1");
        digitalWrite(RELE, HIGH);   
        break;      
    }
    
    key_value = results.value;                                      // para evitar repetición del valor
    irrecv.resume();          // recibir el siguiente valor
  }
}
