# coding: utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import tree

##=====================================
## Lee datos, quita los null
## transforma a float
## reinicia los indices
##=====================================
def leeTabla(ruta="naftrac.csv"):
    '''
    Lee los datos del archivo en ruta
    El archivo debe de ser un csv descargado de Yahoo finance
    Regresa un pandas dataframe
    '''
    data=pd.read_csv(ruta,dtype=str)
    data=data[data.iloc[:,2]!="null"]
    data["Open"]=data["Open"].astype('float')
    data["High"]=data["High"].astype('float')
    data["Close"]=data["Close"].astype('float')
    data["Adj Close"]=data["Adj Close"].astype('float')
    data["Volume"]=data["Volume"].astype('int')
    data=data.reset_index()
    return data

##============================================
## Separa los datos de entrenamiento
##============================================
def splitData(data,ptrain=0.80):
    '''
    Obtiene el conjunto de entrenamiento.
    Es una proporción (ptrain) del conjunto completo
    Regresa el conjunto de entrenamiento (dataTrain) y el índice
    en donde comienza el conjunto de prueba (se utiliza en otras funciones)
    '''
    n=data.shape[0]-1 #Numero de indices validos
    trainIndiceFin=int(np.floor(ptrain*n))
    #En que indice del conjunto de datos completo
    #inician las observaciones para validacion
    testIndiceInicio=trainIndiceFin+1
    dataTrain=data.iloc[0:(trainIndiceFin+1),]
    dataTrain=dataTrain.reset_index()

    return dataTrain,testIndiceInicio

##===================================================
## Crea las observaciones para probar el modelo
##===================================================
def creaTest(data,indiceInicio,hback=7):
    '''
    Crea el conjunto de datos de PRUEBA
    ENTRADA
    data: tabla completa (datos del csv)

    indiceInicio: es el índice obtenido con la función splitData,
    es decir, testIndiceInicio

    hback: número de periodos hacia atrás para calcular las variaciones
    respecto al momento actual

    SALIDA
    atributos: lista de lista con las variaciones entre los hback puntos
    hacia atrás y el punto más actual

    '''
    n=data.shape[0]-1 #Numero de indices validos
    atributos=[]
    for i in range(indiceInicio,n+1):
        renglon=[]
        #Los atributos son los cambios entre el precio en t y t-1,
        # t y t-2,...,t y t-hback
        for j in range(1,hback+1):
            renglon.append(data["Close"][i]/data["Close"][i-j]-1)
        atributos.append(renglon)
    return atributos

##============================================
## Crea el dataset para el arbol de decision
##============================================
def creaDataSet(data,hforw=15,hback=7,umbral=0.01):
    '''
    Crea el las etiquetas del conjunto de ENTRENAMIENTO
    La idea es mirar hacia adelante hforw periodos, si la variación entre
    el precio en t y el precio en t+hforw rebasa un umbral, recolectar
    las variaciones entre el precio en t y los precios en t-1,t-2,..,t-hback
    estas variaciones serán los atributos.
    La etiqueta es de acuerdo al signo de la variación entre t y t+hforw,
    si es positiva entonces etiqueta 1 (buy), si es negativa entonces etiqueta -1
    (sell), si no rebasa el umbral, etiqueta 0 (hold)

    ENTRADA
    data: El conjunto de ENTRENAMIENTO creado con splitData

    hforw: Periodos hacia adelante

    hbakc: periodos hacia atrás

    umbral: Cambio mínimo (hacia arriba o hacia abajo) para que sea considerado
    un cambio significativo

    SALIDA:
    atributos: Variaciones entre t y t-1,t-2,...,t-hback (lista de listas)

    clases: Etiquetas correspondiente a cada "renglon" en los atributos

    contBuy: Total de señales de compra

    contSell: Total de señales de venta

    contHold: Total de señales de hold

    indicesBuy: Índices de las señales de compra

    indicesSell: Índices de las señales de venta

    indicesHold: Índices de las señales de hold
    '''
    n=data.shape[0]-1 #Numero de indices validos
    fin=data.shape[0]-hforw-1 #Ultimo indice valido considerando forward look
    inicio=hback
    umbral=0.01 #cambio minimo para que se considere una senial (podria considerar dos umbrales)
    contBuy=0 #Contador de seniales de compra generadas
    contSell=0 #Contador de seniales de venta generadas
    contHold=0
    atributos=[]
    clases=[]
    indicesBuy=[]
    indicesSell=[]
    indicesHold=[]

    for i in range(inicio,fin+1):
        renglon=[]
        #Si se rebasa el umbral
        if abs(data["Adj Close"][i+hforw]/data["Adj Close"][i]-1)>umbral:
            #Los atributos son los cambios entre el precio en t y t-1,
            # t y t-2,...,t y t-hback
            for j in range(1,hback+1):
                renglon.append(data["Adj Close"][i]/data["Adj Close"][i-j]-1)

            atributos.append(renglon)
            if (data["Adj Close"][i+hforw]/data["Adj Close"][i]-1)>0:
                clases.append(1) #Compra
                contBuy=contBuy+1
                indicesBuy.append(i)
            elif (data["Adj Close"][i+hforw]/data["Adj Close"][i]-1)<0:
                clases.append(-1) #venta
                contSell=contSell+1
                indicesSell.append(i)
        else:
            #Los atributos son los cambios entre el precio en t y t-1,
            # t y t-2,...,t y t-hback
            for j in range(1,hback+1):
                renglon.append(data["Adj Close"][i]/data["Adj Close"][i-j]-1)
            clases.append(0) #hold
            contHold=contHold+1
            indicesHold.append(i)
            atributos.append(renglon)
    return atributos,clases,contBuy,contSell,contHold,indicesBuy,indicesSell,indicesHold

##==============================================
## Aprende el árbol
##==============================================
def aprendeArbol(atributos,clases):
    '''
    Ajusta un árbol de clasificación utilizando como criterio para dividir
    la entropía en el conjunto de datos.

    ENTRADA:
    atributos: Lista de listas creada con la función creaDataSet que contiene
    los atributos

    clases: Clase que corresponde a cada "renglón" en atributos

    '''
    arbol=tree.DecisionTreeClassifier(criterion="entropy",random_state=1)
    arbol=arbol.fit(atributos,clases)
    return arbol

##===============================================
## Obtiene las predicciones
##===============================================
def predicciones(arbol,data,atributos,indiceInicio,indiceFin):
    '''
    Obtiene las predicciones para un conjunto de atributos

    ENTRADA:
    arbol: árbol de clasificación creado con aprendeArbol

    data: tabla con los datos completos (creada con leeTabla)

    atributos: atributos que se quieren clasificar

    indiceInicio: Índice de inicio (testIndiceInicio para PRUEBA, hback
    para ENTRENAMIENTO)

    indiceFin: Índice de fin (data.shape[0]-1 para PRUEBA, testIndiceInicio -1
    para ENTRENAMIENTO)

    SALIDA:
    predicciones: Clase predicha por el modelo (-1,0 o 1)

    indicesBuy: Índices (relativos a los índices de data) de las señales
     de compra

    indicesSell,indicesHold: Similares a indicesBuy

    '''
    predicciones=arbol.predict(atributos)
    indicesBuy=[]
    indicesHold=[]
    indicesSell=[]
    aux=0

    for i in range(indiceInicio,indiceFin+1):
        if aux>=len(predicciones): break
        if predicciones[aux]==1:
            indicesBuy.append(i)
        elif predicciones[aux]==0:
            indicesHold.append(i)
        elif predicciones[aux]==-1:
            indicesSell.append(i)
        aux=aux+1
    return predicciones,indicesBuy,indicesSell,indicesHold

##===================================================
## Grafica estrategia
##===================================================
def graficaEstrategia(data,indiceInicio,indicesBuy,indicesSell,indicesHold):
    plt.plot(data["Adj Close"][indiceInicio:],'-',color="blue")
    plt.plot(data["Adj Close"][indicesBuy],'o',color="green",ms=5)
    plt.plot(data["Adj Close"][indicesHold],'o',color="black",ms=5)
    plt.plot(data["Adj Close"][indicesSell],'o',color="red",ms=5)
    plt.show()

##===================================================
## Main
## main(data,0.80,15,11,0.05,False) para naftrac
# main(data,0.80,15,23,0.05,False) para amxl
##===================================================
def main(data,ptrain=0.8,hforw=15,hback=11,umbral=0.05,graf=True):
    #data=leeTabla(ruta)
    dataTrain,testIndiceInicio=splitData(data,ptrain) #entrenamiento

    #Crea el conjunto de entrenamiento etiquetando de acuerdo a los parámetros
    atributosTrain,clasesTrain,contBuyTrain,contSellTrain,contHoldTrain,indicesBuyTrain,indicesSellTrain,indicesHoldTrain=creaDataSet(dataTrain,hforw,hback,umbral)

    #Ajusta un árbol de clasificación utilizando entropía como criterio de información
    arbol=aprendeArbol(atributosTrain,clasesTrain)

    #Obtiene los atributos para el conjunto de PRUEBA
    atributosTest=creaTest(data,testIndiceInicio,hback)

    #Obtiene las predicciones para el conjunto de ENTRENAMIENTO
    prediccionesTrain,indicesBuyTrain,indicesSellTrain,indicesHoldTrain=predicciones(arbol,data,atributosTrain,hback,testIndiceInicio-1)

    #Obtiene las predicciones para el conjunto de PRUEBA
    prediccionesTest,indicesBuyTest,indicesSellTest,indicesHoldTest=predicciones(arbol,data,atributosTest,testIndiceInicio,data.shape[0]-1)

    #Obtiene el exceso sobre buy and hold para el conjunto de ENTRENAMIENTO
    gananciaTrain,indicesBuyTrain,indicesSellTrain=gananciaExceso(data,hback,testIndiceInicio-1,indicesBuyTrain,indicesSellTrain,indicesHoldTrain)

    #Obtiene el exceso sobre buy and hold para el conjunto de PRUEBA
    gananciaTest,indicesBuyTest,indicesSellTest=gananciaExceso(data,testIndiceInicio,data.shape[0]-1,indicesBuyTest,indicesSellTest,indicesHoldTest)

    if graf:
        graficaEstrategia(data,testIndiceInicio,indicesBuyTest,indicesSellTest,[])
    return gananciaTrain,gananciaTest


##======================================================================
## Fitness
## Es la ganancia en exceso sobre Buy and Hold obtenida siguiendo la estrategia
## Recibe los índices de compra,venta,hold, la tabla completa, índice de inicio
##  índice final y costo de transacción
## La primer señal generada es el primer índice con una señal de compra
## No se permiten ventas en corto
## No se ejecutan señales contiguas semejantes
## El precio de ejecución es el precio de cierre del siguiente día
## El último momento en que se puede hacer una transacción es en fin-1
## Si en fin-1 la posición fue de compra, se cierra con los precios de fin
##=========================================================================
def gananciaExceso(data,inicio,fin,indicesBuy,indicesSell,indicesHold,costo=0.02):
    '''
     Es la ganancia en exceso relativa a Buy and Hold
     si se sigue la estrategia del árbol.

     ENTRADA
     data: Datos del csv (obtenidos con leeTabla)

     inicio: índice de inicio testIndiceInicio si es para prueba, hback si es
     para entrenamiento

     fin: índice final, data.shape[0]-1 si es para prueba, testIndiceInicio-1
     si es para entrenamiento.

     indicesBuy,indicesSell,indicesHold: lista de índices que contienen
     los momentos de compra,venta,hold respectivamente.
     Son índices relativos a los índices de data y se obtienen con la función
     predicciones

     La primer señal generada es el primer índice con una señal de compra
     No se permiten ventas en corto
     No se ejecutan señales contiguas iguales
     El precio de ejecución es el precio de cierre ajustado del siguiente día
     El último momento en que se puede hacer una transacción es en fin-1
     Si en fin-1 la posición fue de compra, se cierra con los precios de fin

    SALIDA
    exceso: Exceso de ganancia sobre buy and hold (como número decimal)

    indicesBuyEfectivas: índice del día en que se ejectua la señal de compra
    (un periodo después de recibir la señal)

    indicesSellEfectivas: Similar a indicesBuyEfectivas pero para señales de
    venta
    '''
    indices=[] #Guarda todos los indices
    indicesBuyEfectivas=[] #Guarda las compras hechas
    indicesSellEfectivas=[] #Guarda las ventas hechas
    indices.extend(indicesBuy)
    indices.extend(indicesSell)
    indices.extend(indicesHold)
    if indices==[]: return 0
    indices.sort() #Ordena de menor a mayor
    #Buy and hold
    buyHold=round(data["Adj Close"][fin]*(1+costo)/data["Adj Close"][inicio]*(1+costo)-1,6)
    inicio=min(indicesBuy) #En que momento se hace la primer compra
    if inicio==fin: return -1*buyHold

    gananciaAcumulada=0
    precioCompra=0
    precioVenta=0
    flagUltimaSen=""

    #En range fin implica fin-1
    for i in range(inicio,fin):
        if flagUltimaSen!="BUY" and i in indicesBuy:
            precioCompra=data["Adj Close"][i+1]*(1+costo)
            indicesBuyEfectivas.append(i+1)
            flagUltimaSen="BUY"
        elif flagUltimaSen!="SELL" and i in indicesSell:
            precioVenta=data["Adj Close"][i+1]*(1+costo)
            flagUltimaSen="SELL"
            indicesSellEfectivas.append(i+1)
            gananciaAcumulada=round(gananciaAcumulada+(precioVenta/precioCompra-1),6)

    #Al final cierra la última posición abierta
    if flagUltimaSen=="BUY":
        precioVenta=data["Adj Close"][fin]*(1+costo)
        indicesSellEfectivas.append(fin)
        gananciaAcumulada=round(gananciaAcumulada+(precioVenta/precioCompra-1),6)

    #Exceso de ganancia sobre buy and hold
    exceso=round(gananciaAcumulada-buyHold,6)
    return exceso,indicesBuyEfectivas,indicesSellEfectivas


##=====================================================
## Algoritmo genético
##=====================================================
#def algoritmoGenetico(ruta="naftrac.csv",ptrain=0.8,pmuta=0.01,popSize=10,numGen=100,kBest=3):
