# coding: utf-8

## Conjunto de funciones relacionadas al artículo
## Financial Time Series Segmentation Based On Turning Points

import numpy as np

##==============================================================================
## Función para determinar mínimos/máximos locales
## Con esta función se obtiene el primer nivel de abstracción de la serie
##==============================================================================
def max_min_lev1(serie, w = 1):
    '''
    ENTRADA
    serie: Numpy array con la información de la serie de tiempo
    (se supone que se ordena de forma cronológica creciente)

    w: Entero >= 1 que representa la ventana de tiempo para comparar el
    precio serie[i] (serie[i] vs serie[i +- w])

    SALIDA
    level1: numpy array que representa la serie de tiempo sólamente con sus
    mínimos y máximos locales (primer nivel de abstracción)

    indices: lista con los índices de los puntos locales
    '''

    #longitud de la serie
    n = serie.shape[0]

    indices = []

    for i in range(w, n-w):

        #Es mínimo local?
        if serie[i] < serie[i + w] and serie[i] < serie[i - w]:
            indices.append(i)

        #Es máximo local?
        elif serie[i] > serie[i + w] and serie[i] > serie[i - w]:
            indices.append(i)

    level1 = serie[indices]

    return level1, indices

##==============================================================================
## Función para determinar si el precio en un momento i corresponde a una
## tendencia a la alza
##==============================================================================
def uptrend(serie, i):
    '''
    ENTRADA
    serie: Numpy array con la información de la serie de tiempo o una
    abstracción de ella a algún nivel
    (se supone que se ordena de forma cronológica creciente)

    i: Entero que representa el índice inicial

    SALIDA
    boolean: True si se detecta una tendencia a la alza, False en otro caso
    '''

    p = serie[i] #P[i]
    p1 = serie[i + 1] #P[i + 1]
    p2 = serie[i + 2] #P[i + 2]
    p3 = serie[i + 3] #P[i + 3]

    if p < p1 and p < p2 and p1 < p3 and p2 < p3 and np.abs(p1 - p2) < np.abs(p - p2) + np.abs(p1 - p3):
        return True
    else:
        return False


##==============================================================================
## Función para determinar si el precio en un momento i corresponde a una
## tendencia a la baja
##==============================================================================
def downtrend(serie, i):
    '''
    ENTRADA
    serie: Numpy array con la información de la serie de tiempo o una
    abstracción de ella a algún nivel
    (se supone que se ordena de forma cronológica creciente)

    i: Entero que representa el índice inicial

    SALIDA
    boolean: True si se detecta una tendencia a la baja, False en otro caso
    '''

    p = serie[i] #P[i]
    p1 = serie[i + 1] #P[i + 1]
    p2 = serie[i + 2] #P[i + 2]
    p3 = serie[i + 3] #P[i + 3]

    if p > p1 and p > p2 and p1 > p3 and p2 > p3 and np.abs(p2 - p1) < np.abs(p - p2) + np.abs(p1 - p3):
        return True
    else:
        return False


##==============================================================================
## Función para determinar el nivel de abstracción 2
##==============================================================================
def abs_lev2(serie):
    '''
    ENTRADA
    serie: Numpy array con la información de la serie de tiempo o una
    abstracción de ella a algún nivel
    (se supone que se ordena de forma cronológica creciente)

    SALIDA

    level2: numpy array que representa la abstracción

    indices: lista con los índices utilizados de la serie original
    '''

    i = 0
    n = serie.shape[0]
    indices = []

    while i <= n - 1 -3:

        #En esta parte yo omito la función same-trend
        #ya que implícitamente involucra un umbral

        if uptrend(serie, i) or downtrend(serie, i):
            indices.append(i)
            indices.append(i + 3)
            i = i + 3
        else:
            indices.append(i)
            i = i +1

    level2 = serie[indices]

    return level2, indices
