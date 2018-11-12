# coding: utf-8

##==============================================================================
## Conjunto de funciones relacionadas a la metodología OCAT
## Autor: David Montalván
##==============================================================================
import numpy as np
import pandas as pd

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
        val_unico = np.array(atributos.iloc[:,j])

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
            val_unico = np.array(atributos.iloc[:,j])

            #convierte en ceros y unos
            # val_atributo <= val_unico => 1, 0 en otro caso
            ceros_unos = (val_atributo <= val_unico).astype(np.int)

            #agrega a renglon_bin
            renglon_bin.extend(list(ceros_unos))

        binarizados.append(renglon_bin)

    #convierte en pandas dataframe
    nombres_columnas = crea_nombres(atributos)
    binarizados = pd.DataFrame(binarizados, columns = nombres_columnas)

    return binarizados
