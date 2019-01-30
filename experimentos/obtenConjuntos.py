# coding: utf-8

import pandas as pd

##==============================================================================
## Función para guardar los conjuntos de entrenamiento y de prueba
##==============================================================================
def diccDatos(arch_csv = "./entrena_prueba.csv", ruta_entrena = "../datasets/atributos_clases_dicc-1/", ruta_prueba = "../datasets/atributos_clases_dicc-1/"):
	'''
	ENTRADA
	arch_csv: String con la ruta del CSV que contiene el nombre de los archivos con cada conjunto

	ruta_entrena: String con la ruta de la carpeta que contiene los conjuntos de entrenamiento

	ruta_prueba: String con la ruta de la carpeta que contiene los conjuntos de prueba

	SALIDA
	un diccionario con dicc['entrenamiento'] una lista que almacena los conjuntos de entrenamiento
	y dicc['prueba'] una lista que almacena los conjuntos de prueba
	'''

	#Lee el archivo CSV que contiene en el nombre de cada archivo
	datos_csv = pd.read_csv(arch_csv)

	#número de archivos
	n_arch = datos_csv.shape[0]

	#diccionario que guardará los datos
	dicc = {}
	dicc['entrenamiento'] = []
	dicc['prueba'] = []

	#colecta la información
	for i in range(0, n_arch):

		#nombre del archivo de entrenamiento
		arch_entrena = ruta_entrena + datos_csv.loc[i, 'entrena']

		#nombre del archivo de prueba
		arch_prueba = ruta_prueba + datos_csv.loc[i, 'entrena']

		dicc['entrenamiento'].append(pd.read_csv(arch_entrena))
		dicc['prueba'].append(pd.read_csv(arch_prueba))

	return dicc	

