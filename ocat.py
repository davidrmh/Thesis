# coding: utf-8

##==============================================================================
## Conjunto de funciones relacionadas a la metodología OCAT
## Autor: David Montalván
##==============================================================================
import numpy as np
import pandas as pd
from copy import deepcopy

##==============================================================================
## Crear nombres para los atributos binarizados
##==============================================================================
def crea_nombres(atributos):
    '''
    ENTRADA
    atributos: Pandas dataframe con las observaciones y los atributos

    SALIDA
    lista con los nombres correspondientes a cada columna del dataframe con
    los datos binarizados (ver función binariza)
    Los nombres tendrán la siguiente forma
    nombre_original_columna + ':' + índice_valor_único_columna
    '''

    #número de columnas
    n_col = atributos.shape[1]

    lista_nombres = []

    for j in range(0, n_col):
        #Valores sin repeticiones del atributo j
        val_unico = np.unique(np.array(atributos.iloc[:,j]))

        #prefijo
        prefijo = atributos.iloc[:,j].name

        for n in range(0, len(val_unico)):
            lista_nombres.append(prefijo + ':' + str(n))

    return lista_nombres


##==============================================================================
## Binarización de atributos continuos
##==============================================================================
def binariza(atributos):
    '''
    ENTRADA
    atributos: Pandas dataframe con las observaciones y los atributos

    SALIDA
    pandas dataframe con los valores binarizados
    '''

    #número de columnas
    n_col = atributos.shape[1]

    #número de observaciones
    n_obs = atributos.shape[0]

    #Para almacenar los datos binarizados
    binarizados = []

    for i in range(0, n_obs):
        #esta lista contendrá la observación i binarizada
        renglon_bin = []

        for j in range(0, n_col):
            #valor continuo de la observación i atributo j
            val_atributo = atributos.iloc[i,j]

            #Valores sin repeticiones del atributo j
            val_unico = np.unique(np.array(atributos.iloc[:,j]))

            #convierte en ceros y unos
            # val_atributo >= val_unico => 1, 0 en otro caso
            ceros_unos = (val_atributo >= val_unico).astype(np.int)

            #agrega a renglon_bin
            renglon_bin.extend(list(ceros_unos))

        binarizados.append(renglon_bin)

    #convierte en pandas dataframe
    nombres_columnas = crea_nombres(atributos)
    binarizados = pd.DataFrame(binarizados, columns = nombres_columnas)

    return binarizados

##==============================================================================
## Separa los datos en E+ y E-
##==============================================================================
def separaDatos(datos, tabla_bin, clase_pos = 1, clase_ignora = ''):
  '''
  ENTRADA
  datos: Pandas dataframe con los datos crudos (sin binarizar). Debe de contener
  una columna llamada 'Clase'

  tabla_bin: Pandas dataframe que representa los atributos de 'datos' binarizados

  clase_pos: Clase positiva

  clase_ignora: Clase (distinta de clase_pos) que se ignora.
  Si clase_ignora = '', no se ignora ninguna clase. Esta clase se ignora del
  conjunto de observaciones de la clase negativa

  SALIDA
  pos, neg: Pandas dataframes que son un subconjunto de tabla_in.
  pos representa E+
  neg representa E-
  '''
  #conjunto con los índices de E-
  indices_neg = set(datos[datos['Clase'] != clase_pos].index)

  if clase_ignora != '':

    #conjunto de índices de la clase_ignora
    indices_ignora = set(datos[datos['Clase'] == clase_ignora].index)

    #remueve indices_ignora de indices_neg
    indices_neg = set.difference(indices_neg, indices_ignora)

  #lista con los indices de la clase positiva
  indices_pos = list(datos[datos['Clase'] == clase_pos].index)

  #separa datos
  pos = tabla_bin.loc[indices_pos, :]
  neg = tabla_bin.loc[indices_neg, :]

  #reset de índices
  pos = pos.reset_index(drop = True)
  neg = neg.reset_index(drop = True)

  return pos, neg


##==============================================================================
## Función para calcular las cantidades POS(a) y NEG(a)
##==============================================================================
def numero_pos_neg(datos_bin, nombre_atributo):
    '''
    ENTRADA
    datos_bin: Pandas dataframe con observaciones binarizadas

    nombre_atributo: String con el nombre de una columna de datos_bin
    La forma de estos strings es 'POS/nombre_columna' o 'NEG/nombre_columna'
    (Ver función listaAtributos)

    SALIDA
    entero que representa POS(a) o NEG(a) de acuerdo al conjunto que representa datos_bin
    '''
    #Extrae el nombre de la columna
    nom_col = nombre_atributo.split('/')[1]
    #si es POS
    if 'POS/' in nombre_atributo:
      conteo = len(datos_bin[datos_bin[nom_col] == 1])
    elif 'NEG/' in nombre_atributo:
      conteo = len(datos_bin[datos_bin[nom_col] == 0])
    else:
      print 'ERROR: EL NOMBRE DEL ATRIBUTO NO TIENE LA ESTRUCTURA REQUERIDA'
      print nombre_atributo  
      return ''
    return conteo

##==============================================================================
## Función para crear una lista con el conjunto de todos los atributos
## este conjunto incluirá el atributo 'A' como '\hat(A)' (A negado)
##==============================================================================
def listaAtributos(columnas):
    '''
    ENTRADA
    columnas: pandas.core.indexes.base.Index que contiene el nombre de las
    columnas de la tabla binarizada. Se obtiene con tabla_bin.columns

    SALIDA
    lista con strings que representan los atributos
    La forma de estos strings es 'POS/nombre_columna' o 'NEG/nombre_columna'
    '''
    #Aquí se guardarán los atributos
    lista = []

    #Crea los atributos con POS/
    lista.extend('POS/' + columnas)

    #Crea los atributos con NEG/
    lista.extend('NEG/' + columnas)

    return lista


