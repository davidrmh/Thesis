# coding: utf-8

import pandas as pd
import numpy as np

##==============================================================================
## Datos de Yaho Finance
## Lee datos, quita los null
## transforma a float
## reinicia los indices
##==============================================================================
def leeTabla(ruta="naftrac.csv"):
    data=pd.read_csv(ruta)
    data=data[data.iloc[:,2]!="null"]
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
def movingAverage(data,window,tipoPrecio='Close'):
    '''
    Calcula un promedio móvil

    ENTRADA:
    data: pandas dataframe que se obtiene con la función leeTabla
    window: ventana de tiempo
    tipoPrecio: Precio a utilizar, por ejemplo Cierre

    SALIDA:
    MA: pandas data series con el promedio móvil en t
    t inicia en el índice window-1
    '''

    #Obtiene la serie de acuerdo al tipo de precio
    serie=data[tipoPrecio]

    #último índice
    ultimoIndice=len(serie)-1

    #Valida que la ventana de tiempo sea correcta
    #(no necesite más datos de los que tiene)
    if window>ultimoIndice:
        return 0

    #índice de inicio
    inicio=window-1

    #Aquí guardo el MA
    MA=[]

    #Aquí guardo las fechas
    fechas=[]

    for t in range(0,ultimoIndice-window+2):
        MA.append(np.nanmean(serie.iloc[t:window+t]))
        fechas.append(data['Date'].iloc[window-1+t])

    #Agrega en un dataframe
    MA=pd.Series(MA)
    fechas=pd.Series(fechas)
    resultado=pd.DataFrame(data={"Date":fechas,"MA":MA})

    return resultado
