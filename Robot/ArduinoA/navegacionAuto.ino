// Distingue el sub-caso de navegación (evitando obstáculos según el caso), para entregarle el giro, velocidad, y desplazamiento a los motores
void navegacionAutomatica(int giro, float distAdesplazar, int *modoPuntero, int *casoNavegacionPuntero, int *despPuntero) //  REMOVE PUNTEROS AFTER TESTING??????
{ 
  if (IMPRIMIR_NAV) Serial.println(F("--- MOVER ROBOT ---"));

  _Bool casoDesconocido = false;
  // Si el robot NO tiene un margen seguro en frente o a sus lados 
  if (distanciaSonarFI <= DISTANCIA_PARADA || distanciaSonarFD <= DISTANCIA_PARADA || 
      distanciaSonarI1 <= DISTANCIA_LADO_DIAGONAL_SEGURO || distanciaSonarI2 <= DISTANCIA_LADO_SEGURO ||
      distanciaSonarD1 <= DISTANCIA_LADO_DIAGONAL_SEGURO || distanciaSonarD2 <= DISTANCIA_LADO_SEGURO)
  {
    // Caso A: Si el robot se encuentra al OBSTÁCULO DE FRENTE demasiado cerca, parar
    if (distanciaSonarFI <= DISTANCIA_PARADA || distanciaSonarFD <= DISTANCIA_PARADA)
    {
      parada();
      *casoNavegacionPuntero = 1;  
    }   
    // Caso B: Si el robot se encuentra al OBSTÁCULO DE LADO demasiado cerca, desviarse hacia el lado opuesto
    else if (distanciaSonarI1 <= DISTANCIA_LADO_DIAGONAL_SEGURO || distanciaSonarI2 <= DISTANCIA_LADO_SEGURO || 
             distanciaSonarD1 <= DISTANCIA_LADO_DIAGONAL_SEGURO || distanciaSonarD2 <= DISTANCIA_LADO_SEGURO)
    {
      obstaculoLado();
      *casoNavegacionPuntero = 2;     
    }
  }
  // Si el robot SÍ tiene un margen seguro en frente o a sus lados 
  else if (distanciaSonarFI > DISTANCIA_PARADA && distanciaSonarFD > DISTANCIA_PARADA &&
           distanciaSonarI1 > DISTANCIA_LADO_DIAGONAL_SEGURO && distanciaSonarI2 > DISTANCIA_LADO_SEGURO &&
           distanciaSonarD1 > DISTANCIA_LADO_DIAGONAL_SEGURO && distanciaSonarD2 > DISTANCIA_LADO_SEGURO)
  {
    // Decidir si el robot está entre filas
    float distanciaSonaresID2 = distanciaSonarI2 + distanciaSonarD2; // utilizar los valores de un sonar derecho (D) y izq (I). La suma determina la cantidad de epsacio libre alrededor => fila o no
    if (IMPRIMIR_NAV) {Serial.print(F("distanciaSonaresID2: ")); Serial.println(distanciaSonaresID2);}
    
    // Si el robot no está entre filas -------------------------------------------------------------------------------------------------
    if (distanciaSonaresID2 > DISTANCIA_FILA ) // CHANGE to dif value after testing
    {    
      /* Casos donde no hay que evitar obstáculos */
      // Caso F: Navegación hacia objetivo con un obstaculo no existente o muy lejano
      if (distanciaSonarFI >= DISTANCIA_GRANDE && distanciaSonarFD >= DISTANCIA_GRANDE)
      {
        obstaculoAdistanciaGrande(giro, distAdesplazar);
        *despPuntero = DESP_POSITIVO;
        *casoNavegacionPuntero = 6;             
      }
      // Caso E: Navegación hacia objetivo con un obstaculo no muy lejano
      else if (DISTANCIA_MEDIA < distanciaSonarFI && DISTANCIA_MEDIA < distanciaSonarFD)
      {
        obstaculoAdistanciaMedia(giro, distAdesplazar); 
        *despPuntero = DESP_POSITIVO;
        *casoNavegacionPuntero = 5;             
      }
      /* Casos donde hay un obstáculo cerca. Aquí empieza evitación de obstáculos */
      // Caso D: SÍ hay suficiente espacio para desviarse y evitar el obstáculo en frente del robot
      else if (DISTANCIA_CORTA < distanciaSonarFI && distanciaSonarFI <= DISTANCIA_MEDIA ||
               DISTANCIA_CORTA < distanciaSonarFD && distanciaSonarFD <= DISTANCIA_MEDIA)
      {
        obstaculoAdistanciaPequena(giro);     
        *despPuntero = DESP_POSITIVO;
        *casoNavegacionPuntero = 4;             
      }
      // Caso C: NO hay suficiente espacio para desviarse y evitar el obstáculo en frente del robot, retroceder para volver a un caso anterior
      else if (DISTANCIA_PARADA < distanciaSonarFI && distanciaSonarFI <= DISTANCIA_CORTA ||
               DISTANCIA_PARADA < distanciaSonarFD && distanciaSonarFD <= DISTANCIA_CORTA)  
               
      {
        if (DISTANCIA_PARADA >= distanciaSonarA)
        {
          if (IMPRIMIR_NAV) Serial.println(F("En F......no espacio para retroceder, parando......"));
          parar();
        }
        else if (DISTANCIA_PARADA < distanciaSonarA)
        {
          if (IMPRIMIR_NAV) Serial.println(F("En F....retrocediendo......."));
          frenteAobstaculo();
          *despPuntero = DESP_NEGATIVO;
        }
        
        *casoNavegacionPuntero = 3;             
      }
      // Caso Z: Caso de seguridad (si el robot no detecta ningún de los casos anteriores)
      else
      { 
        casoDesconocido = true;
        *casoNavegacionPuntero = 0;             
      }      
    }
    // Si el robot está entre filas-----------------------------------------------------------------------------------------------------------------------
    else if (distanciaSonaresID2 <= DISTANCIA_FILA) 
    {
       if (IMPRIMIR_NAV) Serial.println(F("-------------------------Entre Filas-------------------------"));
       *despPuntero = DESP_POSITIVO;
  
       int velocidad;    
       if (distAdesplazar > DISTANCIA_MEDIA)                      // Si hay mucha distancia entre nuestro punto objetivo y el robot
         velocidad = VEL_NORMAL;
       else if (distAdesplazar <= DISTANCIA_MEDIA)                  // Si el robot casi está en su punto objetivo
         velocidad = VEL_LENTA;
      
       giro = direccionEntreFilas(distanciaSonarI1,distanciaSonarD1);
       if (IMPRIMIR_NAV) {Serial.print(F("ENTREFILAS Giro: ")); Serial.println((char)giro);}
       activarMotores(giro,velocidad,desp);
       *casoNavegacionPuntero = 7;             
    }
    else
    { 
      casoDesconocido = true;
      *casoNavegacionPuntero = 0;             
    }    
  }
  else
  { 
    casoDesconocido = true;
    *casoNavegacionPuntero = 0;             
  }

  if (casoDesconocido)
  { 
    if (IMPRIMIR_NAV) Serial.print(F("Caso desconocido en navegación autónoma...EMERGENCIA: ")); 
    *modoPuntero = MODO_EMERGENCIA;
    parar();
  }      

  // Se resetea las variables de condiciones
  giro = 0;
  distAdesplazar = 0;
}

// Caso A: Si el robot se encuentra al OBSTÁCULO DE FRENTE demasiado cerca, parar
void parada(void)
{
  if (IMPRIMIR_NAV) Serial.println(F("A: Obstáculo en frente demasiado cerca...parando"));
  parar();
  (3000);
}  

// Caso B: Si el robot se encuentra al OBSTÁCULO DE LADO demasiado cerca, desviarse hacia el lado opuesto
void obstaculoLado()
{
  if (IMPRIMIR_NAV) Serial.print(F("B: Obstáculo a un lado...apartándome a la "));
  
  int giro;
  if (distanciaSonarI1 < DISTANCIA_LADO_DIAGONAL_SEGURO || distanciaSonarI2 < DISTANCIA_LADO_SEGURO)                  
    giro = GIRO_DERECHA;
  else if (distanciaSonarD1 < DISTANCIA_LADO_DIAGONAL_SEGURO || distanciaSonarD2 < DISTANCIA_LADO_SEGURO)
    giro = GIRO_IZQUIERDA;

  if (IMPRIMIR_NAV) Serial.println((char)giro);

  int velocidad = VEL_LENTA;
  activarMotores(giro,velocidad,desp);
  delay(300);
}

// Caso C: Navegación hacia objetivo con un obstaculo no existente o muy lejano
void obstaculoAdistanciaGrande(int giro, float distAdesplazar)
{
  if (IMPRIMIR_NAV) Serial.print(F("C: Obstáculo muy lejos: "));

  int desp = DESP_POSITIVO;                     
  if (IMPRIMIR_NAV) Serial.print(F("Desplazamiento positivo, "));

  int velocidad;
  if (distAdesplazar >= DISTANCIA_MEDIA)                          // punto objetivo no está cerca todavía
  {
    velocidad = VEL_RAPIDA;                   
    if (IMPRIMIR_NAV) Serial.println(F("velocidad rápida"));    
  }
  else if (distAdesplazar < DISTANCIA_MEDIA)                      // punto objetivo está cerca
  {
    velocidad = VEL_LENTA;                     
    if (IMPRIMIR_NAV) Serial.println(F("velocidad lenta"));   
  }
  
  if (IMPRIMIR_NAV) {Serial.print(F("giro: ")); Serial.println((char)giro);}    
  activarMotores(giro,velocidad,desp); 
}  

// Caso D: Navegación hacia objetivo con un obstaculo no muy lejano
void obstaculoAdistanciaMedia(int giro, float distAdesplazar)       
{
  if (IMPRIMIR_NAV) Serial.print(F("D: Obstáculo no muy lejos: "));

  int desp = DESP_POSITIVO;
  if (IMPRIMIR_NAV) Serial.print(F("Desplazamiento positivo, "));

  int velocidad;
  if (distAdesplazar >= DISTANCIA_MEDIA)                          // punto objetivo no está cerca todavía
  {
    velocidad = VEL_NORMAL; 
    //velocidad = VEL_LENTA;    
    if (IMPRIMIR_NAV) Serial.println(F("Velocidad normal(lenta debug)"));
  
  }
  else if (distAdesplazar < DISTANCIA_MEDIA)                      // punto objetivo está cerca
  {          
    velocidad = VEL_LENTA;
    if (IMPRIMIR_NAV) Serial.println(F("Velocidad lenta"));   
  } 
  
    if (IMPRIMIR_NAV) {Serial.print(F("giro: ")); Serial.println((char)giro);}    
    activarMotores(giro,velocidad,desp);  
}

// Caso E: SÍ hay suficiente espacio para desviarse y evitar el obstáculo en frente del robot
void obstaculoAdistanciaPequena(int giro)
{
  if (IMPRIMIR_NAV) Serial.print(F("E: Obstáculo cerca!...Evitándolo "));

  // Elegir lado con más espacio
  char ladoSonarUtilizado;          
  if (distanciaSonarD2 >= distanciaSonarI2 && distanciaSonarD2 >= DISTANCIA_GIRO_MIN)       // si hay espacio a la derecha, girar a la derecha
  {
    if (IMPRIMIR_NAV) Serial.println(F("...más espacio a la derecha"));                  
    giro = GIRO_DERECHA;
    ladoSonarUtilizado = 'I';
  }
  else if (distanciaSonarD2 < distanciaSonarI2 && distanciaSonarI2 >= DISTANCIA_GIRO_MIN)  // si hay espacio a la izquierda, girar a la izquierda
  {
    if (IMPRIMIR_NAV)  Serial.println(F("...más espacio a la izquierda")); 
    giro = GIRO_IZQUIERDA;
    ladoSonarUtilizado = 'D';
  }
  else if (distanciaSonarD2 >= DISTANCIA_GIRO_MIN)
  {
    if (IMPRIMIR_NAV)  Serial.println(F("...espacio para girar a la derecha")); 
    giro = GIRO_IZQUIERDA;
    ladoSonarUtilizado = 'D';
  }
  else if (distanciaSonarI2 >= DISTANCIA_GIRO_MIN)
  {
    if (IMPRIMIR_NAV)  Serial.println(F("...espacio para girar a la izquierda")); 
    giro = GIRO_IZQUIERDA;
    ladoSonarUtilizado = 'I';
  }
  else                                                                    // TO DO..GO BACK 3 INCHES (WATCH OUT FOR THE BACK SENSOR WHILE YOU DO THAT)
  {
    if (IMPRIMIR_NAV) Serial.println(F("NO PUEDO GIRAR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"));
    *modoPuntero = MODO_EMERGENCIA;
    parar();
  }      
       
  // Hallar el radio de evitación
  if (IMPRIMIR_NAV) {Serial.print(F("min(FI, FD): ")); Serial.print(min(distanciaSonarFI, distanciaSonarFD)); Serial.print(F(" 45*PI/180: ")); Serial.println(45*PI/180);}  
  float radioLado = min(distanciaSonarFI, distanciaSonarFD);        
  float radioLadoFrente = min(distanciaSonarFI, distanciaSonarFD)/cos(45*PI/180); 
  if (IMPRIMIR_NAV) {Serial.print(F("radioLadoFrente before loop: ")); Serial.println(radioLadoFrente);}  
  
  // EVITAR OBSTÁCULO --------------------------------------------------------- 
  _Bool giroCompleto = false; // parte 1
  _Bool evitarObst = false;   // parte 2
      
//  int velocidad = VEL_LENTA;
//  int desp = DESP_GIRO;
  int velocidad;
  //int desp;

  if (IMPRIMIR_NAV) {Serial.println(F("Bucle de evitación ----------"));}  
  while (true)
  {
    erroresMotor();
    leerSonars();     
    
    if (distanciaSonarFI <= DISTANCIA_PARADA ||distanciaSonarFD <= DISTANCIA_PARADA)
    {
      if (IMPRIMIR_NAV) Serial.println(F("En caso E OBSTACULO MUY CERCA PARANDO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"));
      *modoPuntero = MODO_EMERGENCIA;
      parar();
      break;
    }
    
    float distanciaSonaresID2 = distanciaSonarI2 + distanciaSonarD2; // utilizar los valores de un sonar derecho (D) y izq (I). La suma determina la cantidad de epsacio libre alrededor => fila o no
    if (distanciaSonaresID2 <= DISTANCIA_FILA )
    {
      if (IMPRIMIR_NAV) Serial.println(F("Entrefilas detectado...saliendo de caso E y entrando en caso entrefilas"));
      break;
    }

    _Bool distanciaLadoSegura;
    if (distanciaSonarI1 > DISTANCIA_LADO_DIAGONAL_SEGURO || distanciaSonarI2 > DISTANCIA_LADO_SEGURO || 
        distanciaSonarD1 > DISTANCIA_LADO_DIAGONAL_SEGURO || distanciaSonarD2 > DISTANCIA_LADO_SEGURO)
    {
      obstaculoLado();     
      *despPuntero = DESP_POSITIVO;
      distanciaLadoSegura = true;
    }
    if (distanciaSonarI1 <= DISTANCIA_LADO_DIAGONAL_SEGURO || distanciaSonarI2 <= DISTANCIA_LADO_SEGURO || 
        distanciaSonarD1 <= DISTANCIA_LADO_DIAGONAL_SEGURO || distanciaSonarD2 <= DISTANCIA_LADO_SEGURO)
    {
      obstaculoLado();     
      *despPuntero = DESP_POSITIVO;
      distanciaLadoSegura = false;
    }

    if (evitarObst == false)
    {
      float distanciaLado; 
      float distanciaLadoFrente; 
      if (ladoSonarUtilizado == 'I')
      {
        distanciaLado = distanciaSonarI2;
        distanciaLadoFrente = distanciaSonarI1;  /////////// EDIT THIS LENGTH
      }
      else if (ladoSonarUtilizado == 'D')
      {
        distanciaLado = distanciaSonarD2;
        distanciaLadoFrente = distanciaSonarD1;  /////////// EDIT THIS LENGTH
      }

      float dif_distLadoFrente_radioLadoFrente = distanciaLadoFrente - radioLadoFrente; // parte 1 y 2
      float dif_distLado_radioLado = distanciaLado - radioLado;
      
      int errorDireccion = 0;          // parte 2
      
      leerMagnetometro();          // obtener datos de magnetometro
      if (IMPRIMIR_NAV)  {Serial.print(F("direccionAct: ")); Serial.println(direccionAct);}

      if (DISTANCIA_CORTA < distanciaSonarFI && distanciaSonarFI < DISTANCIA_MEDIA ||
          DISTANCIA_CORTA < distanciaSonarFD && distanciaSonarFD < DISTANCIA_MEDIA)
      {
        giroCompleto = false;
      }
      
      // PARTE 1: Girar el robot sin desplazar---------------------------------------------------------
      if (giroCompleto == false)
      {
        if (IMPRIMIR_NAV)  Serial.println(F("Parte 1: orientando para estar paralelo con obstáculo ----------------------------------------------------------------------------------"));
                
        if (DISTANCIA_CORTA < distanciaSonarFI && distanciaSonarFI < DISTANCIA_MEDIA ||
            DISTANCIA_CORTA < distanciaSonarFD && distanciaSonarFD < DISTANCIA_MEDIA)
        {
          velocidad = VEL_LENTA;
          *despPuntero = DESP_GIRO;
          //desp = DESP_GIRO;
          if (IMPRIMIR_NAV) Serial.println(F("ACTIVANDO MOTORES PARA GIRAR: "));
          activarMotores(giro,velocidad,desp);  
          
          giroCompleto = false;
        }
        else if ((distanciaSonarFI > DISTANCIA_MEDIA && distanciaSonarFD > DISTANCIA_MEDIA) && giroCompleto == false) 
        {
          parar();
          if (IMPRIMIR_NAV) Serial.println(F("PARADO POR 2 Seg"));
          delay(2000); // Opcional! Sólo para demonstración
          giroCompleto = true;
          //*modoPuntero = MODO_INACTIVO; break;
        }
        else
        {
          if (IMPRIMIR_NAV) Serial.println(F("ELSE BREAKING..............................."));
          break;
        }
      }
      
      //PARTE 2: Seguir alrededor del obstáculo hasta que el robot vuelva a orientarse en su direccionObj original-------------------------------------------
      if (giroCompleto == true && distanciaLadoSegura == true)
      {
        if (IMPRIMIR_NAV)  Serial.println(F("Parte 2: desplazando alrededor de obstáculo ----------------------------------------------------------------------------------"));
        
        errorDireccion = direccionAct - direccionObj;
        if (IMPRIMIR_NAV)  {Serial.print(F("direccionAct: ")); Serial.print(direccionAct);  Serial.print(F("   direccionObj: ")); Serial.print(direccionObj); Serial.print(F(" errorDireccion: ")); Serial.println(errorDireccion);}
                
        if (abs(errorDireccion) > TOL_DIRECCION)
        {
          if (IMPRIMIR_NAV)  {Serial.print(F("dif_distLadoFrente_radioLadoFrente: ")); Serial.println(dif_distLadoFrente_radioLadoFrente);}
          if (IMPRIMIR_NAV)  {Serial.print(F("TOL_DISTANCIA: ")); Serial.println(TOL_DISTANCIA);}

          if (-1*TOL_DISTANCIA > dif_distLadoFrente_radioLadoFrente || dif_distLadoFrente_radioLadoFrente > TOL_DISTANCIA)
          {
            if (IMPRIMIR_NAV)  {Serial.print(F("-----distanciaLadoFrente: ")); Serial.print(distanciaLadoFrente);  Serial.print(F("  radioLadoFrente: ")); Serial.println(radioLadoFrente);}           
            
            if (distanciaLadoFrente < radioLadoFrente)      // Menos grande que radioLadoFrente
            {
              if (ladoSonarUtilizado == 'I')
              {
                if (IMPRIMIR_NAV)  Serial.println(F("---Utilizando lado I"));           
                giro = GIRO_DERECHA;
              }
              else if (ladoSonarUtilizado == 'D')
              {
                if (IMPRIMIR_NAV)  Serial.println(F("---Utilizando lado D"));           
                giro = GIRO_IZQUIERDA;
              }
            }
            else if(distanciaLadoFrente > radioLadoFrente)   // Más grande que radioLadoFrente                          
            {
              if(ladoSonarUtilizado == 'I')
              {
                if (IMPRIMIR_NAV)  Serial.println(F("---Utilizando lado I"));                           
                giro = GIRO_IZQUIERDA;
              }
              else if (ladoSonarUtilizado == 'D')
              {
                if (IMPRIMIR_NAV)  Serial.println(F("---Utilizando lado D"));                           
                giro = GIRO_DERECHA;
              }
            }
            else if (distanciaLadoFrente == radioLadoFrente)                           
            {
              giro = GIRO_RECTO;
            }        
          } 
           
          // TODO ADD GIRO TO ARRAY
          //desp = DESP_POSITIVO;
          *despPuntero = DESP_POSITIVO;
          velocidad = VEL_LENTA;
          activarMotores(giro,velocidad,desp);
        }
        else if (abs(errorDireccion) <= TOL_DIRECCION)
        {
          if (dif_distLado_radioLado > TOL_DISTANCIA)/////////////////////////
          {
            if(ladoSonarUtilizado == 'I')
            {
              if (IMPRIMIR_NAV)  Serial.println(F("---Part 2 last section going right"));                           
              giro = GIRO_DERECHA;
            }
            else if (ladoSonarUtilizado == 'D')
            {
              if (IMPRIMIR_NAV)  Serial.println(F("---Part 2 last section going left"));                           
              giro = GIRO_IZQUIERDA;
            }
          
            *despPuntero = DESP_POSITIVO;
            velocidad = VEL_LENTA;
            activarMotores(giro,velocidad,desp);
            delay(500);
          }
          
          if (IMPRIMIR_NAV)  Serial.println(F("obstáculo evitado.."));
          evitarObst = true;
          break;   
        }                                      
      }     
    }
  }
    
  giroCompleto = false;
  evitarObst = false;
}
    
// Caso F: NO hay suficiente espacio para desviarse y evitar el obstáculo en frente del robot, retroceder para volver a un caso anterior
void frenteAobstaculo(void)
{
  if (IMPRIMIR_NAV) Serial.print(F("F: Al frente de obstáculo!...Desplazando hacia atras!"));
  int giro = GIRO_ATRAS;
  int velocidad = VEL_LENTA;                   
  int desp = DESP_NEGATIVO; 
  activarMotores(giro,velocidad,desp);
}
    
// Mantiene el robot en la mitad de las filas útil
int direccionEntreFilas(float distanciaSonarI1, float distanciaSonarD1) 
{ 
  if (IMPRIMIR_NAV) Serial.println(F("DIRECCIONENTREFILAS()--------"));
  float difSonaresLadosFrentes = distanciaSonarI1 - distanciaSonarD1;
  
  //float distanciaSonaresID2 = distanciaSonarI2+distanciaSonarD2; // Sonares de lado ven la fila
  //bool SonarsDIenFila false;  
  //if distanciaSonaresID2 < DISTANCIA_FILA)

  int giro;
  if (-1*TOL_ENTREFILAS > difSonaresLadosFrentes || difSonaresLadosFrentes > TOL_ENTREFILAS)                    // asegurar que la diferrencia es significativa  
  {  
    if (distanciaSonarD1 > distanciaSonarI1)       // si hay más distancia a la derecha, mover a otra dirección
    {
      if (IMPRIMIR_NAV) Serial.println(F("ENTREFILAS: Moviendo hacia lado D"));
      giro = GIRO_DERECHA;
    }
    else if (distanciaSonarD1 < distanciaSonarI1)  // si hay más distancia a la izquierda, mover a otra dirección
    {
      if (IMPRIMIR_NAV) Serial.println(F("ENTREFILAS: Moviendo hacia lado I"));
      giro = GIRO_IZQUIERDA;
    }
    else if (distanciaSonarD1 == distanciaSonarI1)
    {
      if (IMPRIMIR_NAV) Serial.println(F("ENTREFILAS: Dentro de tolerancia y centrado"));
      giro = GIRO_RECTO;
    }
  }
  else                                                          // si el robot ya esta ne la mitad de las filas, no girar
  {
    if (IMPRIMIR_NAV) Serial.println(F("ENTREFILAS: Fuera de tolerancia y centrado"));
    giro = GIRO_RECTO;
  }

  return giro;
}



