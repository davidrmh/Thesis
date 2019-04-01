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
        val_unico.sort() #ordena de menor a mayor

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
            val_unico.sort()

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
## Función para obtener la cobertura de un atributo
##==============================================================================
def obtenCobertura(tabla_bin, atributo):
  '''
  ENTRADA
  tabla_bin: pandas dataframe que representa un conjunto de atributos binarizados

  atributo: String. La forma de este string es 'POS/nombre_columna' o 'NEG/nombre_columna'
  (Ver función listaAtributos)

  SALIDA
  Lista que con los índices de las observaciones que cubre el atributo
  '''
  #Extrae el nombre de la columna
  nom_col = atributo.split('/')[1]
  #si es POS
  if 'POS/' in atributo:
    indices = list(tabla_bin[tabla_bin[nom_col] == 1].index)
  elif 'NEG/' in atributo:
    indices = list(tabla_bin[tabla_bin[nom_col] == 0].index)
  else:
    print 'ERROR: EL NOMBRE DEL ATRIBUTO NO TIENE LA ESTRUCTURA REQUERIDA'
    print nombre_atributo  
    return ''

  return indices  

##==============================================================================
## Función para obtener la cobertura de una disyunción
## una disyunción se representa como una lista de atributos de la forma
## 'POS/nombre_columna' o 'NEG/nombre_columna'
##==============================================================================
def obtenCoberturaDisyuncion(tabla_bin, lista_atributos):
  '''
  ENTRADA
  tabla_bin: pandas dataframe que representa un conjunto de atributos binarizados

  lista_atributos: Lista de strings con la forma '(NEG)POS/nombre_columna'

  SALIDA
  Lista que con los índices de las observaciones que cubren los atributos
  '''

  lista = []
  for atributo in lista_atributos:

    lista.extend(obtenCobertura(tabla_bin, atributo))

  #elimina repetidas
  lista = list(set(lista))

  return lista

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

##==============================================================================
## Implementación del algoritmo RA1 (Randomized Algorithm 1)
## Se obtiene un conjunto (num_iter) de cláusulas en forma CNF
## Se da preferencia a aquella cláusula CNF con menor longitud
## Una cláusula en CNF se representa como [[A1, A2,..Am],[Ai,Aj,...,Ak],...]
## en donde cada lista interior es la disyunción de atributos binarios
##==============================================================================
def ra1(tabla_pos, tabla_neg, num_iter = 5, top_k = 5):
  '''
  ENTRADA
  tabla_pos, tabla_neg: Pandas dataframe que representan las observaciones
  binarizadas de la clase positiva y negativa respectivamente
  (ver función separaDatos)

  num_iter: Entero positivo que representa el número de iteraciones.
  Este será el número de cláusulas CNF que se obtendrán

  top_k: Entero positivo. Representa la longitud de la lista con los top_k
  mejores puntajes

  SALIDA
  lista de listas, cada lista interior representa una cláusula CNF
  '''
  np.random.seed(54321)
  lista_cnf = []
  lista_atributos = listaAtributos(tabla_pos.columns)

  for i in range(0, num_iter):
    clasula_cnf = []

    #copia de tabla_neg
    tmp_neg = deepcopy(tabla_neg)

    while tmp_neg.shape[0] != 0:
      disyuncion = []
      #copia lista_atributos
      tmp_atributos = deepcopy(lista_atributos)

      #diccionario para almacenar |NEG(ai)|
      dicc_neg = {}
      for atributo in tmp_atributos:

        #calcula |NEG(ai)|
        conteo_neg = numero_pos_neg(tmp_neg, atributo)

        #Para evitar división entre cero
        if conteo_neg == 0:
          conteo_neg = 0.00001
        dicc_neg[atributo] = conteo_neg

      #copia de tabla_pos
      tmp_pos = deepcopy(tabla_pos) 

      while tmp_pos.shape[0] != 0:
        
        #lista para almacenar |POS(ai)|
        lista_pos = []

        #lista para almacenar |POS(ai)| / |NEG(ai)|
        lista_puntaje = []

        #calcula puntaje
        for j in range(0, len(tmp_atributos)):
          #Obtiene el atributo
          atributo = tmp_atributos[j]
          
          #calcula |POS(ai)|
          conteo_pos = numero_pos_neg(tmp_pos, atributo)
          lista_pos.append(conteo_pos)

          #calcula el cociente
          lista_puntaje.append(conteo_pos / dicc_neg[atributo])

        #Obtiene el top k
        lista_argsort = list(np.argsort(lista_puntaje))

        if len(lista_argsort) > top_k:
          #Se toman todos los elementos
          #este caso es cuando el número de atributos es menor a top_k
          lista_top = lista_argsort[:]
        else:
          #Se toman sólo top_k elementos
          lista_top = lista_argsort[:top_k]

        #Selecciona un elemento al azar
        indice_azar = np.random.choice(lista_top, size=1)[0]

        #atributo correspondiente a indice_azar
        atributo_azar = tmp_atributos[indice_azar]

        #agrega a disyunción
        disyuncion.append(atributo_azar)

        #Obtiene cobertura de atributo_azar en tmp_pos
        cobertura_atributo = obtenCobertura(tmp_pos, atributo_azar)

        #nuevos índices de tmp_pos
        indices_pos = list(set.difference(set(tmp_pos.index), set(cobertura_atributo)))

        #Actualiza tmp_pos y tmp_atributos
        tmp_pos = tmp_pos.iloc[indices_pos,:].reset_index(drop = True)
        tmp_atributos.remove(atributo_azar)

        print 'Faltan ' + str(tmp_pos.shape[0]) + ' observaciones positivas'

      #obtiene la cobertura de la disyunción en tmp_neg
      cobertura_disy = obtenCoberturaDisyuncion(tmp_neg, disyuncion)

      #nuevo índices de tmp_neg
      indices_neg = list(set.difference(set(tmp_neg.index), set(cobertura_disy)))

      #actualiza tmp_neg
      tmp_neg = tmp_neg.iloc[indices_neg,:].reset_index(drop = True)
      print 'Faltan ' + str(tmp_neg.shape[0]) + ' observaciones negativas'

      #agrega disyunción a cláusula CNF
      clasula_cnf.append(disyuncion)

    #agrega clausula_cnf a lista_cnf
    lista_cnf.append(clasula_cnf)
    print 10*'='
    print 'Fin de la iteración ' + str(i + 1)
    print 10*'='

  return lista_cnf  



