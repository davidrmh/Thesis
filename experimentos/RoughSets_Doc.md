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
| (13.5, Inf] | (1.67, 2.55] | (2.28,2.48] |
|-------------|--------------|-------------|
| (12.5,13.5] | (1.67,2.55]  | [-Inf,2.28] |
| (12.5,13.5] | (1.67,2.55]  | (2.48, Inf] |
