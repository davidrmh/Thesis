# coding: utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

##==============================================================================
## Lee datos, quita los null
## transforma a float
## reinicia los indices
## Datos de Yahoo Finance (fechas en orden ascendiente)
##==============================================================================
def leeTabla(ruta="naftrac.csv"):
    '''
    Lee los datos del archivo en ruta
    El archivo debe de ser un csv descargado de Yahoo finance
    Regresa un pandas dataframe
    '''
    data=pd.read_csv(ruta,dtype=str)
    data=data[data.iloc[:,2]!="null"]
    data=data[data.iloc[:,2]!=0]
    data["Open"]=data["Open"].astype('float')
    data["High"]=data["High"].astype('float')
    data["Close"]=data["Close"].astype('float')
    data["Adj Close"]=data["Adj Close"].astype('float')
    data["Volume"]=data["Volume"].astype('int')
    data=data.reset_index(drop=True)
    return data
##==============================================================================
## Función para obtener el conjunto de entrenamiento
##==============================================================================
def entrenamientoDataSet(datos,fechaFin):
    '''
    ## ENTRADA
    ## datos: Pqandas DataFrame creado con leeTabla
    ##
    ## fechaFin: String en formato 'YYYY-MM-DD' que representa la última fecha
    ## del conjunto de entrenamiento
    ##
    ## SALIDA
    ## entrenamiento: Pandas DataFrame con los datos de entrenamiento
    '''

    #Encuentra el índice correspondiente a la fechaFin
    #Validando que la fecha se encuentre en los datos
    if len(datos[datos['Date']==fechaFin])!= 0:
        indiceFin=datos[datos['Date']==fechaFin].index[0]
    else:
        print "Fecha no encontrada, elige una nueva"
        return 0

    #Se incluye la fechaFin en el conjunto de entrenamiento
    entrenamiento=datos.iloc[0:(indiceFin+1)]

    return entrenamiento

##==============================================================================
##                           MÉTODO 1
##==============================================================================
def etiquetaEntrenamiento(datos,fechaInicio,hforw=15,hback=7,umbral=0.00):
    '''
    Crea las etiquetas del conjunto de ENTRENAMIENTO
    La idea es mirar hacia adelante hforw periodos, si la variación entre
    el precio en t y el precio en t+hforw rebasa un umbral, recolectar
    las variaciones entre el precio en t y los precios en t-1,t-2,..,t-hback
    estas variaciones serán los atributos.
    La etiqueta es de acuerdo al signo de la variación entre t y t+hforw,
    si es positiva entonces etiqueta 1 (buy), si es negativa entonces etiqueta -1
    (sell), si no rebasa el umbral, etiqueta 0 (hold)

    ENTRADA
    data: El conjunto de ENTRENAMIENTO creado con entrenamientoDataSet

    fechaInicio: String en formato 'YYYY-MM-DD' que representa la fecha de inicio

    hforw: Periodos hacia adelante

    hback: periodos hacia atrás

    umbral: Cambio mínimo (hacia arriba o hacia abajo) para que sea considerado
    un cambio significativo

    SALIDA:

    '''
    n=datos.shape[0]-1 #Numero de indices validos
    fin=datos.shape[0]-hforw-1 #Ultimo indice valido considerando forward look
    inicio=hback
    indiceInicio=datos[datos['Date']==fechaInicio].index[0]

    #valida compatilibidad entre fecha inicio entre fechaInicio y hback
    if indiceInicio < inicio:
        print "Revisa la fecha de inicio o el parámetro hback"
        return 0

    atributos=[]
    clases=[]

    for i in range(inicio,fin+1):
        renglon=[]
        #Si se rebasa el umbral
        if abs(datos["Adj Close"][i+hforw]/datos["Adj Close"][i]-1)>umbral:
            #Los atributos son los cambios entre el precio en t y t-1,
            # t y t-2,...,t y t-hback
            for j in range(1,hback+1):
                renglon.append(datos["Adj Close"][i]/datos["Adj Close"][i-j]-1)

            atributos.append(renglon)
            if (datos["Adj Close"][i+hforw]/datos["Adj Close"][i]-1)>0:
                clases.append(1) #Compra
            elif (datos["Adj Close"][i+hforw]/datos["Adj Close"][i]-1)<0:
                clases.append(-1) #venta
        else:
            #Los atributos son los cambios entre el precio en t y t-1,
            # t y t-2,...,t y t-hback
            for j in range(1,hback+1):
                renglon.append(datos["Adj Close"][i]/datos["Adj Close"][i-j]-1)
            clases.append(0) #hold
            atributos.append(renglon)

    #Crea el DataFrame
    fechas=datos['Date'].iloc[indiceInicio:]
    precios=datos['Adj Close'].iloc[indiceInicio:]
    etiquetas=pd.DataFrame(atributos)
    etiquetas['Clase']=clases
    etiquetas=etiquetas.iloc[indiceInicio:]
    etiquetas['Date']=fechas
    etiquetas['Adj Close']=precios
    etiquetas=etiquetas.reset_index(drop=True)

    #Etiqueta de acuerdo a los percentiles 25 50 75
    numAtributos=etiquetas.shape[1]-3 #No considera columnas Clase, Date y Adj Close

    #Aquí guardo los percentiles 25,50 y 75 de cada columna
    #Es una lista de numpy arrays
    percentiles=[]

    for i in range(0,numAtributos):
        percentiles.append(np.percentile(etiquetas[i],q=[25,50,75]))

    #Actualiza la tabla etiquetas de acuerdo
    #a los percentiles

    for i in range(0,numAtributos):
        #indices a modificar
        indicesPercentil25=etiquetas[etiquetas[i]<=percentiles[i][0]].index
        indicesPercentil50=etiquetas[ (etiquetas[i]>percentiles[i][0]) & (etiquetas[i]<=percentiles[i][1]) ].index
        indicesPercentil75=etiquetas[ (etiquetas[i]>percentiles[i][1]) & (etiquetas[i]<=percentiles[i][2]) ].index
        indicesPercentil100=etiquetas[etiquetas[i]>percentiles[i][2]].index

        #Utilizo loc para evitar el warning que genera iloc
        etiquetas[i].loc[indicesPercentil25]=1
        etiquetas[i].loc[indicesPercentil50]=2
        etiquetas[i].loc[indicesPercentil75]=3
        etiquetas[i].loc[indicesPercentil100]=4


    return etiquetas,percentiles
