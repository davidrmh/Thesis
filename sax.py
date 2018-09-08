# coding: utf-8

## Estos códigos están relacionados a la metodología SAX

import scipy.stats
import numpy as np

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
