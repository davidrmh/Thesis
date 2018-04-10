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
    arbol=tree.DecisionTreeClassifier(criterion="entropy",random_state=1)
    arbol=arbol.fit(atributos,clases)
    return arbol

##===============================================
## Obtiene las predicciones
##===============================================
def predicciones(arbol,data,atributos,indiceInicio,indiceFin):
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
## main(data2,0.80,15,11,0.05,False) para naftrac
##===================================================
def main(data,ptrain=0.8,hforw=15,hback=11,umbral=0.05,graf=True):
    #data=leeTabla(ruta)
    dataTrain,testIndiceInicio=splitData(data,ptrain) #entrenamiento

    #Crea el conjunto de entrenamiento etiquetando de acuerdo a los parámetros
    atributosTrain,clasesTrain,contBuyTrain,contSellTrain,contHoldTrain,indicesBuyTrain,indicesSellTrain,indicesHoldTrain=creaDataSet(dataTrain,hforw,hback,umbral)

    #Ajusta un árbol de clasificación utilizando entropía como criterio de información
    arbol=aprendeArbol(atributosTrain,clasesTrain)

    #Obtiene los atributos para el conjunto de prueba
    atributosTest=creaTest(data,testIndiceInicio,hback)

    #Obtiene las predicciones para el conjunto de entrenamiento
    prediccionesTrain,indicesBuyTrain,indicesSellTrain,indicesHoldTrain=predicciones(arbol,data,atributosTrain,hforw,testIndiceInicio-1)

    #Obtiene las predicciones para el conjunto de prueba
    prediccionesTest,indicesBuyTest,indicesSellTest,indicesHoldTest=predicciones(arbol,data,atributosTest,testIndiceInicio,data.shape[0]-1)

    #Obtiene el exceso sobre buy and hold para el conjunto de entrenamiento
    gananciaTrain,indicesBuyTrain,indicesSellTrain=gananciaExceso(data,hforw,testIndiceInicio-1,indicesBuyTrain,indicesSellTrain,indicesHoldTrain)

    #Obtiene el exceso sobre buy and hold para el conjunto de prueba
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
##======================================================================
def gananciaExceso(data,inicio,fin,indicesBuy,indicesSell,indicesHold,costo=0.02):
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
