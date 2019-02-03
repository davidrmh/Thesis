# Flujo de trabajo

## Crear conjuntos de entrenamiento

+ import indicadores as ind, datasets as dat.

1. Con ind.leeTabla leer los datos de Yahoo Finance.

2. Con dat.separaBloques separar el conjunto de datos en bloques del mismo tamaño.

3. Con dat.etiquetaBloques obtén las etiquetas de cada bloque.

4. Con dat.guardaCSV guarda cada bloque etiquetado en la ruta correspondiente.

5. Carga el diccionario para crear los atributos.

6. Actualizar el archivo *CSV* que contiene el nombre de los conjuntos etiquetados.

7. Con dat.creaEntrenamiento se crearán los conjuntos de entrenamiento.
