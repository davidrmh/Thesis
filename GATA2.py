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
    data['Date']=pd.to_datetime(data['Date'])
    data["Open"]=data["Open"].astype('float')
    data["High"]=data["High"].astype('float')
    data["Close"]=data["Close"].astype('float')
    data["Adj Close"]=data["Adj Close"].astype('float')
    data["Volume"]=data["Volume"].astype('int')
    data=data.reset_index()
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
ruta="~/Documents/naftrac.csv"
datos=leeTabla(ruta)

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
