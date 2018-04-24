# Experimento con árboles de decisión (CART)

### Conjunto de datos

* Precios de cierre ajustados obtenidos de Yahoo Finance para las series accionarias *NAFTRAC* y *AMXL*, comprendiendo un periodo de tiempo desde *Enero 02 2014* hasta *Abril 05 2018*

* El conjunto de entrenamiento comprende el 80% (en orden cronológico) de las observaciones de dicho periodo, mientras que el 20% restante corresponde al conjunto de prueba.

## Descripción del experimento

### Modelo

Se creó un **conjunto de entrenamiento** de la siguiente forma:

1. Para cada tiempo $t$, se calculan las variaciones entre el precio ( de cierre ajustado) en $t$, $P_{t}$, y una catidad de **hback** precios del pasado, es decir, se calculan las variaciones

$$\dfrac{P_{t}-P_{t-1}}{P_{t-1}},\dfrac{P_{t} -P_{t-2}}{P_{t-2}},\ldots,\dfrac{P_{t}-P_{t-hback}}{P_{t-hback}}$$
 estas variaciones formarán los atributos de nuestro conjunto de datos.

2. A estas variaciones se les asocia una etiqueta de acuerdo a un **umbral>0** y al signo de la variación entre el precio $P_{t}$ y un precio futuro que está **hforw** periodos después, $P_{t+hforw}$, concretamente

    * Si $\dfrac{P_{t+hforw}-P_{t}}{P_{t}} > umbral$ y $\dfrac{P_{t+hforw}-P_{t}}{P_{t}}>0$ , entonces *Compra* $(1)$

    * Si $\dfrac{P_{t+hforw}-P_{t}}{P_{t}} < umbral$ y $\dfrac{P_{t+hforw}-P_{t}}{P_{t}}<0$ , entonces *Venta* $(-1)$

    * En otro caso *Espera* $(0)$

3. Finalmente se termina con un tabla de la siguiente forma

|$t$|Variación $t$ y $t-1$|Variación $t$ y $t-2$|$\ldots$|Variación $t$ y $t-hback$|Clase|
|--|--|--|--|--|--|
|hback|0.04|-0.01|$\ldots$|0.10|1|
|hback+1|0.03|0.01|$\ldots$|-0.05|-1|
|hback+2|-0.02|0.01|$\ldots$|0.05|0|
|$\vdots$|$\vdots$|$\vdots$|$\vdots$|$\vdots$|$\vdots$|
|n|

4. Utilizando la tabla anterior, se ajusta un árbol de clasificación (CART) utilizando la **entropía** como medida de información.

### Desempeño

Para medir el desempeño del modelo, se utilizó el exceso de ganancia sobre la estretegia **Buy & Hold**, es decir, la diferencia entre la ganancia generada al tomar las decisiones generadas por el árbol y la ganancia generada al comprar en el inicio del periodo y vender al final del mismo.

Se consideró también lo siguiente:

1. La primera acción ejecutada debe ser una señal de compra (no es posible vender algo que no se tiene)

2. Señales contiguas iguales no se ejecutan, es decir, una vez ejecutada una señal de compra, se tiene que esperar hasta la próxima señal de venta.

3. El precio de compra/venta es el precio de cierre (ajustado) del día siguiente al que se generó la señal.

4. Si la última señal generada fue de compra y no hubo señal de venta antes de que terminara el plazo de tiempo, entonces se cierra esta posición (se vende) con el precio del último periódo.

### Resultados

* **NAFTRAC** para esta acción se utilizaron los siguiente parámetros:

  + $hforw$=15 días.
  + $hback$=11 días.
  + $umbral$=0.03

 El exceso de ganancia sobre **Buy & Hold** durante el periodo de prueba (*Junio 08 2017 a Abril 05 2018*) fue de $4.39$%.
   

 * **AMXL** para esta acción se utilizaron los siguiente parámetros:
    + $hforw$=15 días.
    + $hback$=23 días.
    + $umbral$=0.0101

 El exceso de ganancia sobre **Buy & Hold** durante el periodo de prueba (*Mayo 30 2017 a Abril 05 2018*) fue de $12.55$%.    
