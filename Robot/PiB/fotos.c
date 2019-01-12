// Analiza los píxeles RGB para calcular el VARI (un índice de la cantidad de verde)

#include <stdio.h>
#include <stdlib.h>

#include "headers/bmp.h"

int main(int argc, char *argv[])
{
    // Asegurarse de tener una imagen para analizar
    if (argc != 2)
    {
        fprintf(stderr, "Usage: ./fotos infile \n");
        return 1;
    }

    // Guardar el nombre de la imagen
    char *infile = argv[1];


    // Abrir la imagen
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // Leer el encabezamiento de la imagen BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // Leer el encabezamiento de la imagen BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // Comprobar que se trata de un archivo BMP 4.0 de 24 bits
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 || bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    // Determinar el colchón
    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

	float vari = 0.0;
	
	int numPixelesTotal = 0;
	int numPixelesBuenos = 0;

    // Recorrer las filas de la imagen
    for (int i = 0, biHeight = abs(bi.biHeight); i < biHeight; i++)
    {
		// Recorrer los píxeles de la fila
        for (int j = 0; j < bi.biWidth; j++)
        {
            // Cada pixel contiene 3 valores
            RGBTRIPLE triple;

            // Leer el pixel actual del archivo
            fread(&triple, sizeof(RGBTRIPLE), 1, inptr);
            
			// Calcular el numerador y el denominador del VARI para este pixel
			int numerador = triple.rgbtGreen - triple.rgbtRed;
			int denominador = triple.rgbtGreen + triple.rgbtRed - triple.rgbtBlue;
			
			// Para evitar la excepción al dividir por 0	
			if (denominador == 0)
				denominador++;
            	
			vari = numerador/denominador;	

			// Considerar que un pixel es bueno si tiene suficiente VARI
			if (vari >= 0.6) 
				numPixelesBuenos++;			 	

            numPixelesTotal++;
        }

        // Ignorar el colchón
        fseek(inptr, padding, SEEK_CUR);
    }

	int porcentajeVerde = numPixelesBuenos / numPixelesTotal * 100;
	printf("%i", porcentajeVerde);

    // Cerrar la imagen
    fclose(inptr);

    return 0;
}

// 2019-01-05_16:11:57.405537_T.bmp gives 42 97 50
// determine plant health by rgb
