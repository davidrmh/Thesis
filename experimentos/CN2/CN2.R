source('../auxRoughSets.R')
source('../obtenConjuntos.R')
source('../auxFun.R')
##==============================================================================================
## VARIABLES GLOBALES
##
## PARA EL MÓDULO 'obtenConjuntos.R'
arch_csv = "../entrena_prueba.csv"
ruta_entrena = "../../datasets/atributos_clases_dicc-2/"
ruta_prueba = "../../datasets/atributos_clases_dicc-2/" 
ruta_etiqueta = "../../datasets/etiquetado/"
##==============================================================================================


##==============================================================================================
## Función para obtener un conjunto de reglas a partir de un conjunto de entrenamiento
##
## ENTRADA
## entrena: tibble con el conjunto de entrenamiento, se obtiene de la lista
## l[['entrenamiento']][[idx]] creada con la función listaDatos del módulo obtenConjuntos
##
## K: Entero que controla la complejidad del algoritmo. En cada iteración 'K' de los mejores predicados
## son extendidos para todos los descriptores posibles
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
CN2.fit <- function(entrena, K = 5, metodoDisc = "unsupervised.intervals",
                   param = list(nOfIntervals = 4)){
  
  #Convierte en objeto de la clase 'DecisionTable'
  entrenaDT <- convierteDT(entrena)
  
  #Discretiza atributos
  entrenaDT <- discretiza(entrenaDT, entrenaDT, metodoDisc, param)
  
  #Obtiene las reglas
  reglas <- RI.CN2Rules.RST(entrenaDT, K)
  
  return(reglas)
  
}


##==============================================================================================
## Función main: Ajusta un modelo para cada conjunto de entrenamiento, realiza las predicciones
## para el conjunto de prueba correspondiente y guarda un csv con las columnas Date, Precios y Clase
## con el fin de ser evaluado con distintas métricas
##
## ENTRADA
## ruta_dest: String con la ruta de la carpeta en donde se guardarán las predicciones para cada
## conjunto de prueba
##
## K: Entero que controla la complejidad del algoritmo. En cada iteración 'K' de los mejores predicados
## son extendidos para todos los descriptores posibles
##
## metodoDisc: String que representa el método de discretización 
##
## param: Lista de la forma param[[key]] en donde key es un string que corresponde al nombre de un parámetro
## relativo al método de discretización, por ejemplo param[['nOfIntervals']] para "unsupervised.intervals"
##
## ignoraEspera: Booleano. TRUE => se ignora la clase 'espera' (0)
##
## SALIDA
## Crea archivos en ruta_dest
##==============================================================================================
CN2.main <- function(ruta_dest = "./CN2_resultados_dicc2/", K = 5, 
                    metodoDisc = "unsupervised.intervals", param = list(nOfIntervals = 4), ignoraEspera = FALSE){
  
  #Carga los conjuntos de entrenamiento, prueba y etiquetado
  conjuntos <- listaDatos(arch_csv, ruta_entrena, ruta_prueba, ruta_etiqueta)
  
  #número de modelos a ajustar
  n_modelos <- length(conjuntos[['entrenamiento']])
  
  #Abre el archivo CSV que contiene en el nombre de cada archivo
  datos_csv <- read.csv(arch_csv, stringsAsFactors = FALSE)
  
  #Ajusta modelos
  for(i in 1:n_modelos){
    
    #obtiene las reglas
    try({
      entrena <- conjuntos[['entrenamiento']][[i]]
      if(ignoraEspera){entrena <- quitaEspera(entrena)}
      reglas <- CN2.fit(entrena, K, metodoDisc, param)
      
      #Obtiene las predicciones para el conjunto de prueba
      prueba <- conjuntos[['prueba']][[i]]
      predicciones <- reglas.predice(reglas, entrena, prueba, metodoDisc, param)
      
      #Crea tibble que contendrá las predicciones
      etiquetado <- conjuntos[['etiquetado']][[i]]
      etiquetado[,'Clase'] <- predicciones
      
      #nombre del archivo de salida
      #aux1 tiene la forma "2_naftrac-etiquetado_2013-07-01_2013-11-04_90"
      aux1 <- str_split(datos_csv[i,'etiquetado'],'.csv')[[1]][1]
      nom_salida <- str_c(ruta_dest,aux1, '_predicciones.csv')
      
      #guarda archivo CSV
      write.csv(etiquetado, file = nom_salida, row.names = FALSE)
      
      #guarda archivo TXT con las reglas
      
      #Nombre del archivo de salida para guardar las reglas
      nom_salida_reglas <- str_c(ruta_dest,aux1, '_reglas.txt')
      write(x = as.character(reglas), file = nom_salida_reglas)
      
      #mensaje auxiliar
      print(paste("Se crea archivo ", nom_salida, sep = ""), quote = FALSE)
    })  
  }
  print("Predicciones guardadas")
}
