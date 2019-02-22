##==============================================================================================
## Funciones para visualizar datos
##==============================================================================================
source("auxFun.R")

##==============================================================================================
## Función para visualizar una estrategia
##
## ENTRADA
## datos: Dataframe con al menos las columnas Date y Clase
##
## eje_y: String que representa el precio a utilizar como precio de ejecución
##
## step: Entero positivo que representa el número de periodos hacia el futuro
##
## SALIDA
## Gráfica de la estrategia. S
visualizaEstrategia <- function(datos, eje_y = "open", step = 1){
  
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
  
  #Calcula los precios de ejecución
  fechasCompra <- datos$Date[indicesCompra]
  preciosCompra <- preciosEjecucion(datos, fechasCompra, tipo = eje_y)
  fechasVenta <- datos$Date[indicesVenta]
  preciosVenta <- preciosEjecucion(datos, fechasVenta, tipo = eje_y)
  
  #Obtiene los precios a graficar
  precios<-preciosEjecucion(datos, datos$Date, tipo = eje_y)
  
  #Crea la gráfica
  ylab <- paste("Precio ejecución = ", eje_y, sep = "")
  xlab <- "Fecha"
  main <- paste("Estrategia ", datos$Date[1], " al ", datos$Date[n_obs], sep = "")
  subtitulo <- "Azul = compra, rojo = venta"
  
  plot(as.Date(datos$Date), precios, type = "l", xlab = xlab, ylab = ylab, main = main, sub = subtitulo)
  points(as.Date(datos$Date[indicesCompra]), preciosCompra, pch = 16, cex = 1.5, col = "blue")
  points(as.Date(datos$Date[indicesVenta]), preciosVenta, pch = 16, cex = 1.5, col = "red")
  
}
