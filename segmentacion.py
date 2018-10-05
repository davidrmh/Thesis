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
