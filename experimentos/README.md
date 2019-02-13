# Experimentos

Aquí almaceno los experimentos y sus resultados.

Cada modelo tiene su carpeta.

El archivo **entrena_prueba.csv** contiene los nombres de los archivos de
entrenamiento y de prueba que utilizará cada modelo.
Este archivo debe de leerse con el código en los archivos **obtenConjuntos**.

La estructura de este archivo debe ser la siguiente:

+ 3 columnas (entrena, prueba, etiquetado)

+ La columna **entrena** contiene los nombres de los archivos que se utilizarán
como conjuntos de entrenamiento.

+ La columna **prueba** contiene los nombres de los archivos que se utilizarán
como conjuntos de prueba.

+ La columna **etiquetado** contiene los archivos correspondientes a la columna
**prueba** pero con los precios de Yahoo Finance y la columna *Clase*. Estos
archivos se utilizarán para crear los archivos necesarios para calcular las
métricas de desempeño.
 


