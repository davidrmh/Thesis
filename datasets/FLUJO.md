# Flujo de trabajo

## Crear conjuntos de entrenamiento

+ import indicadores as ind, datasets as dat, etiqueta as eti

1. Con ind.leeTabla leer los datos de Yahoo Finance.

2. Con dat.separaBloques separar el conjunto de datos en bloques del mismo tamaño.

3. Con dat.etiquetaBloques obtén las etiquetas de cada bloque, utilizando limpia = False

4. Con eti.limpiaRepetidas quita las señales repetidas, así se crea el bloque de datos etiquetados sin señales repetidas.

5. Con dat.guardaCSV guarda cada bloque etiquetado en la ruta correspondiente.

6. Carga el diccionario para crear los atributos.

7. Actualizar el archivo *CSV* (archivos_etiquetados.csv) que contiene el nombre de los conjuntos etiquetados.

8. Con dat.creaEntrenamiento se crearán los conjuntos de entrenamiento.
