# Explicación de las funciones del paquete RoughSets de R.

## SF.asDecisionTable
La función ```SF.asDecisionTable``` convierte **data.frames** en objetos del tipo **DecisionTable**.

El parámetro *decision.attr* representa el índice en donde se encuentra el atributo que representa la clase.

El parámetro *indx.nominal* es un vector lógico el cual indica que atributos son del tipo nominal (TRUE).

## D.discretization.RST
La función ```D.discretization.RST``` se utiliza para discretizar los valores de un objeto **DecisionTable** (ver función ```SF.asDecisionTable```).

Esta función regresa los valores de corte (cut values) para poder crear los intervalos en los que dividirán los atributos continuos.

En la tesis se utilizaron los métodos ```D.discretize.quantiles.RST.```(discretización por cuantiles) y ```D.discretize.equal.intervals.RST.``` (discretización por intervalos de misma longitud).

## SF.applyDecTable
La función ```SF.applyDecTable``` requiere de un objeto del tipo **DecisionTable** (ver función ```SF.asDecisionTable```) que contiene los datos sin discretizar y los cut values correspondientes a estos datos (ver función ```D.discretization.RST```). Como resultado, se obtiene una nueva **DecisionTable** que contiene la discretización de los atributos de la tabla original de acuerdo a los cut values.

Un ejemplo de la forma de la tabla resultante es:

|**Atributo 1**|**Atributo 2**|**Atributo 3**|
|-------------|--------------|-------------|
| (13.5, Inf] | (1.67, 2.55] | (2.28,2.48] |
| (12.5,13.5] | (1.67,2.55]  | [-Inf,2.28] |
| (12.5,13.5] | (1.67,2.55]  | (2.48, Inf] |

## RI.AQRules.RST
El código se encuentra en esta [liga](https://github.com/janusza/RoughSets/blob/master/R/RuleInduction.R).

1. ```decIdx = attr(decision.table, "decision.attr")``` obtiene el índice de la columna que contiene las clases.

2. ```attr(decision.table, "nominal.attrs")``` revisa que la tabla tenga sólamente atributos nominales (o que esté discretizada).

3.  Obtiene la clase de cada observación ```clsVec``` y las clases existentes  ```uniqueCls``. Obtiene el nombre de la columna que contiene las clases ```decisionName```
```
	clsVec <- decision.table[,decIdx]
	uniqueCls <- unique(clsVec)
	decisionName = colnames(decision.table)[decIdx]
```

4. 
```
  INDrelation = BC.IND.relation.RST(decision.table, (1:ncol(decision.table))[-decIdx])
```

### BC.IND.relation.RST
El código de esta función está en [liga](https://github.com/janusza/RoughSets/blob/master/R/BasicRoughSets.R).

 This function implements a fundamental part of RST: the indiscernibility relation.

 This binary relation indicates whether it is possible to discriminate any given pair of objects from an information system.

 Esta función recibe un objeto del tipo **Decision.Table** (únicamente con atributos nominales) y un vector (*feature.set*) con los índices de cada atributo.
 ```BC.IND.relation.RST <- function(decision.table, feature.set = NULL)```

 1. Obtiene los datos
 ```
 	objects <- decision.table
	nominal.att <- attr(decision.table, "nominal.attrs")
	decision.attr <- attr(decision.table, "decision.attr")
 ```

 2. 
 ```
 	#compute the indiscernibility classes
	if (length(feature.set) == 1){
		IND = split(1:nrow(objects), do.call(paste, list(objects[ , feature.set])))
	} else {
		IND = split(1:nrow(objects), do.call(paste, objects[ , feature.set]))
	}
 ```
  ```do.call(paste, objects[ , feature.set])``` concatena cada columna en *objects* obteniéndose un vector (**character**) con el mismo número de renglones que *objects*.

  ```IND = split(1:nrow(objects), do.call(paste, objects[ , feature.set]))``` La función ```split``` convierte el resultado de ```do.call``` en un **factor** (lo que elimina repeticiones). Básicamente la variable *IND* es una lista de vectores cuyos nombres son el resultado de ```do.call``` (sin repeticiones) y este vector contiene los índices de *objects* que contienen el nombre del vector (estas observaciones son indiscernibles).

  3. Sólamente construye la clase, lo importante es la variable *IND*.
  ```
  	## construct class
	mod <- list(IND.relation = IND, type.relation = "equivalence", type.model = "RST")	
	class.mod <- ObjectFactory(mod, classname = "IndiscernibilityRelation")
	
	return(class.mod)
  ```