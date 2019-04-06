source('../auxRoughSets.R')
source('../obtenConjuntos.R')
source('../auxFun.R')
source('../evaluaReglas.R')
##==============================================================================================
## VARIABLES GLOBALES
##
## PARA EL MÓDULO 'obtenConjuntos.R'
arch_csv = "../entrena_prueba.csv"
ruta_entrena = "../../datasets/atributos_clases_dicc-2/"
ruta_prueba = "../../datasets/atributos_clases_dicc-2/" 
ruta_etiqueta = "../../datasets/etiquetado/"
# AJUSTAR VARIABLES  DEL MÓDULO evaluaReglas.R (función evaluaReglas)
glob_bandaSuperior <- 0.035 #numero positivo
glob_bandaInferior <- -0.03 #número negativo
glob_tipoEjec <- 'mid'
glob_h <- 1
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
## acumReglas: Booleano TRUE => las reglas se acumulan.
##
## top_k: Entero no negativo que representa el número de las k mejores reglas a extraer
## si top_k > |reglas| o top_k = 0 entonces top_k = |reglas|. SÓLO UTILIZAR CUANDO acumReglas = TRUE
##
## boolForzar: Booleano. TRUE => Se obliga a que la primera compra coincida con la primera compra de BH
##
## boolPenaliza: Booleano. TRUE => Se penalizan las reglas que generaron pérdidas
## SALIDA
## Crea archivos en ruta_dest
##==============================================================================================
CN2.main <- function(ruta_dest = "./CN2_resultados_dicc2/", K = 5, 
                    metodoDisc = "unsupervised.intervals", param = list(nOfIntervals = 4),
                    ignoraEspera = FALSE, acumReglas = FALSE, top_k = 5, boolForzar = FALSE, boolPenaliza = FALSE){
  
  #Carga los conjuntos de entrenamiento, prueba y etiquetado
  conjuntos <- listaDatos(arch_csv, ruta_entrena, ruta_prueba, ruta_etiqueta)
  
  #número de modelos a ajustar
  n_modelos <- length(conjuntos[['entrenamiento']])
  
  #Abre el archivo CSV que contiene en el nombre de cada archivo
  datos_csv <- read.csv(arch_csv, stringsAsFactors = FALSE)
  
  #Para acumular las reglas (en forma de string)
  reglasAcum <- c()

  #Para registrar la ganancia de cada regla
  #(sólo se utiliza cuando se acumulan reglas)
  lista_ganancia_reglas <- list()
  
  #Ajusta modelos
  for(i in 1:n_modelos){
    
    #nombre del archivo de salida
    #aux1 tiene la forma "2_naftrac-etiquetado_2013-07-01_2013-11-04_90"
    aux1 <- str_split(datos_csv[i,'etiquetado'],'.csv')[[1]][1]
    nom_salida <- str_c(ruta_dest,aux1, '_predicciones.csv')
    nom_salida_reglas_acum <- str_c(ruta_dest, '/reglas/',aux1,'_reglas_acum.txt')
    
    #obtiene las reglas
    try({
      entrena <- conjuntos[['entrenamiento']][[i]]
      if(ignoraEspera){entrena <- quitaEspera(entrena)}
      reglas <- CN2.fit(entrena, K, metodoDisc, param)
      
      #Crea tibble que contendrá las predicciones
      etiquetado <- conjuntos[['etiquetado']][[i]]
      
      #Obtiene las predicciones para el conjunto de prueba
      prueba <- conjuntos[['prueba']][[i]]
      
      #Acumula reglas
      if(acumReglas){
        reglasAcum <- c(reglasAcum, as.character(reglas))
        
        #Elimina repetidas
        reglasAcum <- unique(reglasAcum)

        #Agrego a lista_ganancia_reglas
        lista_ganancia_reglas <- agregaReglas(reglasAcum, lista_ganancia_reglas)
        
        #Obtiene las top_k reglas de compra y venta
        reglasCompra <- reglasAcum[str_detect(reglasAcum, "THEN  is 1;")]
        reglasVenta <- reglasAcum[str_detect(reglasAcum, "THEN  is -1;")]
        
        #top_k reglas de compra
        if(top_k == 0 || top_k > length(reglasCompra)){
          reglasCompra <- ordenaReglas(reglasCompra, length(reglasCompra), lista_ganancia_reglas)
        }
        else{
          reglasCompra <- ordenaReglas(reglasCompra, top_k, lista_ganancia_reglas)
        }
        
        if(top_k == 0 || top_k > length(reglasVenta)){
          reglasVenta <- ordenaReglas(reglasVenta, length(reglasVenta), lista_ganancia_reglas)
        }
        else{
          reglasVenta <- ordenaReglas(reglasVenta, top_k, lista_ganancia_reglas)
        }
        
        #junta las top_k reglas de compra y venta
        reglasAcum <- c(reglasCompra, reglasVenta)

        #Guardar reglas acumuladas que aplicaron para este periodo (crear una carpeta reglas)
        write(x = as.character(reglasAcum), file = nom_salida_reglas_acum)
        
        #Realiza las predicciones
        etiquetado <- evaluaReglas(reglasAcum, prueba, etiquetado, glob_tipoEjec, glob_h, ruta_dest = ruta_dest, prefijo = aux1, boolForzar = boolForzar)
      }
      
      else{
        etiquetado <- evaluaReglas(as.character(reglas), prueba, etiquetado, glob_tipoEjec, glob_h, ruta_dest = ruta_dest, prefijo = aux1, boolForzar = boolForzar)
        #predicciones <- reglas.predice(reglas, entrena, prueba, metodoDisc, param)
        #etiquetado$Clase <- predicciones
      }

      if(boolPenaliza){
        #Actualiza la ganancia de cada regla
        nombre_log <- str_c(ruta_dest, "/log/", aux1, "_log.csv")
        lista_ganancia_reglas <- actualizaLista(nombre_log, lista_ganancia_reglas, reglasAcum) 
      }
      
      #guarda archivo CSV
      write.csv(etiquetado, file = nom_salida, row.names = FALSE)
      
      #guarda archivo TXT con las reglas
      
      #Nombre del archivo de salida para guardar las reglas
      nom_salida_reglas <- str_c(ruta_dest,'/reglas/',aux1, '_reglas.txt')
      write(x = as.character(reglas), file = nom_salida_reglas)
      
      #mensaje auxiliar
      print(paste("Se crea archivo ", nom_salida, sep = ""), quote = FALSE)
    })  
  }

  #Agrega archivo con los parámetros utilizados
  arch_param <- paste(ruta_dest, "parametros.txt", sep = "")
  write("", arch_param, append = FALSE)
  write(paste("K = ", K, sep = ""), arch_param, append = TRUE)
  
  #Por el momento sólo utilizaré dos métodos de discretización
  write(paste("Método discretización = ", metodoDisc, sep = ""), arch_param, append = TRUE)
  write(paste("Número intervalos = ", param[["nOfIntervals"]], sep = ""), arch_param, append = TRUE)
  
  write(paste("Ignora espera = ", ignoraEspera , sep = ""), arch_param, append = TRUE)
  write(paste("Tipo de precio de ejecución = ", glob_tipoEjec, " h = ", glob_h, sep = ""), arch_param, append  = TRUE)
  write(paste("Banda superior = ", glob_bandaSuperior), arch_param, append = TRUE)
  write(paste("Banda inferior = ", glob_bandaInferior), arch_param, append = TRUE)
  write(paste("Acumula reglas = ", acumReglas, sep = ""), arch_param, append = TRUE)
  write(paste("Forzar primera compra = ", boolForzar, sep = ""), arch_param, append = TRUE)
  
  if(acumReglas){
    write(reglasAcum, paste(ruta_dest,"reglas_acumuladas.txt", sep = ""))
    write(paste("top_k = ",  top_k, sep = ""), arch_param, append = TRUE)
  }
  
  print("Predicciones guardadas")
}
