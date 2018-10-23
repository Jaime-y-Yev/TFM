// EVITAR OBSTÁCULOS DURANTE EL DSPLAZAMIENTO

// Inicializar los variables utilizado en los próximos pasos
int desp;
int velocidad;


_Bool obstaculoAdistanciaGrande = false;
_Bool obstaculoAdistanciaMedia = false;
_Bool obstaculoAdistanciaPequena = false;
_Bool frenteAobstaculo = false;
_Bool parada = false;



void moverRobot(float *distanciaSonarIPuntero,float *distanciaSonarDPuntero,float *distanciaSonarFIPuntero,float *distanciaSonarFDPuntero, float *distanciaSonarAPuntero,int giro,float distAdesplazar, int *errorPuntero, int *modoPuntero)
{
    // Definir los casos posibles donde NO hay un obstáculo o está muy lejos
    if (*distanciaSonarFIPuntero >= DISTANCIA_GRANDE && *distanciaSonarFDPuntero >= DISTANCIA_GRANDE)
      obstaculoAdistanciaGrande = true; //
    else if ((DISTANCIA_CORTA <= *distanciaSonarFIPuntero && *distanciaSonarFIPuntero < DISTANCIA_GRANDE) && (DISTANCIA_CORTA <= *distanciaSonarFDPuntero && *distanciaSonarFDPuntero < DISTANCIA_GRANDE))       // |-------------|-----------------|-------------|
      obstaculoAdistanciaMedia = true;
    
    // Definir los casos donde hay un obstáculo cerca. Aquí empieza evitación del obstáculo
    else if ((*distanciaSonarFIPuntero < DISTANCIA_CORTA && *distanciaSonarFIPuntero > DISTANCIA_OBSTACULO)||(*distanciaSonarFDPuntero < DISTANCIA_CORTA && *distanciaSonarFDPuntero > DISTANCIA_OBSTACULO))
      obstaculoAdistanciaPequena = true;  
    else if ((*distanciaSonarFIPuntero <= DISTANCIA_OBSTACULO && *distanciaSonarFIPuntero > DISTANCIA_PARADA)||(*distanciaSonarFDPuntero <= DISTANCIA_OBSTACULO && *distanciaSonarFDPuntero > DISTANCIA_PARADA))
      frenteAobstaculo = true;
    else if ((*distanciaSonarFIPuntero <= DISTANCIA_PARADA)||(*distanciaSonarFDPuntero <= DISTANCIA_PARADA))
      parada = true;
  

  // Decirir si el robot está entre filas
  float distanciaSonaresDI = *distanciaSonarIPuntero+*distanciaSonarDPuntero; // utilizar los valores de un sonar derecho (D) y izq (I). La suma determina la cantidad de epsacio libre alrededor => fila o no
  
  // Si el robot no está entre filas-------------------------------------------------------------------------------------------------
  if (distanciaSonaresDI >= DISTANCIA_FILA ) // CHANGE to dif value after testing
  {
    // Caso A: No hay obstáculos-----
    if (obstaculoAdistanciaGrande)
    { 
      if (imprimir_nav == 1)
      {
        Serial.println("A: Obstáculo muy lejos: ");
      }
      
      desp = DESP_ADELANTE;
      
      if (imprimir_nav == 1)
      {
        Serial.print("Desplazamiento positivo, ");
      }
      
      if (distAdesplazar >= DISTANCIA_CORTA)       // Punto objetivo no está cerca todavía
      {
        velocidad = V_RAPIDA;
        
        if (imprimir_nav == 1)
        {
          Serial.println("Velocidad rápida");
        }
      }
      else if (distAdesplazar < DISTANCIA_CORTA)   // Punto objetivo está cerca
      {
        velocidad = V_LENTA;
        
        if (imprimir_nav == 1)
        {
          Serial.println("Velocidad lenta");
        }
      }
    }

    // Caso B: Hay algún obstáculo no muy lejos-----
    if (obstaculoAdistanciaMedia)       
    {
      if (imprimir_nav == 1)
      {
        Serial.println("B: Obstáculo no muy lejos: ");
      }
      
      desp = DESP_ADELANTE;
      
      if (imprimir_nav == 1)
      {
        Serial.print("Desplazamiento positivo, ");
      }
      
      if (distAdesplazar >= DISTANCIA_CORTA)       // Punto objetivo no está cerca todavía
      {
        velocidad = V_NORMAL;
        
        if (imprimir_nav == 1)
        {
          Serial.println("Velocidad normal");
        }
      }
      else if (distAdesplazar < DISTANCIA_CORTA)   // Punto objetivo está cerca
      {  
        
        velocidad = V_LENTA;
        
        if (imprimir_nav == 1)
        {
          Serial.println("Velocidad lenta");
        }
      }  
    }

    // Caso C: Empieza evitación de obstáculos. Hay un obstaculo cerca----
    if (obstaculoAdistanciaPequena)
    {
      if (imprimir_nav == 1)
      {
        Serial.println("C: Obstáculo cerca! ");
      }
      
      desp = DESP_ADELANTE;
      velocidad = V_LENTA;

      if (imprimir_nav == 1)
      {
        Serial.print("Girando para evitarlo ");
      }
      
      if (giro == RECTA) // evitar obstaculos cuando sólo quieres ir adelante
      {
        // Girar al lado que tiene maś espacio
        if (*distanciaSonarDPuntero > *distanciaSonarIPuntero && *distanciaSonarDPuntero > DISTANCIA_GIRO_MIN)  // si hay espacio a la derecha, girar a la derecha
        {
          giro = DERECHA;
           
          if (imprimir_nav == 1)
          {
            Serial.print("...a la derecha"); 
          }
        }
        if (*distanciaSonarDPuntero < *distanciaSonarIPuntero && *distanciaSonarIPuntero > DISTANCIA_GIRO_MIN) // hay espacio a la izquierda, girar a la izquierda
        {
          giro = IZQUIERDA;
          
          if (imprimir_nav == 1)
          { 
            Serial.print("...a la izquierda"); 
          }
        }
      }

      // Girar en la dirección donde hay espacio adecuado
      if ((giro == DERECHA && *distanciaSonarDPuntero >= DISTANCIA_GIRO_MIN) || (giro == IZQUIERDA && *distanciaSonarIPuntero < DISTANCIA_GIRO_MIN && *distanciaSonarDPuntero >= DISTANCIA_GIRO_MIN)) 
        giro = DERECHA; 
      if ((giro == IZQUIERDA && *distanciaSonarIPuntero >= DISTANCIA_GIRO_MIN) || (giro == DERECHA && *distanciaSonarDPuntero < DISTANCIA_GIRO_MIN && *distanciaSonarIPuntero >= DISTANCIA_GIRO_MIN))
        giro = IZQUIERDA; 
    }

    
    // Caso D: Hay un obstáculo al frente del robot----
    if (frenteAobstaculo)
    {
      if (imprimir_nav == 1)
      { 
        Serial.println("D: Al frente de obstáculo! ");
      }
      
      velocidad = V_LENTA;
      
      if(*distanciaSonarAPuntero > DISTANCIA_PARADA)  // si hay espacio para mover atras
      {
        if (imprimir_nav == 1)
        { 
          Serial.print("Desplazando atras!");
        }
        
        parar();    
        
        desp = ATRAS;
      }
      if(*distanciaSonarAPuntero <= DISTANCIA_PARADA) // si no hay espacio para mover atras, esperar
      {
        if (imprimir_nav == 1)
        {
          Serial.print("D: Parado completamente. Esperando ayuda...");
        }
        
        parar();
//        delay(5000);
        
        // !!TODO send error ms back to pi
      }
        
    }
  }
    
  // Si el robot está entre filas-------------------------------------------------------------------------------------------------
  if (distanciaSonaresDI < DISTANCIA_FILA )
  {
    if (imprimir_nav == 1)
    {
      Serial.println("Navegando entre filas");
    }
    
    if (frenteAobstaculo == false && parada == false)             // Si el robot no está frente de obstaculo y tiene espacio para mover adelante entre filas
    {
      desp = DESP_ADELANTE;
      
      if (distAdesplazar >= DISTANCIA_CORTA)                      // Si hay mucha distancia entre nuestro punto objetivo y el robot
      {
        velocidad = V_NORMAL;
        giro = direccionEntreFilas(distanciaSonarIPuntero,distanciaSonarDPuntero);
      } 
      else if (distAdesplazar < DISTANCIA_CORTA)                  // Si el robot casi está en su punto objetivo
      {        
        velocidad = V_LENTA;
        giro = direccionEntreFilas(distanciaSonarIPuntero,distanciaSonarDPuntero);
      }      
    }
    else                                                          // Frenar, esperar hasta que el obstáculo se mueve
    {
      giro = PARAR;
      *modoPuntero = MODO_EMERGENCIA                              // mandar un mensaje de emergencia a PiA 
    }
  }

  // Utilizando giro, velocidad y dirección de desplazamiento hallado arriba, se activa los motores
  activarMotores(giro,velocidad,desp);              

  // Se resetea las variables de condiciones
  obstaculoAdistanciaGrande = false;
  obstaculoAdistanciaMedia = false;
  obstaculoAdistanciaPequena = false;
  frenteAobstaculo = false;

}


// Mantiene el robot en la mitad de las filas útil
int direccionEntreFilas(float *distanciaSonarIPuntero, float *distanciaSonarDPuntero) 
{ 
  int giro;
  
  float dif = *distanciaSonarIPuntero - *distanciaSonarDPuntero;
  
  if (-1*TOL_SONAR >  dif || dif > TOL_SONAR)                    // asegurar que la diferrencia es significativa  
  {  
    if (*distanciaSonarDPuntero > *distanciaSonarIPuntero)       // si hay más distancia a la derecha, mover a otra dirección
    {
        if (imprimir_nav == 1)
        {
          Serial.println("Moviendo hacia lado I");
        }
        giro = IZQUIERDA;

    }
    else if (*distanciaSonarDPuntero < *distanciaSonarIPuntero)  // si hay más distancia a la izquierda, mover a otra dirección
    {
        if (imprimir_nav == 1)
        {
          Serial.println("Moviendo hacia lado D");
        }
        giro = DERECHA;
    }
    else                                                          // si el robot ya esta ne la mitad de las filas, no girar
    {
      giro = RECTA;
    }
  }
  return giro;
  //delay(500); 
}

