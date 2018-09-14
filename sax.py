# coding: utf-8

## Estos códigos están relacionados a la metodología SAX

import scipy.stats
import numpy as np
import copy as cp
import pandas as pd

##==============================================================================
## Función para dividir una distribución normal en N divisiones equiprobables
##==============================================================================
def divide_normal(num_divisiones = 2):
    '''
    ENTRADA
    num_divisiones: Entero >= 2

    SALIDA
    beta: numpy array con num_divisiones - 1 elementos, cada elemento
    representa un breakpoint en la curva normal.
    La división se lee de izquierda a derecha
    '''

    if num_divisiones <= 1:
        print 'El número de divisiones necesita ser al menos 2'
        return 0

    #Inicializa el arreglo con las divisiones
    beta = np.zeros(num_divisiones - 1)

    #Probabilidad
    prob = 1.0 / num_divisiones

    #El primer breakpoint es el cuantil 1/prob
    beta[0] = scipy.stats.norm.ppf(prob)

    #Obtiene el resto de los breakpoints
    #Este resultado se basa en el siguiente razonamiento
    #Encontra b_{i} tal que P[b_{i-1} <= Z <= b{i}] = prob
    # b{i} = cuantil i / num_divisiones

    for i in range(1, num_divisiones - 1):
        beta[i] = scipy.stats.norm.ppf(float(i + 1) / num_divisiones)

    return beta


##===========================================================================##
## Función para obtener los segmentos horizontales representativos de una
## ventana de datos. (Piecewise Aggregate Approximation)
## METODOLOGÍA SAX
##===========================================================================##
def segmentos(window, num_seg = 3):
    '''
    ENTRADA
    window: numpy array con shape (n,) que contiene los valores de una ventana de tiempo

    num_seg: entero que indica el número de segmentos a obtener

    SALIDA
    segmentos: Numpy array con los segmentos horizontales
    window_norm: numpy array con la información de window estandarizada
    '''

    #Longitud de la ventana
    n = window.shape[0]

    #Media y desviación estándar
    mu = window.mean()
    sigma = window.std(ddof = 1)

    #Estandariza los datos
    window_norm = (window - mu) / sigma

    #Auxiliar para obtener los segmentos
    k = int(n / num_seg)

    segmentos = np.zeros(num_seg)


    #Caso en que n / num-seg no sea un entero
    if n % num_seg > 0:

        #parte decimal
        decimal = n / float(num_seg) - k

        #auxiliares para ponderar los extremos del segmento
        izq = 1
        der = decimal

        for i in range(0, num_seg):

            #Obtiene los datos para el cálculo del segmento
            x = cp.deepcopy(window_norm[i * k:(i + 1) * k + 1])

            #Modifica los extremos
            x[0] = x[0] * izq
            x[-1] = x[-1] * der

            #calcula el segmento
            segmentos[i] = (float(num_seg) / n) * np.sum(x)

            #Actualiza las ponderaciones de los extremos
            izq = 1 - der
            der = 1 + decimal - izq

    #Caso en que n / num_seg es un entero
    else:
        for i in range(0, num_seg):

            #Obtiene los datos para el cálculo del segmento
            x = window_norm[i * k:(i + 1) * k]

            #calcula el segmento
            segmentos[i] = (float(num_seg) / n) * np.sum(x)

    return segmentos, window_norm

##===========================================================================##
## Función para convertir un segmento en una palabra
##===========================================================================##
def palabra(segmentos, beta, alfabeto):
    '''
    ENTRADA
    segmentos: numpy array que representa los segmentos de una ventana
    (ver función segmentos)

    beta: numpy array que contiene los breakpoints de una curva normal
    (ver función divide_normal)

    alfabeto: numpy array de longitud len(beta) + 1. Cada entrada es una
    letra del alfabeto a utilizar

    SALIDA
    word: String que representa el segmento
    '''
    word = ''

    for segmento in segmentos:

        #Casos base
        if segmento <= beta[0]:
            word = word + alfabeto[0]
        elif segmento > beta[-1]:
            word = word + alfabeto[-1]

        else:
            for i in range(1, len(beta)):

                #extremo izquierdo
                bleft = beta[i-1]

                #extremo derecho
                bright = beta[i]

                if bleft < segmento and segmento <= bright:
                    word = word + alfabeto[i]

    return word

##===========================================================================##
## Función para crear ventanas deslizantes a partir de una serie de tiempo
## y una ventana de tiempo dada.
## La serie de tiempo se supone ordenada de forma creciente relativo al tiempo
##
## La idea para crear cada ventana es la siguiente
## ventana 1 = serie[0:k] (es decir se incluye serie[0,1,...,k-1])
## ventana 2 = serie[1:k+1] (es decir se incluye serie[1,2,...,k])
## ventana 3 = serie[2:k+2] (es decir se incluye serie[2,3,...,k+1])
## ventana j = serie[j-1:k+j-1] (es decir se incluye serie[j-1,j,...,k + j - 2])
##
## se crean un total de n - k + 1 ventanas
##===========================================================================##
def ventanas(serie, k):
    '''
    ENTRADA
    serie: Numpy array con los datos de la serie de tiempo

    k: Entero que representa el tamaño de cada ventana

    SALIDA
    windows: lista con las ventanas creadas. Se supone un orden creciente
    respecto al tiempo
    '''

    #longitud de la serie de tiempo
    n = len(serie)

    #revisa que k < n
    if k>n:
        print 'k debe de ser menor que len(serie)'
        return 0

    windows = []

    for j in range(1, n - k + 2):
        windows.append(serie[j-1:k + j - 1])

    return windows


##===========================================================================##
## Función para calcular la tabla de distancias entre los caracteres
## de un alfabeto dado
##===========================================================================##
def tabla_distancias(alfabeto, beta):
    '''
    ENTRADA
    alfabeto: Lista con el alfabeto utilizado

    beta: divisiones de la distribución normal (ver función divide_normal)

    SALIDA
    tabla: pandas DataFrame con la distancia de cada letra. La dimension es
    len(alfabeto) X len(alfabeto)
    '''

    #longitud del alfabeto
    n = len(alfabeto)

    #inicializa la tabla
    tabla = np.zeros(shape = (n , n))

    #llena la tabla
    for i in range(0,n): #renglón
        for j in range(0,n): #columna
            if np.abs(i-j)>1:
                if j - 1 > i:
                    tabla[i][j] = beta[j-1] - beta[i]
                elif i > j + 1:
                    tabla[i][j] = beta[i-1] - beta[j]

    #convierte a DataFrame
    tabla = pd.DataFrame(data = tabla, index = alfabeto, columns = alfabeto)

    return tabla

##===========================================================================##
## Función para calcular la función MINDIST
##===========================================================================##
def mindist(palabra1, palabra2, tabla, n):
    '''
    ENTRADA
    palabra1, palabra2: Strings creados con la función palabra

    tabla: pandas DataFrame creado con la función tabla_distancias.

    n: Tamaño de la ventana. Debe ser el mismo parámetro que fue utilizado para
    la función ventanas

    SALIDA
    distancia: número real que representa la distancia entre las palabras
    '''
    #número de segmentos (un carácter por segmento)
    w = len(palabra1)

    #para acumular la suma
    suma = 0

    for i in range(0, w):
        suma = suma + tabla.loc[palabra1[i], palabra2[i]]**2

    distancia = np.sqrt(float(n) / w) * np.sqrt(suma)

    return distancia

##===========================================================================##
## Función para encontrar los patrones en un conjunto de ventanas de tiempo
##===========================================================================##
def encuentra_patrones(windows, num_seg, beta, alfabeto):
    '''
    ENTRADA
    windows: windows: lista con las ventanas creadas. Se supone un orden creciente
    respecto al tiempo (ver función ventanas)

    num_seg: Número de segmentos en el que se divide una ventana en particular

    beta: numpy array con len(alfabeto) - 1 elementos, cada elemento
    representa un breakpoint en la curva normal.

    alfabeto: Lista con el alfabeto utilizado

    SALIDA
    patrones: Diccionario con cada key igual a un patrón y value el número de
    veces que se repitió dicho patrón
    '''

    patrones ={}

    for window in windows:

        #Obtiene los segmentos horizontales
        seg = segmentos(window, num_seg)[0]

        #obtiene la palabra
        word = palabra(seg, beta, alfabeto)

        #agrega al diccionario (en caso de ser necesario) e incrementa el conteo
        if patrones.has_key(word):
            patrones[word] = patrones[word] + 1
        else:
            patrones[word] = 1

    return patrones

##===========================================================================##
## Función para generar un alfabeto
##===========================================================================##
def genera_alfabeto(num_letras = 5):
    '''
    ENTRADA
    num_letras: número de letras que contendrá el alfabeto

    SALIDA
    alfabeto: lista de la forma ['A0','A1',...'An']
    '''

    alfabeto = []

    for i in range(0, num_letras):
        letra = 'A' + str(i)
        alfabeto.append(letra)
    return alfabeto    
