##==============================================================================================
## Conjunto de funciones auxiliares
##==============================================================================================
library(dplyr)

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