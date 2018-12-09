void navegacionManual(char mensaje[])
{
  String respuesta = 'X' + String(mensaje[2]) + String(mensaje[3]) + 'x'; 
  Serial.println(respuesta);
  Serial.flush();
  
  int velocidad = VEL_LENTA; 
    
  if (mensaje[2] == 'p' && mensaje[3] == 'f') parar();  
  else if (mensaje[2] == 'p' && mensaje[3] == 's') pararadaSuave();  
  else if (mensaje[2] == 'a' && mensaje[3] == 'r') avanzarRecto(velocidad); 
  else if (mensaje[2] == 'a' && mensaje[3] == 'i') avanzarIzquierda(velocidad);
  else if (mensaje[2] == 'a' && mensaje[3] == 'd') avanzarDerecha(velocidad);
  else if (mensaje[2] == 'r' && mensaje[3] == 'r') retrocederRecto(velocidad);
  else if (mensaje[2] == 'r' && mensaje[3] == 'i') retrocederIzquierda(velocidad);
  else if (mensaje[2] == 'r' && mensaje[3] == 'd') retrocederDerecha(velocidad);
  else if (mensaje[2] == 'g' && mensaje[3] == 'i') giroIzquierda(velocidad);
  else if (mensaje[2] == 'g' && mensaje[3] == 'd') giroDerecha(velocidad);
  else if (mensaje[2] == 'z' && mensaje[3] == 'e') rc.ResetEncoders(DIRECCION_MEMORIA_RC);
}


