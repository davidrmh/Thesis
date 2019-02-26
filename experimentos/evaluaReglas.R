##==============================================================================================
## Funciones para evaluar las reglas del paquete Roughsets de forma arbitraria
##==============================================================================================
library(stringr)

##==============================================================================================
## VARIABLES GLOBALES
##==============================================================================================
ultimaOperacion <- "espera"
claseDefault <- 0

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
## eitquetado: Dataframe con los precios del periodo (proviene de los archivos etiquetados)
##
## SALIDA
## Dataframe etiquetado con la columna 'Clase' conteniendo la estrategia del periodo de acuerdo
## a las reglas
##==============================================================================================
evaluaReglas <- function(reglas, atributos, etiquetado){
  
  #número de observaciones
  n_obs <- dim(atributos)[1]
  
  #Obtiene la clase de cada observación
  for(i in 1:n_obs){
    observacion <- atributos[i,]
    
    #Clasifica las reglas de acuerdo a su tipo (cuidado con los espacios!)
    reglasCompra <- reglas[str_detect(reglas, "THEN  is 1;")]
    reglasVenta <- reglas[str_detect(reglas, "THEN  is -1;")]
    #PODRÍA ORDENAR LAS REGLAS DE ACUERDO A supportSize o laplace (ver str_extract)
    
    
  }
  
  
}