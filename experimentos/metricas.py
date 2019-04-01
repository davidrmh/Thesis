# coding: utf-8
import pandas as pd
import numpy as np
##==============================================================================
## VARIABLES GLOBALES
##==============================================================================
capital=100000.00
comision=0.25/100
tasa=0.0/100
glob_bandaSuperior = 4.0 / 100 #número positivo
glob_bandaInferior = -3.0 / 100 #numero negativo


##==============================================================================
## Función para inicializar variables globales  
##==============================================================================
def inicializaGlobales(dicc):
  '''
  ENTRADA

  dicc: Diccionario con el valor de cada parámetro

  SALIDA
  inicializa variables globales
  '''
  global capital
  global comision
  global glob_bandaSuperior
  global glob_bandaInferior
  
  capital = dicc['capital']
  comision = dicc['comision']
  glob_bandaSuperior = dicc['bandaSuperior']
  glob_bandaInferior = dicc['bandaInferior']
  #tasa = dicc['tasa']
  return


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
	indiceFecha = datos[datos['Date']==fecha].index[0];
	ultimoIndice = datos.shape[0] - 1

	#Para evitar error 'out of bounds'
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
## Cálculo de Buy and Hold
##==============================================================================
def buyHold(datos, tipoEjec = 'open', h = 0, version = 'normal'):
    '''
    ENTRADA
    datos: Pandas dataframe con los precios y la columna Clase

    tipoEjec: String que indica el tipo de precio de ejecución (ver función precioEjecucion)

    h: Entero positivo que representa el número de periodos en el futuro, a partir de  'fecha',
    en el cual se calculará el precio de ejecución

    version: String que representa la versión de buy-and-hold que se calcula.
    'normal' => Compra al inicio y venta al final del periodo
    'mod' => Compra = primera compra. Venta = última venta

    SALIDA
    float que representa la ganancia de buy-and-hold
    '''
    #Obtiene fecha de inicio y fecha fin
    if version == 'normal':
        fechaInicio=datos['Date'].iloc[0]
        fechaFin=datos['Date'].iloc[-1]
    elif version == 'mod':
        #Al menos hay una compra y una venta
        if len(datos[datos['Clase'] == 1].index) > 0 and len(datos[datos['Clase'] == -1].index) > 0:
            indiceInicio = datos[datos['Clase'] == 1].index[0]
            indiceFin = datos[datos['Clase'] == -1].index[-1]
            fechaInicio = datos.loc[indiceInicio,'Date']
            fechaFin = datos.loc[indiceFin,'Date']
        else:
            return 0    

    #Cálculo de BH
    efectivo = capital

    #precio de compra
    precioInicioEjec = precioEjecucion(datos, fechaInicio, tipoEjec, h)

    #acciones compradas
    acciones = np.floor(efectivo / (precioInicioEjec * (1 + comision)))

    #efectivo restante después de la compra
    efectivo = efectivo-precioInicioEjec * acciones * (1 + comision)

    #precio venta
    precioFinEjec = precioEjecucion(datos, fechaFin, tipoEjec, h)

    #efectivo final después de la venta
    efectivo=efectivo  + acciones * precioFinEjec * (1 - comision)

    #Ganancia BH
    gananciaBH=(efectivo - capital)/capital

    #Si la ganancia BH < 0 entonces no convenía vender al final
    #del periodo, una persona (inteligente) no haría tal movimiento
    #Sólo vendería si se supera su umbral de riesgo
    diferencia_porcentual = (precioFinEjec * (1 - comision) ) / ( precioInicioEjec * (1 + comision) ) - 1
    if gananciaBH < 0 and diferencia_porcentual > glob_bandaInferior:
        gananciaBH = 0 # No vender (no se reconoce la pérdida)

    return gananciaBH    

##==============================================================================
## Función para calcular el Excess Return de una estrategia
##==============================================================================
def excessReturn(datos, flagOper = True, tipoEjec = 'open', h = 0, flagTot = False,
 dicc_glob = {'capital':100000.0, 'comision':0.25 / 100, 'bandaSuperior':0.035, 'bandaInferior':-0.03, 'tasa':0}, version = 'normal'):
    '''
    ENTRADA:
    datos. Pandas DataFrame con los precios y la columna Clase

    flagOper. Booleano. True => Considera el número de transacciones
    False => No considera el número de transacciones

   	tipoEjec: String que indica el tipo de precio de ejecución (ver función precioEjecucion)

    h: Entero positivo que representa el número de periodos en el futuro, a partir de  'fecha',
    en el cual se calculará el precio de ejecución

	flagTot: Booleano. True => Se calcula ganancia total porcentual. False => Se calcula el exceso de ganancia

    dicc_glob: Diccionario para inicializar las variables globales

    version: String que representa la versión de buy-and-hold que se calcula.
    'normal' => Compra al inicio y venta al final del periodo
    'mod' => Compra = primera compra. Venta = última venta

    SALIDA:
    exceso. Float. Exceso de ganancia
    '''
    ##################################################################
    ###Cálculo de la ganancia siguiendo la estrategia del individuo###
    ##################################################################
    inicializaGlobales(dicc_glob)
    flagPosicionAbierta = False
    ultimoPrecio = 0
    efectivo = capital
    acciones = 0
    intereses = 0
    #fUltimaOperacion = pd.to_datetime(fechaInicio,format='%Y-%m-%d')
    numSignals = datos.shape[0]
    #contador de operaciones
    contOper = 0

    #ganancia acumulada porcentual
    ganancia_acum_porcentual = 0

    #No se incluye el último periodo, por eso es numSignals - 1
    #en este periodo se cierra la posición abierta (en caso de haberla)
    for t in range(0,numSignals - 1):

        #Se calcula el precio de ejecución
        fecha = datos['Date'].iloc[t]
        precioEjec = precioEjecucion(datos, fecha, tipoEjec, h)

        #Cálculo los intereses acumulados hasta el momento
        #PENDIENTE

        #es posible comprar?
        #Se ejecuta compra cuando se tiene dinero y no se había comprado previamente
        if datos['Clase'].iloc[t] == 1 and compraPosible(efectivo,precioEjec) and not flagPosicionAbierta:

            #Se compran más acciones (Se invierte todo el dinero posible)
            acciones = acciones + np.floor(efectivo / (precioEjec * (1 + comision)))

            #Se reduce el efectivo
            efectivo = efectivo - precioEjec * acciones * (1 + comision)

            #Se registra una posición abierta
            flagPosicionAbierta=True

            #Se registra el último precio de compra
            ultimoPrecioCompra=precioEjec

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

            #calcula la ganancia acumulada hasta el momento
            #ganancia_acum_porcentual = ganancia_acum_porcentual + (efectivo / capital - 1)
            ganancia_acum_porcentual = (efectivo / capital - 1)

            #Disminuyen acciones
            acciones=0

            #Se cierra una posición abierta
            flagPosicionAbierta=False

            #Se incrementa el contador de operaciones
            contOper = contOper + 1

    #Se cierra posición abierta (si la hay)

    #Esta parte era para forzar una venta al final del periodo
    #sin importar si generaba una pérdida
    '''
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

    #Se calcula ganancia final
    ganancia = (efectivo - capital) / capital
    '''
    #Si al final del episodio hay una posición abierta, sólo se vende cuando:
    # 1. La venta genera ganancias
    # 2. La diferencia entre los precios de compra y venta rebasa el umbral de riesgo
    if flagPosicionAbierta:

        #cálculo del precio de ejecución
        fecha = datos['Date'].iloc[numSignals - 1]
        precioEjec = precioEjecucion(datos, fecha, tipoEjec, h)

        #diferencia entre precios
        #considerando costos de transacción
        diferencia_porcentual = ( precioEjec*(1 - comision) ) / (ultimoPrecioCompra*(1 + comision) ) - 1

        #Caso: Venta UltimaOperacion genera ganancias
        #o La diferencia entre los precios de compra y venta rebasa el umbral de riesgo
        if diferencia_porcentual > 0 or diferencia_porcentual < glob_bandaInferior:

            #Aumenta el efectivo y disminuyen acciones
            efectivo = efectivo + acciones * precioEjec * (1 - comision)
            acciones = 0

            #Aumenta ganancia acumulada porcentual
            #ganancia_acum_porcentual = ganancia_acum_porcentual + (efectivo / capital - 1)
            ganancia_acum_porcentual = (efectivo / capital - 1)

            #Ajusta 'datos' para el cálculo de BH
            datos.loc[numSignals - 1, 'Clase'] = -1

    #Ganancia total porcentual
    if flagTot:
      return ganancia_acum_porcentual * capital

    gananciaBH = buyHold(datos, tipoEjec, h, version)  

    #Exceso de ganancia (buscamos maximizar esta cantidad)
    exceso = ganancia_acum_porcentual - gananciaBH

    #Se ajusta por el número de operaciones
    if flagOper:
        exceso = exceso / contOper

    return exceso

##==============================================================================
## Función para crear un CSV con los resultados de métrica en cada archivo
##==============================================================================
def evaluaMetrica(ruta_pred = './AQ/AQ_resultados/', ruta_arch = 'arch_evaluar.csv', ruta_dest='./AQ/', metrica = 'exret', aux = 'AQ',
 dicc = {'flagOper': False, 'tipoEjec': 'open', 'h': 0},
  dicc_glob = {'capital':100000.0, 'comision':0.25 / 100, 'bandaSuperior':0.035, 'bandaInferior':-0.03, 'tasa':0}, version = 'normal'):
	'''
	ENTRADA

	ruta_pred: String con la ruta de la carpeta que contiene los archivos con las predicciones

	ruta_arch: String con la ruta del archivo que contiene el nombre de los cojuntos de datos a evaluar

	ruta_dest: String que contiene la ruta del archivo en donde se guardarán los resultados

	metrica: string con el nombre de la métrica a evaluar
	'exret' = excessReturn
	'totret' = Ganancia total porcentual

	aux: String auxiliar para nombrar el archivo de salida, el nombre tendrá la forma 'metricas-' + aux

	dicc: Diccionario con los parámetros utilizados en la métrica a evaluar (key = string con el nombre del parámetro)

    dicc_glob: Diccionario para inicializar las variables globales

    version: String que representa la versión de buy-and-hold que se calcula.
    'normal' => Compra al inicio y venta al final del periodo
    'mod' => Compra = primera compra. Venta = última venta

	SALIDA
	Crea un CSV con el resultado de las métricas para cada archivo
	'''
	#Abre el archivo en ruta_arch
	archivos = pd.read_csv(ruta_arch)

	#número de archivos
	numArch = archivos.shape[0]

	#nombre del archivo de salida
	nombre_salida = ruta_dest +'-'.join(['metrica', metrica, aux]) + '.csv'

	#Obtiene los parámetros de la métrica
	if metrica == 'exret' or metrica == 'totret':
		flagOper = dicc['flagOper']
		tipoEjec = dicc['tipoEjec']
		h = dicc['h']

	#dataframe de salida
	salida = pd.DataFrame()

	for i in range(0, numArch):

		#nombre del archivo con las predicciones
		arch_pred = archivos.loc[i,'archivo']
		nombre_pred = ruta_pred + arch_pred
		datos = pd.read_csv(nombre_pred)

		#Calcula la métrica correspondiente
		if metrica == 'exret':
			performance = excessReturn(datos, flagOper, tipoEjec, h, False, dicc_glob, version)
			salida.loc[i, 'archivo'] = arch_pred
			salida.loc[i, metrica] = performance

		elif metrica == 'totret':
			performance = excessReturn(datos, flagOper, tipoEjec, h, True, dicc_glob)
			salida.loc[i, 'archivo'] = arch_pred
			salida.loc[i, metrica] = performance

	#Guarda el csv
	salida.to_csv(nombre_salida, index = False)

	print 'Métrica evaluada, revisa el archivo'

	return
