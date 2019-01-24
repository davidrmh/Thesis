# coding: utf-8

'''
Funciones para crear los conjuntos de prueba y de entrenamiento
'''

import indicadores as ind
import pandas as pd
import numpy as np

##==============================================================================
## Función para separar los datos en bloques consecutivos del mismo tamaño
##==============================================================================
def separaBloques(datos, lon = 90):
	'''
	ENTRADA

	datos: Pandas dataframe con los datos del CSV
	(idealmente creado con la función leeTabla del módulo indicadores)

	lon: Entero que representa el número de observaciones de cada bloque

	SALIDA
	Lista con los bloques de datos

	'''

	#número de observaciones
	n_obs = datos.shape[0]

	#número de bloques posibles
	n_bloques = int(n_obs / lon)

	#lista para almacenar los bloques
	bloques = []

	for j in range(0, n_bloques):

		#obtiene el bloque j
		bloque =  datos.iloc[j*lon:(j+1)*lon,]

		#Reinicia los índices
		bloque = bloque.reset_index(drop = True)

		#agrega a la lista
		bloques.append(bloque)

	return bloques	

