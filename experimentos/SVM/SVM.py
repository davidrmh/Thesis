# coding: utf-8

#Modifica sys.path para poder importar los módulos necesarios
import sys
sys.path.append('../')
from obtenConjuntos import diccDatos
from preprocesamiento import escala
from sklearn import svm
import pandas as pd
import numpy as np

##==============================================================================================
## VARIABLES GLOBALES PARA diccDatos
arch_csv = '../entrena_prueba.csv'
ruta_entrena = '../../datasets/atributos_clases_dicc-1/'
ruta_prueba = '../../datasets/atributos_clases_dicc-1/'
ruta_etiqueta = '../../datasets/etiquetado/' 
##==============================================================================================

##==============================================================================================
## Parámetros del modelo
params = {}
params['c'] = 1.0
params['kernel'] = 'rbf'
params['degree'] = 3 #Sólo para kernel polinomial
params['gamma'] = 'auto'
params['class_weight'] = 'balanced'
params['decision'] = 'ovr'  #one-versus-rest o one-versus-one (ovr, ovo)
##==============================================================================================


def SVM_main(ruta_dest = './SVM_resultados_dicc1/', metodo = 'scale'):
  '''
  Ajusta un modelo de SVM para realizar las predicciones

  ENTRADA
  ruta_dest: String con la ruta de la carpeta en donde se guardarán las predicciones
  para cada conjunto de prueba.

  metodo: String con el método para ajustar los datos utilizando la función escala

  SALIDA
  crea archivos en ruta_dest
  '''

  #carga los conjuntos de entrenamiento, prueba y etiquetado
  dicc = diccDatos(arch_csv, ruta_entrena, ruta_prueba, ruta_etiqueta)

  #número de modelos a ajustar
  n_modelos = len(dicc['entrenamiento'])

  #abre el archivo CSV que contiene el nombre de cada archivo
  datos_csv = pd.read_csv(arch_csv)

  #Ajusta modelos
  for i in range(0, n_modelos):

    #obtiene los atributos (con escalamiento)
    entrena = dicc['entrenamiento'][i]
    prueba = dicc['prueba'][i]
    entrena_ajust, prueba_ajust = escala(entrena, prueba, metodo)

    #obtiene las clases del conjunto de entrenamiento
    clases = entrena['Clase']

    #ajusta el modelo
    modelo = svm.SVC(C = params['c'],
    kernel = params['kernel'],
    degree = params['degree'],
    #gamma = params['gamma'],
    class_weight = params['class_weight'],
    decision_function_shape = params['decision'])
    modelo.fit(entrena_ajust, clases)

    #Realiza las predicciones
    predicciones = modelo.predict(prueba_ajust)

    #agrega las predicciones al archivo correspondiente
    etiquetado = dicc['etiquetado'][i]
    etiquetado['Clase'] = predicciones

    #Crea el nombre de los archivos
    #aux1 tiene la forma "2_naftrac-etiquetado_2013-07-01_2013-11-04_90"
    aux1 = datos_csv.loc[i,'etiquetado'].split('.csv')[0]
    nom_salida = ruta_dest + aux1 + '_predicciones.csv'

    #guarda el csv
    etiquetado.to_csv(nom_salida, index = False)

    #mensaje auxiliar
    print 'Se guarda el archivo ' + aux1

  return  





