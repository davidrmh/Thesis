# coding: utf-8

import pandas as pd
import numpy as np
from copy import deepcopy

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
    data=data.reset_index(drop=True)
    return data


##==============================================================================
## Variables globales
## Ventanas de tiempo mayores o iguales a dos
##==============================================================================
tiposIndicadores=["BB","MA","MACross"]
tiposPrecios=["Adj Close"] #Por el momento utilizaré cierres ajustados
numeroMaximoIndicadores=5 #Máximo de indicadores por individuo
fechaInicio='2015-01-02'
ventanasTiempoBollinger=[20,30,40,50,100,150]
ventanasTiempoMA=[5,10,50,100,200]
numeroMaximoDesviaciones=2.0 #El parámetro k en bandas de Bollinger
datos=leeTabla()
capitalInicial=100000 #cien mil pesos (mínimo solicitado por las casas de bolsa)
tasa=0.00 #tasa que te da el banco 1% (idea: Promedio CETES - X BP)
comision=0.25/100 #Comisión del 25% sobre el monto total negociado
semilla=0 #Para obtener resultados reproducibles

##==============================================================================
## Funciones para obtener parámetros de los indicadores
##==============================================================================
#Número real
def selectNumericalReal(limits):
    '''
    Selecciona un número real entre dos límites
    '''
    #np.random.seed(semilla)
    return np.random.uniform(limits[0],limits[1],1)[0]

#Número entero
def selectNumericalInteger(limits):
    '''
    Selecciona un número entero entre dos límites
    '''
    #np.random.seed(semilla)
    return np.random.choice(range(limits[0],limits[1]+1),1)[0]

#Categoría
def selectCategorical(kinds):
    '''
    Selecciona una categoría de una lista
    '''
    #np.random.seed(semilla)
    return np.random.choice(kinds,1)[0]

##==============================================================================
## Señales Moving Average
## identifica las señales de acuerdo a un indicador MA
##==============================================================================
def signalMA(precioActual,precioAnterior,mediaActual,mediaAnterior):
    '''
    ENTRADA
    precioActual: Número que representa el precio en el tiempo t
    precioAnterior: Número que representa el precio en el tiempo t-1
    mediaActual: Número que representa el promedio móvil en el tiempo t
    mediaAnterior: Número que representa el promedio móvil en el tiempo t-1

    SALIDA:
    signal: 1=compra, 0=hold, -1=venta.
    '''
    #es señal de compra?
    if precioAnterior < mediaAnterior and precioActual>mediaActual:
        return 1

    #es señal de venta?
    elif precioAnterior > mediaAnterior and precioActual<mediaActual:
        return -1

    #se señal de espera?
    else:
        return 0

##==============================================================================
## Moving average quitando NA
## La columna Signal corresponde a la señal de operación
## 1=Compra, 0=Hold, -1=Venta
##==============================================================================
def movingAverage(data,fechaInicio,window,tipoPrecio='Adj Close'):
    '''
    Calcula un promedio móvil

    ENTRADA:
    data: pandas dataframe que se obtiene con la función leeTabla
    fechaInicio: string de la forma 'YYYY-MM-DD'
    window: ventana de tiempo
    tipoPrecio: Precio a utilizar, por ejemplo Cierre

    SALIDA:
    resultado: pandas data frame con columnas Date, MA y Signal
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

    #Señales
    #1: compra
    #0: hold
    #-1: venta
    signal=[]

    #auxiliares
    precioActual=0
    precioAnterior=0
    mediaActual=0
    mediaAnterior=0
    flagPrimera=True

    for t in range(0,ultimoIndice - inicio+1):
        mediaActual=np.nanmean(serie.iloc[inicio-window+1+t:inicio + t+1])
        MA.append(mediaActual)

        #identifica señales
        #El primer tiempo siempre es hold
        if not flagPrimera: #si no es la primera señal
            precioActual=serie.iloc[inicio+t]
            precioAnterior=serie.iloc[inicio+t-1]
            signal.append(signalMA(precioActual,precioAnterior,mediaActual,mediaAnterior))

        else:
            flagPrimera=False
            signal.append(0)

        fechas.append(data['Date'].iloc[inicio+t])
        mediaAnterior=mediaActual

    #Agrega en un dataframe
    MA=pd.Series(MA)
    fechas=pd.Series(fechas)
    signal=pd.Series(signal)
    resultado=pd.DataFrame(data={"Date":fechas,"MA":MA,"Signal":signal})

    return resultado

##==============================================================================
## Señales bandas de Bollinger
## Identifica las señales de operación de acuerdo a las bandas de Bollinger
##==============================================================================
def signalBollinger(precioActual,precioAnterior,bandaUpActual,bandaUpAnterior,bandaLowActual,bandaLowAnterior):
    '''
    ENTRADA
    precioActual: Número que representa el precio en el tiempo t
    precioAnterior: Número que representa el precio en el tiempo t-1
    bandaUpActual: Número que representa el valor de la banda superior en t
    bandaUpAnterior: Número que representa el valor de la banda superior en t-1
    bandaLowActual: Número que representa el valor de la banda inferior en t
    bandaLowAnterior: Número que representa el valor de la banda inferior en t-1

    SALIDA
    1=compra, 0=hold, -1=venta.
    '''
    if precioActual > bandaUpActual and precioAnterior > bandaUpAnterior:
        return 1
    elif precioActual > bandaLowActual and precioAnterior < bandaLowAnterior:
        return 1
    elif precioActual < bandaLowActual and precioAnterior < bandaLowAnterior:
        return -1
    elif precioActual < bandaUpActual and precioAnterior > bandaUpAnterior:
        return -1
    else:
        return 0

##==============================================================================
## Calcula bandas de Bollinger
## utiliza un promedio movil simple para ser consistentes con el cálculo
## de la desviación estándar
## La desviación estándar se calcula dividiendo entre N-1
##==============================================================================
def bollinger(data,fechaInicio,window,k=2,tipoPrecio='Adj Close'):
    '''
    ENTRADA
    data: pandas dataframe que se obtiene con la función leeTabla
    fechaInicio: string de la forma 'YYYY-MM-DD'
    window: window: ventana de tiempo
    k: número de desviaciones estándar
    tipoPrecio: Precio a utilizar, por ejemplo Cierre

    SALIDA
    resultado: Pandas DataFrame con columnas Date, MA, LowB,UpB y Signal
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
    precioActual=0
    precioAnterior=0
    bandaUpActual=0
    bandaUpAnterior=0
    bandaLowActual=0
    bandaLowAnterior=0
    flagPrimera=True
    media=0
    desviacion=0
    signal=[]

    #Aquí guardo las fechas
    fechas=[]

    for t in range(0,ultimoIndice - inicio+1):
        media=np.nanmean(serie.iloc[inicio-window+1+t:inicio + t+1])
        desviacion=np.nanstd(serie.iloc[inicio-window+1+t:inicio + t+1],ddof=1)
        bandaUpActual=media + k*desviacion
        bandaLowActual=media - k*desviacion

        if not flagPrimera:
            precioActual=serie.iloc[inicio+t]
            precioAnterior=serie.iloc[inicio+t-1]
            signal.append(signalBollinger(precioActual,precioAnterior,bandaUpActual,bandaUpAnterior,bandaLowActual,bandaLowAnterior))
        else:
            signal.append(0)
            flagPrimera=False

        MA.append(media)
        low.append(bandaLowActual)
        up.append(bandaUpActual)

        fechas.append(data['Date'].iloc[inicio+t])
        bandaUpAnterior=bandaUpActual
        bandaLowAnterior=bandaLowActual

    #Agrega en un dataframe
    MA=pd.Series(MA)
    low=pd.Series(low)
    up=pd.Series(up)
    signal=pd.Series(signal)
    fechas=pd.Series(fechas)
    resultado=pd.DataFrame(data={"Date":fechas,"MA":MA,"UpBand":up,"LowBand":low,"Signal":signal})

    return resultado

##==============================================================================
## Señales para Moving Averages Crossover
##==============================================================================
def signalMACross(diferencias):
    '''
    ENTRADA
    diferencias: pandas Series que se calcula como ShortMA - LongMA

    SALIDA
    signal: lista con las señales correspondientes
    signal[0]==0 siempre
    '''

    signal=[0]
    n=len(diferencias)

    for t in range(1,n):
        if diferencias.iloc[t] > 0 and diferencias.iloc[t-1]<0:
            signal.append(1)
        elif diferencias.iloc[t] < 0 and diferencias.iloc[t-1]>0:
            signal.append(-1)
        else:
            signal.append(0)
    return signal
##==============================================================================
## Moving Averages Crossover
## Calcula dos promedios móviles (simples)
##==============================================================================
def movingAveragesCross(data,fechaInicio,windowShort,windowLong,tipoPrecio='Adj Close'):
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
    diferencias=MAshort - MAlong
    signal=signalMACross(diferencias)
    resultado=pd.DataFrame(data={"Date":fechas,"shortMa":MAshort, "longMA":MAlong, "Diferencia":diferencias, "Signal":signal})

    return resultado

##==============================================================================
## Clase indicador
## podría cambiar el 200 por una variable goblal, pero en la práctica
## este número es el horizonte más amplio utilizado.
##==============================================================================
class indicador:
    '''
    Crea de manera aleatoria un indicador técnico
    '''

    def __init__(self,datos,fechaInicio):
        '''
        Inicializa el indicador
        datos: pandas DataFrame creado con la función leeTabla
        fechaInicio: string con la fecha de inicio 'YYYY-MM-DD'
        '''
        #Tipo de indicador (string)
        self.tipo=selectCategorical(tiposIndicadores)

        #bandas de Bollinger
        if self.tipo=="BB":
            #Ventana de tiempo (entero)
            self.ventanaTiempo=selectNumericalInteger([2,200])

            #Parámetro k (real)
            self.k=selectNumericalReal([0.01,numeroMaximoDesviaciones])

            #Tipo de precio (string)
            self.tipoPrecio=selectCategorical(tiposPrecios)

            #Datos relativos al indicador (DataFrame)
            #Aquí se guardarán las señales
            self.datos=bollinger(datos,fechaInicio,self.ventanaTiempo,k=self.k,tipoPrecio=self.tipoPrecio)

        #Moving Average
        if self.tipo=="MA":

            #Ventana de tiempo (entero)
            self.ventanaTiempo=selectNumericalInteger([2,200])

            #Tipo de precio (string)
            self.tipoPrecio=selectCategorical(tiposPrecios)

            self.datos=movingAverage(datos,fechaInicio,self.ventanaTiempo,tipoPrecio=self.tipoPrecio)

        #Moving averages crossover
        if self.tipo=="MACross":
            self.ventana1=selectNumericalInteger([2,200])
            self.ventana2=selectNumericalInteger([2,200])
            self.ventanaTiempoCorto=min(self.ventana1,self.ventana2)
            self.ventanaTiempoLargo=max(self.ventana1,self.ventana2)

            #Tipo de precio (string)
            self.tipoPrecio=selectCategorical(tiposPrecios)

            self.datos=movingAveragesCross(datos,fechaInicio,self.ventanaTiempoCorto,self.ventanaTiempoLargo,tipoPrecio=self.tipoPrecio)

##==============================================================================
## Función para crear un individuo
## la longitud es aleatoria entre 1 y numeroMaximoIndicadores
##==============================================================================
def creaIndividuo(datos,fechaInicio,numeroMaximoIndicadores=5):
    '''
    Crea un individuo, el cual estará representado por una lista
    con un número aleatorio de indicadores

    ENTRADA
    datos: pandas DataFrame creado con la función leeTabla
    fechaInicio: string con la fecha de inicio 'YYYY-MM-DD'
    numeroMaximoIndicadores: Entero que representa la longitud máxima del
    individuo

    SALIDA
    resultado: lista cuya i-ésima entrada es un objeto de la clase indicador
    '''

    n=selectNumericalInteger([1,numeroMaximoIndicadores])
    resultado=[]
    for i in range(0,n):
        resultado.append(indicador(datos,fechaInicio))

    return resultado

##==============================================================================
## Función para obtener la señal de operación
## utilizando el voto mayoritario para los indicadores de un individuo
##==============================================================================
def votoMayoria(individuo):
    '''
    ENTRADA
    individuo: objeto creado con la función creaIndividuo

    SALIDA
    resultado: pandas DataFrame con columnas Date y Signal
    '''
    #Aquí guardo la decisión final
    finalSignal=[]

    #Auxiliar para crear la el DataFrame con las señales
    signals=[]

    for indicador in individuo:
        signals.append(indicador.datos['Signal'])

    #Dataframe cuya i-ésima columna corresponde
    #a las señales del i-ésimo indicador
    signals=pd.concat(signals,axis=1)

    #auxiliares
    cuentaBuy=0
    cuentaSell=0
    cuentaHold=0
    n=signals.shape[0]

    for t in range(0,n):
        renglon=list(signals.iloc[t])
        cuentaBuy=renglon.count(1)
        cuentaSell=renglon.count(-1)
        cuentaHold=renglon.count(0)

        if cuentaBuy==cuentaHold==cuentaSell:
            #Si no hay mayoría entonces hold
            finalSignal.append(0)
        elif cuentaBuy>cuentaHold and cuentaBuy > cuentaSell:
            #Hay mayoría de señales buy
            finalSignal.append(1)
        elif cuentaHold>cuentaBuy and cuentaHold>cuentaSell:
            #Hay mayoría de señales hold
            finalSignal.append(0)
        elif cuentaSell>cuentaBuy and cuentaSell>cuentaHold:
            #Hay mayoría de señales sell
            finalSignal.append(-1)
        #Los casos de siguientes es para considerar empate entre dos señales
        #Se selecciona al azar alguna de las mayoritarias
        elif cuentaBuy==cuentaSell and cuentaBuy > cuentaHold:
            finalSignal.append(np.random.choice([-1,1],1)[0])
        elif cuentaBuy==cuentaHold and cuentaBuy > cuentaSell:
            finalSignal.append(np.random.choice([0,1],1)[0])
        elif cuentaSell==cuentaHold and cuentaSell > cuentaBuy:
            finalSignal.append(np.random.choice([-1,0],1)[0])


    fechas=individuo[0].datos['Date']
    finalSignal=pd.Series(finalSignal)
    resultado=pd.DataFrame(data={'Date':fechas,'Signal':finalSignal})

    return resultado

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
## Función de aptitud
## 1. Crear un subconjunto que inicie en la fecha de inicio
## 2. Calcular B&H (considerando intereses y comisiones)
## 3. Obtener voto de mayoría
## Si se compra y se tiene efectivo
##   efectivo se reduce y acciones aumentan
## Si se vende y se tienen acciones
##   efectivo aumenta y acciones se reducen
## Si se espera y se tiene efectivo
##   efectivo gana intereses
## Precio de ejecución = (Low + High)/2 en t+1 (t el día de la señal)
## Ganacia de intereses = (t-tUltima)/252 * r_{tUltima} * efectivo_{tUltima}
## La tasa de interés añade una dificultad adicional (de momento fijarla a 1%)
## Al momento de comprar, para evitar quedar con dinero en saldo negativo
## se necesitan comprar Acciones = np.floor(efectivo / precio*(1+comision))
## de esta forma no nos quedamos con dinero
## Comisión 0.25% del total de la transacción
## Nuevo balance si se compra
## efectivo = efectivo - precio ejecución * acciones *(1+comision)
## Acciones=Acciones antes + Acciones adquiridas
## Nuevo balance si se vende
## Nuevo efectivo = efectivo + precio ejecución * acciones *(1-comision)
## Acciones = Acciones antes - acciones vendidas
## Cerrar posiciones abiertas en la última fecha, es decir, se deben de
## vender todas las acciones y sólo quedarse con el efectivo
## Ganancia estrategia = (capital final - capital inicial)/cap inicial
##==============================================================================
def fitness(datos,individuo,fechaInicio):
    '''
    Función para calcular la aptitud de un individuo

    ENTRADA
    datos: Pandas DataFrame creado con leeTabla
    individuo: lista creada con creaIndividuo
    fechaInicio: string de la forma 'YYYY-MM-DD'

    SALIDA
    gananciaBH: Ganancia de la estrategia Buy and Hold
    gananciaInd: Ganancia del individuo
    exceso: Diferencia entre gananciaInd y gananciaBH
    '''

    ##################################################################
    ##Cálculo de la ganancia siguiendo la estrategia de Buy and Hold##
    ##################################################################
    efectivo=float(capitalInicial)
    indiceInicio=datos[datos['Date']==fechaInicio].index[0]
    indiceFin=datos['Date'].shape[0]-1

    #Precio de ejecución al inicio del periodo
    #es el promedio entre el máximo y el mínimo del día
    precioInicioLow=float(datos['Low'].iloc[indiceInicio])
    precioInicioHigh=float(datos['High'].iloc[indiceInicio])
    precioInicioMid=(precioInicioLow+precioInicioHigh)/2

    #Precio de ejecución al final del periodo
    #es el promedio entre el máximo y el mínimo del día
    precioFinLow=float(datos['Low'].iloc[indiceFin])
    precioFinHigh=float(datos['High'].iloc[indiceFin])
    precioFinMid=(precioFinLow+precioFinHigh)/2

    #Calculamos las acciones para comprar de tal forma que no
    #quedemos debiendo dinero.
    accionesCompra=np.floor(efectivo/(precioInicioMid*(1+comision)))
    efectivo=efectivo-precioInicioMid*accionesCompra*(1+comision)

    #Ganancia de intereses
    #Como es una persona invirtiendo se suponen intereses simples
    fechaFin=datos['Date'].iloc[indiceFin] #fechaFin como string
    fInicio=pd.to_datetime(fechaInicio,format='%Y-%m-%d')
    fFin=pd.to_datetime(fechaFin,format='%Y-%m-%d')
    deltaDias=(fFin-fInicio)/np.timedelta64(1,'D') #Diferencia en días
    #Para los intereses se consideran fines de semana
    intereses=efectivo*tasa*deltaDias/365

    #Vendemos las acciones compradas en el pasado
    #y calculamos el efectivo final asi como la ganancia de Buy and Hold
    efectivo=efectivo + intereses +accionesCompra*precioFinMid*(1-comision)
    gananciaBH=(efectivo - capitalInicial)/capitalInicial

    ##################################################################
    ###Cálculo de la ganancia siguiendo la estrategia del individuo###
    ##################################################################
    #Señales considerar el voto de la mayoría
    signals=votoMayoria(individuo)

    #efectivo
    efectivo=capitalInicial

    #fecha última operación (auxiliar para el cálculo de los intereses)
    #fecha actual (auxiliar para el cálculo de los intereses)
    fUltimaOperacion=pd.to_datetime(fechaInicio,format='%Y-%m-%d')
    fActual=pd.to_datetime(fechaInicio,format='%Y-%m-%d')

    #auxiliar para cerrar posiciones abiertas al final del periodo
    flagPosicionAbierta=False

    #auxiliar para tener coincidencia entre los índices de los datos y
    #los índices de signals
    datosFiltrados=datos.iloc[indiceInicio:].reset_index(drop=True)

    #Número de índices válidos
    n=datosFiltrados.shape[0]-1

    #Acciones compradas
    accionesCompra=0

    #intereses
    intereses=0

    #flag ultima señal
    #Se podría utilizar para evitar repetir señales del mismo tipo
    #Por el momento no la utilizaré
    flagUltimaSignal=''

    #Se inicia en 1 ya que el primer día no hay señales
    #se hace menos 1 ya que el último día se cierran las posiciones abiertas
    for t in range(1,n-1):

        #cálculo del precio de ejecución
        precioLow=float(datosFiltrados['Low'].iloc[t+1])
        precioHigh=float(datosFiltrados['High'].iloc[t+1])
        precioEjecucion=(precioLow + precioHigh)/2.0

        #Cálculo los intereses acumulados hasta el momento
        #NOTA: La señal se recibe al final del día por eso se aplican
        #los intereses en este momento
        fecha=datosFiltrados['Date'].iloc[t]
        fActual=pd.to_datetime(fecha,format="%Y-%m-%d")
        deltaDias=(fActual-fUltimaOperacion)/np.timedelta64(1,'D')
        intereses=efectivo*tasa*deltaDias/365
        efectivo=efectivo+intereses

        #Si es posible comprar
        if signals['Signal'].iloc[t]==1 and compraPosible(efectivo,precioEjecucion):

            #Se compran más acciones
            accionesCompra=accionesCompra + np.floor(efectivo/(precioEjecucion*(1+comision)))

            #Se reduce el efectivo
            efectivo=efectivo-precioEjecucion*accionesCompra*(1+comision)

            #Se registra una posición abierta
            flagPosicionAbierta=True


        #Si es posible vender
        #No se permiten ventas en corto por eso accionesCompra > 0
        #Se venden todas las acciones en un sólo momento
        elif signals['Signal'].iloc[t]==-1 and accionesCompra>0:

            #Aumenta el efectivo
            efectivo=efectivo + accionesCompra*precioEjecucion*(1-comision)

            #Disminuyen acciones
            accionesCompra=0

            #Se cierra una posición abierta
            flagPosicionAbierta=False

        fUltimaOperacion=fActual

    #Se cierra posición abierta
    if flagPosicionAbierta:
        #cálculo del precio de ejecución
        precioLow=float(datosFiltrados['Low'].iloc[n])
        precioHigh=float(datosFiltrados['High'].iloc[n])
        precioEjecucion=(precioLow + precioHigh)/2.0

        #Aumenta el efectivo
        efectivo=efectivo + accionesCompra*precioEjecucion*(1-comision)

        #Disminuyen acciones
        accionesCompra=0

    #Se calcula ganancia final
    gananciaInd=(efectivo-capitalInicial)/capitalInicial

    #Exceso de ganancia
    exceso=gananciaInd-gananciaBH


    return [exceso,gananciaInd,gananciaBH]

##==============================================================================
## Función para realizar la cruza de dos individuos
## regresa sólo el hijo más apto
##==============================================================================

def cruza(individuo1,individuo2,datos,fechaInicio):
    '''
    ENTRADA
    individuo: Objetos creados con la función creaIndividuo
    datos: pandas DataFrame creado con leeTabla
    fechaInicio: string en formato 'YYYY-MM-DD'

    SALIDA
    hijo: hijo más apto
    '''

    n1=len(individuo1)
    n2=len(individuo2)

    if n1==n2:
        #corta en el punto medio
        n3=int(n1/2)

        hijo1=individuo1[0:(n3+1)] + individuo2[n3+1:]
        hijo2=individuo2[0:(n3+1)] + individuo1[n3+1:]

    elif n1>n2:
        #El individuo1 tiene más indicadores que el individuo2
        hijo1=individuo1[0:(n2+1)]
        hijo2=individuo2[:] + individuo1[n2+1:]

    elif n2>n1:
        #El individuo2 tiene más indicadores que el individuo2
        hijo1=individuo2[0:(n1+1)]
        hijo2=individuo1[:] + individuo2[n1+1:]

    #Calcula la aptitud de cada hijo
    aptitudHijo1=fitness(datos,hijo1,fechaInicio)
    aptitudHijo2=fitness(datos,hijo2,fechaInicio)

    if aptitudHijo1==aptitudHijo2:
        return hijo1
    elif aptitudHijo1<aptitudHijo2:
        return hijo2
    else:
        return hijo1

##==============================================================================
## Función para ejecutar el algoritmo genético
## 1. Crea población
## 2. Calcula el fitness
## 3. Registra los k-mejores (k-elitismo)
## 4. Normaliza fitness para que todos sean positivos (sumar a cada uno max-min)
## 5. Calcular las probabilidades de selección (método de la ruleta)
## 6. De acuerdo a las probabilidades seleccionar dos padres y cruzar
## 7. Generar nueva generación
## 8. Mutar (sobre parámetros de cada indicador)
## 9. Despliegue del mejor/peor fitness hasta el momento y el número de generación
##==============================================================================
def genetico(datos,fechaInicio,numGen=500,sizePoblacion=20,maxIndicadores=15,objetivo=0.05,kMejores=3):
    '''
    ENTRADA
    datos: pandas DataFrame creado con leeTabla
    fechaInicio: string en formato 'YYYY-MM-DD'
    numGen: entero que representa el número de generaciones máximas
    sizePoblacion: entero que representa el tamaño de la población
    maxIndicadores: entero que representa el número máximo de indicadores por individuo
    objetivo: flotante que representa el objetivo en exceso de ganancia
    kMejores: entero que representa el parámetro de elitismo

    SALIDA
    resultado: lista con primer elemento el fitness del mejor individuo y
    segundo elemento el individuo de dicho fitness
    '''

    #aquí guardo los individuos
    poblacion=[]
    nuevaPoblacion=list(np.zeros(sizePoblacion))

    #aptitud de cada individuo
    aptitudes=np.zeros(sizePoblacion)
    aptitudesNormalizadas=np.zeros(sizePoblacion)

    #Probabilidades de selección
    probabilidades=np.zeros(sizePoblacion)

    #para registrar la mejor y peor aptitud
    maxFit=-100
    minFit=100

    #Mejor individuo
    mejorInd=[]

    #contador generación
    conteoGen=1

    #inicializa población
    print "Creando primer poblacion"
    for i in range(0,sizePoblacion):
        poblacion.append(creaIndividuo(datos,fechaInicio,maxIndicadores))
    print "Inicia proceso de evolucion"

    #proceso de evolución
    #Se ejecuta mientras no se llegue al máximo de generaciones
    #o no se tenga la aptitud objetivo
    while conteoGen<numGen and maxFit<objetivo:

        #Calcula aptitudes
        for i in range(0,sizePoblacion):
            aptitudes[i]=fitness(datos,poblacion[i],fechaInicio)[0]

        #Normaliza las aptitudes (para que sean positivas)
        #y calcula las probabilidades de selección
        aptitudesNormalizadas=aptitudes+200 #OJO (En teoría lo más que se puede perder es el 100% del capital inicial)
        probabilidades=aptitudesNormalizadas/np.sum(aptitudesNormalizadas)

        #Registra la mejor aptitud
        indice=aptitudes.argsort()[len(aptitudes)-1]
        if maxFit<aptitudes[indice]:
            maxFit=aptitudes[indice]
            mejorInd=deepcopy(poblacion[indice])

        #registra la peor aptitud
        indice=aptitudes.argsort()[0]
        if minFit>aptitudes[indice]:
            minFit=aptitudes[indice]

        #Elitismo, conserva los k mejores
        for i in range(0,kMejores):
            #argsort ordena de menor a mayor
            indice=aptitudes.argsort()[len(aptitudes)-1-i]
            nuevaPoblacion[i]=deepcopy(poblacion[indice])

        #Comienza la cruza
        aux=kMejores
        while aux<sizePoblacion:
            indices=np.random.choice(range(0,len(poblacion)),p=probabilidades,size=2,replace=False)
            padre1=poblacion[indices[0]]
            padre2=poblacion[indices[1]]
            nuevaPoblacion[aux]=cruza(padre1,padre2,datos,fechaInicio)
            aux=aux+1


        #Mutación(PENDIENTE)

        #Imprime progreso
        print "Mejor aptitud= " + str(round(maxFit,6)) + " Peor= " + str(round(minFit,6)) + " Generacion= " + str(conteoGen)

        #Reinicia para la siguiente iteración
        poblacion=deepcopy(nuevaPoblacion)
        nuevaPoblacion=list(np.zeros(sizePoblacion))
        conteoGen=conteoGen+1

    resultado=[maxFit,mejorInd]
    return resultado
