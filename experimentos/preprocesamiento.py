# coding: utf-8
'''
Funciones para preprocesamiento de datos
'''
from sklearn import preprocessing
import numpy as np
import pandas as pd
from copy import deepcopy

def escala(entrena, prueba, metodo = 'scale'):
  '''
  Función para ajustar los datos de entrenamiento y prueba de acuerdo a 
  un método de escalamiento seleccionado

  ENTRADA
  entrena, prueba: Pandas dataframes con los datos de entrenamiento y prueba.
  Estos se obtienen del diccionario creado con la función diccDatos del módulo
  obtenConjuntos.py

  metodo: String que representa el método de escalamiento
  'scale' => Media cero y desviación estándar uno
  'minmax' => Rango entre cero y uno
  'maxabs' => Valor absoluto más grande igual a uno

  SALIDA
  Dos pandas dataframes con los atributos de entrenamiento y prueba ajustados.
  '''

  #obtiene los atributos eliminando las columnas 'Date' y 'Clase'
  atributos_entrena = deepcopy(entrena)
  del atributos_entrena['Date']
  del atributos_entrena['Clase']
  atributos_prueba = deepcopy(prueba)
  del atributos_prueba['Clase']
  del atributos_prueba['Date']

  #Nombre de las columnas
  columnas = atributos_entrena.columns

  #Selecciona el tipo de ajuste
  if metodo == 'scale':
    scaler =  preprocessing.StandardScaler()
  elif metodo == 'minmax':
    scaler = preprocessing.MinMaxScaler()
  elif metodo == 'maxabs':
    scaler = preprocessing.MaxAbsScaler()

  #Ajusta los datos
  scaler.fit(atributos_entrena)
  entrena_ajust = scaler.transform(atributos_entrena)
  prueba_ajust = scaler.transform(atributos_prueba)

  #convierte en pandas dataframes
  entrena_ajust = pd.DataFrame(entrena_ajust)
  entrena_ajust.columns = columnas
  prueba_ajust = pd.DataFrame(prueba_ajust)
  prueba_ajust.columns = columnas

  return entrena_ajust, prueba_ajust