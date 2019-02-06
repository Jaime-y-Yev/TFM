// Leer el magnetometro para obtener la dirección actual del robot
void leerMagnetometro()
{
  //delay(5);
  lsm.read();

  float direccionActMagnetometro = atan2((int)lsm.magData.x, (int)lsm.magData.y);

  direccionActMagnetometro += ANGULO_DEC;                             // ajustar los valores según la ubicación física del robot (ubicación = Madrid, España en este caso)

  // Asegurar que la dirección es entre 0 a 360 grados
  if (direccionActMagnetometro > 2*PI)              
    direccionActMagnetometro -= 2*PI;
  if (direccionActMagnetometro < 0)
    direccionActMagnetometro += 2*PI;

  direccionActMagnetometro = direccionActMagnetometro * 180 / M_PI;   // convertir de radianes a grados 

  *direccionActPuntero = (int)direccionActMagnetometro;

  if (IMPRIMIR_MAG) {Serial.print(F("direccionAct = ")); Serial.println(direccionAct);}
}


// Calcular cuanto el robot tiene que girar para desplazar en la dirección obj
int calcularGiro()
{
  // Obtener el valor de giro preliminar
  int errorDireccion = direccionObj - direccionAct;
  if (IMPRIMIR) {Serial.print(F("errorDireccion: ")); Serial.println(errorDireccion);} 

  int giro;
  // Si la dirección está dentro de una tolerancia, el robot no gira
  if (abs(errorDireccion) <= TOL_DIRECCION)    
    giro = GIRO_RECTO;
  // Si la dirección no está dentro de una tolerancia elegir la dirección del giro 
  else if (abs(errorDireccion) > TOL_DIRECCION) 
  {
    if (errorDireccion < 0)
    {
      if (abs(errorDireccion) >= 180)
        giro = GIRO_IZQUIERDA;

      else if (abs(errorDireccion) < 180)
        giro = GIRO_DERECHA;
    }
    else if (errorDireccion > 0)
    {
      if (errorDireccion >= 180)
        giro = GIRO_DERECHA;

      else if (errorDireccion < 180)
        giro = GIRO_IZQUIERDA;
    }
  }
  
  // Devolver la dirección 
  return giro;
}
