// CONTROLAR LOS MOTORES DEL ROBOT UTILIZANDO COMANDOS OBTENIDOS EN LA PÁGINA DE LEER----------------------------------

// Funciones que directamente comunican con el controlador de motores:

void avanzar(int velocidad1, int velocidad2)      // Avanzar recto, avanzar izquierda, avanzar derecha
{
  rc.ForwardM1(DIRECCION_MEMORIA_RC,velocidad1);
  rc.ForwardM2(DIRECCION_MEMORIA_RC,velocidad2); 
}

void retroceder(int velocidad1, int velocidad2)   // Retroceder recto, retroceder izquierda, retroceder derecha
{
  rc.BackwardM1(DIRECCION_MEMORIA_RC,velocidad1);
  rc.BackwardM2(DIRECCION_MEMORIA_RC,velocidad2);  
}

void giroIzquierda(int velocidad)                 // Girar en la dirección izquierda
{
  rc.BackwardM1(DIRECCION_MEMORIA_RC,velocidad);
  rc.ForwardM2(DIRECCION_MEMORIA_RC,velocidad);  
}

void giroDerecha(int velocidad)                   // Girar en la dirección derecha
{
  rc.ForwardM1(DIRECCION_MEMORIA_RC,velocidad);
  rc.BackwardM2(DIRECCION_MEMORIA_RC,velocidad);  
}

void parar(void)                                   // Parar los motores
{
  avanzar(0, 0);
}


// Funciones que convierten comandos simples utilizando las funciones anteriores:

void avanzarRecto(int velocidad)
{
  avanzar(velocidad, velocidad);
}

void retrocederRecto(int velocidad)
{
  retroceder(velocidad, velocidad);
}

void avanzarIzquierda(int velocidad)
{
  avanzar(velocidad*PORCENTAJE, velocidad);
}

void avanzarDerecha(int velocidad)
{
  avanzar(velocidad, velocidad*PORCENTAJE); 
}

void retrocederIzquierda(int velocidad)
{
  retroceder(velocidad*PORCENTAJE, velocidad);
}

void retrocederDerecha(int velocidad)
{
  retroceder(velocidad, velocidad*PORCENTAJE);
}

// Dependiendo de los comandos de la página calcular, se controla los motores con estos comandos.
// Giro refiere a dirección (derecha, izq, recta), desplazamiento refiere a movimiento (adeltante, atrás), velocidad refiere a la velocidad de desplazamiento según el comando
void activarMotores(int giro,int velocidad, int desp)
{
  if (giro == RECTA)
  {
    avanzarRecto(velocidad);
//    Serial.println("Avanzando recto");
  }
  else if (giro == IZQUIERDA)
  {
    if (desp == DESP_ADELANTE)
    {
      avanzarIzquierda(velocidad);
//      Serial.println("Avanzando izquierda");
    }
    else if (desp == DESP_GIRO)
    {
      giroIzquierda(velocidad);
//      Serial.println("Girando izquierda");
    }
  }
  else if (giro == DERECHA)
  {
    if (desp == DESP_ADELANTE)
    {
      avanzarDerecha(velocidad);
//      Serial.println("Avanzando derecha");
    }
    else if (desp == DESP_GIRO)
    {
      giroDerecha(velocidad);
//      Serial.println("Girando derecha");
    }
  }  
  else if (giro == ATRAS)
  {
    retrocederRecto(velocidad);
//    Serial.println("Retrocediendo recto");
  }
  else if (giro == ATRAS_IZQUIERDA) 
  {
    if (desp == DESP_ATRAS)
    {
      retrocederIzquierda(velocidad);
//      Serial.println("Retrocediendo izquierda");
    }
    else if (desp == DESP_GIRO)
    {
      giroDerecha(velocidad);//
//      Serial.println("Girando y retrocediendo izquierda");
    }
  }
  else if (giro == ATRAS_DERECHA)
  {
    if (desp == DESP_ATRAS)
    {
      retrocederDerecha(velocidad);
//      Serial.println("Retrocediendo derecha");
    }
    else if (desp == DESP_GIRO)
    {
      giroIzquierda(velocidad); //
//      Serial.println("Girando y retrocediendo derecha");
    }
  }
  
}









