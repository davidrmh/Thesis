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
## SALIDA
## una lista anidada con dos listas l[['entrenamiento']][[idx]] y l[['prueba']][[idx]]
## las cuales contienen los conjuntos de entrenamiento y prueba respectivamente (tibbles)
##==============================================================================================
listaDatos <- function(arch_csv = "./entrena_prueba.csv", ruta_entrena = "../datasets/atributos_clases_dicc-1/", ruta_prueba = "../datasets/atributos_clases_dicc-1/"){
  
  #Abre el archivo CSV que contiene en el nombre de cada archivo
  datos_csv <- read.csv(arch_csv, stringsAsFactors = FALSE)
  
  #número de archivos
  n_arch <- dim(datos_csv)[1]
  
  #lista que almacena las conjuntos
  lista <- list()
  lista[['entrenamiento']]  <- list()
  lista[['prueba']]  <- list()
  
  #Almacena las conjuntos
  for(i in 1:n_arch){
    
    #nombre del i-ésimo archivo de entrenamiento
    arch_entrena <- str_c(ruta_entrena, datos_csv[i,'entrena'])
    
    #nombre del i-ésimo archivo de prueba
    arch_prueba <- str_c(ruta_entrena, datos_csv[i,'entrena'])
    
    lista[['entrenamiento']][[i]] <- as.tibble(read.csv(arch_entrena))
    lista[['prueba']][[i]] <- as.tibble(read.csv(arch_prueba))

  }
  
  lista
}

