# coding: utf-8
import pandas as pd
import numpy as np
import copy as cp
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

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
## Función para obtener un subconjunto de datos de acuerdo a fechas dadas
##==============================================================================
def subconjunto(datos,fechaInicio,fechaFin):
    '''
    ## ENTRADA
    ## datos: Pandas DataFrame creado con leeTabla
    ##
    ##fechaInicio: String en formato 'YYYY-MM-DD' que representa la fecha inicial
    ##
    ## fechaFin: String en formato 'YYYY-MM-DD' que representa la última fecha
    ##
    ## SALIDA
    ## subconjunto: Pandas DataFrame con el subconjunto de datos
    '''

    #Encuentra el índice de inicio
    indiceInicio=datos[datos['Date']==fechaInicio].index[0]
    if not indiceInicio:
        print "Fecha inicio no encontrada"
        return 0
    #Encuentra el índice final
    indiceFin=datos[datos['Date']==fechaFin].index[0]
    if not indiceFin:
        print "Fecha fin no encontrada"
        return 0

    subconjunto = datos[indiceInicio:(indiceFin + 1) ]
    subconjunto=subconjunto.reset_index(drop=True)
    return subconjunto

##==============================================================================
## Función para graficar una estrategia
##==============================================================================
def graficaEstrategia(datos):
    '''
    ENTRADA
    datos: Pandas DataFrame con al menos las columnas Date, Adj Close y Clase

    SALIDA
    Gráfica de la estrategia
    '''
    indicesBuy=datos[datos['Clase']==1].index
    indicesSell=datos[datos['Clase']==-1].index
    indicesHold=datos[datos['Clase']==0].index
    precios=datos['Adj Close']
    fechaInicio=datos['Date'].iloc[0]
    fechaFin=datos['Date'].iloc[-1]
    formatter=DateFormatter('%y-%m-%d')
    fechas=datos['Date']

    fig, ax = plt.subplots()
    plt.plot(fechas,precios,'-',color="black",label="Close Price")
    plt.plot(precios.iloc[indicesBuy],'^',color="black",ms=14,label="Buy")
    plt.plot(precios.iloc[indicesSell],'v',color="black",ms=14,label="Sell",markerfacecolor='None',markeredgewidth=1.5)
    #plt.plot(precios.iloc[indicesHold],'x',color="black",ms=14,label="Espera")
    plt.title("Strategy for the period " + fechaInicio + "  " + fechaFin,{'fontsize':24})
    plt.legend(loc="best",ncol=2,fontsize='xx-large')
    ax.xaxis.set_tick_params(rotation=90, labelsize=20)
    ax.yaxis.set_tick_params(labelsize=20)
    ax.locator_params(tight=True, nbins=10)
    plt.show()



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

            #print "El día " + fecha + " se compran " + str(acciones) + " acciones"
            #print "A un precio de " + str(precioEjecucion)


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

            #print "El día " + fecha + " se venden " + str(acciones)

            #Disminuyen acciones
            acciones=0

            #Se cierra una posición abierta
            flagPosicionAbierta=False

            #Se reinicia el contador de dias
            contLimite=0

            #print "A un precio de " + str(precioEjecucion)

    #Se cierra posición abierta (si la hay)

    if flagPosicionAbierta:
        #cálculo del precio de ejecución
        fecha=prueba['Date'].iloc[numSignals-1]
        precioLow=float(datos[datos['Date']==fecha]['Low'])
        precioHigh=float(datos[datos['Date']==fecha]['High'])
        precioEjecucion=(precioLow + precioHigh)/2.0

        #Aumenta el efectivo
        efectivo=efectivo + acciones*precioEjecucion*(1-comision)

        #print "Se cierra posicion con " + str(acciones) + " acciones"
        #print "a un precio de " + str(precioEjecucion)

        #Disminuyen acciones
        acciones=0

    #Se calcula ganancia final
    ganancia=(efectivo-capital)/capital

    return ganancia,gananciaBH

##==============================================================================
##                      METODO 2 (ALGORITMO GENÉTICO)
##==============================================================================

capital=100000.00
comision=0.25/100
tasa=0.0/100

##==============================================================================
## Función de fitness para el etiquetamiento del método 2
##==============================================================================
def fitnessMetodo2(datos):
    '''
    ENTRADA:
    datos. Pandas DataFrame con los precios y la columna Clase

    SALIDA:
    exceso. Float. Exceso de ganancia
    '''

    acciones=0
    flagPosicionAbierta=False
    ultimoPrecio=0
    precioEjecucion=0
    efectivo=capital
    numSignals=datos.shape[0]

    fechaInicio=datos['Date'].iloc[0]
    fechaFin=datos['Date'].iloc[numSignals-1]
    indiceInicio=datos[datos['Date']==fechaInicio].index[0]
    indiceFin=datos[datos['Date']==fechaFin].index[0]

    ##################################################################
    ##Cálculo de la ganancia siguiendo la estrategia de Buy and Hold##
    ##################################################################

    #Se compra en el segundo día del conjunto de datos
    #esto es para comparar correctamente con la estrategia generada
    precioInicioHigh=float(datos['High'].iloc[indiceInicio + 1])
    precioInicioLow=float(datos['Low'].iloc[indiceInicio + 1])
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

    #No se incluye el último periodo, por eso es numSignals - 1
    #en este periodo se cierra la posición abierta (en caso de haberla)
    for t in range(0,numSignals-1):

        #Auxiliar para la variable variacion
        #para evitar comprar y vender el mismo día
        flagCompraReciente=False

        #Se calcula el precio de ejecución
        #promedio de H y L de t+1
        #También se obtiene el precio de apertura de t+1
        fecha=datos['Date'].iloc[t+1]
        precioLow=float(datos[datos['Date']==fecha]['Low'])
        precioHigh=float(datos[datos['Date']==fecha]['High'])
        precioOpen=float(datos[datos['Date']==fecha]['Open'])
        precioEjecucion=(precioLow + precioHigh)/2.0

        #Cálculo los intereses acumulados hasta el momento
        #PENDIENTE

        #es posible comprar?
        #Se ejecuta compra cuando se tiene dinero y no se había comprado previamente
        if datos['Clase'].iloc[t]==1 and compraPosible(efectivo,precioEjecucion) and not flagPosicionAbierta:

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

            #print "El día " + fecha + " se compran " + str(acciones) + " acciones"
            #print "A un precio de " + str(precioEjecucion)


        #es posible vender?
        #No se permiten ventas en corto por eso acciones > 0
        #Se venden todas las acciones en un sólo momento
        #Se vende cuando:
        #--Hay señal de venta y se tienen acciones
        if acciones>0 and datos['Clase'].iloc[t]==-1:

            #Aumenta el efectivo
            efectivo=efectivo + acciones*precioEjecucion*(1-comision)

            #print "El día " + fecha + " se venden " + str(acciones)

            #Disminuyen acciones
            acciones=0

            #Se cierra una posición abierta
            flagPosicionAbierta=False

            #Se reinicia el contador de dias
            contLimite=0

            #print "A un precio de " + str(precioEjecucion)

    #Se cierra posición abierta (si la hay)

    if flagPosicionAbierta:
        #cálculo del precio de ejecución
        fecha=datos['Date'].iloc[numSignals-1]
        precioLow=float(datos[datos['Date']==fecha]['Low'])
        precioHigh=float(datos[datos['Date']==fecha]['High'])
        precioEjecucion=(precioLow + precioHigh)/2.0

        #Aumenta el efectivo
        efectivo=efectivo + acciones*precioEjecucion*(1-comision)

        #print "Se cierra posicion con " + str(acciones) + " acciones"
        #print "a un precio de " + str(precioEjecucion)

        #Disminuyen acciones
        acciones=0

    #Se calcula ganancia final
    ganancia=(efectivo-capital)/capital

    #Exceso de ganancia (buscamos maximizar esta cantidad)
    exceso=ganancia-gananciaBH

    return exceso

##==============================================================================
## Función para crear la población
##==============================================================================
def creaPoblacion (numPeriodos,popSize,proba=""):
    '''
    ENTRADA
    numPeriodos: Entero. Número de periodos en el subconjunto de datos
    (idealmente datos.shape[0])

    popSize: Entero. Número de individuos en la población

    proba: Lista con numPeriodos elementos, cada uno de ellos es una
    lista con la probabilidad de seleccionar un -1, 0 o 1.
    Por ejemplo para dos periodos [[0.2,0.2,0.6],[0.6,0.4,0]]

    SALIDA
    poblacion. numpy array de popSize x numPeriodos (matriz) cuyo i-ésimo
    renglón representa una posible estrategia para el periodo de interés
    '''
    aux=[]
    poblacion=[]
    for i in range(0,popSize):
        aux=[]
        for t in range(0,numPeriodos):
            if proba=="":
                #aux guarda la información del individuo i
                r=np.random.choice([-1,0,1],size=1)[0]

                if t==(numPeriodos-1):
                    #la última señal es señal de venta
                    r=-1

                aux.append(r)
            else:
                r=np.random.choice([-1,0,1],size=1,p=proba[t])[0]

                if t==(numPeriodos-1):
                    #la última señal es señal de venta
                    r=-1

                aux.append(r)
        poblacion.append(aux)

    poblacion=np.array(poblacion)

    return poblacion



##==============================================================================
## Función para regresar calcular el fitness de cada individuo en la población
##==============================================================================
def fitnessPoblacion (datos,poblacion):
    '''
    ENTRADA
    datos. Pandas DataFrame con los precios

    poblacion: numpy array  (idealmente creado con la función creaPoblacion)

    SALIDA
    fitness: numpy array. arreglo cuya i-ésima entrada representa el fitness
    proporcional (probabilidad) del i-ésimo individuo (i-ésimo renglón de población)

    sinAjuste: numpy array. Arreglo cuya i-ésima entrada representa el fitness del
    i-ésimo individuo (i-ésimo renglón de población)
    '''
    fitness=[]
    auxDatos=cp.deepcopy(datos)

    for i in poblacion:
        auxDatos.loc[:,('Clase')]=i #De esta forma para evitar el warning
        fitness.append(fitnessMetodo2(auxDatos))

    sinAjuste=cp.deepcopy(fitness)
    sinAjuste=np.array(sinAjuste)

    #Normaliza para que todas las entradas sean positivas
    margen=0.001 #para evitar entradas con 0
    probas=np.array(fitness)-np.min(fitness) + margen
    probas=probas/np.sum(probas)

    return probas,sinAjuste

##==============================================================================
## Función para seleccionar los k-mejores individuos de una población
##==============================================================================
def kMejores(poblacion,fitness,k):
    '''
    ENTRADA
    poblacion: numpy array creado con la función creaPoblacion

    fitness: numpy array. Arreglo cuya i-ésima entrada representa el fitness del
    i-ésimo individuo (i-ésimo renglón de población)

    k: Entero mayor o igual a 1

    SALIDA
    mejores: numpy array con los k individuos con mayor fitness
    '''

    #argsort funcion de menor a mayor por eso se utiliza reverse
    aux=list(np.argsort(fitness))
    aux.reverse() #Método destructivo

    #elige los k-mejores
    mejores=poblacion[aux[0:k],:]

    return mejores
##==============================================================================
## Función para actualizar las probabilidades de acuerdo a los k-mejores
##==============================================================================
def actualizaProbabilidades (mejores):
    '''
    ENTRADA
    mejores. numpy array creado con la función kMejores

    SALIDA
    proba: Lista con numPeriodos elementos, cada uno de ellos es una
    lista con la probabilidad de seleccionar un -1, 0 o 1.
    Por ejemplo para dos periodos [[0.2,0.2,0.6],[0.6,0.4,0]]
    '''

    numPeriodos=mejores.shape[1]
    k=mejores.shape[0]
    aux=[] #almacena tres probabilidades(para -1,0 y 1)
    probas=[]
    for t in range(0,numPeriodos):
        aux=[]
        for i in [-1,0,1]:
            #p es la probabilidad de tener el valor i
            #en el periodo t
            p=float(np.sum(mejores[:,t]==i))/k
            aux.append(p)
        probas.append(aux)

    return probas


##==============================================================================
## Función para etiquetar los datos de acuerdo al método 2
##==============================================================================

def etiquetaMetodo2 (datos,numGen=30,popSize=50):
    '''
    Etiqueta los datos utilizando un algoritmo genético que busca
    la combinación de señales compra,venta,hold que generen mayor ganancia

    ENTRADA
    datos: Pandas DataFrame. Conjunto de entrenamiento

    SALIDA
    datos: Pandas DataFrame. Conjunto de entrenamiento con la nueva columna
    Clase, que contiene la estrategia encontrada por el algoritmo genético.

    proba: Lista con numPeriodos elementos, cada uno de ellos es una
    lista con la probabilidad de seleccionar un -1, 0 o 1.
    Por ejemplo para dos periodos [[0.2,0.2,0.6],[0.6,0.4,0]]
    '''

    numPeriodos=datos.shape[0]
    k=int(popSize/2) #k-mejores

    #poblacion inicial
    poblacion=creaPoblacion(numPeriodos,popSize,proba="")

    mejorFitness=-100
    mejorEstrategia=""

    for i in range(0,numGen):

        #Calcula el fitness de la poblacion
        probas,fitness=fitnessPoblacion(datos,poblacion)

        #Encuentra los k mejores
        mejores=kMejores(poblacion,probas,k)

        #Guarda los mejores hasta el momento
        if fitness[np.argmax(fitness)]>mejorFitness:
            mejorFitness=fitness[np.argmax(fitness)]
            mejorEstrategia=mejores[0]

        #actualiza probabilidades
        probas=actualizaProbabilidades(mejores)

        #crea la nueva población
        poblacion=creaPoblacion(numPeriodos,popSize,probas)

        print "Fin de la generacion " + str(i)
        print "Mejor fitness hasta el momento " + str(round(np.max(mejorFitness),6))

    #añade la estrategia del mejor individuo
    datos.loc[:,('Clase')]=mejores[0,:]

    return datos,probas

##==============================================================================
## Función para crear los features para el etiquetado del modelo 2
##==============================================================================
def featuresModelo2 (datos,fechaInicio,fechaFin,hback=7,percentiles=False):
    '''
    La idea es muy similar a la función etiquetaMetodo1
    Crea los atributos de los datos
    La idea es calcular las variaciones entre el precio en t y los precios
    en t-1,t-2,..,t-hback estas variaciones serán los atributos.

    ENTRADA
    data: Pandas DataFrame. Tabla con los datos del csv

    fechaInicio: String en formato 'YYYY-MM-DD' que representa la fecha de inicio

    fechaFin: String en formato 'YYYY-MM-DD' que representa la fecha fin

    hback: periodos hacia atrás

    SALIDA:
    etiquetas: Pandas DataFrame con los atributos discretizados

    continuos: Pandas DataFrame con los atributos continuos

    percentiles: Lista. Lista con np arrays representando los percentiles
    de cada atributo
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
    clases=[]

    #Calcula las variaciones para todo el conjunto de datos
    #Después se filtrará de acuerdo a los parámetros de fecha
    for i in range(indiceInicio,indiceFin+1):
        renglon=[]

        #Los atributos son los cambios entre el precio en t y t-1,
        # t y t-2,...,t y t-hback
        for j in range(1,hback+1):
            renglon.append(datos["Adj Close"][i]/datos["Adj Close"][i-j]-1)
        atributos.append(renglon)

    #Crea el DataFrame
    etiquetas=pd.DataFrame(atributos)
    fechas=datos['Date'].iloc[indiceInicio : (indiceFin +1) ].reset_index(drop=True)
    precios=datos['Adj Close'].iloc[indiceInicio : (indiceFin + 1) ].reset_index(drop=True)
    etiquetas['Date']=fechas
    etiquetas['Adj Close']=precios
    etiquetas=etiquetas.reset_index(drop=True)
    continuos=cp.deepcopy(etiquetas) #Atributos continuos

    #Etiqueta de acuerdo a los percentiles 25 50 75
    numAtributos=etiquetas.shape[1]-3 #No considera columnas Clase, Date y Adj Close

    #Aquí guardo los percentiles 25,50 y 75 de cada columna
    #Es una lista de numpy arrays

    if not percentiles:
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
## Otra función para obtener los atributos
##==============================================================================
def featuresVer2Modelo2(datos,inicio,fin):
    '''
    Es una función sencilla la cual sólo extrae los precios
    Open High Low y Adj Close del día.

    Utilizar este método sólo con clasificadores que admiten atributos
    continuos.

    ENTRADA
    datos: Pandas DataFrame con al menos las columnas Open High Low y Adj Close
    (idealmente el archivo creado con la función leeTabla)

    inicio: String en formato 'YYYY-MM-DD' que indica la fecha de inicio

    fin: String en formato 'YYYY-MM-DD' que indica la fecha final

    SALIDA
    features: Pandas DataFrame con las columnas Open High Low y Adj Close
    '''

    indiceInicio=datos[datos['Date']==inicio].index[0]
    indiceFin=datos[datos['Date']==fin].index[0]
    features=pd.DataFrame()
    features['Open']=datos['Open'].iloc[indiceInicio:(indiceFin+1)]
    features['Low']=datos['Low'].iloc[indiceInicio:(indiceFin+1)]
    features['High']=datos['High'].iloc[indiceInicio:(indiceFin+1)]
    features['Adj Close']=datos['Adj Close'].iloc[indiceInicio:(indiceFin+1)]
    features['Date']=datos['Date'].iloc[indiceInicio:(indiceFin+1)]
    #Esta última columna es para ajustar a la forma que debe de tener
    #la tabla para poder ser utilizada por los modelos del archivo
    #experimentos.py
    features['Adj Close Aux']=datos['Adj Close'].iloc[indiceInicio:(indiceFin+1)]
    features=features.reset_index(drop=True)

    return features


##=============================================================================
## Función para guardar los conjuntos de entrenamiento etiquetados
##=============================================================================
def guardaEntrenamiento(datos,fechas,prefijo="naftrac"):
    '''
    ENTRADA
    prefijo: String. Prefijo del nombre de cada archivo
    El nombre tendrá la siguiente forma
    prefijo + "-" + inicioEntrena + ".csv"

    datos: Pandas DataFrame creado con la función leeTabla
    (csv de Yahoo Finance con toda la información)

    fechas: Pandas DataFrame con las siguientes columnas
    inicioEntrena,finEntrena,inicioPrueba,finPrueba que contiene
    las fechas de inicio y fin de cada conjunto de datos

    SALIDA
    Guarda en el directorio de trabajo los archivos que contienen la
    información de la mejor estrategia a seguir para el conjunto de
    entrenamiento entre las fechas dadas
    '''

    #Número de fechas
    numeroFechas=fechas.shape[0]

    for i in range(0,numeroFechas):
        inicio=fechas.iloc[i,0]
        fin=fechas.iloc[i,1]
        nombreArchivo=prefijo + "-" + str(inicio) + ".csv"
        print "Iniciando con el archivo " + nombreArchivo
        entrenamiento=subconjunto(datos,inicio,fin)
        entrenamiento,proba=etiquetaMetodo2(entrenamiento)

        #Guarda el los datos
        entrenamiento.to_csv(nombreArchivo,index=False)

    return 0
