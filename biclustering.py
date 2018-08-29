# coding: utf-8
import entrena_prueba as ent
import indicadores as ind
import normaliza as nor
import etiqueta as eti
import pandas as pd
from sklearn import svm
from sklearn import tree
import numpy as np

##==============================================================================
## Biclustering Opción 1
##==============================================================================

#Datos de CSV
datos = ind.leeTabla('naftrac.csv')

#Parámetros
dicc = {1: {'parametros': {'colName': 'Adj Close', 'window': 10}, 'tipo': 'simpleMA'},
 2: {'parametros': {'colName': 'Adj Close', 'k': 2.0, 'window': 10},
  'tipo': 'bollinger'},
 3: {'parametros': {'colName': 'Adj Close', 'window': 10},
  'tipo': 'exponentialMA'},
 4: {'parametros': {'colName': 'Adj Close',
   'longWindow': 26,
   'shortWindow': 12,
   'signalWindow': 9},
  'tipo': 'MACD'}}

#Fechas para el conjunto de entrenamiento
start_train = '2015-01-02'
end_train = '2015-01-30'

#Fechas para el conjunto de prueba
start_test = '2015-02-03'
end_test = '2015-03-02'

#nombre del conjuto de entrenamiento etiquetado
pathTrain = 'naftrac-2015-01-02-2015-01-30.csv'

#Obtiene el valor de los indicadores para el conjunto de entrenamiento
#Esto se hace sólo con el fin de obtener las lista lmin y lmax, necesarias
#para normalizar el conjunto de prueba
listaIndEntrena = ind.creaIndicadores(datos, dicc, start_train, end_train)
atributosEntrena = ind.combinaIndicadores(listaIndEntrena)
atributosEntrenaNorm,lmin,lmax = nor.normaliza_min_max(atributosEntrena)

#Obtiene el valor de los indicadores para el conjunto de prueba
listaIndPrueba = ind.creaIndicadores(datos, dicc, start_test, end_test)
atributosPrueba = ind.combinaIndicadores(listaIndPrueba)
atributosPruebaNorm,lmin,lmax = nor.normaliza_min_max(atributosPrueba,lmin,lmax)

#Carga el conjunto de entrenamiento
entrena = pd.read_csv(pathTrain)

#Ajusta el modelo (Support Vector Machine)
modelo=svm.SVC(C=0.7,class_weight={0:0.1,1:0.45,-1:0.45})
modelo.fit(atributosEntrenaNorm,entrena['Clase'])

#Ajusta el modelo (Árbol c4.5)
arbol = tree.DecisionTreeClassifier(random_state=0,max_depth=5)
arbol.fit(atributosEntrenaNorm,entrena['Clase'])

#Realiza predicciones sobre el conjunto de prueba
prediccionesSVMPrueba = modelo.predict(atributosPruebaNorm)
prediccionesArbolPrueba = modelo.predict(atributosPruebaNorm)

#Crea un dataframe con el fin de evaluar las predicciones
evaluacionSVMPrueba = eti.subconjunto(datos,start_test, end_test)
evaluacionSVMPrueba['Clase'] = prediccionesSVMPrueba
fitnessSVMPrueba = eti.fitnessMetodo2(evaluacionSVMPrueba)

evaluacionArbolPrueba = eti.subconjunto(datos,start_test, end_test)
evaluacionArbolPrueba['Clase'] = prediccionesArbolPrueba
fitnessArbolPrueba = eti.fitnessMetodo2(evaluacionArbolPrueba)

##==============================================================================
## Biclustering opción 2 (tres vectores representativos, uno por cada decisión)
##==============================================================================
#Datos de CSV
datos = ind.leeTabla('naftrac.csv')

#Parámetros
dicc = {1: {'parametros': {'colName': 'Adj Close', 'window': 10}, 'tipo': 'simpleMA'},
 2: {'parametros': {'colName': 'Adj Close', 'k': 2.0, 'window': 10},
  'tipo': 'bollinger'},
 3: {'parametros': {'colName': 'Adj Close', 'window': 10},
  'tipo': 'exponentialMA'},
 4: {'parametros': {'colName': 'Adj Close',
   'longWindow': 26,
   'shortWindow': 12,
   'signalWindow': 9},
  'tipo': 'MACD'}}

#Fechas para el conjunto de entrenamiento
start_train = '2015-01-02'
end_train = '2015-03-31'

#Fechas para el conjunto de prueba
start_test = '2015-04-01'
end_test = '2015-04-30'

#nombre del conjuto de entrenamiento etiquetado
pathTrain = 'naftrac-2015-01-02-2015-03-31.csv'

#Obtiene el valor de los indicadores para el conjunto de entrenamiento
#Esto se hace sólo con el fin de obtener las lista lmin y lmax, necesarias
#para normalizar el conjunto de prueba
listaIndEntrena = ind.creaIndicadores(datos, dicc, start_train, end_train)
atributosEntrena = ind.combinaIndicadores(listaIndEntrena)
atributosEntrenaNorm,lmin,lmax = nor.normaliza_min_max(atributosEntrena)

#Obtiene el valor de los indicadores para el conjunto de prueba
listaIndPrueba = ind.creaIndicadores(datos, dicc, start_test, end_test)
atributosPrueba = ind.combinaIndicadores(listaIndPrueba)
atributosPruebaNorm,lmin,lmax = nor.normaliza_min_max(atributosPrueba,lmin,lmax)

#Carga el conjunto de entrenamiento
entrena = pd.read_csv(pathTrain)

#Obtiene vectores representativos
#Esto sería una función que recibe el conjunto de entrenamiento
#y el diccionario con los vectores representativos
#regresa el diccionario actualizado
diccVectores = {}
diccVectores['compra'] = []
diccVectores['venta'] = []
diccVectores['espera'] = []

diccVectores['compra'].append(np.array(entrena[entrena['Clase']==1].mean()[0:-1]))
diccVectores['venta'].append(np.array(entrena[entrena['Clase']==-1].mean()[0:-1]))
diccVectores['espera'].append(np.array(entrena[entrena['Clase']==0].mean()[0:-1]))

#Obtiene las decisiones para el conjunto de prueba
#Esto será una función que recibe el conjunto de prueba (normalizado) y el
#diccionario con los vectores representativos.
clasePrueba = []

#Se calcula la distancia a cada vector representativo y se suma
#La distancia total más pequeña será la que determina la decisión
distCompra = 0
distVenta = 0
distEspera = 0

#número de observaciones
nObs = atributosPruebaNorm.shape[0]

#número de vectores representativos por clase
nVec = len(diccVectores['compra'])

for i in range(0,nObs):
    observacion = np.array(atributosPruebaNorm.iloc[i,:])

    distCompra = 0
    distVenta = 0
    distEspera = 0

    for j in range(0, nVec):

        #vector compra
        vectorCompra = diccVectores['compra'][j]

        #vector venta
        vectorVenta = diccVectores['venta'][j]

        #vector espera
        vectorEspera = diccVectores['espera'][j]

        #puedo implementar varias funciones de distancia
        distCompra = distCompra + np.sqrt(np.sum((observacion - vectorCompra)**2))

        distVenta = distVenta + np.sqrt(np.sum((observacion - vectorVenta)**2))

        distEspera = distEspera + np.sqrt(np.sum((observacion - vectorEspera)**2))


    #Obtiene la decisión
    argmin = np.argmin([distVenta, distEspera, distCompra])

    if argmin == 0:
        clasePrueba.append(-1)
    elif argmin == 1:
        clasePrueba.append(0)
    elif argmin == 2:
        clasePrueba.append(1)


#Crea un dataframe con el fin de evaluar las predicciones
evaluacionPrueba = eti.subconjunto(datos,start_test, end_test)
evaluacionPrueba['Clase'] = clasePrueba
fitnessPrueba = eti.fitnessMetodo2(evaluacionPrueba)
