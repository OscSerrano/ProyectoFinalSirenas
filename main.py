# Código micropython para detectar sirenas
# Video del funcionamiento: https://drive.google.com/file/d/1I7ACsc-8k_UShNSQnLwYYqsoDF_Eltar/view?usp=sharing

from machine import Pin, ADC
from time import sleep
from ulab import numpy as np
import re

#Configuracion de pin
pin_Microfono = Pin(34, mode=Pin.IN)
adc = ADC(pin_Microfono)

#Configuracion del ADC
adc.atten(ADC.ATTN_11DB)

#Parametros de lectura de datos
tasa_Muestreo = 18250
cantidad_Lecturas = 256

lecturas = ''	#Clasificación de frecuencias - comportamiento de la señal

#Expresión regular -> encontrar repeticiones - detectar patrones de comportamiento
patron = r"((AAAAA|AAAA|AAA|AA)(BBBBB|BBBB|BBB|BB))((AAAAA|AAAA|AAA|AA)(BBBBB|BBBB|BBB|BB))+"
#patron = r".*(A{2,4}B{2,4}){2,}.*"  ->	MicroPython no admite este tipo de notación


#Toma 256 lecturas del sensor de audio y almacena los valores en un arreglo  
def leer_Microfono():
	#La función adc.read() convierte los valores analógicos a digital
	datos = np.array([adc.read() for _ in range(cantidad_Lecturas)], dtype=np.float)
	return datos

#Encuentra la frecuencia dominante (mayor potencia) entre las 256 lecturas
def frecuencia_Dominante(datos):
	#Aplica la transformada de rápida de Fourier (fft) a los 256 valores leídos.
	resultadoFft = np.array(np.fft.fft(datos), dtype=np.float)
	
	#Descartamos el primer valor real de la fft - Valor sin sentido (altisimo) debido a ruido.  
	resultadoFft[0][0] = 0
	
	#Elevar parte real e imaginaría al cuadrado para representar magnitudes completas mediante un indice
	magnitudesCuadradas = resultadoFft[0]**2 + resultadoFft[1]**2
	
	#Encuentra el mayor de los indices - mayor magnitud
	magnitudMaxima = np.argmax(magnitudesCuadradas)
	
	#Obtener el valor de la frecuencia en Hz
	frecuenciaDominante = magnitudMaxima * tasa_Muestreo / cantidad_Lecturas
	
	return frecuenciaDominante

#Busca si la variable "lecturas" coincide con el patrón predeterminado
def detectar_Sirena():
	global lecturas
	print(lecturas) 
	
	#Usa expresiónes regulares para buscar coincidencias del patrón
	encontrada = re.search(patron ,lecturas)	
    
	#Vaciar variable "lecturas" para siguiente muestra
	lecturas = ''

	#Mostrar mensaje indicando si encontro o no la sirena
	if encontrada: return 'Sirena encontrada'
	else: return 'Sirena NO encontrada'
   

#Bucle principal del programa
while True:
	datos = leer_Microfono()	#Obtención de señal
	frecuencia = frecuencia_Dominante(datos)	#Detectar frecuencia más potente
	print(frecuencia)

	#Clasificación de frecuencias
	if 300 < frecuencia < 1200: lecturas += 'B'
	elif 1500 < frecuencia < 17000: lecturas += 'A'
	else: lecturas += '-'
    
	#Número de lecturas necesarias para comprobar la detección de sirena
	if len(lecturas) > 30: print(detectar_Sirena())
    
	#Controlar el tiempo de toma de muestra
	sleep(0.2)
