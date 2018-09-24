# coding: utf-8
import pandas as pd
import numpy as np
from copy import deepcopy

##==============================================================================
## Función para comparar dos series de acuerdo a un operador dado
##==============================================================================
def compara_series(serie1, serie2, op, dataframe):
    '''
    ENTRADA
    serie1, serie2: Pandas series con los datos a comparar

    op: string con el símbolo del operador booleano (<, <=, >, >=)

    dataframe: Pandas dataframe en donde se agrega la columna resultante de
    realizar la comparación

    SALIDA
    df: Pandas dataframe en donde se agrega la columna resultante de
    realizar la comparación
    '''

    #Revisa que se tenga la misma cantidad de datos
    if len(serie1) != len(serie2):
        print 'ERROR: Las series deben tener la misma longitud'
        return 0

    #obtiene el nombre de la columna resultante
    colName = serie1.name + op + serie2.name

    if op == '<':
        resultado = serie1 < serie2
    elif op =='<=':
        resultado = serie1 <= serie2
    elif op == '>':
        resultado = serie1 > serie2
    elif op == '>=':
        resultado = serie1 >= serie2
    elif op == '==':
        resultado = serie1 == serie2
    else:
        print 'ERROR: operador no soportado'
        return 0

    #convierte a 0-1
    resultado = 1 * resultado

    #agrega a dataframe
    df = deepcopy(dataframe)
    df[colName] = resultado

    return df

##==============================================================================
## Función para crear las combinaciones de n en 2 a partir de un conjunto
## de strings
##==============================================================================
def n_en_2(lista):
    '''
    ENTRADA
    lista: Lista de strings

    SALIDA
    comb: Lista con todas las posibles parejas de elementos en lista
    '''

    #obtiene la longitud de la lista
    n = len(lista)

    comb = []

    for i in range(0, n):
        for j in range(i + 1, n):
            comb.append([lista[i], lista[j]])

    return comb        
