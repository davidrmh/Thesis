
###============================================================
### Función para graficar una estrategia
###============================================================
grafica_estrategia <- function(filename){
  # ENTRADA
  # filename: Ruta del archivo csv (creado con python, debe de tener una Columna Clase)
  
  # SALIDA
  # gráfica
  
  datos <- read.csv(filename)
  plot(datos$Adj.Close, type = "l", main = "Rojo = Venta \n Azul = Compra \n (Momentos de ejecución)", lwd = 2)
  indices_buy <- which(datos$Clase == 1)
  indices_sell <- which(datos$Clase == -1)
  points(x = indices_buy + 1, datos$Adj.Close[indices_buy + 1], col = "blue", pch = 25, cex = 1.5, lwd = 2)
  points(x = indices_sell + 1, datos$Adj.Close[indices_sell + 1], col = "red", pch = 25, cex = 1.5, lwd = 2)
  points(x = length(datos$Adj.Close), y = datos$Adj.Close[length(datos$Adj.Close)], col = "red", pch = 16, cex = 1.5)
  
}

###============================================================
### Función para graficar segmentos de recta
### Esta función se creó para el etiquetado MANUAL
###============================================================
segmentos_recta <- function(filename){
 # ENTRADA
 # filename: Ruta del archivo csv (creado con python, debe de tener una Columna Clase)
  
 # SALIDA
 # gráfica
  
  #lee los datos
  datos <- read.csv(filename)
  
  #obtiene los índices de compra
  ind_compra <- which(datos$Clase == 1)
  
  #obtiene los índices de venta
  ind_venta <- which(datos$Clase == -1)
  
  #Número de índices
  n <- length(ind_compra)
  
  #grafica la estrategia
  grafica_estrategia(filename)
  
  #añade segmentos de recta
  for(i in 1:n){
    
    compra = datos['Adj.Close'][ind_compra[i] + 1 ,1]
    venta = datos['Adj.Close'][ind_venta[i] + 1,1]
    
    segments(x0 = ind_compra[i] + 1 , y0 = compra, x1 = ind_venta[i] + 1 , y1 = venta, lwd = 4, col = "darkgreen")
    
    if(i > 1){
      compra = datos['Adj.Close'][ind_compra[i] + 1 ,1]
      venta = datos['Adj.Close'][ind_venta[i-1] + 1,1]
      segments(x0 = ind_compra[i] + 1 , y0 = compra, x1 = ind_venta[i-1] + 1 , y1 = venta, lwd = 4, col = "darkgreen")
    }
    
  }
}