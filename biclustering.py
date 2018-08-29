# coding: utf-8
import entrena_prueba as entrena
import indicadores as ind
import normaliza as nor
import etiqueta as eti
import pandas as pd
from sklearn import svm
from sklearn import tree

##==============================================================================
## Biclustering Opción 1
##==============================================================================

#Datos de CSV
datos = ind.leeTabla()

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
