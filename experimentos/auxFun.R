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

