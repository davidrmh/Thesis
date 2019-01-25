# coding: utf-8

'''
Funciones para crear los conjuntos de prueba y de entrenamiento
'''

import indicadores as ind
import etiqueta as eti
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

##==============================================================================
## Función para etiquetar los bloques creados con separaBloques
##==============================================================================
def etiquetaBloques(bloques,numGen=30,popSize=50, flagOper = True, limpia = True):
    '''
    Etiqueta los datos utilizando un algoritmo genético que busca
    la combinación de señales compra,venta,hold que generen mayor ganancia

    ENTRADA
    bloques: Lista con los bloques a etiquetar (cada bloque es un pandas dataframe)

    numGen: Entero, número de generaciones.

    popSize: Entero, tamaño de la población.

    flagOper: Booleano. True => Considera el número de transacciones
    False => No considera el número de transacciones

    limpia: Booleano. True => Limpia señales repetidas

    SALIDA
    Lista con los bloques etiquetados
    '''

    bloques_eti = []

    #número de bloques
    n_bloq = len(bloques)

    #auxiliar
    cont = 0

    for bloque in bloques:

    	etiquetado = eti.etiquetaMetodo2(bloque, numGen, popSize, flagOper, limpia)

    	print 50*'='

    	cont = cont + 1

    	print 'Finaliza bloque ' + str(cont) + ' de ' + str(n_bloq)

    	print 50*'='

    	bloques_eti.append(etiquetado)

    return bloques_eti	

##==============================================================================
## Función para crear archivos csv a partir de una lista que contiene
## pandas dataframes. Idealmente esta función se utiliza con la lista de 
## la función etiquetaBloques
##==============================================================================
def guardaCSV(lista, ruta = '/datasets/', activo = 'naftrac'):
	'''
	ENTRADA

	lista: Lista que contiene los dataframes

	ruta: String con la carpeta en donde se guardarán los csv

	activo: String con el nombre del activo
	'''

	#auxiliar para el nombre de los archivos
	aux = 1
	for bloque in lista:

		#Extrae fecha inicial y fecha final
		n_obs = bloque.shape[0]
		fecha_in = str(bloque.loc[0,'Date']).split(' ')[0]
		fecha_fin = str(bloque.loc[n_obs-1,'Date']).split(' ')[0]

		#Crea el nombre del archivo
		nombre = '_'.join([str(aux), activo, fecha_in, fecha_fin, str(n_obs) ])
		nombre = ruta + nombre + '.csv'

		#Escribe el csv
		bloque.to_csv(path_or_buf = nombre, index = False)

		aux = aux + 1

	return	
    	

