# coding: utf-8
import pandas as pd
import numpy as np
import copy as cp
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
    etiquetas: Pandas DataFrame con los atributos discretizados

    continuos: Pandas DataFrame con los atributos continuos

    percentiles: Lista. Lista con np arrays representando los percentiles
    de cada atributo

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
    continuos=cp.deepcopy(etiquetas) #Atributos continuos

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


    return etiquetas,continuos,percentiles

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

    etiquetas: Pandas DataFrame con los atributos discretizados

    continuos: Pandas DataFrame con los atributos continuos

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
    continuos=cp.deepcopy(datosPrueba)

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

    return datosPrueba,continuos

##==============================================================================
## Función para determinar si una compra es posible
## se basa en np.floor(efectivo/(precio*(1+comision)))>0
##==============================================================================
def compraPosible(efectivo,precioEjecucion):
    '''
    ENTRADA
    efectivo: Número que representa el dinero disponible
    precioEjecucion: Número que representa el precio en el que se comprará

    SALIDA
    bool: True si es posible comprar False en otro caso
    '''
    if np.floor(efectivo/(precioEjecucion*(1+comision)))>0:
        return True
    else:
        return False

##==============================================================================
## Función para evaluar las predicciones de acuerdo al etiquetamiento
## del Método 1
##==============================================================================
capital=100000.00
comision=0.25/100
tasa=0.0/100

def evaluaMetodo1(datos,prueba,hforw=15,umbral=0.015):
    acciones=0
    flagPosicionAbierta=False
    ultimoPrecio=0
    precioEjecucion=0
    efectivo=capital
    numSignals=len(prueba['Clase'])

    fechaInicio=prueba['Date'].iloc[0]
    fechaFin=prueba['Date'].iloc[numSignals-1]

    ##################################################################
    ##Cálculo de la ganancia siguiendo la estrategia de Buy and Hold##
    ##################################################################
    precioInicioHigh=float(datos[datos['Date']==fechaInicio]['High'])
    precioInicioLow=float(datos[datos['Date']==fechaInicio]['Low'])
    precioInicioMid=(precioInicioLow + precioInicioHigh)/2.0
    acciones=np.floor(efectivo/(precioInicioMid*(1+comision)))
    efectivo=efectivo-precioInicioMid*acciones*(1+comision)

    precioFinHigh=float(datos[datos['Date']==fechaFin]['High'])
    precioFinLow=float(datos[datos['Date']==fechaFin]['Low'])
    precioFinMid=(precioFinLow + precioFinHigh)/2.0


    #Ganancia de intereses PENDIENTE
    #Como es una persona invirtiendo se suponen intereses simples
    fInicio=pd.to_datetime(fechaInicio,format='%Y-%m-%d')
    fFin=pd.to_datetime(fechaFin,format='%Y-%m-%d')
    deltaDias=(fFin-fInicio)/np.timedelta64(1,'D') #Diferencia en días
    #Para los intereses se consideran fines de semana
    intereses=efectivo*tasa*deltaDias/365

    #Vendemos las acciones compradas en el pasado
    #y calculamos el efectivo final asi como la ganancia de Buy and Hold
    efectivo=efectivo + intereses +acciones*precioFinMid*(1-comision)
    gananciaBH=(efectivo - capital)/capital

    ##################################################################
    ###Cálculo de la ganancia siguiendo la estrategia del individuo###
    ##################################################################

    efectivo=capital
    acciones=0
    intereses=0
    fUltimaOperacion=pd.to_datetime(fechaInicio,format='%Y-%m-%d')
    variacion=0

    #Para contar el número de periodos que se repite la señal
    #Cuando contador == hforw, la orden de venta se ejecuta
    contLimite=0




    #No se incluye el último periodo, por eso es numSignals - 1
    #en este periodo se cierra la posición abierta (en caso de haberla)
    for t in range(0,numSignals-1):

        #Auxiliar para la variable variacion
        #para evitar comprar y vender el mismo día
        flagCompraReciente=False

        #Se calcula el precio de ejecución
        #promedio de H y L de t+1
        #También se obtiene el precio de apertura de t+1
        fecha=prueba['Date'].iloc[t+1]
        precioLow=float(datos[datos['Date']==fecha]['Low'])
        precioHigh=float(datos[datos['Date']==fecha]['High'])
        precioOpen=float(datos[datos['Date']==fecha]['Open'])
        precioEjecucion=(precioLow + precioHigh)/2.0

        #Cálculo los intereses acumulados hasta el momento
        #PENDIENTE

        #es posible comprar?
        #Se ejecuta compra cuando se tiene dinero y no se había comprado previamente
        if prueba['Clase'].iloc[t]==1 and compraPosible(efectivo,precioEjecucion) and not flagPosicionAbierta:

            #Se compran más acciones (Se invierte todo el dinero posible)
            acciones=acciones + np.floor(efectivo/(precioEjecucion*(1+comision)))

            #Se reduce el efectivo
            efectivo=efectivo-precioEjecucion*acciones*(1+comision)

            #Se registra una posición abierta
            flagPosicionAbierta=True

            #Se registra el último precio de compra
            ultimoPrecio=precioEjecucion

            #Se actualiza flagCompraReciente
            flagCompraReciente=True

            #Se reinicia contLimite
            contLimite=0

            #Se reinicia variación
            variacion=0

            print "El día " + fecha + " se compran " + str(acciones) + " acciones"
            print "A un precio de " + str(precioEjecucion)


        #Aumenta el contador de días
        #Cierre de posición después de cierto número de días
        #if prueba['Clase'].iloc[t]==1 or prueba['Clase'].iloc[t]==0 :
        #    contLimite=contLimite+1

        #el mercado abre en t+1 al mínimo nivel de ganancia deseado
        if not flagCompraReciente and ultimoPrecio!=0:
            variacion=precioOpen/ultimoPrecio - 1
            contLimite=contLimite + 1

        #es posible vender?
        #No se permiten ventas en corto por eso acciones > 0
        #Se venden todas las acciones en un sólo momento
        #Se vende cuando:
        #--Hay señal de venta
        #--Se llega al límite de dias
        if acciones>0 and (prueba['Clase'].iloc[t]==-1 or contLimite>=hforw or variacion>=umbral):

            #Aumenta el efectivo
            efectivo=efectivo + acciones*precioEjecucion*(1-comision)

            print "El día " + fecha + " se venden " + str(acciones)

            #Disminuyen acciones
            acciones=0

            #Se cierra una posición abierta
            flagPosicionAbierta=False

            #Se reinicia el contador de dias
            contLimite=0

            print "A un precio de " + str(precioEjecucion)

    #Se cierra posición abierta (si la hay)

    if flagPosicionAbierta:
        #cálculo del precio de ejecución
        fecha=prueba['Date'].iloc[numSignals-1]
        precioLow=float(datos[datos['Date']==fecha]['Low'])
        precioHigh=float(datos[datos['Date']==fecha]['High'])
        precioEjecucion=(precioLow + precioHigh)/2.0

        #Aumenta el efectivo
        efectivo=efectivo + acciones*precioEjecucion*(1-comision)

        print "Se cierra posicion con " + str(acciones) + " acciones"
        print "a un precio de " + str(precioEjecucion)

        #Disminuyen acciones
        acciones=0

    #Se calcula ganancia final
    ganancia=(efectivo-capital)/capital

    return ganancia,gananciaBH
