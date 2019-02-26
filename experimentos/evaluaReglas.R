##==============================================================================================
## Funciones para evaluar las reglas del paquete Roughsets de forma arbitraria
##==============================================================================================
library(stringr)

##==============================================================================================
## VARIABLES GLOBALES
##==============================================================================================
ultimaOperacion <- "espera"
claseDefault <- 0

##==============================================================================================
## Función para evaluar un conjunto de reglas del paquete Roughsets
##
## ENTRADA
## reglas: vector con las reglas en forma de string
##
## atributos: Dataframe con los atributos del periodo
##
## eitquetado: Dataframe con los precios del periodo (proviene de los archivos etiquetados)
##
## SALIDA
## Dataframe etiquetado con la columna 'Clase' conteniendo la estrategia del periodo de acuerdo
## a las reglas
##==============================================================================================
evaluaReglas <- function(reglas, atributos, etiquetado){
  
  #número de observaciones
  n_obs <- dim(atributos)[1]
  
  #Obtiene la clase de cada observación
  for(i in 1:n_obs){
    observacion <- atributos[i,]
    
    #Clasifica las reglas de acuerdo a su tipo (cuidado con los espacios!)
    reglasCompra <- reglas[str_detect(reglas, "THEN  is 1;")]
    reglasVenta <- reglas[str_detect(reglas, "THEN  is -1;")]
    #PODRÍA ORDENAR LAS REGLAS DE ACUERDO A supportSize o laplace (ver str_extract)
    
    
  }
  
  
}