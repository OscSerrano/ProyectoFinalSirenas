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
lecturas = ''
#patron = r".*(A{2,4}B{2,4}){2,}.*"
patron = r"((AAAAA|AAAA|AAA|AA)(BBBBB|BBBB|BBB|BB))((AAAAA|AAAA|AAA|AA)(BBBBB|BBBB|BBB|BB))+"

def leer_Microfono():
	datos = np.array([adc.read() for _ in range(cantidad_Lecturas)], dtype=np.float)
	return datos

def frecuencia_Dominante(datos):
	resultadoFft = np.array(np.fft.fft(datos), dtype=np.float)
	resultadoFft[0][0] = 0
	
	magnitudesCuadradas = resultadoFft[0]**2 + resultadoFft[1]**2
	
	magnitudMaxima = np.argmax(magnitudesCuadradas)
	
	frecuenciaDominante = magnitudMaxima * tasa_Muestreo / cantidad_Lecturas
	
	
	return frecuenciaDominante

def detectar_Sirena():
    global lecturas
    #lecturas = 'AAABBBAAABBBAAABBB'
    print(lecturas)
    encontrada = re.search(patron ,lecturas)
    lecturas = ''
    if encontrada: return 'Sirena encontrada'
    else: return 'Sirena NO encontrada'
   

while True:
	datos = leer_Microfono()
	frecuencia = frecuencia_Dominante(datos)
	print(frecuencia)
	if 300 < frecuencia < 1200: lecturas += 'B'
	elif 1500 < frecuencia < 17000: lecturas += 'A'
	else: lecturas += '-'
    
	if len(lecturas) > 15: print(detectar_Sirena())
    
	
	sleep(0.3)
