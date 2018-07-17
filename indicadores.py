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
def simpleMA(datos,start,window=10,colName='Adj Close',resName=''):
    '''
    NOTA: Los datos están ordenados de forma creciente relativo a la fecha

    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start: String en formato YYYY-MM-DD que representa la fecha de inicio de
    los valores del MA

    window: Entero que representa la ventana de tiempo del MA

    colName: String con el nombre de la columna que contiene los datos numéricos

    resName: String que representa el nombre de la columna con los datos del MA

    SALIDA
    datos: Dataframe datos con la columna resName añadida e iniciando en el
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
    lastIndex=datos.shape[0] - 1

    #En este numpy array guardo los datos del MA
    MA=np.zeros(datos.shape[0])

    #La variable aux se utiliza para llena el arreglo MA
    aux=indiceInicio

    for t in range(0,lastIndex-indiceInicio+1):

        #Extrae los datos del bloque correspondiente y calcula el promedio
        MA[aux+t]=np.mean(datos[colName].iloc[indiceInicio - window +1 +t : indiceInicio + t +1])

    #Añade la nueva columna
    datos[resName]=MA

    #Filtra a partir del índice correspondiente a la fecha start
    datos=datos.iloc[indiceInicio:,:]
    datos=datos.reset_index(drop=True)

    return datos

##==============================================================================
## Función para calcular bandas de bollinger
##==============================================================================
def bollinger(datos,start,window=10,k=2.0,colName='Adj Close'):
    '''
    NOTA: Los datos están ordenados de forma creciente relativo a la fecha

    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start: String en formato YYYY-MM-DD que representa la fecha de inicio de
    los valores del indicador

    window: Entero que representa la ventana de tiempo

    k: Real que representa el número de desviaciones estándar

    colName: String con el nombre de la columna que contiene los datos numéricos

    SALIDA
    datos: Dataframe datos con nuevas columnas relacionadas al indicador
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
    lastIndex=datos.shape[0] - 1

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
    datos[resBMA]=MA
    datos[resBUp]=Up
    datos[resBDown]=Down

    #Filtra a partir del índice correspondiente a la fecha start
    datos=datos.iloc[indiceInicio:,:]
    datos=datos.reset_index(drop=True)

    return datos
