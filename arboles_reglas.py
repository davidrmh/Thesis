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
    data=pd.read_csv(ruta)
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
    hforw=15 #Forward look
    fin=data.shape[0]-hforw-1 #Ultimo indice valido considerando forward look
    hback=7 #Backward look (tambien es el indice de inicio)
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
        if abs(data["Close"][i+hforw]/data["Close"][i]-1)>umbral:
            #Los atributos son los cambios entre el precio en t y t-1,
            # t y t-2,...,t y t-hback
            for j in range(1,hback+1):
                renglon.append(data["Close"][i]/data["Close"][i-j]-1)

            atributos.append(renglon)
            if (data["Close"][i+hforw]/data["Close"][i]-1)>0:
                clases.append(1) #Compra
                contBuy=contBuy+1
                indicesBuy.append(i)
            elif (data["Close"][i+hforw]/data["Close"][i]-1)<0:
                clases.append(-1) #venta
                contSell=contSell+1
                indicesSell.append(i)
        else:
            #Los atributos son los cambios entre el precio en t y t-1,
            # t y t-2,...,t y t-hback
            for j in range(1,hback+1):
                renglon.append(data["Close"][i]/data["Close"][i-j]-1)
            clases.append(0) #hold
            contHold=contHold+1
            indicesHold.append(i)
            atributos.append(renglon)
    return atributos,clases,contBuy,contSell,contHold,indicesBuy,indicesSell,indicesHold

##==============================================
## Aprende el árbol
##==============================================
def aprendeArbol(atributos,clases):
    arbol=tree.DecisionTreeClassifier()
    arbol=arbol.fit(atributos,clases)
    return arbol

##===============================================
## Obtiene las predicciones
##===============================================
def predicciones(arbol,data,atributos,indiceInicio):
    predicciones=arbol.predict(atributos)
    n=data.shape[0]-1 #Numero de indices validos
    indicesBuy=[]
    indicesHold=[]
    indicesSell=[]
    aux=0

    for i in range(indiceInicio,n+1):
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
    plt.plot(data["Close"][indiceInicio:],'-',color="blue")
    plt.plot(data["Close"][indicesBuy],'o',color="green",ms=5)
    plt.plot(data["Close"][indicesHold],'o',color="black",ms=5)
    plt.plot(data["Close"][indicesSell],'o',color="red",ms=5)
    plt.show()

##===================================================
def main(ruta="naftrac.csv",ptrain=0.8,hforw=15,hback=7,umbral=0.01):
    data=leeTabla(ruta)
    dataTrain,testIndiceInicio=splitData(data,ptrain)
    atributosTrain,clasesTrain,contBuyTrain,contSellTrain,contHoldTrain,indicesBuyTrain,indicesSellTrain,indicesHoldTrain=creaDataSet(dataTrain,hforw,hback,umbral)
    arbol=aprendeArbol(atributosTrain,clasesTrain)
    atributosTest=creaTest(data,testIndiceInicio,hback)
    prediccionesTest,indicesBuyTest,indicesSellTest,indicesHoldTest=predicciones(arbol,data,atributosTest,testIndiceInicio)
    graficaEstrategia(data,testIndiceInicio,indicesBuyTest,indicesSellTest,indicesHoldTest)
