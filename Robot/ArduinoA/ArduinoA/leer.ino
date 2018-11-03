//  PROCESAR LOS VALORES PRODUCIDOS POR LOS SENSORES DE ARDUINO A

// DIRECCIÓN---------------------------------------------------------------------------------------------------------

// Leer el magnetometro para obtener la dirección actual del robot
void leerMagnetometro()
{
  delay(5);
  lsm.read();

  float direccionActMagnetometro = atan2((int)lsm.magData.x, (int)lsm.magData.y);

  direccionActMagnetometro += ANGULO_DEC;                          // ajustar los valores según la ubicación física del robot (ubicación = Madrid, España en este caso)

  if (direccionActMagnetometro > 2 * PI)                           // asegurar que la dirección es entre 0 a 360 grados
    direccionActMagnetometro -= 2 * PI;
  if (direccionActMagnetometro < 0)
    direccionActMagnetometro += 2 * PI;

  direccionActMagnetometro = direccionActMagnetometro * 180 / M_PI; // convertir de radianes a grados 

  *direccionActPuntero = (int)direccionActMagnetometro;
}

// Calcular cuanto el robot tiene que girar para desplazar en la dirección obj
int calcularGiro()
{
  int giro;

  // Obtener el valor de giro preliminar
  *errorDireccionPuntero = *direccionObjPuntero - *direccionActPuntero; 
  
  // Ajustar el valor preliminar para obtener un valor entre 0 a 360
      if (errorDireccion < -180)
        errorDireccion += 360;
      if (errorDireccion > 180)
        errorDireccion -= 360;

  char direccion;

  // Si la dirección está dentro de una tolerancia, le robot no gira
  if (abs(errorDireccion) <= TOL_DIRECCION)    
    giro = RECTA;

  // Si la dirección no está dentro de una tolerancia elegir la dirección del giro 
  else if (abs(errorDireccion) > TOL_DIRECCION) 
  {
    if (errorDireccion< 0)
    {
      if (errorDireccion >= 180)
        giro = DERECHA;

      else if (errorDireccion < 180)
        giro = IZQUIERDA;
    }
    else if (errorDireccion > 0)
    {
      if (errorDireccion >= 180)
        giro = IZQUIERDA;

      else if (errorDireccion < 180)
        giro = DERECHA;
    }
  }
  // Devolver la dirección 
  return giro;
}


// DISTANCIA---------------------------------------------------------------------------------------------

// Leer los sonares, aplicando sus propias  variables calibradas y definidas antes del setup
void calcularDistanciaSonar(int trig, int echo, float m, float b, float *distanciaSonarPuntero)
{
  float distancia = -0.1;
  while (distancia < 0.0)
  {
    //if ()
    //{
      digitalWrite(trig, LOW);
      delayMicroseconds(2);
      digitalWrite(trig, HIGH);
      delayMicroseconds(10);
      digitalWrite(trig,LOW);
      delayMicroseconds(15);

      float duracion = pulseIn(echo, HIGH);
      distancia = (m * duracion + b) / 100;
    //}
  } 

  *distanciaSonarPuntero = distancia;  // Dividimos entre 100 para convertir cm a m
}

void leerSonars()
{
  calcularDistanciaSonar(TRIGFI, ECHOFI, M_SONARFI, B_SONARFI, distanciaSonarFIPuntero);
  delay(10);
  calcularDistanciaSonar(TRIGFD, ECHOFD, M_SONARFD, B_SONARFD, distanciaSonarFDPuntero);
  delay(10);
  calcularDistanciaSonar(TRIGI, ECHOI, M_SONARI, B_SONARI, distanciaSonarIPuntero);
  delay(10);
  calcularDistanciaSonar(TRIGD, ECHOD, M_SONARD, B_SONARD, distanciaSonarDPuntero);
  delay(10);
  calcularDistanciaSonar(TRIGA, ECHOA, M_SONARA, B_SONARA, distanciaSonarAPuntero);

}
// Calcular la distancia desplazada por el robot utilizando los encoders
void calcularDistanciaAct(float *distanciaActPuntero)
{
  uint8_t status1;
  bool valid1;
  int32_t enc1 = rc.ReadEncM1(DIRECCION_MEMORIA_RC, &status1, &valid1);

  uint8_t status2;
  bool valid2;
  int32_t enc2 = rc.ReadEncM2(DIRECCION_MEMORIA_RC, &status2, &valid2);

  float distancia1 = enc1 * RATIO_DIST_ENCODER_1 / 100;    // Se divide entre 100 para convertir cm a m
  float distancia2 = enc2 * RATIO_DIST_ENCODER_2 / 100;    // Se divide entre 100 para convertir cm a m


  *distanciaActPuntero = (distancia1 + distancia2) / 2;    // Se divide entre 100 para convertir cm a m
}


void displayspeed(void)
{
  uint8_t status1,status2,status3,status4;
  bool valid1,valid2,valid3,valid4;
  
  int32_t enc1= rc.ReadEncM1(DIRECCION_MEMORIA_RC, &status1, &valid1);
  int32_t enc2 = rc.ReadEncM2(DIRECCION_MEMORIA_RC, &status2, &valid2);
  int32_t speed1 = rc.ReadSpeedM1(DIRECCION_MEMORIA_RC, &status3, &valid3);
  int32_t speed2 = rc.ReadSpeedM2(DIRECCION_MEMORIA_RC, &status4, &valid4);
  Serial.print("Encoder1:");
  if(valid1){
    Serial.print(enc1);
    Serial.print(" ");
    Serial.print(status1,HEX);
    Serial.print(" ");
  }
  else{
    Serial.print("invalid ");
  }
  Serial.print("Encoder2:");
  if(valid2){
    Serial.print(enc2);
    Serial.print(" ");
    Serial.print(status2,HEX);
    Serial.print(" ");
  }
  else{
    Serial.print("invalid ");
  }
  Serial.print("Speed1:");
  if(valid3){
    Serial.print(speed1);
    Serial.print(" ");
  }
  else{
    Serial.print("invalid ");
  }
  Serial.print("Speed2:");
  if(valid4){
    Serial.print(speed2);
    Serial.print(" ");
  }
  else{
    Serial.print("invalid ");
  }
  Serial.println();
}

