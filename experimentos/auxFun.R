##==============================================================================================
## Conjunto de funciones auxiliares
##==============================================================================================
library(dplyr)
library(stringr)

# Esta variable sirve como los ifdef de c++
# se utiliza para evitar importar el código si ya se ha importado
AUX_FUN_R <- "AUX_FUN_R"

##==============================================================================================
## Función para remover la clase ESPERA (Clase 0) de un conjunto de datos
##
## ENTRADA
## datos: Pandas dataframe o tibble que contiene una columna llamada Clase
##
## SALIDA
## Pandas dataframe sin las observaciones en las que Clase == 0
##==============================================================================================
quitaEspera <- function(datos){
  
  return(dplyr::filter(datos, Clase != 0))
  
}

##==============================================================================================
## Función para calcular el precio de ejecución para un conjunto de fechas dadas
##
## ENTRADA
##  datos: Pandas dataframe con los precios y la columna Date
##
##  fechas: Vector con elementos del tipo 'factor' que representa las fechas de ejecución
##
##  tipo: String que representa el tipo de precio de ejecución a calcular
##
## 	'open': precioEjecucion = Precio de apertura en el día 'fecha' + h
##
##  'mid': precioEjecucion = promedio entre High y Low en 'fecha' +  h
##
##  'adj.close': precioEjecucion = Cierre ajustado en 'fecha' + h
##
##  'close': Precio de Ejecucion = Cierre en 'fecha' + h
##
##
## SALIDA
##  Vector con el precio de ejecución correspondiente a cada elemento en 'fechas'
##==============================================================================================
preciosEjecucion <- function(datos, fechas, tipo = 'open'){
  
  #Para almacenar los precios de ejecución
  preciosEj <- c()
  
  for(fecha in fechas){
    
    #índice de la observación correspondiente
    indice <- which(datos$Date == fecha)
    
    if(tipo == 'open'){
      precio <- datos$Open[indice]
      preciosEj <- c(preciosEj, precio)
    }
    
    else if(tipo == 'mid'){
      precio <- mean(c(datos$High[indice], datos$Low[indice]))
      preciosEj <- c(preciosEj, precio)
    }
    
    else if(tipo == 'Adj.Close'){
      precio <- datos$Adj.Close[indice]
      preciosEj <- c(preciosEj, precio)
    }
    
    else if(tipo == 'Close'){
      precio <- datos$Close[indice]
      preciosEj <- c(preciosEj, precio)
    }
    
  }
  
  preciosEj
}

##==============================================================================================
## Función para agregar nuevas reglas a la lista lista_ganancia_reglas
##
## ENTRADA
## reglas: Vector con strings que representan reglas
## cada regla tiene la forma IF MFI.14 is [-Inf,29.9] THEN  is 1; (supportSize=3; laplace=0.8)
##
## lista: lista que contiene la ganancia acumulada de cada regla
##
## SALIDA
## lista con las reglas que antes no se tenían
##==============================================================================================
agregaReglas <- function(reglas, lista){
  for(regla in reglas){
    #Sólo agrega las reglas que no se tenían
    if(is.null(lista[[regla]])){
      lista[[regla]] <- 0
    }
  }
  return(lista)
}

##==============================================================================================
## Función para actualizar la ganancia de cada regla de acuerdo al archivo log más reciente
##
## ENTRADA
## nombre_log: ruta del archivo log
##
## lista: lista que contiene la ganancia acumulada de cada regla
##
## reglas: Vector de strings que representan reglas
##
## SALIDA
## lista con la nueva ganancia de cada regla
##==============================================================================================
actualizaLista <- function(nombre_log, lista, reglas){
  #Abre el archivo log
  df_log <- read.csv(nombre_log, stringsAsFactors = FALSE)
  
  #Si no se realizaron operaciones no hay nada que actualizar
  if(nrow(df_log) == 0){
    return(lista)
  }
  #obtiene los índices de compra y de venta
  indices_compra <- which(str_detect(df_log$accion, "Compra"))
  indices_venta <- which(str_detect(df_log$accion, "Venta"))
  
  #memoria para saber que reglas penalizar por no ser utilizadas
  memoria <- c()
  
  #para registrar pérdidas
  registro_perdidas <- c()
  
  for(i in 1:length(indices_compra)){
    
    #calcula la ganancia de cada regla
    precioCompra <- df_log$precioEjec[indices_compra[i]]
    precioVenta <- df_log$precioEjec[indices_venta[i]]
    ganancia <- precioVenta / precioCompra - 1
    
    if(ganancia > 0){
      puntos <- 1
    }
    else{
      registro_perdidas <- c(registro_perdidas, ganancia)
      puntos <- -1
    }
    
    #Actualiza la lista con las ganancias
    regla_compra <- df_log$regla[indices_compra[i]]
    regla_venta <- df_log$regla[indices_venta[i]]
    lista[[regla_compra]] <- lista[[regla_compra]] + ganancia
    
    #Agrega regla de compra a la memoria
    memoria <- c(memoria, regla_compra)
    
    #Extrae los valores de supportSize de cada regla
    soporte_compra <- as.numeric(str_replace_all(str_extract(regla_compra, "supportSize=."), "supportSize=",""))
    
    #Extrae los valores de laplace de cada regla
    laplace_compra <-as.numeric(str_replace_all(str_extract(regla_compra, "laplace=\\d{1,2}\\.\\d{1,}"),"laplace=",""))
    
    #Actualiza log
    df_log$puntaje_regla[indices_compra[i]] <- lista[[regla_compra]] + soporte_compra + laplace_compra
    
    #Para la regla de venta sólo se actuliza si no fue venta por fin de periodo
    if(!str_detect(regla_venta, "No aplica")){
      lista[[regla_venta]] <- lista[[regla_venta]] + ganancia
      
      #obtiene soporte y laplace de la regla de venta
      soporte_venta <- as.numeric(str_replace_all(str_extract(regla_venta, "supportSize=."), "supportSize=",""))
      laplace_venta <-as.numeric(str_replace_all(str_extract(regla_venta, "laplace=\\d{1,2}\\.\\d{1,}"),"laplace=",""))
      
      #Actualiza log
      df_log$puntaje_regla[indices_venta[i]] <- lista[[regla_venta]] + soporte_venta + laplace_venta
      
      #Agrega a la memoria 
      memoria <- c(memoria, regla_venta)
    }
    else{
      df_log$puntaje_regla[indices_venta[i]] <- 0
    }
  }
  
  #Penaliza las reglas que no se utilizaron
  if(is.null(registro_perdidas)){
    perdida_media <- 0
  }
  else{
    perdida_media <- mean(registro_perdidas)  
  }
  for(regla in reglas){
    if(!(regla %in% memoria)){
      lista[[regla]] <- lista[[regla]] + perdida_media  
    }
    
  }
  
  #guarda log
  write.csv(x = df_log, file = nombre_log, row.names = FALSE)
  return(lista)
}





















