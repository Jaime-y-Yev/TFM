// Leer un sonar, aplicando sus propias variables calibradas y definidas antes del setup
void calcularDistanciaSonar(int trig, int echo, float m, float b, float *distanciaSonarPuntero)
{
  float distancia = -0.1;
  while (distancia < 0.0)                   // al arrancar el robot, evitar el valor por defecto de los sonares
  {
    digitalWrite(trig, LOW);
    delayMicroseconds(2);
    digitalWrite(trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig,LOW);
    delayMicroseconds(15);

    float duracion = pulseIn(echo, HIGH);
    //distancia = (m * duracion + b) ;   // dividimos entre 100 para convertir cm a m
    distancia = (m * duracion + b) / 100;   // dividimos entre 100 para convertir cm a m (MINISIMULACION)

  } 

  *distanciaSonarPuntero = distancia;  
}

// Leer los siete sonares
void leerSonars()
{
  calcularDistanciaSonar(TRIG_FI, ECHO_FI, M_FI, B_FI, distanciaSonarFIPuntero);
  if (IMPRIMIR_SONARS) {Serial.print(F("distanciaSonarFI = "));  Serial.println(distanciaSonarFI);}
  delay(10);
  
  calcularDistanciaSonar(TRIG_FD, ECHO_FD, M_FD, B_FD, distanciaSonarFDPuntero);
  if (IMPRIMIR_SONARS) {Serial.print(F("distanciaSonarFD = "));  Serial.println(distanciaSonarFD);}
  delay(10);

  calcularDistanciaSonar(TRIG_I1, ECHO_I1, M_I1, B_I1, distanciaSonarI1Puntero);
  if (IMPRIMIR_SONARS) {Serial.print(F("distanciaSonarI1 = "));  Serial.println(distanciaSonarI1);}  
  delay(10);
  
  calcularDistanciaSonar(TRIG_I2, ECHO_I2, M_I2, B_I2, distanciaSonarI2Puntero);
  if (IMPRIMIR_SONARS) {Serial.print(F("distanciaSonarI2 = "));  Serial.println(distanciaSonarI2);}  
  delay(10);
   
  calcularDistanciaSonar(TRIG_D1, ECHO_D1, M_D1, B_D1, distanciaSonarD1Puntero);
  if (IMPRIMIR_SONARS) {Serial.print(F("distanciaSonarD1 = "));  Serial.println(distanciaSonarD1);}
  delay(10);
  
  calcularDistanciaSonar(TRIG_D2, ECHO_D2, M_D2, B_D2, distanciaSonarD2Puntero);
  if (IMPRIMIR_SONARS) {Serial.print(F("distanciaSonarD2 = "));  Serial.println(distanciaSonarD2);}
  delay(10);
  
  calcularDistanciaSonar(TRIG_A, ECHO_A, M_A, B_A, distanciaSonarAPuntero);
  if (IMPRIMIR_SONARS) {Serial.print(F("distanciaSonarA = "));  Serial.println(distanciaSonarA);}
}

// Calcular la distancia desplazada por el robot utilizando los encoders
void calcularDistanciaAct()
{
  uint8_t status1;
  bool valid1;
  int32_t enc1 = rc.ReadEncM1(DIRECCION_MEMORIA_RC, &status1, &valid1);

  uint8_t status2;
  bool valid2;
  int32_t enc2 = rc.ReadEncM2(DIRECCION_MEMORIA_RC, &status2, &valid2);

  //Serial.print(F("enc1 = ")); Serial.print(enc1, DEC); Serial.print(F(" enc2 = ")); Serial.println(enc2, DEC);

  float distancia1 = enc1 * RATIO_DIST_ENCODER_1 / 100;    // Se divide entre 100 para convertir cm a m
  float distancia2 = enc2 * RATIO_DIST_ENCODER_2 / 100;    // Se divide entre 100 para convertir cm a m

  *distanciaActPuntero = (distancia1 + distancia2) / 2;    
}
