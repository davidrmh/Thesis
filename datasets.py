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

    	

