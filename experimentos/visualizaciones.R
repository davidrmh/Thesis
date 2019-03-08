##==============================================================================================
## Funciones para visualizar datos
##==============================================================================================
source("auxFun.R")

##==============================================================================================
## Función para combinar dataframe 
##
## ENTRADA
## ruta: Ruta del archivo que contiene la lista de los archivos a combinar
## (estos archivos deben de ser escritos en orden cronológico) (archivo combinaArchivos.csv)
##
## SALIDA
## un dataframe con la información de cada dataframe
## Este dataframe se puede utilizar con la función visualizaEstrategia (debe tener columnas Date y Clase)
##==============================================================================================
combinaDatos <- function(ruta){
  
  #aquí se almancena toda la información
  resultado <- data.frame()
  
  #vector con la ruta de cada archivo
  lista_archivos <- read.csv(ruta, stringsAsFactors = FALSE)
  
  #número de archivos
  n_arch <- dim(lista_archivos)[1]
  
  for(i in 1:n_arch){
    resultado <- rbind(resultado, read.csv(lista_archivos[i,] ))
  }

  return(resultado)
  
}


##==============================================================================================
## Función para visualizar una estrategia (SIN SEÑALES REPETIDAS)
##
## ENTRADA
## datos: Dataframe con al menos las columnas Date y Clase
##
## eje_y: String que representa el precio a utilizar como precio de ejecución
##
## step: Entero positivo que representa el número de periodos hacia el futuro
##
## bandaInf: Número negativo que representa la banda inferior (en porcentaje)
## SALIDA
## Gráfica de la estrategia. S
visualizaEstrategia <- function(datos, eje_y = "open", step = 0, bandaInf = - 3 / 100, comision = 0.25 / 100){
  
  #Número de observaciones
  n_obs <- nrow(datos)
  
  #Obtiene los momentos en los que se realiza una compra
  indicesCompra <- which(datos$Clase == 1) + step
  
  #Obtiene los momentos en los que se realiza una venta
  indicesVenta <- which(datos$Clase == -1) + step
  
  #Corrección de índices de venta
  if( any(indicesVenta > n_obs )){
    
    #Se limita al último periodo
    indicesVenta[which(indicesVenta > n_obs)] <- n_obs
  }
  
  #Corrección de índices de compra
  if( any(indicesCompra > n_obs)){
    
    #Se prohibe comprar al final del periodo
    datos$Clase[which(indicesCompra > n_obs)] <- 0
    indicesCompra <- which(datos$Clase == 1) + step
  }
  
  #Revisa las posiciones que quedan abiertas
  if(length(indicesCompra) > length(indicesVenta)){
    
    #Obtiene datos de la última compra
    ultimoIndiceCompra <- indicesCompra[length(indicesCompra)]
    fechaUltimaCompra <- datos$Date[ultimoIndiceCompra]
    ultimoPrecioCompra <- preciosEjecucion(datos, fechaUltimaCompra, tipo = eje_y)
    
    #Obtiene datos del último día en el episodio
    fechaUltimoDia <- datos$Date[length(datos$Date)]
    precioUltimoDia <- preciosEjecucion(datos, fechaUltimoDia, tipo = eje_y)
    
    #Analiza si se debe de vender o no
    #Se vende cuando:
    #1. La venta genera ganancias (sin importar la banda superior)
    #2. El precio de venta (considerando comisiones) cae debajo del umbral de riesgo (banda inferior)
    diferenciaPorcentual <- ( precioUltimoDia*(1 - comision) )/ ( (ultimoPrecioCompra)*(1 + comision) ) - 1
    
    if(diferenciaPorcentual > 0 || diferenciaPorcentual < bandaInf){
      #El último día se vende
      indicesVenta <- c(indicesVenta, n_obs)
    }
    
    else{
      #No si considera la compra que generó la posición abierta
      indiceRemover <- which(indicesCompra == ultimoIndiceCompra)
      indicesCompra[indiceRemover] <- 0
      
    }
  }
  
  
  #Calcula los precios de ejecución
  fechasCompra <- datos$Date[indicesCompra]
  preciosCompra <- preciosEjecucion(datos, fechasCompra, tipo = eje_y)
  fechasVenta <- datos$Date[indicesVenta]
  preciosVenta <- preciosEjecucion(datos, fechasVenta, tipo = eje_y)
  
  #Obtiene los precios a graficar
  precios<-preciosEjecucion(datos, datos$Date, tipo = eje_y)
  
  #Revisa si
  
  #Crea la gráfica
  ylab <- paste("Precio ejecución = ", eje_y, sep = "")
  xlab <- "Fecha"
  main <- paste("Estrategia ", datos$Date[1], " al ", datos$Date[n_obs], sep = "")
  subtitulo <- "Azul = compra, rojo = venta"
  
  plot(as.Date(datos$Date), precios, type = "l", xlab = xlab, ylab = ylab, main = main, sub = subtitulo)
  points(as.Date(datos$Date[indicesCompra]), preciosCompra, pch = 16, cex = 1.5, col = "blue")
  points(as.Date(datos$Date[indicesVenta]), preciosVenta, pch = 16, cex = 1.5, col = "red")
  
}
