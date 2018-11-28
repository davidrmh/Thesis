# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from copy import deepcopy
from ta.momentum import money_flow_index
from ta.momentum import rsi
from ta.momentum import wr
from ta.volume import ease_of_movement

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
    data["Low"]=data["Low"].astype('float')
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
        resName=colName + "-MA-" + str(window)

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

    #añade metadatos
    resultado.tipo = 'simpleMA'
    resultado.resName = resName

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
    resBUp=colName + '-BB-Up-' + str(window) + '-' + str(k)
    resBDown=colName + '-BB-Down-'+ str(window) + '-' + str(k)
    resBMA=colName + '-BB-MA-' + str(window) + '-' + str(k)

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

    #agrega metadatos
    resultado.tipo = 'bollinger'
    resultado.resBUp = resBUp
    resultado.resBDown = resBDown

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
        resName=colName + "-EMA-" + str(window)

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

    #Agrega metadatos
    resultado.tipo = 'exponentialMA'
    resultado.resName = resName

    return resultado

##==============================================================================
## Función para calcular un MACD
##==============================================================================
def MACD(datos,start,end='',shortWindow=12,longWindow=26,signalWindow=9,colName='Adj Close'):
    '''
    NOTA: Los datos están ordenados de forma creciente relativo a la fecha

    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start: String en formato YYYY-MM-DD que representa la fecha de inicio de
    los valores.

    end: String en formato YYYY-MM-DD que representa la fecha final

    shortWindow: Entero que representa la ventana de tiempo del EMA de corto plazo

    longWindow: Entero que representa la ventana de tiempo del EMA de largo plazo

    signalWindow: Entero que representa la ventana de tiempo del signalLine

    colName: String que representa el nombre de la columna con la cual se calculará el indicador

    SALIDA
    resultado: Dataframe datos con las columnas relacionadas al indicador MACD
    '''

    #Localiza la fecha de inicio y revisa si hay suficiente información
    indiceInicio=datos[datos['Date']==start].index[0]
    if longWindow > indiceInicio + 1:
        print 'No hay suficiente historia para esta fecha'
        return datos

    #Último índice
    if end=='':
        lastIndex=datos.shape[0] - 1
    else:
        lastIndex=datos[datos['Date']==end].index[0]

    #Nombre de las columnas
    nameShortEMA=colName + "-short-EMA-" + str(shortWindow)
    nameLongEMA=colName + "-long-EMA-" + str(longWindow)
    nameSignal=colName + "-signal-EMA-" + str(signalWindow)
    MACDName= colName + "-MACD-" + "-short-" + str(shortWindow) + "-long-" + str(longWindow)

    #Calcula los EMA de corto y largo plazo, después su diferencia
    shortEMA= exponentialMA(datos,start,end,window=shortWindow,colName=colName,resName=nameShortEMA)
    #shortEMA=shortEMA[nameShortEMA]
    longEMA= exponentialMA(datos,start,end,window=longWindow,colName=colName,resName=nameLongEMA)
    #longEMA=longEMA[nameLongEMA]

    #Diferencia
    MACD=shortEMA[nameShortEMA] - longEMA[nameLongEMA]

    #Calcula signal line
    signalLine=exponentialMA(datos,start,end,window=signalWindow,colName=colName,resName=nameSignal)
    #signalLine=signalLine[nameSignal]

    #Agrega las columnas
    resultado=deepcopy(datos.iloc[indiceInicio:lastIndex +1,:])
    resultado=resultado.reset_index(drop=True)
    resultado[nameShortEMA]=shortEMA[nameShortEMA]
    resultado[nameLongEMA]=longEMA[nameLongEMA]
    resultado[MACDName]=MACD
    resultado[nameSignal]=signalLine[nameSignal]

    #agrega metadatos
    resultado.tipo = 'MACD'
    resultado.MACDName = MACDName

    return resultado

##==============================================================================
## Función para calcular el indicador rate of change (ROC)
##==============================================================================
def roc(datos,start,end='',window=10,colName='Adj Close'):
    '''
    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start, end: strings en formato 'YYYY-MM-DD' representando la fecha de inicio
    y la fecha final respectivamente

    window: Entero que representa la ventan de tiempo a utilizar

    colName: String que representa el nombre de la columna con la cual se calculará el indicador

    SALIDA
    resultado: Dataframe datos con una columna extra conteniendo la información
    del ROC
    '''
    #Localiza la fecha de inicio y revisa si hay suficiente información
    indiceInicio=datos[datos['Date']==start].index[0]
    if window > indiceInicio + 1:
        print 'No hay suficiente historia para esta fecha'
        return datos

    #Último índice
    if end=='':
        lastIndex=datos.shape[0] - 1
    else:
        lastIndex=datos[datos['Date']==end].index[0]


    #En este numpy array guardo los datos del ROC
    ROC=np.zeros(datos.shape[0])

    #La variable aux se utiliza para llena el arreglo
    aux=indiceInicio

    for t in range(0,lastIndex-indiceInicio+1):

        #Extrae los datos del bloque correspondiente y calcula el promedio
        ROC[aux+t] = 100*(datos[colName].iloc[indiceInicio + t] / datos[colName].iloc[indiceInicio - window +1 +t] - 1)

    #Añade la nueva columna
    resName = colName + '-ROC-' + str(window)
    resultado=deepcopy(datos)
    resultado[resName]=ROC

    #Filtra a partir del índice correspondiente a la fecha start
    resultado=resultado.iloc[indiceInicio:lastIndex+1,:]
    resultado=resultado.reset_index(drop=True)

    #añade metadatos
    resultado.tipo = 'roc'
    resultado.resName = resName

    return resultado

##==============================================================================
## Función para calcular Money Flow Index (MFI)
##==============================================================================
def mfi(datos, start, end = '', window = 14):
    '''
    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start, end: strings en formato 'YYYY-MM-DD' representando la fecha de inicio
    y la fecha final respectivamente

    window: Entero que representa la ventan de tiempo a utilizar

    SALIDA
    resultado: Dataframe datos con una columna extra conteniendo la información
    del MFI
    '''

    #Localiza la fecha de inicio y revisa si hay suficiente información
    indiceInicio=datos[datos['Date']==start].index[0]
    if window > indiceInicio + 1:
        print 'No hay suficiente historia para esta fecha'
        return datos

    #Último índice
    if end=='':
        lastIndex=datos.shape[0] - 1
    else:
        lastIndex=datos[datos['Date']==end].index[0]

    #calcula el indicador
    MFI = money_flow_index(datos['High'], datos['Low'], datos['Adj Close'], datos['Volume'], n = window)

    #agrega la nueva columna
    resultado = deepcopy(datos)
    resName = 'MFI-' + str(window)
    resultado[resName] = MFI

    #Filtra a partir del índice correspondiente a la fecha start
    resultado=resultado.iloc[indiceInicio:lastIndex+1,:]
    resultado=resultado.reset_index(drop=True)

    #añade metadatos
    resultado.tipo = 'mfi'
    resultado.resName = resName

    return resultado

##==============================================================================
## Función para calcular un RSI
##==============================================================================
def RSI(datos, start, end, window = 10, colName = 'Adj Close'):
    '''
    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start, end: strings en formato 'YYYY-MM-DD' representando la fecha de inicio
    y la fecha final respectivamente

    window: Entero que representa la ventan de tiempo a utilizar

    colName: String que representa el nombre de la columna con la cual se calculará el indicador

    SALIDA
    resultado: Dataframe datos con una columna extra conteniendo la información
    del indicador
    '''
    #Localiza la fecha de inicio y revisa si hay suficiente información
    indiceInicio=datos[datos['Date']==start].index[0]
    if window > indiceInicio + 1:
        print 'No hay suficiente historia para esta fecha'
        return datos

    #Último índice
    if end=='':
        lastIndex=datos.shape[0] - 1
    else:
        lastIndex=datos[datos['Date']==end].index[0]

    #calcula el indicador
    indicador = rsi(datos[colName], window)

    #agrega la nueva columna
    resultado = deepcopy(datos)
    resName = colName + '-RSI-' + str(window)
    resultado[resName] = indicador

    #Filtra a partir del índice correspondiente a la fecha start
    resultado=resultado.iloc[indiceInicio:lastIndex+1,:]
    resultado=resultado.reset_index(drop=True)

    #añade metadatos
    resultado.tipo = 'rsi'
    resultado.resName = resName

    return resultado

##==============================================================================
## Función para calcular Williams %R
##==============================================================================
def williams(datos, start, end, window = 10):
    '''
    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start, end: strings en formato 'YYYY-MM-DD' representando la fecha de inicio
    y la fecha final respectivamente

    window: Entero que representa la ventan de tiempo a utilizar

    SALIDA
    resultado: Dataframe datos con una columna extra conteniendo la información
    del indicador
    '''
    #Localiza la fecha de inicio y revisa si hay suficiente información
    indiceInicio=datos[datos['Date']==start].index[0]
    if window > indiceInicio + 1:
        print 'No hay suficiente historia para esta fecha'
        return datos

    #Último índice
    if end=='':
        lastIndex=datos.shape[0] - 1
    else:
        lastIndex=datos[datos['Date']==end].index[0]

    #calcula el indicador
    indicador = wr(datos['High'], datos['Low'], datos['Adj Close'], window)

    #agrega la nueva columna
    resultado = deepcopy(datos)
    resName = 'Williams-R-' + str(window)
    resultado[resName] = indicador

    #Filtra a partir del índice correspondiente a la fecha start
    resultado=resultado.iloc[indiceInicio:lastIndex+1,:]
    resultado=resultado.reset_index(drop=True)

    #añade metadatos
    resultado.tipo = 'williams'
    resultado.resName = resName

    return resultado

##==============================================================================
## Función para calcular Ease of Movement
##==============================================================================
def ease_mov(datos, start, end, window = 10):
    '''
    ENTRADA
    datos: Pandas dataframe que contiene al menos una columna de fechas (DATE) y otra
    columna numérica

    start, end: strings en formato 'YYYY-MM-DD' representando la fecha de inicio
    y la fecha final respectivamente

    window: Entero que representa la ventan de tiempo a utilizar

    SALIDA
    resultado: Dataframe datos con una columna extra conteniendo la información
    del indicador
    '''
    #Localiza la fecha de inicio y revisa si hay suficiente información
    indiceInicio=datos[datos['Date']==start].index[0]
    if window > indiceInicio + 1:
        print 'No hay suficiente historia para esta fecha'
        return datos

    #Último índice
    if end=='':
        lastIndex=datos.shape[0] - 1
    else:
        lastIndex=datos[datos['Date']==end].index[0]

    #calcula el indicador
    indicador = ease_of_movement(datos['High'], datos['Low'], datos['Adj Close'], datos['Volume'], window)

    #agrega la nueva columna
    resultado = deepcopy(datos)
    resName = 'Ease-Mov-' + str(window)
    resultado[resName] = indicador

    #Filtra a partir del índice correspondiente a la fecha start
    resultado=resultado.iloc[indiceInicio:lastIndex+1,:]
    resultado=resultado.reset_index(drop=True)

    #añade metadatos
    resultado.tipo = 'ease-mov'
    resultado.resName = resName

    return resultado


##==============================================================================
## Función para crear una lista con la información de distintos indicadores
##==============================================================================
def creaIndicadores (datos, dicc = {}, start = '', end = ''):
    '''
    ENTRADA
    dicc: Un diccionario de la forma
    dicc[key] = {'tipo':'FUNCION','parametros':{'window':10,...}}
    en donde FUNCIÓN corresponde al nombre de alguna de las funciones
    para calcular un indicador en particular.
    parametros es un diccionario con los parámetros del indicador de interés

    start, end: Strings de la format 'YYYY-MM-DD' representando la fecha
    de inicio y final de los datos

    datos: Pandas dataframe con la información del CSV de Yahoo Finance

    SALIDA
    resultado: Lista de pandas dataframes
    '''

    resultado = []
    for key in dicc.keys():
        tipo = dicc[key]['tipo']

        if tipo == 'simpleMA':
            #simpleMA(datos,start,end,window,colName='Adj Close')
            window = dicc[key]['parametros']['window']
            colName = dicc[key]['parametros']['colName']
            resultado.append(simpleMA(datos,start,end,window,colName))

        elif tipo == 'bollinger':
            #bollinger(datos,start,end,window,k,colName='Adj Close')
            window = dicc[key]['parametros']['window']
            colName = dicc[key]['parametros']['colName']
            k = dicc[key]['parametros']['k']
            resultado.append(bollinger(datos,start,end,window,k,colName))

        elif tipo == 'exponentialMA':
            #exponentialMA(datos,start,end,window,colName)
            window = dicc[key]['parametros']['window']
            colName = dicc[key]['parametros']['colName']
            resultado.append(exponentialMA(datos,start,end,window,colName))

        elif tipo == 'MACD':
            #MACD(datos,start,end,shortWindow,longWindow,signalWindow,colName='Adj Close'):
            shortWindow = dicc[key]['parametros']['shortWindow']
            longWindow = dicc[key]['parametros']['longWindow']
            signalWindow = dicc[key]['parametros']['signalWindow']
            colName = dicc[key]['parametros']['colName']
            resultado.append(MACD(datos, start, end, shortWindow, longWindow, signalWindow, colName))

        elif tipo == 'roc':
            #roc(datos,start,end,window,colName='Adj Close')
            window = dicc[key]['parametros']['window']
            colName = dicc[key]['parametros']['colName']
            resultado.append(roc(datos,start,end,window,colName))

        elif tipo == 'mfi':    
            #mfi(datos, start, end , window)
            window = dicc[key]['parametros']['window']
            resultado.append(mfi(datos, start, end, window))

        elif tipo == 'rsi':
            #RSI(datos, start, end, window, colName)
            window = dicc[key]['parametros']['window']
            colName = dicc[key]['parametros']['colName']
            resultado.append(RSI(datos,start,end,window,colName))

        elif tipo == 'williams':
            #williams(datos, start, end, window)
            window = dicc[key]['parametros']['window']
            resultado.append(williams(datos,start,end,window))

        elif tipo == 'ease-mov':
            #ease_mov(datos, start, end, window)
            window = dicc[key]['parametros']['window']
            resultado.append(ease_mov(datos,start,end,window))


    return resultado

##==============================================================================
## Función para combinar una lista de indicadores
##==============================================================================
def combinaIndicadores(listaIndicadores):
    '''
    ENTRADA
    listaIndicadores: Lista creada con la función creaIndicadores

    SALIDA
    resultado: Pandas dataframe con las columnas de interés de cada
    indicador

    '''

    #Aquí se guardará cada columna de interés
    columnas = []

    for element in listaIndicadores:
        if element.tipo == 'simpleMA':
            key = element.resName
            columnas.append(element[key])

        elif element.tipo == 'bollinger':
            key1 = element.resBUp
            key2 = element.resBDown
            columnas.append(element[key1])
            columnas.append(element[key2])

        elif element.tipo == 'exponentialMA':
            key = element.resName
            columnas.append(element[key])

        elif element.tipo == 'MACD':
            key = element.MACDName
            columnas.append(element[key])

        elif element.tipo == 'roc':
            key = element.resName
            columnas.append(element[key])

        elif element.tipo == 'mfi':
            key = element.resName
            columnas.append(element[key])

        elif element.tipo == 'rsi':
            key = element.resName
            columnas.append(element[key])

        elif element.tipo == 'williams':
            key = element.resName
            columnas.append(element[key])

        elif element.tipo == 'ease-mov':
            key = element.resName
            columnas.append(element[key])

    resultado = pd.concat(columnas, axis = 1)

    return resultado

