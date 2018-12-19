###============================================================
## VARIABLES GLOBALES
###============================================================

#Costos de transacción
costo_trans <- .25/100

#Capital Inicial
capital_inicial <- 100000

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
### Función para graficar una estrategia
###============================================================
grafica_estrategia_2 <- function(datos, col.name){
  # ENTRADA
  # datos: Data frame con los datos etiquetados y los precios
  # col.name: String con el nombre de la columna que contiene las etiquetas
  
  # SALIDA
  # gráfica
  
  plot(datos$Adj.Close, type = "l", main = "Rojo = Venta \n Azul = Compra \n (Momentos de ejecución)", lwd = 2)
  indices_buy <- which(datos[col.name] == 1)
  indices_sell <- which(datos[col.name] == -1)
  points(x = indices_buy, datos$Adj.Close[indices_buy], col = "blue", pch = 25, cex = 1.5, lwd = 2)
  points(x = indices_sell, datos$Adj.Close[indices_sell], col = "red", pch = 25, cex = 1.5, lwd = 2)
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
### Función para seleccionar un periodo aleatorio
###============================================================
subconjunto <- function(filename, longitud = 252){
  # ENTRADA
  # filename: Ruta del archivo csv de Yahoo Finance
  # (sin NULL: i.e. se limpió on la función leeTabla del módulo indicadores.py)
  # longitud: longitud del periodo
  
  # Salida
  # Data frame con los datos correspondientes al periodo
  
  #lee los datos
  datos <- read.csv(filename)  
  
  #obtiene fechas
  fechas <- datos$Date
  
  #número de observaciones
  n_obs <- length(fechas)
  
  #obtiene una fecha inicial aleatoria
  fecha_inicial <- sample(fechas[1:(n_obs - longitud)], size = 1)
  
  #índice de la fecha inicial
  indice_fecha_inicial <- which(datos$Date == fecha_inicial)
  
  #subconjunto de datos
  sub_datos <- datos[indice_fecha_inicial:(indice_fecha_inicial + longitud - 1),]
  
  return(sub_datos)
  
}


###============================================================
### Función para graficar los segmentos de manera progresiva
###============================================================
segmentos_recta_prog <- function(datos){
  # ENTRADA
  # datos: Data frame con los precios (idealmente creado con la función subconjunto)
  
  # SALIDA
  # gráfica
  # Data.frame con los mismos datos del csv y una columna Clase
  
  
  #extrae los precios
  #precios_cierre <- as.numeric(datos$Close)
  precios_cierre <- as.numeric(datos$Adj.Close)
  precios_apertura <- as.numeric(datos$Open) 
  
  #número de observaciones
  n_obs <- length(precios_cierre)
  
  #grafica el primer punto
  y_min <- min(min(datos$Low), min(datos$Adj.Close), min(datos$Close), min(datos$High)) - 3
  y_max <- max(max(datos$Low), max(datos$Adj.Close), max(datos$Close), max(datos$High)) + 3
  plot(1,precios_apertura[1], xlim = c(1, n_obs), ylim = c(y_min, y_max) , cex = 0, ylab = "precio", xlab = "")
  title(sub = "Negro = Precio Cierre, Verde = Precio Apertura")
  
  #para almacenar las decisiones
  vec_clase <- c(0)
  
  #ganancia acumulada
  ganancia_acum <- 0
  
  #Acciones
  acciones <- 0
  
  #Capital
  capital <- capital_inicial
  
  #flag primera compra
  flag_primera_compra <- TRUE
  
  #segmentos horizontales en t-1
  segmento_horizontal_prev <- c()
  
  
  for(t in 2:n_obs){
    
  
    
    
    y1_apertura <- precios_apertura[t-1]
    y2_apertura <- precios_apertura[t]
    if(t >= 3){
      y1_cierre <- precios_cierre[t-1]
      y2_cierre <- precios_cierre[t-2]
      segments(t-1, y1_cierre, t-2, y2_cierre, lwd = 2.5, col = "black")
    }
    segments(t-1, y1_apertura, t, y2_apertura, lwd = 2.5, col = "darkgreen")
    
    #Actualiza xlab
    if(t > 2){
      par(col.lab = "white")
      title(xlab = paste("dia = ", t-1, sep = ""))
      
      par(col.lab = "black")
      title(xlab = paste("dia = ", t, sep = ""))
      
    }
    
    else{
      par(col.lab = "black")
      title(xlab = paste("dia = ", t, sep = ""))
      
    }
    
    clase <- readline("Que decisión tomas (1 = Compra, -1 = Venta) \n")
    
    
    #Compra
    if(clase == 1){
      
      #Precio de ejecución
      #precio_ejecucion <- mean(datos$High[t], datos$Low[t])
      precio_ejecucion <- datos$Open[t]
      
      #Acciones compradas
      acciones <- acciones + floor(capital / (precio_ejecucion*(1 + costo_trans)))
      
      #Se actualiza el capital
      capital_prev <- capital
      capital <- capital - precio_ejecucion*(1 + costo_trans) * acciones
      
      #Se dibuja el punto en el momento de ejecución
      #Como son precios de apertura, se considera el mismo día
      points(x = t, y = precio_ejecucion, col = "blue", pch = 20, cex = 1.5, lwd = 2)
      
      #Dibuja segmentos horizontales
      
      #Primero borra los anteriores
      abline(h = segmento_horizontal_prev, col = "white", lty = 2, lwd = 2)
      
      #obtiene los nuevos segmentos
      for(j in 1:2){
        segmento_horizontal <- locator(n = 1)
        segmento_horizontal_prev <- c(segmento_horizontal_prev, segmento_horizontal$y)
        abline(h = segmento_horizontal$y, col = "blue", lty = 2, lwd = 2)
      }
      
      #registra el precio de la primera compra
      if(flag_primera_compra){
        precio_primera_compra  <- precio_ejecucion
        acciones_primera_compra <- acciones
        flag_primera_compra <- FALSE
      }
      
    }
    
    #Venta
    if(clase == -1){
      
      #Precio de ejecución
      #precio_ejecucion <- mean(datos$High[t], datos$Low[t])
      precio_ejecucion <- datos$Open[t]
      
      #Actualiza capital
      capital <- capital + precio_ejecucion*(1 - costo_trans)*acciones
      
      #Actualiza acciones
      acciones <- 0
      
      #Actualiza ganancia acumulada
      ganancia_acum_prev <- ganancia_acum
      ganancia_acum <- ganancia_acum + (capital - capital_prev)
      
      #Registra el precio de la última venta
      precio_ultima_venta <- precio_ejecucion
      
      #Se dibuja el punto en el momento de ejecución
      points(x = t, y = precio_ejecucion, col = "red", pch = 20, cex = 1.5, lwd = 2)
      
      #Transparenta el título anterior
      par(col.main="white")
      title(paste("Ganancia acumulada ($) = ", round(ganancia_acum_prev, 2), sep = ""))
      
      #nuevo título
      par(col.main="black")
      title(paste("Ganancia acumulada ($) = ", round(ganancia_acum, 2), sep = ""))
    }
    
    if(clase == ""){
      clase <- 0
    }
    
    vec_clase <- c(vec_clase, clase)
    
  } #end for t
  
  #calcula B&H
  ganancia_buy_hold <- precio_ultima_venta*(1- costo_trans)*acciones_primera_compra - precio_primera_compra*(1 + costo_trans) * acciones_primera_compra
  
  #Transparenta el título anterior
  par(col.main="white")
  title(paste("Ganancia acumulada ($) = ", round(ganancia_acum_prev, 2), sep = ""))
  title(paste("Ganancia acumulada ($) = ", round(ganancia_acum, 2), sep = ""))
  
  par(col.main = "black")
  title(paste("Ganancia acumulada estrategia ($) = ", round(ganancia_acum, 2), "\n\n Ganancia acumulada Buy & Hold = ", round(ganancia_buy_hold,2), sep ="" ))
  
  datos$Clase = vec_clase
  
  return(datos)
  
}

###============================================================
### Función para calcular la ganancia de una estrategia (etiquetado)
###============================================================
calcula_ganancia<-function(datos, col.clase = "Clase.manual", cap_inicial = 100000){
  # ENTRADA
  # datos: Data frame con los precios (Open, High, Low, Close, Adj.Close)
  # col.clase: String con el nombre de la columna que contiene la estrategia (columna de -1,0,1)
  # cap_inicial: Número que representa el capital inicial
  #
  # SALIDA
  # ganancia porcentual de la estrategia
  
  #Número de observaciones
  n_obs <- dim(datos)[1]

  #ganancia acumulada
  ganancia_acum <- 0
  
  #Acciones
  acciones <- 0
  
  #Capital
  capital <- cap_inicial

  for(t in 1:n_obs){
    
    clase <- datos[col.clase][t,]
    
    #Compra
    if(clase == 1){
      
      #Precio de ejecución
      #precio_ejecucion <- mean(datos$High[t], datos$Low[t])
      precio_ejecucion <- datos$Open[t]
      
      #Acciones compradas
      
      if(capital <= 0){
        print("Perdiste todo el dinero")
        return(-1)
      }
      
      acciones <- acciones + floor(capital / (precio_ejecucion*(1 + costo_trans)))
      
      #Se actualiza el capital
      capital_prev <- capital
      capital <- capital - precio_ejecucion*(1 + costo_trans) * acciones
    }
    
    #Venta
    else if(clase == -1){
      
      #Precio de ejecución
      #precio_ejecucion <- mean(datos$High[t], datos$Low[t])
      precio_ejecucion <- datos$Open[t]
      
      #Actualiza capital
      capital <- capital + precio_ejecucion*(1 - costo_trans)*acciones
      
      #Actualiza acciones
      acciones <- 0
      
      #Actualiza ganancia acumulada
      ganancia_acum <- ganancia_acum + (capital - capital_prev)
      
    }
    
    
  }
  
  #Calcula el capital final
  capital_final <- cap_inicial + ganancia_acum
  
  #calcula ganancia porcentual
  ganancia_porcentual <- capital_final / cap_inicial - 1
  
  print(paste("La estrategia ", col.clase, " obtuvo un ", round(ganancia_porcentual,2), "% de rendimiento", sep = ""))
  return(ganancia_porcentual)
  
}