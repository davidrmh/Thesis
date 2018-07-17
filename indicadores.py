# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from copy import deepcopy

##==============================================================================
## Datos de Yaho Finance
## Lee datos, quita los null
## transforma a float
## reinicia los indices
##==============================================================================
def leeTabla(ruta="naftrac.csv"):
    '''
    ENTRADA:
    ruta: String con la ruta del archivo csv

    SALIDA:
    data: Pandas dataframe con la información del CSV
    '''
    #Lee datos
    data=pd.read_csv(ruta,na_values=['NaN','null'])

    #quita NaN
    data=data.dropna()

    #Quita columnas sin volumen (NaN implícito)
    data=data[data.iloc[:,6]!=0]

    data['Date']=pd.to_datetime(data['Date'])
    data["Open"]=data["Open"].astype('float')
    data["High"]=data["High"].astype('float')
    data["Close"]=data["Close"].astype('float')
    data["Adj Close"]=data["Adj Close"].astype('float')
    data["Volume"]=data["Volume"].astype('int')
    data=data.reset_index(drop=True)
    return data

##==============================================================================
## Función para calcular un simple moving average
##==============================================================================
def simpleMA(datos,start,end='',window=10,colName='Adj Close',resName=''):
    '''
    NOTA: Los datos están ordenados de forma creciente relativo a la fecha

    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start: String en formato YYYY-MM-DD que representa la fecha de inicio de
    los valores del MA

    end: String en formato YYYY-MM-DD que representa la fecha final

    window: Entero que representa la ventana de tiempo del MA

    colName: String con el nombre de la columna que contiene los datos numéricos

    resName: String que representa el nombre de la columna con los datos del MA

    SALIDA
    resultado: Dataframe datos con la columna resName añadida e iniciando en el
    renglón correspondiente a la fecha start
    '''

    #Localiza la fecha de inicio y revisa si hay suficiente información
    indiceInicio=datos[datos['Date']==start].index[0]
    if window > indiceInicio + 1:
        print 'No hay suficiente historia para esta fecha'
        return datos

    #Nombre de la columna con el MA
    if resName=='':
        resName=colName + "-MA"

    #Último índice
    if end=='':
        lastIndex=datos.shape[0] - 1
    else:
        lastIndex=datos[datos['Date']==end].index[0]


    #En este numpy array guardo los datos del MA
    MA=np.zeros(datos.shape[0])

    #La variable aux se utiliza para llena el arreglo MA
    aux=indiceInicio

    for t in range(0,lastIndex-indiceInicio+1):

        #Extrae los datos del bloque correspondiente y calcula el promedio
        MA[aux+t]=np.mean(datos[colName].iloc[indiceInicio - window +1 +t : indiceInicio + t +1])

    #Añade la nueva columna
    resultado=deepcopy(datos)
    resultado[resName]=MA

    #Filtra a partir del índice correspondiente a la fecha start
    resultado=resultado.iloc[indiceInicio:lastIndex+1,:]
    resultado=resultado.reset_index(drop=True)

    return resultado

##==============================================================================
## Función para calcular bandas de bollinger
##==============================================================================
def bollinger(datos,start,end='',window=10,k=2.0,colName='Adj Close'):
    '''
    NOTA: Los datos están ordenados de forma creciente relativo a la fecha

    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start: String en formato YYYY-MM-DD que representa la fecha de inicio de
    los valores del indicador

    end: String en formato YYYY-MM-DD que representa la fecha final

    window: Entero que representa la ventana de tiempo

    k: Real que representa el número de desviaciones estándar

    colName: String con el nombre de la columna que contiene los datos numéricos

    SALIDA
    resultado: Dataframe datos con nuevas columnas relacionadas al indicador
    '''

    #Localiza la fecha de inicio y revisa si hay suficiente información
    indiceInicio=datos[datos['Date']==start].index[0]
    if window > indiceInicio + 1:
        print 'No hay suficiente historia para esta fecha'
        return datos

    #Nombre de las columnas que se crearán
    resBUp=colName + '-BB-Up'
    resBDown=colName + '-BB-Down'
    resBMA=colName + '-BB-MA'

    #Último índice
    if end=='':
        lastIndex=datos.shape[0] - 1
    else:
        lastIndex=datos[datos['Date']==end].index[0]

    #En este numpy array guardo los datos del MA y las bandas
    MA=np.zeros(datos.shape[0])
    Up=np.zeros(datos.shape[0])
    Down=np.zeros(datos.shape[0])

    #La variable aux se utiliza para llena el arreglo MA
    aux=indiceInicio

    for t in range(0,lastIndex-indiceInicio+1):

        #Extrae los datos del bloque correspondiente y calcula el promedio
        MA[aux+t]=np.mean(datos[colName].iloc[indiceInicio - window +1 +t : indiceInicio + t +1])

        #Calcula las bandas
        desviacion=np.std(datos[colName].iloc[indiceInicio - window +1 +t : indiceInicio + t +1],ddof=1)
        Up[aux+t]= MA[aux+t] + k* desviacion
        Down[aux+t]= MA[aux+t] - k* desviacion

    #Añade las nuevas columnas
    resultado=deepcopy(datos)
    resultado[resBMA]=MA
    resultado[resBUp]=Up
    resultado[resBDown]=Down

    #Filtra a partir del índice correspondiente a la fecha start
    resultado=resultado.iloc[indiceInicio:lastIndex + 1,:]
    resultado=resultado.reset_index(drop=True)

    return resultado

##==============================================================================
## Función para calcular un exponential moving average
##==============================================================================
def exponentialMA(datos,start,end='',window=10,colName='Adj Close',resName=''):
    '''
    NOTA: Los datos están ordenados de forma creciente relativo a la fecha

    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start: String en formato YYYY-MM-DD que representa la fecha de inicio de
    los valores del MA

    end: String en formato YYYY-MM-DD que representa la fecha final

    window: Entero que representa la ventana de tiempo del MA

    colName: String con el nombre de la columna que contiene los datos numéricos

    resName: String que representa el nombre de la columna con los datos del MA

    SALIDA
    resultado: Dataframe datos con la columna resName añadida e iniciando en el
    renglón correspondiente a la fecha start
    '''

    #Localiza la fecha de inicio y revisa si hay suficiente información
    indiceInicio=datos[datos['Date']==start].index[0]
    if window > indiceInicio + 1:
        print 'No hay suficiente historia para esta fecha'
        return datos

    #Nombre de la columna con el MA
    if resName=='':
        resName=colName + "-EMA"

    #Parámetro para suavizamiento
    k=2.0/(window + 1)

    #Último índice
    if end=='':
        lastIndex=datos.shape[0] - 1
    else:
        lastIndex=datos[datos['Date']==end].index[0]

    #En este numpy array guardo los datos del EMA
    EMA=np.zeros(datos.shape[0])

    #Primer valor del EMA
    EMA[indiceInicio]=np.mean(datos[colName].iloc[indiceInicio - window +1 : indiceInicio +1])

    for t in range(1,lastIndex-indiceInicio+1):
        #Calcula el EMA
        EMA[indiceInicio+t]=datos[colName].iloc[indiceInicio+t]*k + EMA[indiceInicio + t-1]*(1-k)

    #Añade la nueva columna
    resultado=deepcopy(datos)
    resultado[resName]=EMA

    #Filtra a partir del índice correspondiente a la fecha start
    resultado=resultado.iloc[indiceInicio:lastIndex + 1,:]
    resultado=resultado.reset_index(drop=True)

    return resultado

##==============================================================================
## Función para calcular un MACD
##==============================================================================
def MACD(datos,start,shortWindow=12,longWindow=26,signalWindow=9,colName='Adj Close'):
    '''
    NOTA: Los datos están ordenados de forma creciente relativo a la fecha

    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start: String en formato YYYY-MM-DD que representa la fecha de inicio de
    los valores.

    shortWindow: Entero que representa la ventana de tiempo del EMA de corto plazo

    longWindow: Entero que representa la ventana de tiempo del EMA de largo plazo

    signalWindow: Entero que representa la ventana de tiempo del signalLine

    colName: String que representa el nombre de la columna con la cual se calculará el indicador

    SALIDA
    resultado: Dataframe datos con las columnas relacionadas al indicador MACD
    '''

## PENDIENTE
## Agregar parámetro end (fechaFinal)
## MACD
## Función para obtener un dataframe con varios indicadores de una lista
## Quitar MA de las bandas de bollinger
## RSI
