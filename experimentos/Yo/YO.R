source('../obtenConjuntos.R')
source('../auxFun.R')
source('../evaluaReglas.R')
##==============================================================================================
## VARIABLES GLOBALES
##
## PARA EL MÓDULO 'obtenConjuntos.R'
arch_csv = "../entrena_prueba.csv"
ruta_entrena = "../../datasets/atributos_clases_dicc-1_rep/"
ruta_prueba = "../../datasets/atributos_clases_dicc-1_rep/" 
ruta_etiqueta = "../../datasets/etiquetado/"
# AJUSTAR VARIABLES  DEL MÓDULO evaluaReglas.R (función evaluaReglas)
glob_bandaSuperior <- 0.03 #numero positivo
glob_bandaInferior <- -0.04 #número negativo
glob_tipoEjec <- 'open'
glob_h <- 0
##==============================================================================================

##==============================================================================================
## Función para evaluar la estrategia de un conjunto de reglas en un archivo txt
##
## ENTRADA
## ruta_txt: String con la ruta del archivo txt que contiene las reglas
##
## ruta_dest: String con la ruta en donde se guardarán los resultados
##
## top_k: Entero no negativo que representa el número de las k mejores reglas a extraer
## si top_k > |reglas| o top_k = 0 entonces top_k = |reglas|.
##
## SALIDA
## crea archivos en ruta_dest
##==============================================================================================
YO.main <- function(ruta_txt = "reglas.txt", ruta_dest = "./yo_resultados/", top_k = 5){
  
  #Carga los conjuntos de entrenamiento, prueba y etiquetado
  conjuntos <- listaDatos(arch_csv, ruta_entrena, ruta_prueba, ruta_etiqueta)
  
  #número de archivos a evaluar
  n_archivos <- length(conjuntos[['prueba']])
  
  #Abre el archivo CSV que contiene en el nombre de cada archivo
  datos_csv <- read.csv(arch_csv, stringsAsFactors = FALSE)
  
  #Carga las reglas y las clasifica en compra o venta
  reglas <- readLines(ruta_txt)
  reglasCompra <- reglas[str_detect(reglas, "THEN  is 1;")]
  reglasVenta <- reglas[str_detect(reglas, "THEN  is -1;")]
  
  #Obtiene las top_k reglas
  if(top_k == 0 || top_k > length(reglasCompra)){
    reglasCompra <- ordenaReglas(reglasCompra, length(reglasCompra))
  }
  else{
    reglasCompra <- ordenaReglas(reglasCompra, top_k)
  }
  
  if(top_k == 0 || top_k > length(reglasVenta)){
    reglasVenta <- ordenaReglas(reglasVenta, length(reglasVenta))
  }
  else{
    reglasVenta <- ordenaReglas(reglasVenta, top_k)
  }
  reglas <- c(reglasCompra, reglasVenta)
  
  for(i in 1:n_archivos){
    
    #Crea tibble que contendrá las predicciones
    etiquetado <- conjuntos[['etiquetado']][[i]]
    
    #Obtiene el conjunto de prueba
    prueba <- conjuntos[['prueba']][[i]]
    
    #Realiza las predicciones
    etiquetado <- evaluaReglas(reglas, prueba, etiquetado, glob_tipoEjec, glob_h)
    
    #nombre del archivo de salida
    #aux1 tiene la forma "2_naftrac-etiquetado_2013-07-01_2013-11-04_90"
    aux1 <- str_split(datos_csv[i,'etiquetado'],'.csv')[[1]][1]
    nom_salida <- str_c(ruta_dest,aux1, '_predicciones.csv')
    
    #guarda archivo CSV
    write.csv(etiquetado, file = nom_salida, row.names = FALSE)
    
    #mensaje auxiliar
    print(paste("Se crea archivo ", nom_salida, sep = ""), quote = FALSE)
    
  }
  
  #Agrega archivo con los parámetros utilizados
  arch_param <- paste(ruta_dest, "parametros.txt", sep = "")
  write("", arch_param, append = FALSE)
  write(paste("Tipo de precio de ejecución = ", glob_tipoEjec, " h = ", glob_h, sep = ""), arch_param, append  = TRUE)
  write(paste("Banda superior = ", glob_bandaSuperior), arch_param, append = TRUE)
  write(paste("Banda inferior = ", glob_bandaInferior), arch_param, append = TRUE)
  write(paste("top_k = ",  top_k, sep = ""), arch_param, append = TRUE)
  
  print("Predicciones guardadas")
  
}
