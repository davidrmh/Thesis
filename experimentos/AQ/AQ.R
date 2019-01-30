source('../auxRoughSets.R')
source('../obtenConjuntos.R')
##==============================================================================================
## Función para obtener un conjunto de reglas a partir de un conjunto de entrenamiento
##
## ENTRADA
## entrena: tibble con el conjunto de entrenamiento, se obtiene de la lista
## l[['entrenamiento']][[idx]] creada con la función listaDatos del módulo obtenConjuntos
##
## confidence: Valor numérico que representa la confianza mínima de las reglas calculadas
##
## timesCovered:  Entero positivo. Representa el número mínimo de reglas que deben de cubrir cada ejemplo
##
## metodoDisc: String que representa el método de discretización 
## ("unsupervised.intervals", "unsupervised.quantiles")
##
## param: Lista de la forma param[[key]] en donde key es un string que corresponde al nombre de un parámetro
## relativo al método de discretización, por ejemplo param[['nOfIntervals']] para "unsupervised.intervals"
##
## SALIDA
## Objeto de la clase "RuleSetRST"
##==============================================================================================
AQ.fit <- function(entrena, confidence = 0.9, timesCovered = 1, metodoDisc = "unsupervised.intervals",
                   param = list(nOfIntervals = 4)){
  
  #Convierte en objeto de la clase 'DecisionTable'
  entrenaDT <- convierteDT(entrena)
  
  #Discretiza atributos
  entrenaDT <- discretiza(entrenaDT, entrenaDT, metodoDisc, param)
  
  #Obtiene las reglas
  reglas <- RI.AQRules.RST(entrenaDT, confidence, timesCovered)
  
  return(reglas)
  
}