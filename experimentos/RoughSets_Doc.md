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
  approximations = BC.LU.approximation.RST(decision.table, INDrelation)
	lowerApproximations = approximations$lower.approximation
	rm(INDrelation, approximations)
```
5. La variable ```descriptorList``` es una lista que contiene los valores únicos de la **Decision.Table** ya discretizada. Es similar a aplicar la función ```unique``` para cada columna de la tabla.
```
	descriptorsList = attr(decision.table, "desc.attrs")[-decIdx]
```

6. 
```
	descriptorsList = attr(decision.table, "desc.attrs")[-decIdx]
	descriptorCandidates = list()
	for (i in 1:length(descriptorsList)) {
		tmpDescriptors = lapply(descriptorsList[[i]],
                            function(v, x) return(list(idx = x, values = v)), i)
		tmpDescriptors = lapply(tmpDescriptors, laplaceEstimate,
		                        decision.table[,-decIdx], clsVec, uniqueCls)
		names(tmpDescriptors) = descriptorsList[[i]]
		descriptorCandidates[[length(descriptorCandidates) + 1]] = tmpDescriptors
	}
```
La variable ```descriptorCandidates``` es una lista que contiene el soporte, la exactitud de Laplace así como la clase mayoritaria (consecuente) de cada elemento en ```descriptorList```. Por ejemplo:

```
$`[-Inf,12.5]`
$`[-Inf,12.5]`$idx
[1] 1

$`[-Inf,12.5]`$values
[1] "[-Inf,12.5]"

$`[-Inf,12.5]`$consequent
[1] "2"

$`[-Inf,12.5]`$support
 [1]  45  48  49  51  52  54  56  57  59  61  62  64  65  66  67  68  70  71  72
[20]  73  74  75  77  78  79  80  81  82  83  84  85  86  88  89  90  91  92  93
[39]  94  95  99 101 108 135 137 138 140 153 154 155 157 158 159 160 161 162 164
[58] 167 172 177

$`[-Inf,12.5]`$laplace
        2 
0.8730159 
```
Nos dice que para el atributo con índice (idx) $1$, el valor ```[-Inf,12.5]``` se observa en mayor medida para la clase ```"2"```. Se podría pensar que esta lista guarda la información de un **selector**.

El código de la función ```laplaceEstimate``` se encuentra [aquí](https://github.com/janusza/RoughSets/blob/master/R/RuleInduction.OtherFuncCollections.R)

7. Calcula las reglas para cada clase. ```lowerApproximations[[i]]``` corresponde a las observaciones de la clase $i$, es decir, el concepto que se quiere aprender.
```
for(i in 1:length(lowerApproximations)) {
		rules[[i]] = computeAQcovering(as.integer(lowerApproximations[[i]]),
                                   descriptorCandidates,
		                               decision.table[,-decIdx],
                                   epsilon = 1 - confidence, K = timesCovered)
	}

```
El resultado es una lista cuyo elemento ```rules[[i]]``` es una lista que representa el conjunto de reglas para la clase $i$. Hasta este punto, el único referente al consecuente de cada regla es el índice $i$, que se relaciona con ```names(lowerApproximations)```.

8. 
```
rules = unlist(rules, recursive = FALSE)
	rules = lapply(rules, function(x) laplaceEstimate(list(idx = x$idx, values = x$values),
	                                                  decision.table, clsVec, uniqueCls, suppIdx = x$support))
```
Calcula la exactitud de Laplace para cada regla e incluye dentro de cada una de ellas el consecuente. Este consecuente corresponde a la clase que cada regla cubre con mayor frecuencia.


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

### BC.LU.approximation.RST
El código de esta función está en [liga](https://github.com/janusza/RoughSets/blob/master/R/BasicRoughSets.R).

 This function implements a fundamental part of RST: computation of lower and upper approximations. 
 The lower and upper approximations determine whether the objects can be certainty or possibly classified 
 to a particular decision class on the basis of available knowledge.

 Básicamente esta función calcula lo que se conoce como aproximación superior e inferior.

 Una aproximación superior para una clase $i$, es el conjunto de observaciones que pertenecen a esa clase, considerando que puede haber observaciones (renglones) indiscirnibles. En el código, esta aproximación se guarda en un vector cuyos nombres corresponden a la concatenación de los valores de cada atributo, por ejemplo si hay una clase 2 se tiene que el primer elemento de esta aproximación es:

 ```
 approx$upper.approximation[["2"]][1] = 
 `(13.5, Inf] [-Inf,1.67] [-Inf,2.28] [-Inf,18] (92,103] (2.61, Inf] (2.65, Inf] [-Inf,0.29] (1.82, Inf] (3.74,5.64] (1.07, Inf] (2.3,3.03] (835, Inf]`
[1] 143 189
 ```
es decir, las observaciones 143 y 189 pertenecen a la clase 2 y además son indiscernibles.

Una aproximación inferior para una clase $i$, es el conjunto de observaciones que pertenecen a esa clase y que además no son indiscernibles con alguna otra observación, es decir los vectores de la forma:

```
 approx$upper.approximation[["2"]][1] = 
 `(13.5, Inf] [-Inf,1.67] [-Inf,2.28] [-Inf,18] (92,103] (2.61, Inf] (2.65, Inf] [-Inf,0.29] (1.82, Inf] (3.74,5.64] (1.07, Inf] (2.3,3.03] (835, Inf]`
[1] 100
 ```
 siempre tendrán longitud igual a 1.

 La parte interesante de esta función es:
 ```
 	IND.decision.attr <- lapply(IND, function(x, splitVec) split(x, splitVec[x]), as.character(objects[[decision.attr]]))
	
	## initialization
	lower.appr <- list()
	upper.appr <- list()
	for(i in 1:length(uniqueDecisions)) {
		tmpIdx1 = which(sapply(IND.decision.attr, function(x) (uniqueDecisions[i] %in% names(x))))
		upper.appr[[i]] = unlist(IND[tmpIdx1])
		tmpIdx2 = which(sapply(IND.decision.attr[tmpIdx1], function(x) (length(x) == 1)))
		if(length(tmpIdx2) > 0) {
			lower.appr[[i]] = unlist(IND[tmpIdx1][tmpIdx2])
		}
		else lower.appr[[i]] = integer()
		colnames(lower.appr[[i]]) <- NULL
		colnames(upper.appr[[i]]) <- NULL
	}
 ```
 ### computeAQcovering
 ```
# Computation of a covering of a lower approximation of a concept by decision rules using the AQ algorithm.

 computeAQcovering <- function(concept, attributeValuePairs, dataTab, epsilon = 0.05, K = 2)
 ```
  * ```Concept``` es un vector de enteros ```as.integer(lowerApproximations[[i]])```. Esto determina la **clase positiva**.

	* ```attributeValuePairs <- descriptorCandidates```

	* ```dataTab <- decision.table[,-decIdx]```

  * ```epsilon = 1 - confidence, K = timesCovered```

	1. Obtiene la semilla. La lista ```selectedAttributeValuePairs``` contiene el soporte y el consecuente de cada atributo en la semilla. Utilizando el lenguaje del aprendizaje de reglas, esta lista contiene la información de cada **selector** en la semilla (que observaciones cubre así como la clase mayoritaria, es decir, el consecuente)
	```
	  seedIdx = sample(uncoveredConcept, 1)
    selectedAttributeValuePairs = mapply(function(avps, v) avps[[as.character(v)]],
                                         attributeValuePairs, dataTab[seedIdx,],
                                         SIMPLIFY = FALSE)
	```

	2. Magia negra :confused: :tired_face: :sob:
	Pero al parecer ya que la variable ```support``` cumple que 
	```
	all(decision.table[support, idx_target] == concept)
	```
	es decir, el soporte sólo contiene observaciones que pertenece al concepto que se está aprendiendo.

```
	 attrOrdering = sample(1:length(selectedAttributeValuePairs))
    suppList = suppList[attrOrdering]
    selectedAttributeValuePairs = selectedAttributeValuePairs[attrOrdering]

    for(i in length(attrOrdering):1)  {
      tmpSupport = Reduce(intersect, suppList[-i])
      if(length(tmpSupport) > 0 && sum(tmpSupport %in% concept)/length(tmpSupport) >= 1-epsilon) {
        support = tmpSupport
        suppList = suppList[-i]
        selectedAttributeValuePairs = selectedAttributeValuePairs[-i]
      }
    }
```

El resto del código se encarga de cubrir los ejemplos (de la clase positiva)restantes, así como asegurar que las reglas cumplan el parámetro ```timesCovered```.
