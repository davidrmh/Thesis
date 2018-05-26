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
    ## datos: Pandas DataFrame creado con leeTabla
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
def etiquetaMetodo1(datos,fechaInicio,fechaFin,hforw=15,hback=7,umbral=0.015):
    '''
    Crea las etiquetas de los datos de entrenamiento
    La idea es mirar hacia adelante hforw periodos, si la variación entre
    el precio en t y el precio en t+hforw rebasa un umbral, recolectar
    las variaciones entre el precio en t y los precios en t-1,t-2,..,t-hback
    estas variaciones serán los atributos.
    La etiqueta es de acuerdo al signo de la variación entre t y t+hforw,
    si es positiva entonces etiqueta 1 (buy), si es negativa entonces etiqueta -1
    (sell), si no rebasa el umbral, etiqueta 0 (hold)

    ENTRADA
    data: Pandas DataFrame. Tabla con los datos del csv

    fechaInicio: String en formato 'YYYY-MM-DD' que representa la fecha de inicio

    fechaFin: String en formato 'YYYY-MM-DD' que representa la fecha fin

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
    indiceFin=datos[datos['Date']==fechaFin].index[0]

    #valida compatilibidad entre fecha inicio entre fechaInicio y hback
    if indiceInicio < inicio:
        print "Revisa la fecha de inicio o el parámetro hback"
        return 0

    atributos=[]
    clases=[]

    #Calcula las variaciones para el conjunto de datos completo
    #Después se filtrará de acuerdo a los parámetros de fecha
    for i in range(indiceInicio,indiceFin+1):
        renglon=[]
        variacion_futuro=datos["Adj Close"][i+hforw-1]/datos["Adj Close"][i]-1
        fecha_aux=datos['Date'].iloc[i]
        #Si se rebasa el umbral
        if variacion_futuro>umbral or variacion_futuro < -1*umbral:
            #Los atributos son los cambios entre el precio en t y t-1,
            # t y t-2,...,t y t-hback
            for j in range(1,hback+1):
                renglon.append(datos["Adj Close"][i]/datos["Adj Close"][i-j]-1)

            atributos.append(renglon)
            if variacion_futuro>0:
                clases.append(1) #Compra
                #print "El dia " + str(fecha_aux) + " se compra"
                #print "Variacion = " + str(variacion_futuro)
            elif variacion_futuro<0:
                #print "El dia " + str(fecha_aux) + " se vende"
                #print "Variacion = " + str(variacion_futuro)
                clases.append(-1) #venta
        else:
            #Los atributos son los cambios entre el precio en t y t-1,
            # t y t-2,...,t y t-hback
            for j in range(1,hback+1):
                renglon.append(datos["Adj Close"][i]/datos["Adj Close"][i-j]-1)
            clases.append(0) #hold
            atributos.append(renglon)

    #Crea el DataFrame
    etiquetas=pd.DataFrame(atributos)
    fechas=datos['Date'].iloc[indiceInicio : (indiceFin +1) ].reset_index(drop=True)
    precios=datos['Adj Close'].iloc[indiceInicio : (indiceFin + 1) ].reset_index(drop=True)
    etiquetas['Clase']=clases #Clase de cada renglón del csv
    #etiquetas=etiquetas.iloc[indiceInicio : (indiceFin + 1 ) ] #filtrado
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

##==============================================================================
## Función para crear el conjunto de prueba
##==============================================================================
def conjuntoPruebaMetodo1 (datos,fechaInicio,fechaFin,percentiles,hback=7):
    '''
    Crea las etiquetas de los datos de prueba
    Se calculan las variaciones entre P_t y P_{t-1}; P_t y P_{t-2}...
    hasta P_t y P_{t-hback}

    Después se utilizan los percentiles calculados con la función etiquetaMetodo1
    para discretizar las variaciones.

    ENTRADA
    data: Pandas DataFrame. Tabla con los datos del csv

    fechaInicio: String en formato 'YYYY-MM-DD' que representa la fecha de inicio

    fechaInicio: String en formato 'YYYY-MM-DD' que representa la fecha final

    percentiles: Lista. Lista de numpy.ndarray con los percentiles

    hback: periodos hacia atrás

    SALIDA:

    '''
    n=datos.shape[0]-1 #Numero de indices validos
    inicio=hback
    indiceInicio=datos[datos['Date']==fechaInicio].index[0]
    indiceFin=datos[datos['Date']==fechaFin].index[0]

    #valida compatilibidad entre fecha inicio entre fechaInicio y hback
    if indiceInicio < inicio:
        print "Revisa la fecha de inicio o el parámetro hback"
        return 0

    atributos=[]

    for i in range(indiceInicio,indiceFin+1):
        renglon=[]
        #Los atributos son los cambios entre el precio en t y t-1,
        # t y t-2,...,t y t-hback
        for j in range(1,hback+1):
            renglon.append(datos["Adj Close"][i]/datos["Adj Close"][i-j]-1)
        atributos.append(renglon)

    #Crea el DataFrame
    fechas=datos['Date'].iloc[indiceInicio:(indiceFin+1)].reset_index(drop=True)
    precios=datos['Adj Close'].iloc[indiceInicio:(indiceFin+1)].reset_index(drop=True)
    datosPrueba=pd.DataFrame(atributos)
    datosPrueba['Date']=fechas
    datosPrueba['Adj Close']=precios
    datosPrueba=datosPrueba.reset_index(drop=True)

    #Etiqueta de acuerdo a los percentiles 25 50 75
    numAtributos=datosPrueba.shape[1]-2 #No considera columnas Date y Adj Close

    #Actualiza la tabla etiquetas de acuerdo
    #a los percentiles

    for i in range(0,numAtributos):
        #indices a modificar
        indicesPercentil25=datosPrueba[datosPrueba[i]<=percentiles[i][0]].index
        indicesPercentil50=datosPrueba[ (datosPrueba[i]>percentiles[i][0]) & (datosPrueba[i]<=percentiles[i][1]) ].index
        indicesPercentil75=datosPrueba[ (datosPrueba[i]>percentiles[i][1]) & (datosPrueba[i]<=percentiles[i][2]) ].index
        indicesPercentil100=datosPrueba[datosPrueba[i]>percentiles[i][2]].index

        #Utilizo loc para evitar el warning que genera iloc
        datosPrueba[i].loc[indicesPercentil25]=1
        datosPrueba[i].loc[indicesPercentil50]=2
        datosPrueba[i].loc[indicesPercentil75]=3
        datosPrueba[i].loc[indicesPercentil100]=4

    return datosPrueba
