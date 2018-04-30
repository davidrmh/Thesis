# coding: utf-8

import pandas as pd
import numpy as np

##==============================================================================
## Variables globales
## Ventanas de tiempo mayores o iguales a dos
##==============================================================================


##==============================================================================
## Datos de Yaho Finance
## Lee datos, quita los null
## transforma a float
## reinicia los indices
##==============================================================================
def leeTabla(ruta="naftrac.csv"):
    data=pd.read_csv(ruta)
    data=data[data.iloc[:,2]!="null"]
    data['Date']=pd.to_datetime(data['Date'])
    data["Open"]=data["Open"].astype('float')
    data["High"]=data["High"].astype('float')
    data["Close"]=data["Close"].astype('float')
    data["Adj Close"]=data["Adj Close"].astype('float')
    data["Volume"]=data["Volume"].astype('int')
    data=data.reset_index()
    return data

##==============================================================================
## Funciones para obtener parámetros de los indicadores
##==============================================================================
#Número real
def selectNumericalReal(limits):
    '''
    Selecciona un número real entre dos límites
    '''
    return np.random.uniform(limits[0],limits[1],1)[0]

#Número entero
def selectNumericalInteger(limits):
    '''
    Selecciona un número entero entre dos límites
    '''
    return np.random.choice(range(limits[0],limits[1]+1),1)[0]

#Categoría
def selectCategorical(kinds):
    '''
    Selecciona una categoría de una lista
    '''
    return np.random.choice(kinds,1)[0]
##==============================================================================
## Moving average quitando NA
##==============================================================================
def movingAverage(data,fechaInicio,window,tipoPrecio='Close'):
    '''
    Calcula un promedio móvil

    ENTRADA:
    data: pandas dataframe que se obtiene con la función leeTabla
    fechaInicio: string de la forma 'YYYY-MM-DD'
    window: ventana de tiempo
    tipoPrecio: Precio a utilizar, por ejemplo Cierre

    SALIDA:
    resultado: pandas data frame con columnas Date y MA
    Regresa 0 si no hay suficiente información
    '''

    #Obtiene la serie de acuerdo al tipo de precio
    serie=data[tipoPrecio]

    #último índice
    ultimoIndice=len(serie)-1

    #índice de inicio
    inicio=data[data['Date']==fechaInicio].index[0]

    #Valida que exista historia suficiente para calcular el indicador
    if window>inicio+1:
        return 0

    #Aquí guardo el MA
    MA=[]

    #Aquí guardo las fechas
    fechas=[]

    for t in range(0,ultimoIndice - inicio+1):
        MA.append(np.nanmean(serie.iloc[inicio-window+1+t:inicio + t+1]))
        fechas.append(data['Date'].iloc[inicio+t])

    #Agrega en un dataframe
    MA=pd.Series(MA)
    fechas=pd.Series(fechas)
    resultado=pd.DataFrame(data={"Date":fechas,"MA":MA})

    return resultado

##==============================================================================
## Calcula bandas de Bollinger
## utiliza un promedio movil simple para ser consistentes con el cálculo
## de la desviación estándar
## La desviación estándar se calcula dividiendo entre N-1
##==============================================================================
def bollinger(data,fechaInicio,window,k=2,tipoPrecio='Close'):
    '''
    ENTRADA
    data: pandas dataframe que se obtiene con la función leeTabla
    fechaInicio: string de la forma 'YYYY-MM-DD'
    window: window: ventana de tiempo
    k: número de desviaciones estándar
    tipoPrecio: Precio a utilizar, por ejemplo Cierre

    SALIDA
    resultado: Pandas DataFrame con columnas Date, MA, LowB,UpB
    Regresa 0 si no hay suficiente información
    '''

    #Obtiene la serie de acuerdo al tipo de precio
    serie=data[tipoPrecio]

    #último índice
    ultimoIndice=len(serie)-1

    #índice de inicio
    inicio=data[data['Date']==fechaInicio].index[0]

    #Valida que exista historia suficiente para calcular el indicador
    if window>inicio+1:
        return 0

    #MA y bandas
    MA=[]
    low=[]
    up=[]

    #auxiliares
    media=0
    desviacion=0

    #Aquí guardo las fechas
    fechas=[]

    for t in range(0,ultimoIndice - inicio+1):
        media=np.nanmean(serie.iloc[inicio-window+1+t:inicio + t+1])
        desviacion=np.nanstd(serie.iloc[inicio-window+1+t:inicio + t+1],ddof=1)
        MA.append(media)
        low.append(media - k*desviacion)
        up.append(media + k*desviacion)
        fechas.append(data['Date'].iloc[inicio+t])

    #Agrega en un dataframe
    MA=pd.Series(MA)
    low=pd.Series(low)
    up=pd.Series(up)
    fechas=pd.Series(fechas)
    resultado=pd.DataFrame(data={"Date":fechas,"MA":MA,"UpBand":up,"LowBand":low})

    return resultado

##==============================================================================
## Moving Average Crossover
## Calcula dos promedios móviles (simples)
##==============================================================================
def movingAverageCross(data,fechaInicio,windowShort,windowLong,tipoPrecio='Close'):
    '''
    Calcula dos promedios móviles
    ENTRADA
    data: pandas DataFrame creado con leeTabla
    fechaInicio: string de la forma 'YYYY-MM-DD'
    windowShort: ventana de tiempo más pequeña
    windowLong: ventana de tiempo más grande
    tipoPrecio: tipo de precio a utilizar

    SALIDA
    resultado: Pandas DataFrame con columnas Date, shortMA, longMA
    Regresa 0 si no hay suficiente información
    '''

    MAshort=movingAverage(data,fechaInicio,windowShort,tipoPrecio)
    MAlong=movingAverage(data,fechaInicio,windowLong,tipoPrecio)

    #Revisa si fue posible calcular ambos indicadores
    if len(MAshort)==1 or len(MAlong)==0:
        return 0

    fechas=MAshort['Date']
    MAshort=MAshort['MA']
    MAlong=MAlong['MA']
    resultado=pd.DataFrame(data={"Date":fechas,"shortMa":MAshort, "longMA":MAlong})

    return resultado
