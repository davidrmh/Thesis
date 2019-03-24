# coding: utf-8
import pandas as pd
import numpy as np
import copy as cp
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

##==============================================================================
## VARIABLES GLOBALES
##==============================================================================
capital=100000.00
comision=0.25/100
tasa=0.0/100
#Fija semilla
np.random.seed(54321)
incentivoSig = 15.0 / 100 # porcentaje de señales (efectivas) para evitar tener pocas observaciones útiles

##==============================================================================
## Función para inicializar variables globales
##==============================================================================
def inicializaGlobales():
    capital=100000.00
    comision=0.25/100
    tasa=0.0/100
    return

##==============================================================================
## Función para obtener un subconjunto de datos de acuerdo a fechas dadas
##==============================================================================
def subconjunto(datos,fechaInicio,fechaFin):
    '''
    ## ENTRADA
    ## datos: Pandas DataFrame creado con leeTabla
    ##
    ##fechaInicio: String en formato 'YYYY-MM-DD' que representa la fecha inicial
    ##
    ## fechaFin: String en formato 'YYYY-MM-DD' que representa la última fecha
    ##
    ## SALIDA
    ## subconjunto: Pandas DataFrame con el subconjunto de datos
    '''

    #Encuentra el índice de inicio
    indiceInicio=datos[datos['Date']==fechaInicio].index[0]
    if not indiceInicio:
        print "Fecha inicio no encontrada"
        return 0
    #Encuentra el índice final
    indiceFin=datos[datos['Date']==fechaFin].index[0]
    if not indiceFin:
        print "Fecha fin no encontrada"
        return 0

    subconjunto = datos[indiceInicio:(indiceFin + 1) ]
    subconjunto=subconjunto.reset_index(drop=True)
    return subconjunto

##==============================================================================
## Función para determinar si una compra es posible
## se basa en np.floor(efectivo/(precio*(1+comision)))>0
##==============================================================================
def compraPosible(efectivo,precioEjec):
    '''
    ENTRADA
    efectivo: Número que representa el dinero disponible
    precioEjecucion: Número que representa el precio en el que se comprará

    SALIDA
    bool: True si es posible comprar False en otro caso
    '''
    if np.floor(efectivo/(precioEjec*(1+comision)))>0:
        return True
    else:
        return False

##==============================================================================
## Función para calcular el precio de ejecución
##==============================================================================
def precioEjecucion(datos, fecha, tipo = 'open', h = 0):
    '''
    ENTRADA
    datos: Pandas dataframe con la columna Date y los distintos precios

    fecha: string con formato 'YYYY-MM-DD' que representa la fecha en que se 
    calcula el precio de ejecución

    h: Entero positivo que representa el número de periodos en el futuro, a partir de  'fecha',
    en el cual se calculará el precio de ejecución

    tipo: String que indica el tipo de precio de ejecución

    'open': precioEjecucion = Precio de apertura en el día 'fecha' + h
    
    'mid': precioEjecucion = promedio entre High y Low en 'fecha' +  h

    'adj.close': precioEjecucion = Cierre ajustado en 'fecha' + h

    'close': Precio de Ejecucion = Cierre en 'fecha' + h

    SALIDA
    float que representa el precio de ejecución
    '''

    indiceFecha = datos[datos['Date']==fecha].index[0]
    ultimoIndice = datos.shape[0] - 1

    #para evitar out of bouds
    if indiceFecha + h > ultimoIndice:
        h = 0

    if tipo == 'open':
        return float(datos['Open'].iloc[indiceFecha + h])

    elif tipo == 'mid':
        return (float(datos['High'].iloc[indiceFecha + h]) + float(datos['Low'].iloc[indiceFecha + h])) / 2.0

    elif tipo == 'adj.close':
        #Este 'if' es para compatibilidad con dataframes que siguen las reglas de R al nombrar las columnas

        if 'Adj.Close' in datos.columns:
            #Columna nombrada por R
            return float(datos['Adj.Close'].iloc[indiceFecha + h])
        else:
            return float(datos['Adj Close'].iloc[indiceFecha + h])  

    elif tipo == 'close':
        return float(datos['Close'].iloc[indiceFecha + h])

    else:
        print 'ERROR: TIPO DE PRECIO NO RECONOCIDO'
        return ''


##==============================================================================
##                      EITQUETAMIENTO (ALGORITMO GENÉTICO)
##==============================================================================

##==============================================================================
## Función de fitness para el etiquetamiento del método 2
##==============================================================================
def fitnessMetodo2(datos, flagOper = True, tipoEjec = 'open', h = 0):    
    '''
    ENTRADA:
    datos. Pandas DataFrame con los precios y la columna Clase

    flagOper. Booleano. True => Considera el número de transacciones
    False => No considera el número de transacciones

    tipoEjec: String que indica el tipo de precio de ejecución (ver función precioEjecucion)

    h: Entero positivo que representa el número de periodos en el futuro, a partir de  'fecha', 
    en el cual se calculará el precio de ejecución

    SALIDA:
    exceso. Float. Exceso de ganancia
    '''
    inicializaGlobales()

    acciones=0
    flagPosicionAbierta=False
    ultimoPrecio=0
    efectivo=capital
    numSignals=datos.shape[0]

    fechaInicio=datos['Date'].iloc[0]
    fechaFin=datos['Date'].iloc[numSignals-1]

    ##################################################################
    ##Cálculo de la ganancia siguiendo la estrategia de Buy and Hold##
    ##################################################################

    #Se compra en el segundo día del conjunto de datos
    #esto es para comparar correctamente con la estrategia generada
    precioInicioEjec = precioEjecucion(datos, fechaInicio, tipoEjec, h)
    acciones = np.floor(efectivo / (precioInicioEjec * (1 + comision)))
    efectivo = efectivo-precioInicioEjec * acciones * (1 + comision)
    precioFinEjec = precioEjecucion(datos, fechaFin, tipoEjec, h)


    #Ganancia de intereses PENDIENTE
    #Como es una persona invirtiendo se suponen intereses simples
    fInicio=pd.to_datetime(fechaInicio,format='%Y-%m-%d')
    fFin=pd.to_datetime(fechaFin,format='%Y-%m-%d')
    deltaDias=(fFin-fInicio)/np.timedelta64(1,'D') #Diferencia en días
    #Para los intereses se consideran fines de semana
    intereses=efectivo*tasa*deltaDias/365

    #Vendemos las acciones compradas en el pasado
    #y calculamos el efectivo final asi como la ganancia de Buy and Hold
    efectivo=efectivo + intereses +acciones*precioFinEjec*(1-comision)
    gananciaBH=(efectivo - capital)/capital

    ##################################################################
    ###Cálculo de la ganancia siguiendo la estrategia del individuo###
    ##################################################################

    efectivo=capital
    acciones=0
    intereses=0
    fUltimaOperacion=pd.to_datetime(fechaInicio,format='%Y-%m-%d')
    #contador de operaciones
    contOper = 0
    contOperGanancia = 0

    #No se incluye el último periodo, por eso es numSignals - 1
    #en este periodo se cierra la posición abierta (en caso de haberla)
    for t in range(0,numSignals-1):

        #para evitar comprar y vender el mismo día
        flagCompraReciente=False

        #Se calcula el precio de ejecución
        fecha = datos['Date'].iloc[t]
        precioEjec = precioEjecucion(datos, fecha, tipoEjec, h)

        #Cálculo los intereses acumulados hasta el momento
        #PENDIENTE

        #es posible comprar?
        #Se ejecuta compra cuando se tiene dinero y no se había comprado previamente
        if datos['Clase'].iloc[t]==1 and compraPosible(efectivo,precioEjec) and not flagPosicionAbierta:

            #Se compran más acciones (Se invierte todo el dinero posible)
            acciones = acciones + np.floor(efectivo / (precioEjec * (1 + comision)))

            #Se reduce el efectivo
            efectivo = efectivo - precioEjec * acciones * (1 + comision)

            #Se registra una posición abierta
            flagPosicionAbierta=True

            #Se registra el último precio de compra
            ultimoPrecioCompra=precioEjec

            #Se actualiza flagCompraReciente
            flagCompraReciente=True

            #Se incrementa el contador de operaciones
            contOper = contOper + 1

        #es posible vender?
        #No se permiten ventas en corto por eso acciones > 0
        #Se venden todas las acciones en un sólo momento
        #Se vende cuando:
        #--Hay señal de venta y se tienen acciones
        if acciones>0 and datos['Clase'].iloc[t]==-1:

            #Aumenta el efectivo
            efectivo=efectivo + acciones * precioEjec * (1 - comision)

            #Disminuyen acciones
            acciones=0

            #Se cierra una posición abierta
            flagPosicionAbierta=False

            #Se incrementa el contador de operaciones
            contOper = contOper + 1
            if precioEjec > ultimoPrecioCompra:
                contOperGanancia = contOperGanancia + 1

    #Se cierra posición abierta (si la hay)

    if flagPosicionAbierta:
        #cálculo del precio de ejecución
        fecha = datos['Date'].iloc[numSignals - 1]
        precioEjec = precioEjecucion(datos, fecha, tipoEjec, h)

        #Aumenta el efectivo
        efectivo = efectivo + acciones * precioEjec * (1 - comision)

        #Disminuyen acciones
        acciones = 0

        #Se incrementa el contador de operaciones
        contOper = contOper + 1
        if precioEjec > ultimoPrecioCompra:
            contOperGanancia = contOperGanancia + 1


    #Se calcula ganancia final
    ganancia = (efectivo - capital) / capital

    #Exceso de ganancia (buscamos maximizar esta cantidad)
    exceso = ganancia - gananciaBH

    #Se ajusta por el número de operaciones
    if flagOper:
        exceso = contOperGanancia * exceso / contOper

    #Se penaliza si hay pocas señales (efectivas y que generen ganancias) 
    datos_limpios = limpiaRepetidas(datos)
    datos_limpios = eliminaPerdidas(datos_limpios, tipoEjec, h)
    n_compras = len(datos_limpios[datos_limpios['Clase'] == 1].index)

    if n_compras < numSignals * incentivoSig:
        exceso = exceso - 0.5

    return exceso

##==============================================================================
## Función para crear la población
##==============================================================================
def creaPoblacion (numPeriodos,popSize,proba=""):
    '''
    ENTRADA
    numPeriodos: Entero. Número de periodos en el subconjunto de datos
    (idealmente datos.shape[0])

    popSize: Entero. Número de individuos en la población

    proba: Lista con numPeriodos elementos, cada uno de ellos es una
    lista con la probabilidad de seleccionar un -1, 0 o 1.
    Por ejemplo para dos periodos [[0.2,0.2,0.6],[0.6,0.4,0]]

    SALIDA
    poblacion. numpy array de popSize x numPeriodos (matriz) cuyo i-ésimo
    renglón representa una posible estrategia para el periodo de interés
    '''
    aux=[]
    poblacion=[]
    for i in range(0,popSize):
        aux=[]
        for t in range(0,numPeriodos):
            if proba=="":
                #aux guarda la información del individuo i
                r=np.random.choice([-1,0,1],size=1)[0]

                if t==(numPeriodos-1):
                    #la última señal es señal de venta
                    r=-1

                aux.append(r)
            else:
                r=np.random.choice([-1,0,1],size=1,p=proba[t])[0]

                if t==(numPeriodos-1):
                    #la última señal es señal de venta
                    r=-1

                aux.append(r)
        poblacion.append(aux)

    poblacion=np.array(poblacion)

    return poblacion

##==============================================================================
## Función para regresar calcular el fitness de cada individuo en la población
##==============================================================================
def fitnessPoblacion (datos,poblacion, flagOper = True, tipoEjec = 'open', h = 0):
    '''
    ENTRADA
    datos. Pandas DataFrame con los precios

    poblacion: numpy array  (idealmente creado con la función creaPoblacion)

    flagOper. Booleano. True => Considera el número de transacciones
    False => No considera el número de transacciones

    tipoEjec: String que indica el tipo de precio de ejecución (ver función precioEjecucion)

    h: Entero positivo que representa el número de periodos en el futuro, a partir de  'fecha', 
    en el cual se calculará el precio de ejecución

    SALIDA
    fitness: numpy array. arreglo cuya i-ésima entrada representa el fitness
    proporcional (probabilidad) del i-ésimo individuo (i-ésimo renglón de población)

    sinAjuste: numpy array. Arreglo cuya i-ésima entrada representa el fitness del
    i-ésimo individuo (i-ésimo renglón de población)
    '''
    fitness=[]
    auxDatos=cp.deepcopy(datos)

    for i in poblacion:
        auxDatos.loc[:,('Clase')]=i #De esta forma para evitar el warning
        fitness.append(fitnessMetodo2(auxDatos, flagOper, tipoEjec, h))

    sinAjuste=cp.deepcopy(fitness)
    sinAjuste=np.array(sinAjuste)

    #Normaliza para que todas las entradas sean positivas
    margen=0.00001 #para evitar entradas con 0
    probas=np.array(fitness)-np.min(fitness) + margen
    probas=probas/np.sum(probas)

    return probas,sinAjuste

##==============================================================================
## Función para seleccionar los k-mejores individuos de una población
##==============================================================================
def kMejores(poblacion,fitness,k):
    '''
    ENTRADA
    poblacion: numpy array creado con la función creaPoblacion

    fitness: numpy array. Arreglo cuya i-ésima entrada representa el fitness del
    i-ésimo individuo (i-ésimo renglón de población)

    k: Entero mayor o igual a 1

    SALIDA
    mejores: numpy array con los k individuos con mayor fitness
    '''

    #argsort funcion de menor a mayor por eso se utiliza reverse
    aux=list(np.argsort(fitness))
    aux.reverse() #Método destructivo

    #elige los k-mejores
    mejores=poblacion[aux[0:k],:]

    return mejores
##==============================================================================
## Función para actualizar las probabilidades de acuerdo a los k-mejores
##==============================================================================
def actualizaProbabilidades (mejores):
    '''
    ENTRADA
    mejores. numpy array creado con la función kMejores

    SALIDA
    proba: Lista con numPeriodos elementos, cada uno de ellos es una
    lista con la probabilidad de seleccionar un -1, 0 o 1.
    Por ejemplo para dos periodos [[0.2,0.2,0.6],[0.6,0.4,0]]
    '''

    numPeriodos=mejores.shape[1]
    k=mejores.shape[0]
    aux=[] #almacena tres probabilidades(para -1,0 y 1)
    probas=[]
    for t in range(0,numPeriodos):
        aux=[]
        for i in [-1,0,1]:
            #p es la probabilidad de tener el valor i
            #en el periodo t
            p=float(np.sum(mejores[:,t]==i))/k
            aux.append(p)
        probas.append(aux)

    return probas

##==============================================================================
## Función para limpiar las señales repetidas
##==============================================================================
def limpiaRepetidas(datos):
    '''
    ENTRADA
    datos: Pandas dataframe con la Columna Clase (ver función etiquetaMetodo2)

    SALIDA
    datosLimpios: Pandas dataframe 'datos' con la columna Clase eliminando las señales
    repetidas
    '''
    #copia datos
    datosLimpios = cp.deepcopy(datos)

    #guarda en un numpy array (para modificar sin warnings de pandas)
    clase = np.array(datosLimpios['Clase'])

    #número de observaciones
    n = clase.shape[0]

    #compra / venta en el pasado?
    flagCompra = False
    flagVenta = False

    for t in range(0, n):

        #Venta en el pasado
        if clase[t] == -1 and flagCompra == False and flagVenta == True:
            clase[t] = 0
        #Se inicia con señal de venta
        elif clase[t] == -1 and flagCompra == False and flagVenta == False:
            clase[t] = 0
        #Compra en el pasado
        elif clase[t] == 1 and flagCompra == True and flagVenta == False:
            clase[t] = 0

        #Cambio de banderas
        elif clase[t] == 1 and flagCompra == False:
            flagCompra = True
            flagVenta = False
        elif clase[t] == -1 and flagVenta == False:
            flagVenta = True
            flagCompra = False

    datosLimpios['Clase'] = clase

    return datosLimpios

##==============================================================================
## Función para eliminar las operaciones que generen pérdidas
##==============================================================================
def eliminaPerdidas(datos, tipoEjec = 'open', h = 0):
    '''
    ENTRADA
    datos: Pandas DataFrame con los precios y la columna Clase

    tipoEjec: String que indica el tipo de precio de ejecución (ver función precioEjecucion)

    h: Entero positivo que representa el número de periodos en el futuro, a partir de  'fecha', 
    en el cual se calculará el precio de ejecución

    SALIDA
    El DataFrame 'datos' sin las operaciones que generan pérdidas
    '''

    #índices de compra
    indicesCompra = datos[datos['Clase'] == 1].index

    #Memoria de los índices de venta que se han analizado
    memoria = []

    #Quita las ventas que ocurren antes de la primera compra
    indicesVenta = datos[datos['Clase'] == -1].index
    indicesVenta = indicesVenta[indicesVenta < indicesCompra[0] ]
    datos.loc[indicesVenta,'Clase'] = 0

    for i in indicesCompra:

        #Obtiene los índices de venta
        indicesVenta = datos[datos['Clase'] == -1].index

        #Filtra para obtener sólo los que son mayores al índice de compra actual
        indicesVenta = indicesVenta[indicesVenta > i]

        #Quita los que ya fueron analizados
        indicesVenta = indicesVenta.difference(pd.Index(memoria))

        #Si todavía hay ventas
        if len(indicesVenta) != 0:

            #Elige el índice de la venta más próxima a la compra actual
            j = indicesVenta[0]

            #Obtiene los precios de ejecución de los movimientos
            fechaCompra = datos['Date'].iloc[i]
            fechaVenta = datos['Date'].iloc[j]
            precioCompra = precioEjecucion(datos, fechaCompra, tipoEjec, h)
            precioVenta = precioEjecucion(datos, fechaVenta, tipoEjec, h)

            #Elimina la operación si ésta causó pérdida
            if precioCompra > precioVenta:
                datos.loc[i, 'Clase'] = 0
                datos.loc[j, 'Clase'] = 0

            #Actualiza la memoria
            memoria.append(j)

    return datos    


##==============================================================================
## Función para etiquetar los datos de acuerdo al método 2
##==============================================================================

def etiquetaMetodo2(datos,numGen=30,popSize=50, flagOper = True, limpia = True, tipoEjec = 'open', h = 0):
    '''
    Etiqueta los datos utilizando un algoritmo genético que busca
    la combinación de señales compra,venta,hold que generen mayor ganancia

    ENTRADA
    datos: Pandas DataFrame. Conjunto de entrenamiento

    flagOper. Booleano. True => Considera el número de transacciones
    False => No considera el número de transacciones

    limpia: Booleano. True => Limpia señales repetidas.

    tipoEjec: String que indica el tipo de precio de ejecución (ver función precioEjecucion)

    h: Entero positivo que representa el número de periodos en el futuro, a partir de  'fecha', 
    en el cual se calculará el precio de ejecución

    SALIDA
    datos: Pandas DataFrame. Conjunto de entrenamiento con la nueva columna
    Clase, que contiene la estrategia encontrada por el algoritmo genético.
    '''

    numPeriodos=datos.shape[0]
    k=int(popSize/2) #k-mejores

    #poblacion inicial
    poblacion=creaPoblacion(numPeriodos,popSize,proba="")

    mejorFitness=-100
    mejorEstrategia=""

    #Para evitar seguir iterando cuando no se puede mejorar
    contadorFlat = 0
    mejorFitnessAnterior = 0

    for i in range(0,numGen):

        if contadorFlat >= 10:
            print 'No ha habido mejora en 10 generaciones'
            break

        #Calcula el fitness de la poblacion
        probas,fitness=fitnessPoblacion(datos,poblacion, flagOper, tipoEjec, h)

        #Encuentra los k mejores
        mejores=kMejores(poblacion,probas,k)

        #Guarda los mejores hasta el momento
        if fitness[np.argmax(fitness)]>mejorFitness:
            mejorFitness=fitness[np.argmax(fitness)]
            mejorEstrategia=mejores[0]
            contadorFlat = 0
            mejorFitnessAnterior = mejorFitness
        else:
            if mejorFitnessAnterior > 0:
                contadorFlat = contadorFlat + 1

        #Para ahorrar tiempo se rompe el loop si mejorFitness > 0.2
        if mejorFitness > 0.2:
            print "Mejor fitness = " + str(round(np.max(mejorFitness),6)) +   " se rebasa el umbral de 0.2"
            break    

        #actualiza probabilidades
        probas=actualizaProbabilidades(mejores)

        #crea la nueva población
        poblacion=creaPoblacion(numPeriodos,popSize,probas)

        print "Fin de la generacion " + str(i)
        print "Mejor fitness hasta el momento " + str(round(np.max(mejorFitness),6))

    #añade la estrategia del mejor individuo
    datos.loc[:,('Clase')]=mejores[0,:]

    #Limpia señales repetidas
    if limpia:
        datos = limpiaRepetidas(datos)

    #Elimina operaciones que generan pérdidas
    datos = eliminaPerdidas(datos, tipoEjec, h)  

    return datos