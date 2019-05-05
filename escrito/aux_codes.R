##==========================================================================================================
## GRÁFICA DE UN ETIQUETADO
## boolLegend es un boolean. TRUE=>Se dibuja leyenda de forma manual.
##==========================================================================================================

#getwd() = carpeta experimentos
datos <- read.csv("../datasets/etiquetado-sin-rep-mid-h-1-90-sp500/14_sp500_2012-08-22_2013-01-02_90.csv")

#precio mid
datos$Mid <- (datos$High + datos$Low) / 2

#Convierte string de fechas a Date object
datos$Date <- as.Date(datos$Date)

graficaEtiquetado <- function(datos, boolLegend = TRUE){

  #índices de compra y venta
  #NOTA: LOS ÍNDICES SE REFIEREN A LOS ÍNDICES EN LOS QUE SE EJECUTA LA ACCIÓN
  #NO SON LOS ÍNDICES EN LOS QUE SE RECIBE LA SEÑAL
  n_obs <- nrow(datos)
  indices_compra <- which(datos$Clase == 1) + 1
  indices_venta <- which(datos$Clase == -1) + 1
  indices_compra[indices_compra > n_obs] <- n_obs
  indices_venta[indices_venta > n_obs] <- n_obs
  #Remueve las ventas y compras que ocurren el último día del periodo
  if(any(indices_compra == indices_venta)){
    n_compras <- length(indices_compra)
    n_ventas <- length(indices_venta)
    indices_compra <- indices_compra[1:(n_compras - 1)]
    indices_venta <- indices_venta[1:(n_ventas - 1)]
  }
  
  #gráfica de la estrategia
  # Guardar en JPEG tamaño 800 x 676
  main <- paste("Etiquetado para el periodo ", datos$Date[1], " / ", datos$Date[n_obs], sep = "")
  
  if(boolLegend){
    plot(datos$Date, datos$Mid, type = "l", lwd = 2.3, xlab = "Fecha", ylab = "Precio de ejecución", main = main)
    points(x = datos$Date[indices_compra], y = datos$Mid[indices_compra], cex = 2, pch = 24, bg = "blue")
    points(x = datos$Date[indices_venta], y = datos$Mid[indices_venta], cex = 2, pch = 25, bg = "red")
    grid(lwd=.8, col = "lightgray", lty = "dotted")
    legend(locator(1), legend = c("Compra", "Venta"), pch = c(24, 25), bty = "n", cex = 1.5, y.intersp = 0.6, pt.bg = c("blue", "red"))  
  }
  else{
    sub <- "Azul = Compra, Rojo = Venta"
    plot(datos$Date, datos$Mid, type = "l", lwd = 2.0, xlab = "Fecha", ylab = "Precio de ejecución", main = main, sub = sub)
    points(x = datos$Date[indices_compra], y = datos$Mid[indices_compra], cex = 2, pch = 16, col="blue")
    points(x = datos$Date[indices_venta], y = datos$Mid[indices_venta], cex = 2, pch = 16, col = "red")
    grid(lwd=1, col = "lightgray", lty = "dotted")
  }
  
  
}


##==========================================================================================================
## GRÁFICA DE BANDAS HORIZONTALES
## indice: Entero que representa el índice de la observación de compra
##==========================================================================================================
# Guardar en JPEG tamaño 800 x 676
graficaBandas <- function(datos, banda_superior = 0.035, banda_inferior = -0.03, indice = 2){
  #índices de compra y venta
  #NOTA: LOS ÍNDICES SE REFIEREN A LOS ÍNDICES EN LOS QUE SE EJECUTA LA ACCIÓN
  #NO SON LOS ÍNDICES EN LOS QUE SE RECIBE LA SEÑAL
  n_obs <- nrow(datos)
  indices_compra <- which(datos$Clase == 1) + 1
  indices_venta <- which(datos$Clase == -1) + 1
  indices_compra[indices_compra > n_obs] <- n_obs
  indices_venta[indices_venta > n_obs] <- n_obs
  #Remueve las ventas y compras que ocurren el último día del periodo
  if(any(indices_compra == indices_venta)){
    n_compras <- length(indices_compra)
    n_ventas <- length(indices_venta)
    indices_compra <- indices_compra[1:(n_compras - 1)]
    indices_venta <- indices_venta[1:(n_ventas - 1)]
  }
  
  #precio mid
  datos$Mid <- (datos$High + datos$Low) / 2
  
  #Convierte string de fechas a Date object
  datos$Date <- as.Date(datos$Date)
  
  plot(datos$Date, datos$Mid, type = "l", lwd = 2, xlab = "Fecha", ylab = "Precio de ejecución", main = "Límites de venta")
  points(x = datos$Date[indices_compra[indice]], y = datos$Mid[indices_compra[indice]], cex = 2, pch = 17)
  abline(h = datos$Mid[indices_compra[indice]]*(1 + banda_superior), lty = 6, lwd = 1.5)
  abline(h = datos$Mid[indices_compra[indice]]*(1 + banda_inferior), lty = 6, lwd = 1.5)
  grid(lwd=1, col = "lightgray", lty = "dotted")
  legend(locator(1), legend = c("Compra"), pch = c(17), bty = "n", cex = 1.5, y.intersp = 0.6)
  
}

##==========================================================================================================
## Grafica todas las estrategias en una carpeta
## el nombre de los archivos debe de contener el texto _predicciones
##==========================================================================================================
graficaEstrategiasFolder <- function(ruta = "../experimentos/AQ/AQ_exp_1_dicc1_mid_penaliza_sp500"){
  
  archivos <- dir(path = ruta, pattern = "_predicciones", full.names = TRUE)
  
  for(arch in archivos){
    datos <- read.csv(arch)
    graficaEtiquetado(datos, FALSE)
  }
  
}






