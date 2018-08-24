# coding: utf-8
import pandas as pd
import numpy as np
import copy as cp

##===========================================================================##
## Función para normalizar los datos utilizando el mínimo y el máximo
##===========================================================================##

def normaliza_min_max(datos,lmin='',lmax=''):
    '''
    ENTRADA
    datos: pandas dataframe con las observaciones y atributos a normalizar

    lmin, lmax: listas con los valores mínimos y máximos utilizados para
    normalizar cada columna
    Si no se especifican, se calculan de los datos.

    SALIDA
    normalizados: pandas dataframe con las observaciones normalizadas

    lmin, lmax: listas con los valores mínimos y máximos utilizados para
    normalizar cada columna
    Si no se especifican, se calculan de los datos.
    '''

    #Número de columnas
    n_col = datos.shape[1]

    #Calcula los mínimos (en caso de ser necesario)
    if lmin == '':
        lmin = []
        for i in range(0,n_col):
            lmin.append(datos.iloc[:,i].astype('float').min())

    #Calcula los máximos (en caso de ser necesario)
    if lmax == '':
        lmax = []
        for i in range(0,n_col):
            lmax.append(datos.iloc[:,i].astype('float').max())

    #Normaliza los datos
    diccionario = {} #para el dataframe final
    eps = 0.00001

    for i in range(0,n_col):
        col_name = datos.columns[i]
        diccionario[col_name] = (datos.iloc[:,i].astype('float') - lmin[i]) / (lmax[i] - lmin[i] + eps)

    normalizados = pd.DataFrame(data = diccionario)

    return normalizados, lmin, lmax
