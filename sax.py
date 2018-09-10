# coding: utf-8

## Estos códigos están relacionados a la metodología SAX

import scipy.stats
import numpy as np
import copy as cp

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
