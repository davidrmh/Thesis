##==============================================================================================
## Funciones para evaluar las reglas del paquete Roughsets de forma arbitraria
##==============================================================================================
library(stringr)
if(!exists("AUX_FUN_R")){
  source("auxFun.R")  
}


##==============================================================================================
## VARIABLES GLOBALES
##==============================================================================================
glob_claseDefault <- 0
glob_bandaSuperior <- 0.02 #numero positivo
glob_bandaInferior <- -0.04 #número negativo
comision <- 0.25 / 100
glob_tabla_log <- data.frame() #Para el archivo log
glob_indice_tabla <- 0 #Esta variable lleva un control de que renglón de glob_tabla_log se está modificando

##==============================================================================================
## Función para evaluar un conjunto de selectores
## un selector tiene la forma "cociente.Adj.Close.num.2.den.1 is (1,1.01]"
##
## ENTRADA
## selectores: Lista que contiene un vector con los selectores
##
## observacion: Dataframe que representa una observación
##
## SALIDA
## TRUE si 'observacion' cumple la condición de cada selector, FALSE en otro caso
##==============================================================================================
evaluaSelectores <- function(selectores, observacion){
  
  #auxiliar número de selectores
  num_selectores <- length(selectores[[1]])
  
  #auxiliar contador de selectores que cubren 'observación'
  cont_exito <- 0
  
  for(selector in selectores[[1]]){
    
    #split auxiliar
    aux_split <- str_split(selector, " is ")
    
    #Obtiene el atributo
    atributo <- aux_split[[1]][1]
    
    #Obtiene los valores del intervalo
    intervalo <- aux_split[[1]][2]
    aux_intervalo <- str_split(intervalo, ",")
    limInf <- aux_intervalo[[1]][1]
    limSup <- aux_intervalo[[1]][2]
    
    #quita (, ), [, ]
    limSup <- str_replace_all(limSup, "\\]","")
    limSup <- str_replace_all(limSup, "\\)","")
    limInf <- str_replace_all(limInf, "\\(","")
    limInf <- str_replace_all(limInf, "\\[","")
    
    #Convierte a número
    limSup <- as.numeric(limSup)
    limInf <- as.numeric(limInf)
    
    #evalua de acuerdo al tipo de intervalo
    
    #(,]
    if(str_detect(aux_intervalo[[1]][1], "\\(") && str_detect(aux_intervalo[[1]][2], "\\]")){
      
      ifelse((limInf < observacion[,atributo]) && (observacion[,atributo] <= limSup), 
             cont_exito <- cont_exito + 1, cont_exito <- 0)
    }
    
    #(,)
    else if(str_detect(aux_intervalo[[1]][1], "\\(") && str_detect(aux_intervalo[[1]][2], "\\)")){
      
      ifelse((limInf < observacion[,atributo]) && (observacion[,atributo] < limSup), 
             cont_exito <- cont_exito + 1, cont_exito <- 0)
    }
    
    #[,)
    else if(str_detect(aux_intervalo[[1]][1], "\\[") && str_detect(aux_intervalo[[1]][2], "\\)")){
      
      ifelse((limInf <= observacion[,atributo]) && (observacion[,atributo] < limSup), 
             cont_exito <- cont_exito + 1, cont_exito <- 0)
    }
    
    #[,]
    else if(str_detect(aux_intervalo[[1]][1], "\\[") && str_detect(aux_intervalo[[1]][2], "\\]")){
      
      ifelse((limInf <= observacion[,atributo]) && (observacion[,atributo] <= limSup), 
             cont_exito <- cont_exito + 1, cont_exito <- 0)
    }
    
  }
  
  ifelse(cont_exito == num_selectores, return(TRUE), return(FALSE))
  
}

##==============================================================================================
## Función para obtener la decisión de un conjunto de reglas sobre una observación (atributos)
##
## ENTRADA
## reglas: Vector que contiene un conjunto de reglas (como strings)
## 
## observacion: Dataframe que representa una observación
##
## SALIDA
## String con la regla que aplica a la observación (FALSE si no aplica ninguna regla)
## HICE ESTA ABERRACIÓN CON EL FIN DEL PODER CREAR LA TABLA DE LOG :(
##==============================================================================================
obtenDecision <- function(reglas, observacion){
  
  for(regla in reglas){
    #Obtiene el antecedente
    antecedente <- str_split(regla, " THEN  is")[[1]][1]
    
    #Quita IF (no es necesario)
    antecedente <- str_replace_all(antecedente, "IF ", "")
    
    #Obtiene los selectores
    selectores <- str_split(antecedente, " and ")
    
    #Evalua cada selector
    if(evaluaSelectores(selectores, observacion)){

      return(regla)
    }
  }
  
  return(FALSE)
}

##==============================================================================================
## Función para ordenar un conjunto de reglas de acuerdo a supportSize + laplace
##
## ENTRADA
## reglas: vector de strings que representan reglas
##
## top_k: Entero positivo que representa el número de las k mejores reglas a extraer
## si top_k > |reglas| entonces top_k = |reglas|
##
## lista_gan: Lista que contiene la ganancia de cada regla
##
## SALIDA
## vector de strings con las reglas ordenadas de mayor a menor de acuerdo a supportSize + laplace
##==============================================================================================
ordenaReglas <- function(reglas, top_k = length(reglas), lista_gan = list()){
  
  #Extrae los valores de supportSize de cada regla
  supportSize <- as.numeric(str_replace_all(str_extract(reglas, "supportSize=."), "supportSize=",""))
  
  #Extrae los valores de laplace de cada regla
  laplace <-as.numeric(str_replace_all(str_extract(reglas, "laplace=\\d{1,2}\\.\\d{1,}"),"laplace=",""))
  
  suma <- supportSize + laplace
  
  #agrega la ganancia de cada regla
  for(i in 1:length(reglas)){
    regla <- reglas[i]
    #Efecto multiplicativo (la suma podría ser otra opción -ver función agregaReglas de auxFun.R-)
    suma[i] <- suma[i] + lista_gan[[regla]]
  }
  
  #Normaliza la suma
  suma <- suma / sum(suma)
  
  #Obtiene la permutación de los elementos ordenados de mayor a menor
  permutacion <- order(suma, decreasing = TRUE)
  
  #obtiene las top_k reglas
  if(top_k > length(reglas)){top_k = length(reglas)}
  reglas_ordenadas <- reglas[permutacion[1:top_k]]
  
  return(reglas_ordenadas)
}
##==============================================================================================
## Función para evaluar un conjunto de reglas del paquete Roughsets
##
## ENTRADA
## reglas: vector con las reglas en forma de string
##
## atributos: Dataframe con los atributos del periodo
##
## etiquetado: Dataframe con los precios del periodo (proviene de los archivos etiquetados)
##
## tipoEjec: String con el tipo de precio de ejecución (ver preciosEjecucion del módulo auxFun.R)
##
## h: Entero no negativo que representa el número de periodos hacia el futuro para calcular el precio de ejecución
##
## ruta_dest: String que representa la ruta destino del archivo log (dentro de esta ruta se debe de tener una carpeta con el nombre log)
##
## prefijo: String que representa el prefijo del archivo log ("2_naftrac-etiquetado_2013-07-01_2013-11-04_90")
##
## boolForzar: Booleano. TRUE => Se obliga a que la primera compra coincida con la primera compra de BH
##
## SALIDA
## Dataframe etiquetado con la columna 'Clase' conteniendo la estrategia del periodo de acuerdo
## a las reglas
##==============================================================================================
evaluaReglas <- function(reglas, atributos, etiquetado, tipoEjec = 'open', h = 0, ruta_dest = './ruta/', prefijo = 'pref', boolForzar = FALSE){
  
  #número de observaciones
  n_obs <- dim(atributos)[1]
  
  #para almacenar las decisiones
  clases <- rep(glob_claseDefault, n_obs)
  
  #Clasifica las reglas de acuerdo a su tipo (cuidado con los espacios!)
  reglasCompra <- reglas[str_detect(reglas, "THEN  is 1;")]
  reglasVenta <- reglas[str_detect(reglas, "THEN  is -1;")]
  #PODRÍA ORDENAR LAS REGLAS DE ACUERDO A supportSize o laplace (ver str_extract)
  
  #Variables auxiliares
  ultimaOperacion <- "espera"
  ultimoPrecioCompra <- 0
  
  #Convierte tibbles as data.frames
  atributos <- as.data.frame(atributos)
  etiquetado <- as.data.frame(etiquetado)
  
  #Dataframe que contendrá el log
  #El precio de ejecución del dataframe ya considerará comisiones 
  x<-rep("espera", n_obs)
  #glob_tabla_log <- data.frame(fechaSen = "", fechaEjec = "", precioEjec = 0, regla = "", accion = x)
  glob_tabla_log <- data.frame(fechaSen = as.character(atributos$Date))
  
  #Nombre del archivo log
  nombre_log <- str_c(ruta_dest, "/log/", prefijo, "_log.csv")
  
  #Obtiene la clase de cada observación
  for(i in 1:(n_obs -1)){
    
    observacion <- atributos[i,]
    fechaSignal <- atributos[i, 'Date']
    indiceEjecucion <- which(atributos[, 'Date'] == fechaSignal) + h
    
    glob_indice_tabla <- i
    glob_tabla_log[glob_indice_tabla, 'fechaSen'] <- as.character(fechaSignal)
    
    #Para evitar out of bounds
    if(indiceEjecucion > n_obs){indiceEjecucion <- which(atributos[, 'Date'] == fechaSignal)}
    
    #Precio de ejecución sin considerar comisiones
    fechaEjecucion <- atributos[indiceEjecucion, 'Date']
    precioEjec <- preciosEjecucion(etiquetado, fechaEjecucion, tipoEjec)
    glob_tabla_log[glob_indice_tabla, 'fechaEjec'] <- as.character(fechaEjecucion)
  
    #Se examinan las reglas de compra cuando la última operación obtenida no fue de compra
    if(ultimaOperacion != "compra"){
      
      decision <- obtenDecision(reglasCompra, observacion)
      
      if(is.character(decision) || (boolForzar && i == 1)){
        clases[i] <- 1
        ultimaOperacion <- "compra"
        ultimoPrecioCompra <- precioEjec
        indiceUltimaCompra <- i
        
        #Actualiza tabla del log
        glob_tabla_log[glob_indice_tabla, 'accion'] <- 'Compra'
        glob_tabla_log[glob_indice_tabla, 'precioEjec'] <- precioEjec * (1 + comision)
        glob_tabla_log[glob_indice_tabla, 'regla'] <- decision
      }
    }
    
    #Venta
    else{
      decision <- obtenDecision(reglasVenta, observacion)
      
      #INFORMACIÓN CONTEXTUAL (BANDAS HORIZONTALES CONSIDERANDO COMISIÓN)
      
      ########################################### IMPORTANTE ###########################################################
      ## La señal de venta de acuerdo a las reglas, utiliza información del tiempo t
      ## La señal de venta de acuerdo a las bandas, utiliza el precio de ejecución en t + h (futuro)
      ## Una señal de venta se interpreta entonces como:
      ## 1. En el día t, las reglas me dicen que venta
      ## 2. En el transcurso del día t + h, espero que el precio de ejecución rebase las bandas horizontales
      ## si este es el caso, la venta se ejectua. (Esto se interpreta como una confirmación de la señal de las reglas)
      ##################################################################################################################
      diferencia_porcentual <- ( precioEjec * (1 - comision) ) / ( (ultimoPrecioCompra * (1 + comision) ) ) - 1
      
      if(is.character(decision) && ((diferencia_porcentual > glob_bandaSuperior) 
                      || (diferencia_porcentual < glob_bandaInferior)) ){
        clases[i] <- -1
        ultimaOperacion <- "venta"
        
        #Actualiza tabla del log
        glob_tabla_log[glob_indice_tabla, 'precioEjec'] <- precioEjec * (1 - comision)
        glob_tabla_log[glob_indice_tabla, 'regla'] <- decision
        
        if(diferencia_porcentual > glob_bandaSuperior){
          glob_tabla_log[glob_indice_tabla, 'accion'] <- 'Venta por banda superior'
        }
        else if(diferencia_porcentual < glob_bandaInferior){
          glob_tabla_log[glob_indice_tabla, 'accion'] <- 'Venta por banda inferior'
        }
        
      }
    }
  }
  
  #Agrega a la columna 'Clase' de 'etiquetado'
  etiquetado$Clase <- clases
  
  #Cierra posiciones abiertas
  if(ultimaOperacion == 'compra'){
    
    observacion <- atributos[n_obs,]
    fechaSignal <- atributos[n_obs, 'Date']
    indiceEjecucion <- which(atributos[, 'Date'] == fechaSignal)
    
    glob_indice_tabla <- n_obs
    glob_tabla_log[glob_indice_tabla, 'fechaSen'] <- as.character(fechaSignal)
    
    #Precio de ejecución sin considerar comisiones
    fechaEjecucion <- atributos[indiceEjecucion, 'Date']
    precioEjec <- preciosEjecucion(etiquetado, fechaEjecucion, tipoEjec)
    glob_tabla_log[glob_indice_tabla, 'fechaEjec'] <- as.character(fechaEjecucion)
    
    #diferencia porcentual
    diferencia_porcentual <- ( precioEjec * (1 - comision) ) / ( (ultimoPrecioCompra * (1 + comision) ) ) - 1
    
    #Se vende si hay una ganancia (la que sea) o se cae debajo de la banda inferior (pánico)
    if(diferencia_porcentual > 0 || diferencia_porcentual < glob_bandaInferior){
      
      glob_tabla_log[glob_indice_tabla, 'precioEjec'] <- precioEjec * (1 - comision)
      glob_tabla_log[glob_indice_tabla, 'regla'] <- "No aplica"
      glob_tabla_log[glob_indice_tabla, 'accion'] <- "Venta fin periodo"
      etiquetado$Clase[n_obs] <- -1
      
    }
    
    else{
      #La última compra no se considera
      glob_tabla_log[indiceUltimaCompra, 'accion'] <- "espera"
      etiquetado$Clase[indiceUltimaCompra] <- 0
    }
  }
  
  #filtra la tabla de log y la guarda
  glob_tabla_log <- subset(glob_tabla_log, accion != "espera")
  write.csv(glob_tabla_log, file = nombre_log, row.names = FALSE)
  
  return(etiquetado)
  
}
