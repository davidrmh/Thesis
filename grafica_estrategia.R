
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

###============================================================
### Función para graficar los segmentos de manera progresiva
###============================================================
segmentos_recta_prog <- function(filename){
  # ENTRADA
  # filename: Ruta del archivo csv (debe tener columna Adj Close)
  
  # SALIDA
  # gráfica
  # Data.frame con los mismos datos del csv y una columna Clase
  
  #lee los datos
  datos <- read.csv(filename)
  
  #extrae los precios
  precios_cierre <- as.numeric(datos$Adj.Close)
  precios_apertura <- as.numeric(datos$Open)
  
  #número de observaciones
  n_obs <- length(precios)
  
  #grafica el primer punto
  plot(1,precios_apertura[1], xlim = c(1, n_obs), ylim = c(min(precios_apertura), max(precios_apertura)) , cex = 0, ylab = "precio", xlab = "día")
  title(sub = "Negro = Precio Cierre, Verde = Precio Apertura")
  
  #para almacenar las decisiones
  vec_clase <- c(0)
  
  #ganancia acumulada
  ganancia_acum <- 0
  
  
  for(t in 2:n_obs){
    
    y1_cierre <- precios_cierre[t-1]
    y2_cierre <- precios_cierre[t]
    y1_apertura <- precios_apertura[t-1]
    y2_apertura <- precios_apertura[t]
    segments(t-1, y1_cierre, t, y2_cierre, lwd = 2.5, col = "black")
    segments(t-1, y1_apertura, t, y2_apertura, lwd = 2.5, col = "darkgreen")
    
    clase <- readline("Que decisión tomas (1 = Compra, -1 = Venta) \n")
    
    if(clase == 1){
      #Se dibuja el punto en el momento de ejecución
      #Como son precios de apertura, se considera el mismo día
      points(x = t + 1, y = precios_apertura[t], col = "blue", pch = 25, cex = 1.5, lwd = 2)
      
      #Precio de ejecución es el promedio high y low del mismo día
      ultimo_precio_compra <- mean(datos$High[t], datos$Low[t])
    }
    
    if(clase == -1){
      #Se dibuja el punto en el momento de ejecución
      points(x = t + 1, y = precios_apertura[t], col = "red", pch = 25, cex = 1.5, lwd = 2)
      precio_venta <- mean(datos$High[t], datos$Low[t])
      par(col.main="white")
      title(paste("Ganancia acumulada ($) = ", round(ganancia_acum, 2), sep = ""))
      ganancia_acum <- ganancia_acum + precio_venta - ultimo_precio_compra
      par(col.main="black")
      title(paste("Ganancia acumulada ($) = ", round(ganancia_acum, 2), sep = ""))
    }
    
    if(clase == ""){
      clase <- 0
    }
    
    vec_clase <- c(vec_clase, clase)
    
  }
  
  datos$Clase = vec_clase
  
  return(datos)
  
}