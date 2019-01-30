library(RoughSets)
##==============================================================================================
## ESTE MÓDULO CONTIENE FUNCIONES AUXILIARES PARA LA LIBRERÍA RoughSets
##==============================================================================================

##==============================================================================================
## Función para convertir un tibble/data.frame a un objeto de la clase 'DecisionTable'
##
## ENTRADA
## entrena: tibble con el conjunto de entrenamiento, se obtiene de la lista
## l[['entrenamiento']][[idx]] creada con la función listaDatos del módulo obtenConjuntos
##
## SALIDA
## Objeto de la clase 'DecisionTable'
##==============================================================================================
convierteDT <- function(entrena){
  #Omite la columna 'Date'
  indexDate <- which(names(entrena) == 'Date')
  entrena <- entrena[,c(-indexDate)]
  
  #Convierte en objeto de la clase 'DecisionTable'
  indexClase <- which(names(entrena) == 'Clase')
  entrenaDT <- SF.asDecisionTable(entrena, indexClase)
  
}


##==============================================================================================
## Función para discretizar un objeto de la clase 'DecisionTable'
##
## ENTRADA
##
## entrenaDT: DecisionTable la cual se utilizar para obtener las discretizaciones
## (idealmente el conjunto de entrenamiento)
##
## salidaDT: DecisionTable la cual se busca discretizar
## (si se buscan las predicciones de una regla es el conjunto de prueba ya convertido a DecisionTable)
## (si se busca ajustar un modelo es igual a entrenaDT)
##
## metodo: String que indica el método de discretización
## ("global.discernibility", "local.discernibility", "unsupervised.intervals", "unsupervised.quantiles")
##
## param: Lista de la forma param[[key]] en donde key es un string que corresponde al nombre de un parámetro
## relativo al método de discretización, por ejemplo param[['nOfIntervals']] para "unsupervised.intervals"
##
## SALIDA
## Un objeto de la clase 'Discretization'
##==============================================================================================
discretiza <- function(entrenaDT, salidaDT, metodo, param){
  
  if(metodo %in% c("unsupervised.intervals", "unsupervised.quantiles")) {
    numInter <- param[['nOfIntervals']]
    cutValues <- D.discretization.RST(entrenaDT, type.method = metodo, nOfIntervals = numInter)
    salidaDT <- SF.applyDecTable(entrenaDT, cutValues)
    return(salidaDT)
  }
  
  #PENDIENTE LOS OTROS DOS MÉTODOS
  
}