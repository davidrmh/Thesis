library(stringr)
library(tibble)
##==============================================================================================
## Función para guardar los conjuntos de entrenamiento y de prueba
##
## ENTRADA
## arch_csv: String con la ruta del CSV que contiene el nombre de los archivos con cada conjunto
##
## ruta_entrena: String con la ruta de la carpeta que contiene los conjuntos de entrenamiento
##
## ruta_prueba: String con la ruta de la carpeta que contiene los conjuntos de prueba
##
## ruta_etiqueta: String con la ruta de la carpeta que contiene los conjuntos etiquetados (sin atributos)
##
## SALIDA
## una lista anidada con tres listas l[['entrenamiento']][[idx]], l[['prueba']][[idx]] y l[['etiquetado']][[idx]]
## las cuales contienen los conjuntos de entrenamiento, prueba y etiquetado respectivamente (tibbles)
##==============================================================================================
listaDatos <- function(arch_csv = "./entrena_prueba.csv", ruta_entrena = "../datasets/atributos_clases_dicc-1/", 
                       ruta_prueba = "../datasets/atributos_clases_dicc-1/", 
                       ruta_etiqueta = "../datasets/etiquetado/"){
  
  #Abre el archivo CSV que contiene en el nombre de cada archivo
  datos_csv <- read.csv(arch_csv, stringsAsFactors = FALSE)
  
  #número de archivos
  n_arch <- dim(datos_csv)[1]
  
  #lista que almacena las conjuntos
  lista <- list()
  lista[['entrenamiento']]  <- list()
  lista[['prueba']]  <- list()
  lista[['etiquetado']]  <- list()
  
  #Almacena las conjuntos
  for(i in 1:n_arch){
    
    #nombre del i-ésimo archivo de entrenamiento
    arch_entrena <- str_c(ruta_entrena, datos_csv[i,'entrena'])
    
    #nombre del i-ésimo archivo de prueba
    arch_prueba <- str_c(ruta_prueba, datos_csv[i,'prueba'])
    
    #nombre del i-esimo archivo etiquetado
    arch_etiq <- str_c(ruta_etiqueta, datos_csv[i,'etiquetado'])
    
    lista[['entrenamiento']][[i]] <- as.tibble(read.csv(arch_entrena))
    lista[['prueba']][[i]] <- as.tibble(read.csv(arch_prueba))
    lista[['etiquetado']][[i]] <- as.tibble(read.csv(arch_etiq))

  }
  
  lista
}

