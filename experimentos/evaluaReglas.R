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
## Booleano. TRUE si la observación cumple el antecedente de alguna regla en reglas. FALSE en otro caso.
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
    if(evaluaSelectores(selectores, observacion)){return(TRUE)}
  }
  
  return(FALSE)
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
## SALIDA
## Dataframe etiquetado con la columna 'Clase' conteniendo la estrategia del periodo de acuerdo
## a las reglas
##==============================================================================================
evaluaReglas <- function(reglas, atributos, etiquetado, tipoEjec = 'open', h = 0){
  
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
  
  #Obtiene la clase de cada observación
  for(i in 1:n_obs){
    
    observacion <- atributos[i,]
    fechaSignal <- atributos[i, 'Date']
    indiceEjecucion <- which(atributos[, 'Date'] == fechaSignal) + h
    fechaEjecucion <- atributos[indiceEjecucion, 'Date']
    precioEjec <- preciosEjecucion(etiquetado, fechaEjecucion, tipoEjec)
  
    #Se examinan las reglas de compra cuando la última operación obtenida no fue de compra
    if(ultimaOperacion != "compra"){
      decision <- obtenDecision(reglasCompra, observacion)
      if(decision){
        clases[i] <- 1
        ultimaOperacion <- "compra"
        ultimoPrecioCompra <- precioEjec
      }
    }
    
    else{
      decision <- obtenDecision(reglasVenta, observacion)
      
      #INFORMACIÓN CONTEXTUAL (BANDAS HORIZONTALES)
      diferencia_porcentual <- precioEjec / ultimoPrecioCompra - 1
      if(decision && ((diferencia_porcentual > glob_bandaSuperior) 
                      || (diferencia_porcentual < glob_bandaInferior)) ){
        clases[i] <- -1
        ultimaOperacion <- "venta"
      }
    }
  }
  
  #Agrega a la columna 'Clase' de 'etiquetado'
  etiquetado$Clase <- clases
  
  return(etiquetado)
  
}