# Explicación de las funciones del paquete RoughSets de R.

## SF.asDecisionTable
La función ```SF.asDecisionTable``` convierte **data.frames** en objetos del tipo **DecisionTable**.

El parámetro *decision.attr* representa el índice en donde se encuentra el atributo que representa la clase.

El parámetro *indx.nominal* es un vector lógico el cual indica que atributos son del tipo nominal (TRUE).

## D.discretization.RST
La función ```D.discretization.RST``` se utiliza para discretizar los valores de un objeto **DecisionTable** (ver función ```SF.asDecisionTable```).

Esta función regresa los valores de corte (cut values) para poder crear los intervalos en los que dividirán los atributos continuos.

En la tesis se utilizaron los métodos ```D.discretize.quantiles.RST.```(discretización por cuantiles) y ```D.discretize.equal.intervals.RST.``` (discretización por intervalos de misma longitud).