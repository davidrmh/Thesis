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
    salidaDT <- SF.applyDecTable(salidaDT, cutValues)
    return(salidaDT)
  }
  
  #PENDIENTE LOS OTROS DOS MÉTODOS
  
}


##==============================================================================================
## Función para realizar las predicciones para un conjunto de reglas
##
## ENTRADA
## reglas: Objeto de la clase "RuleSetRST"
##
## entrena: tibble con el conjunto de entrenamiento, se obtiene de la lista
## l[['entrenamiento']][[idx]] creada con la función listaDatos del módulo obtenConjuntos
##
## prueba: tibble con el conjunto de entrenamiento, se obtiene de la lista
## l[['prueba']][[idx]] creada con la función listaDatos del módulo obtenConjuntos
##
## metodoDisc: String que representa el método de discretización 
## ("global.discernibility", "local.discernibility", "unsupervised.intervals", "unsupervised.quantiles")
##
## param: Lista de la forma param[[key]] en donde key es un string que corresponde al nombre de un parámetro
## relativo al método de discretización, por ejemplo param[['nOfIntervals']] para "unsupervised.intervals"
##
## SALIDA
## vector numérico con las predicciones
##==============================================================================================
reglas.predice <- function(reglas, entrena, prueba, metodoDisc = "unsupervised.intervals",
                           param = list(nOfIntervals = 4)){
  
  predicciones <- predict(reglas, discretiza(convierteDT(entrena),convierteDT(prueba), metodoDisc, param))
  predicciones <- as.numeric(as.vector(predicciones$predictions))
  
  return(predicciones)
  
}









