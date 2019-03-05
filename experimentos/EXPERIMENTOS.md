# Descripción de los experimentos
## AQ
+ **AQ_exp_1**:
  + Diccionario 2 (atributos empíricos)
  + Longitud de periodo: 90
  + Etiquetado: Sin señales repetidas, precio Open
  + confidence = 0.9
  + times covered = 2
  + Metodo discretizacion = unsupervised.intervals
  + Número intervalos = 8
  + Ignora espera = TRUE
  + Tipo de precio de ejecución = mid h = 0
  + Banda superior =  0.035
  + Banda inferior =  -0.03
  + Acumula reglas = TRUE
  + top_k = 5

+ **AQ_exp_2**:
  + Diccionario 2 (atributos empíricos)
  + Longitud de periodo: 90
  + Etiquetado: Sin señales repetidas, precio Open
  + confidence = 0.9
  + times covered = 2
  + Metodo discretizacion = unsupervised.intervals
  + Número intervalos = 8
  + Ignora espera = TRUE
  + Tipo de precio de ejecución = mid h = 0
  + Banda superior =  0.035
  + Banda inferior =  -0.03
  + Acumula reglas = FALSE

+ **AQ_exp_3**:
  + Diccionario 2 (atributos empíricos)
  + Longitud de periodo: 90
  + Etiquetado: Sin señales repetidas, precio Open
  + confidence = 0.9
  + times covered = 2
  + Metodo discretizacion = unsupervised.quantiles
  + Número intervalos = 8
  + Ignora espera = TRUE
  + Tipo de precio de ejecución = mid h = 0
  + Banda superior =  0.035
  + Banda inferior =  -0.03
  + Acumula reglas = TRUE
  + top_k = 5

+ **AQ_exp_4**:
  + Diccionario 2 (atributos empíricos)
  + Longitud de periodo: 90
  + Etiquetado: Sin señales repetidas, precio Open
  + confidence = 0.9
  + times covered = 2
  + Metodo discretizacion = unsupervised.quantiles
  + Número intervalos = 8
  + Ignora espera = TRUE
  + Tipo de precio de ejecución = mid h = 0
  + Banda superior =  0.035
  + Banda inferior =  -0.03
  + Acumula reglas = FALSE

## CN2
+ **CN2_exp_1**
  + Diccionario 2 (atributos empíricos)
  + Longitud de periodo: 90
  + Etiquetado: Sin señales repetidas, precio Open
  + K = 5
  + Método discretización = unsupervised.intervals
  + Número intervalos = 8
  + Ignora espera = TRUE
  + Tipo de precio de ejecución = mid h = 0
  + Banda superior =  0.035
  + Banda inferior =  -0.03
  + Acumula reglas = TRUE
  + top_k = 5

+ **CN2_exp_2**
  + Diccionario 2 (atributos empíricos)
  + Longitud de periodo: 90
  + Etiquetado: Sin señales repetidas, precio Open
  + K = 5
  + Método discretización = unsupervised.intervals
  + Número intervalos = 8
  + Ignora espera = TRUE
  + Tipo de precio de ejecución = mid h = 0
  + Banda superior =  0.035
  + Banda inferior =  -0.03
  + Acumula reglas = FALSE

+ **CN2_exp_3**
  + Diccionario 2 (atributos empíricos)
  + Longitud de periodo: 90
  + Etiquetado: Sin señales repetidas, precio Open
  + K = 5
  + Método discretización = unsupervised.quantiles
  + Número intervalos = 8
  + Ignora espera = TRUE
  + Tipo de precio de ejecución = mid h = 0
  + Banda superior =  0.035
  + Banda inferior =  -0.03
  + Acumula reglas = TRUE
  + top_k = 5

+ **CN2_exp_4**
  + Diccionario 2 (atributos empíricos)
  + Longitud de periodo: 90
  + Etiquetado: Sin señales repetidas, precio Open
  + K = 5
  + Método discretización = unsupervised.quantiles
  + Número intervalos = 8
  + Ignora espera = TRUE
  + Tipo de precio de ejecución = mid h = 0
  + Banda superior =  0.035
  + Banda inferior =  -0.03
  + Acumula reglas = FALSE

## YO
+ **AQ_exp_1**
  + Reglas aprendidas en **AQ/AQ_exp_1/** en los periodos 1 al 5.
  + top_k = 5

+ **AQ_exp_2**
  + Reglas aprendidas en **AQ/AQ_exp_1/** en los periodos 1 al 5.
  + top_k = 0 (todas las reglas)