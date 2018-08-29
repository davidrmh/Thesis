# coding: utf-8
##==============================================================================
## Autor: David Montalván
## Fecha de creación: 2018-08-28
## Última modificación: 2018-08-28
##
## En este archivo se encuentran funciones para crear conjuntos de
## entrenamiento y de prueba
##==============================================================================
import pandas as pd
import numpy as np
import indicadores as ind
import normaliza as nor
import etiqueta as eti

##==============================================================================
## Función para crear un conjunto de entrenamiento basado en un algoritmo
## del tipo EDA para etiquetar los datos
##==============================================================================
def creaEntrenamientoEDA(path,start,end,dicc,numGen=20,popSize=60,norm='minmax'):
    '''
    ENTRADA
    path: String con la ruta del csv de Yahoo Finance

    start, end: String en formato YYYY-MM-DD que representa la fecha de inicio y
    final, respectivamente, del conjunto de entrenamiento.

    dicc: Un diccionario de la forma
    dicc[key] = {'tipo':'FUNCION','parametros':{'window':10,...}}
    en donde FUNCIÓN corresponde al nombre de alguna de las funciones
    para calcular un indicador en particular.
    parametros es un diccionario con los parámetros del indicador de interés
    Ver archivo indicadores.py

    numbGen: Entero que representa el número de generaciones en el proceso
    evolutivo que etiqueta los datos.

    popSize: Entero que representa el tamaño de la población en el proceso
    evolutivo que etiqueta los datos.

    norm: Método para normalizar los datos.

    SALIDA
    resultado: Pandas dataframe con el conjunto de entrenamiento. Los atributos
    están normalizados

    Se escribe este dataframe en un archivo CSV
    '''

    #Obtiene el nombre del archivo de salida
    path_output = path.split('.')[0] + '-' + start + '-' + end + '.csv'

    #Lee el archivo csv de Yahoo Finance
    datos = ind.leeTabla(path)

    #Obtiene el subconjunto de datos que se etiquetarán
    entrena = eti.subconjunto(datos, start ,end)

    #Etiqueta los datos
    entrena = eti.etiquetaMetodo2(entrena, numGen, popSize)[0]

    #Crea la lista que contendrá la información de cada indicador
    listaIndicadores = ind.creaIndicadores(datos, dicc, start, end)

    #Crea el dataframe que combina la información de cada indicador
    #El resultado es un DataFrame con la columna de interés de cada uno de ellos
    atributos = ind.combinaIndicadores(listaIndicadores)

    #Normaliza los atributos
    if norm == 'minmax':
        atributos = nor.normaliza_min_max(atributos)[0]

    #Agrega la columna con las etiquetas
    resultado = pd.concat([atributos, entrena['Clase']], axis = 1)

    #Guarda el csv
    resultado.to_csv(path_or_buf = path_output, index = False, encoding = 'utf-8')

    return resultado
