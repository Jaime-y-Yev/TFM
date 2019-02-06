// Funciones que directamente comunican con el controlador de motores:

void avanzarRecto(int velocidad)
{
  if (IMPRIMIR_MOTORES) {Serial.print(F("Avanzando recto a velocidad "));   Serial.println(velocidad);}
  rc.SpeedAccelM1(DIRECCION_MEMORIA_RC, ACELERACION, velocidad);
  rc.SpeedAccelM2(DIRECCION_MEMORIA_RC, ACELERACION, velocidad);
}

void avanzarIzquierda(int velocidad)
{  
  if (IMPRIMIR_MOTORES) {Serial.print(F("Avanzando izquierda a velocidad "));   Serial.println(velocidad);} 
  rc.SpeedAccelM1(DIRECCION_MEMORIA_RC, ACELERACION, velocidad*VEL_PORCENTAJE);
  rc.SpeedAccelM2(DIRECCION_MEMORIA_RC, ACELERACION, velocidad);  
}

void avanzarDerecha(int velocidad)
{
  if (IMPRIMIR_MOTORES) {Serial.print(F("Avanzando derecha a velocidad "));   Serial.println(velocidad);}
  rc.SpeedAccelM1(DIRECCION_MEMORIA_RC, ACELERACION, velocidad);
  rc.SpeedAccelM2(DIRECCION_MEMORIA_RC, ACELERACION, velocidad*VEL_PORCENTAJE); 
}

void retrocederRecto(int velocidad)
{
  if (IMPRIMIR_MOTORES) {Serial.print(F("Retrocediendo recto a velocidad "));   Serial.println(velocidad);}
  rc.SpeedAccelM1(DIRECCION_MEMORIA_RC, ACELERACION, -velocidad);
  rc.SpeedAccelM2(DIRECCION_MEMORIA_RC, ACELERACION, -velocidad);
}

void retrocederIzquierda(int velocidad)
{
  if (IMPRIMIR_MOTORES) {Serial.print(F("Retrocediendo izquierda a velocidad "));   Serial.println(velocidad);}
  int velLenta = velocidad*VEL_PORCENTAJE;
  rc.SpeedAccelM1(DIRECCION_MEMORIA_RC, ACELERACION, -velLenta);
  rc.SpeedAccelM2(DIRECCION_MEMORIA_RC, ACELERACION, -velocidad);
}

void retrocederDerecha(int velocidad)
{
  if (IMPRIMIR_MOTORES) {Serial.print(F("Retrocediendo derecha a velocidad "));   Serial.println(velocidad);}
  int velLenta = velocidad*VEL_PORCENTAJE;
  rc.SpeedAccelM1(DIRECCION_MEMORIA_RC, ACELERACION, -velocidad);
  rc.SpeedAccelM2(DIRECCION_MEMORIA_RC, ACELERACION, -velLenta);
}

void giroIzquierda(int velocidad)                 // Girar en la dirección izquierda
{
  if (IMPRIMIR_MOTORES) {Serial.print(F("Girando izquierda a velocidad "));   Serial.println(velocidad);}
  rc.SpeedAccelM1(DIRECCION_MEMORIA_RC, ACELERACION, -velocidad);
  rc.SpeedAccelM2(DIRECCION_MEMORIA_RC, ACELERACION, velocidad); 
}

void giroDerecha(int velocidad)                   // Girar en la dirección derecha
{
  if (IMPRIMIR_MOTORES) {Serial.print(F("Girando derecha a velocidad "));   Serial.println(velocidad);}
  rc.SpeedAccelM1(DIRECCION_MEMORIA_RC, ACELERACION, velocidad);
  rc.SpeedAccelM2(DIRECCION_MEMORIA_RC, ACELERACION, -velocidad);  
}

void parar(void)                                   // Parar los motores
{
  if (IMPRIMIR_MOTORES) Serial.println(F("Parando"));
  rc.SpeedAccelM1(DIRECCION_MEMORIA_RC, 2000, 0);
  rc.SpeedAccelM2(DIRECCION_MEMORIA_RC, 2000, 0); 
}

void paradaSuave(void)                                   // Parar los motores
{
  if (IMPRIMIR_MOTORES) Serial.println(F("Parando"));
  rc.SpeedAccelM1(DIRECCION_MEMORIA_RC, ACELERACION, 0);
  rc.SpeedAccelM2(DIRECCION_MEMORIA_RC, ACELERACION, 0); 
}
// Dependiendo de los comandos de la página calcular, se controla los motores con estos comandos.
// Giro refiere a dirección (derecha, izq, recta), desplazamiento refiere a movimiento (adeltante, atrás), velocidad refiere a la velocidad de desplazamiento según el comando
void activarMotores(int giro, int velocidad, int desp)
{
  if (IMPRIMIR_MOTORES) {Serial.print(F("Activando motores con giro ")); Serial.print((char)giro); Serial.print(F(" y desp ")); Serial.print(desp); Serial.println(F(" así que..."));}

  if (giro == GIRO_RECTO)
  {
    avanzarRecto(velocidad);
  }
  else if (giro == GIRO_IZQUIERDA)
  {
    if (desp == DESP_POSITIVO) 
      avanzarIzquierda(velocidad);
    else if (desp == DESP_GIRO) 
      giroIzquierda(velocidad);
  }
  else if (giro == GIRO_DERECHA)
  {   
    if (desp == DESP_POSITIVO) 
      avanzarDerecha(velocidad);
    else if (desp == DESP_GIRO) 
      giroDerecha(velocidad);
  }  
  else if (giro == GIRO_ATRAS)
  {
    retrocederRecto(velocidad);
  }
  else if (giro == GIRO_IZQUIERDA) 
  {
    if (desp == DESP_NEGATIVO) 
      retrocederIzquierda(velocidad);
    else if (desp == DESP_GIRO) 
      giroDerecha(velocidad);
  }
  else if (giro == GIRO_DERECHA)
  {
    if (desp == DESP_NEGATIVO) 
      retrocederDerecha(velocidad);
    else if (desp == DESP_GIRO) 
      giroIzquierda(velocidad);
  }
}

void leerVelocidad()
{
  uint8_t status1, status2;
  bool valid1, valid2;
  int32_t speed1 = rc.ReadSpeedM1(DIRECCION_MEMORIA_RC, &status1, &valid1);
  int32_t speed2 = rc.ReadSpeedM2(DIRECCION_MEMORIA_RC, &status2, &valid2);
  //Serial.print(F("speed1 = ")); Serial.print(speed1, DEC); Serial.print(F(" speed2 = ")); Serial.println(speed2, DEC);
}

void leerEncoders()
{
  uint8_t status1, status2;
  bool valid1, valid2;
  int32_t enc1 = rc.ReadEncM1(DIRECCION_MEMORIA_RC, &status1, &valid1);
  int32_t enc2 = rc.ReadEncM2(DIRECCION_MEMORIA_RC, &status2, &valid2);
  //Serial.print(F("enc1 = ")); Serial.print(enc1, DEC); Serial.print(F(" enc2 = ")); Serial.println(enc2, DEC);
}

void erroresMotor(void)
{
  _Bool valid;
  uint16_t estado = rc.ReadError(DIRECCION_MEMORIA_RC, &valid);
  _Bool error = false;

  if (!(estado & 0x0000)) Serial.println(F("RC Normal"));
  if (estado & 0x0001) {Serial.println(F("RC Error: Sobrecorriente M1")); error = true;} 
  if (estado & 0x0002) {Serial.println(F("RC Error: Sobrecorriente M2")); error = true;} 
  if (estado & 0x0004) {Serial.println(F("RC Error: E-stop")); error = true;} 
  if (estado & 0x0008) {Serial.println(F("RC Error: temperatura")); error = true;} 
  if (estado & 0x0010) {Serial.println(F("RC Error: temperatura 2")); error = true;} 
  if (estado & 0x0020) {Serial.println(F("RC Error: Batería principal alta")); error = true;} 
  if (estado & 0x0040) {Serial.println(F("RC Error: Batería lógica alta")); error = true;} 
  if (estado & 0x0080) {Serial.println(F("RC Error: Batería lógica baja")); error = true;} 
  if (estado & 0x0100) {Serial.println(F("RC Error: M1 driver")); error = true;} 
  if (estado & 0x0200) {Serial.println(F("RC Error: M2 driver")); error = true;} 
  if (estado & 0x0400) {Serial.println(F("RC Aviso: Batería principal alta")); error = true;} 
  if (estado & 0x0800) {Serial.println(F("RC Aviso: Batería principal baja")); error = true;} 
  if (estado & 0x1000) {Serial.println(F("RC Aviso: temperatura M1")); error = true;} 
  if (estado & 0x2000) {Serial.println(F("RC Aviso: temperatura M2")); error = true;} 
  if (estado & 0x4000) Serial.println(F("RC M1 Home")); 
  if (estado & 0x8000) Serial.println(F("RC M2 Home"));

  if (error) 
  {
    if (IMPRIMIR_MOTORES) Serial.println(F("Error motores...modo EMERGENCIA"));
    *modoPuntero = MODO_EMERGENCIA;
  }
}
void suavizarMovimiento(float v1Nueva, float v2Nueva)
{
  uint8_t status1, status2;
  bool valid1, valid2;
  int32_t speed1 = rc.ReadSpeedM1(DIRECCION_MEMORIA_RC, &status1, &valid1);
  int32_t speed2 = rc.ReadSpeedM2(DIRECCION_MEMORIA_RC, &status2, &valid2);
  
  float v1Vieja = (float)speed1;
  float v2Vieja = (float)speed2;
  if (IMPRIMIR_MOTORES) {Serial.print(F("v1Vieja ")); Serial.println(v1Vieja);}
  if (IMPRIMIR_MOTORES) {Serial.print(F("v2Vieja ")); Serial.println(v2Vieja);}
  float difv1 = v1Nueva - v1Vieja;
  float difv2 = v2Nueva - v2Vieja;
  
  if (IMPRIMIR_MOTORES) {Serial.print(F("difv1 ")); Serial.println(difv1);}
  if (IMPRIMIR_MOTORES) {Serial.print(F("difv2 ")); Serial.println(difv2);}
  float v1Temp = 0;
  float v2Temp = 0;
  int i;

  if (v1Nueva == v1Vieja)
  {
    v1Temp = v1Nueva;
  }
  if (v2Nueva == v2Vieja)
  {
    v2Temp = v2Nueva;
  }

  
  Serial.print(F("Before for loop....................................... "));
  for(i=0;i<=6;i++)
  {
    if (IMPRIMIR_MOTORES) {Serial.print(F("i: "));   Serial.println(i);}
    if (v1Nueva > v1Vieja)
    {
      v1Temp = v1Temp + difv1/7;
    }    
    else if (v1Nueva < v1Vieja)
    {
      v1Temp = v1Temp - difv1/7;
    }
    
    if (v2Nueva > v2Vieja)
    {
      v2Temp = v2Temp + difv2/7;
    }    
    else if (v2Nueva < v2Vieja)
    {
      v2Temp = v2Temp - difv2/7;
    }
    
    int v1 = (int)v1Temp;
    int v2 = (int)v2Temp;
    
    if (IMPRIMIR_MOTORES) {Serial.print(F("v1Vieja ")); Serial.println(v1Vieja); Serial.print(F("  v1Nueva ")); Serial.println(v1Nueva); Serial.print(F("  v1Temp "));   Serial.println(v1Temp);}
    if (IMPRIMIR_MOTORES) {Serial.print(F("v2Vieja ")); Serial.println(v2Vieja); Serial.print(F("  v1Nueva ")); Serial.println(v1Nueva); Serial.print(F("  v2Temp "));   Serial.println(v2Temp);}

    rc.SpeedM1(DIRECCION_MEMORIA_RC, v1);
    rc.SpeedM2(DIRECCION_MEMORIA_RC, v2);
   
  }
  
}

