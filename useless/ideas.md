# Biclustering

+ Leer datos.

+ Separar entrenamiento y prueba (funcion subconjunto del archivo etiqueta).

+ Etiquetar entrenamiento.

+ Calcular indicadores y combinarlos en una tabla.

  + (pendiente) Optimizar indicadores de manera
  individual.

+ **Opción 1**

  + Normalizar los indicadores.

  + Entrenar un clasificador.

  + Normalizar el conjunto de prueba y realizar las predicciones.


+ **Opción 2**

  + Normalizar indicadores y juntar los datos junto con la columna con las etiquetas (-1, 0, 1).

  + Agrupar de acuerdo a la etiqueta y obtener el promedio por columna (sólo las columnas de los indicadores), de esta forma obtengo vectores representantes de cada clase.

  + Normalizar el conjunto de prueba y aplicar *K-NN* para obtener la clase que pertenece cada observación.

+ Calcular las métricas de desempeño.

## Observaciones

+ En los códigos debo de asegurarme que el orden de las columnas sea el mismo en
el conjunto de entrenamiento y en el de prueba, además de utilizar los mismos
parámetros para cada indicador.

+ Lo anterior me limita a utilizar sólo un conjunto de parámetros.
