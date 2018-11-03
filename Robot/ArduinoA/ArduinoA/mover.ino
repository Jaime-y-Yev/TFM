// EVITAR OBSTÁCULOS DURANTE EL DSPLAZAMIENTO

// Inicializar los variables utilizado en los próximos pasos
int desp;
int velocidad;


_Bool obstaculoAdistanciaGrande = false;
_Bool obstaculoAdistanciaMedia = false;
_Bool obstaculoAdistanciaPequena = false;
_Bool frenteAobstaculo = false;
_Bool parada = false;


void moverRobot(int giro, float distAdesplazar, int *errorPuntero)
//void moverRobot(float *distanciaSonarIPuntero,float *distanciaSonarDPuntero,float distanciaSonarFI,float *distanciaSonarFDPuntero, float *distanciaSonarAPuntero,int giro,float distAdesplazar, int *errorPuntero, int *modoPuntero)
{
    int imprimir_nav = 1;
    Serial.println();
    
    // Definir los casos posibles donde NO hay un obstáculo o está muy lejos
    if (distanciaSonarFI >= DISTANCIA_GRANDE && *distanciaSonarFDPuntero >= DISTANCIA_GRANDE)
      obstaculoAdistanciaGrande = true; //
    else if ((DISTANCIA_CORTA <= distanciaSonarFI && distanciaSonarFI < DISTANCIA_GRANDE) && (DISTANCIA_CORTA <= *distanciaSonarFDPuntero && *distanciaSonarFDPuntero < DISTANCIA_GRANDE))       // |-------------|-----------------|-------------|
      obstaculoAdistanciaMedia = true;
    
    // Definir los casos donde hay un obstáculo cerca. Aquí empieza evitación del obstáculo
    else if ((distanciaSonarFI < DISTANCIA_CORTA && distanciaSonarFI > DISTANCIA_OBSTACULO)||(*distanciaSonarFDPuntero < DISTANCIA_CORTA && *distanciaSonarFDPuntero > DISTANCIA_OBSTACULO))
      obstaculoAdistanciaPequena = true;  
    else if ((distanciaSonarFI <= DISTANCIA_OBSTACULO && distanciaSonarFI > DISTANCIA_PARADA)||(*distanciaSonarFDPuntero <= DISTANCIA_OBSTACULO && *distanciaSonarFDPuntero > DISTANCIA_PARADA))
      frenteAobstaculo = true;
    else if ((distanciaSonarFI <= DISTANCIA_PARADA)||(*distanciaSonarFDPuntero <= DISTANCIA_PARADA))
      parada = true;
      //parar();

    if (obstaculoAdistanciaGrande||obstaculoAdistanciaMedia)
      *giroPreobstaculoPuntero = giro;
      *direccionPreobstaculoPuntero = *direccionObjPuntero;



  // Decirir si el robot está entre filas
  float distanciaSonaresDI = *distanciaSonarIPuntero+*distanciaSonarDPuntero; // utilizar los valores de un sonar derecho (D) y izq (I). La suma determina la cantidad de epsacio libre alrededor => fila o no
  
  // Si el robot no está entre filas-------------------------------------------------------------------------------------------------
  if (distanciaSonaresDI >= DISTANCIA_FILA ) // CHANGE to dif value after testing
  {
//    // Caso A: No hay obstáculos-----
//    if (obstaculoAdistanciaGrande)
//    { 
//      if (imprimir_nav == 1) Serial.print("A: Obstáculo muy lejos: ");
//  
//      desp = DESP_ADELANTE;
//      
//      if (imprimir_nav == 1) Serial.print("Desplazamiento positivo, ");
//    
//      
//      if (distAdesplazar >= DISTANCIA_CORTA)       // Punto objetivo no está cerca todavía
//      {
//        velocidad = V_RAPIDA;
//        
//        if (imprimir_nav == 1) Serial.println("Velocidad rápida");
//        
//      }
//      else if (distAdesplazar < DISTANCIA_CORTA)   // Punto objetivo está cerca
//      {
//        velocidad = V_LENTA;
//        
//        if (imprimir_nav == 1) Serial.println("Velocidad lenta");   
//        
//      }
//    }
//
//    // Caso B: Hay algún obstáculo no muy lejos-----
//    else if (obstaculoAdistanciaMedia)       
//    {
//      if (imprimir_nav == 1) Serial.print("B: Obstáculo no muy lejos: ");
//
//      desp = DESP_ADELANTE;
//      
//      if (imprimir_nav == 1) Serial.print("Desplazamiento positivo, ");
//
//       
//      if (distAdesplazar >= DISTANCIA_CORTA)       // Punto objetivo no está cerca todavía
//      {
//        velocidad = V_NORMAL;
//        
//        if (imprimir_nav == 1) Serial.println("Velocidad normal");
//       
//      }
//      else if (distAdesplazar < DISTANCIA_CORTA)   // Punto objetivo está cerca
//      {          
//        velocidad = V_LENTA;
//        
//        if (imprimir_nav == 1) Serial.println("Velocidad lenta");
//        
//      }  
//    }

//    // Caso C: Empieza evitación de obstáculos. Hay un obstaculo cerca----
//    else if (obstaculoAdistanciaPequena)
//    {
//      if (imprimir_nav == 1) Serial.print("C: Obstáculo cerca! ");
//      
//      desp = DESP_ADELANTE;
//      velocidad = V_NORMAL;
//
//      if (imprimir_nav == 1) Serial.println("Girando para evitarlo ");
//      
//      
//      if (*giroPreobstaculoPuntero == RECTA) // evitar obstaculos cuando sólo quieres ir adelante
//      {
//        // Girar al lado que tiene maś espacio
//        if (*distanciaSonarDPuntero > *distanciaSonarIPuntero && *distanciaSonarDPuntero > DISTANCIA_GIRO_MIN)  // si hay espacio a la derecha, girar a la derecha
//        {
//          giro = DERECHA;
//           
//          if (imprimir_nav == 1) Serial.println("...a la derecha");        
//          
//        }
//        else if (*distanciaSonarDPuntero < *distanciaSonarIPuntero && *distanciaSonarIPuntero > DISTANCIA_GIRO_MIN) // hay espacio a la izquierda, girar a la izquierda
//        {
//          giro = IZQUIERDA;
//          
//          if (imprimir_nav == 1)  Serial.println("...a la izquierda"); 
//          
//        }
//      }
//
//      // Girar en la dirección donde hay espacio adecuado
//      if ((*giroPreobstaculoPuntero == DERECHA && *distanciaSonarDPuntero >= DISTANCIA_GIRO_MIN) || (giro == IZQUIERDA && *distanciaSonarIPuntero < DISTANCIA_GIRO_MIN && *distanciaSonarDPuntero >= DISTANCIA_GIRO_MIN)) 
//        giro = DERECHA; 
//      if ((*giroPreobstaculoPuntero == IZQUIERDA && *distanciaSonarIPuntero >= DISTANCIA_GIRO_MIN) || (giro == DERECHA && *distanciaSonarDPuntero < DISTANCIA_GIRO_MIN && *distanciaSonarIPuntero >= DISTANCIA_GIRO_MIN))
//        giro = IZQUIERDA; 
//    }

// Caso C: Empieza evitación de obstáculos. Hay un obstaculo cerca----
    if (obstaculoAdistanciaPequena) //// was else if
    {
      if (imprimir_nav == 1) Serial.print("C: Obstáculo cerca! ");

      if (imprimir_nav == 1) Serial.println("Evitándolo ");
             
      if (giroPreobstaculo == RECTA) // evitar obstaculos cuando sólo quieres ir adelante
      {
        // Girar al lado que tiene maś espacio
        if (*distanciaSonarDPuntero > *distanciaSonarIPuntero && *distanciaSonarDPuntero > DISTANCIA_GIRO_MIN)  // si hay espacio a la derecha, girar a la derecha
        {
          giro = DERECHA;
          
         if (imprimir_nav == 1) Serial.println("...más espacio a la derecha 1");                  
        }
        else if (*distanciaSonarDPuntero < *distanciaSonarIPuntero && *distanciaSonarIPuntero > DISTANCIA_GIRO_MIN) // hay espacio a la izquierda, girar a la izquierda
        {
          giro = IZQUIERDA;
          
          if (imprimir_nav == 1)  Serial.println("...más espacio a la izquierda 1"); 
          
        }
      }     
      // Girar en la dirección donde hay espacio adecuado
      if ((giro == DERECHA && *distanciaSonarDPuntero >= DISTANCIA_GIRO_MIN) || (giro == IZQUIERDA && *distanciaSonarIPuntero < DISTANCIA_GIRO_MIN && *distanciaSonarDPuntero >= DISTANCIA_GIRO_MIN)) // 
       { 
        giro = DERECHA;
        if (imprimir_nav == 1) Serial.println("...más espacio a la derecha");                  
       }
      if ((giro == IZQUIERDA && *distanciaSonarIPuntero >= DISTANCIA_GIRO_MIN) || (giro == DERECHA && *distanciaSonarDPuntero < DISTANCIA_GIRO_MIN && *distanciaSonarIPuntero >= DISTANCIA_GIRO_MIN) )
        {
        giro = IZQUIERDA; 
        if (imprimir_nav == 1) Serial.println("...más espacio a la izquierda");                  
        }
        
      // Hallar el radio de evitación
      float radio;
      if (distanciaSonarFI < *distanciaSonarFDPuntero)    
        radio = distanciaSonarFI;
      else if (distanciaSonarFI >= *distanciaSonarFDPuntero)
        radio = *distanciaSonarFDPuntero;
      if (imprimir_nav == 1) {Serial.print("radio before loop: "); Serial.println(radio);}  
  
      // Hallar el lado del robot que va a ser directamente frente de obstáculo
      char ladoSonarUtilizado;
      if (giro == DERECHA)
      {
        ladoSonarUtilizado = 'I'; 
      }
      else if (giro == IZQUIERDA)
      {
        ladoSonarUtilizado = 'D'; 
      }

      // Evitar obstáculo
      int giroPreobstaculo = *giroPreobstaculoPuntero; // REMOVE LATER
      _Bool evitarObst = false;      
      float distanciaLado;
      _Bool giroCompleto = false;
      float dif;
      float Tol; // metros
      int errorDireccion;
      velocidad = V_NORMAL;
      
      if (imprimir_nav == 1) {Serial.println("************while loop starts***********");}  

      while (true)
      {
        leerSonars();
        delay(100);
        if (imprimir_nav == 1) 
        {
          Serial.print("distanciaSonarFI = ");  Serial.println(distanciaSonarFI);
          Serial.print("distanciaSonarFD = ");  Serial.println(distanciaSonarFD);
          Serial.print("distanciaSonarD = ");  Serial.println(distanciaSonarD);   
          Serial.print("distanciaSonarI = ");  Serial.println(distanciaSonarI);   
        }
        if ((distanciaSonarFI <= DISTANCIA_PARADA)||(distanciaSonarFD <= DISTANCIA_PARADA))
        {
          parar();
          break;
        }
        
        if (evitarObst == false)
        {
          if (ladoSonarUtilizado == 'I')
          {
            distanciaLado = distanciaSonarI;
          }
          else if (ladoSonarUtilizado == 'D')
          {
            distanciaLado = distanciaSonarD;
          }

          dif = distanciaLado - radio;
          errorDireccion = 0;
          leerMagnetometro();
          float tolDistGiro = 0.3;        
          // Girar el robot sin desplazar
          if(giroCompleto == false)
          {
             if (imprimir_nav == 1)  Serial.println("orientando para estar paralelo con obstáculo.."); 
             if (imprimir_nav == 1)  {Serial.print("distanciaLado: "); Serial.print(distanciaLado);  Serial.print("  Radio: "); Serial.println(radio);}
             
             desp = DESP_GIRO;
             if (giro == IZQUIERDA)
             {
              giroIzquierda(V_NORMAL);
              Serial.println("girando...Izquierda "); 
             }
             else if (giro == DERECHA)
             {
              giroDerecha(V_NORMAL);
              Serial.println("girando...Derecha "); 
             }

             //activarMotores(giro,velocidad,desp);
             if (imprimir_nav == 1) Serial.println("ACTIVANDO MOTORES PARA GIRAR: ");
             delay(3500);
             parar();
             if (imprimir_nav == 1) Serial.println("PARADO POR 2 Seg");

             delay(2000);

             giroCompleto = true;
             
              
//             if(abs(dif) > tolDistGiro)
//             {
//              desp = DESP_GIRO;
//              activarMotores(giro,velocidad,desp); 
//              Serial.println("ACTIVANDO MOTORES: ");  
//             }
//             else if(abs(dif) <= tolDistGiro)
//             {
//              giroCompleto = true;
//             }
          }

          // Al terminar con el giro, seguir alrededor del obstáculo hasta que el robot vuelva a orientarse en su direccionObj original
          else if(giroCompleto == true)
          {
           if (imprimir_nav == 1)  Serial.println("desplazando alrededor de obstáculo.."); 
           if (imprimir_nav == 1)  Serial.print("direccionAct: "); Serial.print(*direccionActPuntero);  Serial.print("  DireccionObj: "); Serial.println(*direccionObjPuntero);
           
           errorDireccion = direccionAct - direccionObj;
           if(abs(errorDireccion) > TOL_DIRECCION)
           {
            if(-1*TOL_SONAR > dif || dif > TOL_SONAR)
            {
              if(distanciaLado < radio)
              {
                if(ladoSonarUtilizado == 'I')
                {
                  if (imprimir_nav == 1)  Serial.println("---Utilizando lado I");           
                  giro = DERECHA;
                }
                else if (ladoSonarUtilizado == 'D')
                {
                  if (imprimir_nav == 1)  Serial.println("---Utilizando lado D");           
                  giro = IZQUIERDA;
                }
              }

              else if(distanciaLado > radio)                           
              {
                if(ladoSonarUtilizado == 'I')
                {
                  if (imprimir_nav == 1)  Serial.println("---Utilizando lado I");                           
                  giro = IZQUIERDA;
                }
                else if (ladoSonarUtilizado == 'D')
                {
                  if (imprimir_nav == 1)  Serial.println("---Utilizando lado D");                           
                  giro = DERECHA;
                }
              }
              else
                giro = RECTA;
              
              if (imprimir_nav == 1)  {Serial.print("-----distanciaLado: "); Serial.print(distanciaLado);  Serial.print("  Radio: "); Serial.println(radio);}           
              // TODO ADD GIRO TO ARRAY
              if (imprimir_nav == 1)  Serial.println("Activando motores otra vez!!");
              if (imprimir_nav == 1)  {Serial.print("giro: "); Serial.print(giro); Serial.print(" Velocidad: "); Serial.println(velocidad);}
              
              desp = DESP_ADELANTE;
              velocidad =V_NORMAL;
              activarMotores(giro,velocidad,desp);
              if (imprimir_nav == 1)  Serial.print("");
              delay(300);
              
            }                      
          }
          else if(abs(errorDireccion) <= TOL_DIRECCION)
          {
            evitarObst = true;
            if (imprimir_nav == 1)  Serial.println("obstáculo evitado..");
            //parar();
            delay(2000);
            break;   
          }                                      
        }
      }
    }
  }

      //int direccionObstaculoAdistanciaPequena(char ladoSonarUtilizado) 
      if (imprimir_nav == 1)  Serial.println("FUERA DE CASO C"); 
         
  else 
  {
    parar();
    while (true)
    {
      if (imprimir_nav == 1)  Serial.println("INFINITE STOP"); 
    }
   }
  }
      
     
      


      
    


    
//    // Caso D: Hay un obstáculo al frente del robot----
//    else if (frenteAobstaculo)
//    {
//      if (imprimir_nav == 1) Serial.print("D: Al frente de obstáculo! ");
//      
//      velocidad = 0;
//      
//      if(*distanciaSonarAPuntero > DISTANCIA_PARADA)  // si hay espacio para mover atras
//      {
//        if (imprimir_nav == 1) Serial.println("Desplazando atras!");
//               
//        parar();    
//        
//        //desp = ATRAS;
//      }
//      else if(*distanciaSonarAPuntero <= DISTANCIA_PARADA) // si no hay espacio para mover atras, esperar
//      {
//        if (imprimir_nav == 1) Serial.println("D: Parado completamente. Esperando ayuda...");
//                
//        parar();
//        
//        // !!TODO send error ms back to pi
//      }        
//    }
//    
//    // Caso E: Hay un obstáculo al frente del robot----
//    else if (parada)
//    {
//      if (imprimir_nav == 1) Serial.println("E: PARADA ");
//      parar();
//    }   
//  }
//    
//  // Si el robot está entre filas-------------------------------------------------------------------------------------------------
//  if (distanciaSonaresDI < DISTANCIA_FILA )
//  {
//    if (imprimir_nav == 1) Serial.println("Navegando entre filas");
//    
//    
//    if (frenteAobstaculo == false && parada == false)             // Si el robot no está frente de obstaculo y tiene espacio para mover adelante entre filas
//    {
//      desp = DESP_ADELANTE;
//      
//      if (distAdesplazar >= DISTANCIA_CORTA)                      // Si hay mucha distancia entre nuestro punto objetivo y el robot
//      {
//        velocidad = V_NORMAL;
//        giro = direccionEntreFilas(distanciaSonarIPuntero,distanciaSonarDPuntero);
//      } 
//      else if (distAdesplazar < DISTANCIA_CORTA)                  // Si el robot casi está en su punto objetivo
//      {        
//        velocidad = V_LENTA;
//        giro = direccionEntreFilas(distanciaSonarIPuntero,distanciaSonarDPuntero);
//      }      
//    }
//    else                                                          // Frenar, esperar hasta que el obstáculo se mueve
//    {
//      if (imprimir_nav == 1) Serial.println("Stopping emergency");
//      *modoPuntero = MODO_EMERGENCIA ;
//      parar();
//      // mandar un mensaje de emergencia a PiA 
//    }
//  }
//  
//   // Utilizando giro, velocidad y dirección de desplazamiento hallado arriba, se activa los motores
//  
//  if (parada == false && obstaculoAdistanciaPequena == false)
//    activarMotores(giro,velocidad,desp); 
//        
//
//  // Se resetea las variables de condiciones
  obstaculoAdistanciaGrande = false;
  obstaculoAdistanciaMedia = false;
  obstaculoAdistanciaPequena = false;
  frenteAobstaculo = false;
  parada = false;
  giro = 0;
  distAdesplazar = 0;
  *errorPuntero = 0;
//
//
}
//
//
//
//// Mantiene el robot en la mitad de las filas útil
//int direccionEntreFilas(float *distanciaSonarIPuntero, float *distanciaSonarDPuntero) 
//{ 
//  int giro;
//  
//  float dif = *distanciaSonarIPuntero - *distanciaSonarDPuntero;
//  
//  if (-1*TOL_SONAR >  dif || dif > TOL_SONAR)                    // asegurar que la diferrencia es significativa  
//  {  
//    if (*distanciaSonarDPuntero > *distanciaSonarIPuntero)       // si hay más distancia a la derecha, mover a otra dirección
//    {
//      if (imprimir_nav == 1) Serial.println("Moviendo hacia lado I");
//       
//      giro = IZQUIERDA;
//
//    }
//    else if (*distanciaSonarDPuntero < *distanciaSonarIPuntero)  // si hay más distancia a la izquierda, mover a otra dirección
//    {
//      if (imprimir_nav == 1) Serial.println("Moviendo hacia lado D");
//        
//      giro = DERECHA;
//    }
//    else                                                          // si el robot ya esta ne la mitad de las filas, no girar
//    {
//      giro = RECTA;
//    }
//  }
//  return giro;
//  //delay(500); 
//}
//
//

