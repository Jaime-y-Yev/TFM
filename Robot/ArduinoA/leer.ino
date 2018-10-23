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
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  float duracion = pulseIn(echo, HIGH);

  *distanciaSonarPuntero = (m * duracion + b) / 100;  // Dividimos entre 100 para convertir cm a m
}

void leerSonars()
{
  calcularDistanciaSonar(TRIGFI, ECHOFI, M_SONARFI, B_SONARFI, distanciaSonarFIPuntero);
  calcularDistanciaSonar(TRIGFD, ECHOFD, M_SONARFD, B_SONARFD, distanciaSonarFDPuntero);
  calcularDistanciaSonar(TRIGI, ECHOI, M_SONARI, B_SONARI, distanciaSonarIPuntero);
  calcularDistanciaSonar(TRIGD, ECHOD, M_SONARD, B_SONARD, distanciaSonarDPuntero);
  calcularDistanciaSonar(TRIGA, ECHOA, M_SONARA, B_SONARA, distanciaSonarAPuntero);

}
// Calcular la distancia desplazada por el robot utilizando los encoders
void calcularDistanciaAct(float *distanciaActPuntero)
{
  uint8_t status1;
  bool valid1;
  int32_t enc1 = rc.ReadEncM1(DIRECCION_MEMORIA_RC, &status1, &valid1);

  *distanciaActPuntero = enc1 * RATIO_ENCODER_DISTANCIA / 100;    // Se divide entre 100 para convertir cm a m
}




