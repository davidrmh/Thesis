# Diccionarios

+ Aquí se guardan los diccionarios necesarios para establecer los atributos
+ Ver **plantilla.json**
+ Para cargar un diccionario se necesita el módulo json
+ f = open('ruta/al/diccionario.json')
+ dicc = json.load(f)
+ f.close()

## Descripción de los diccionarios

+ **dicc-1.json**: Este diccionario utiliza 5 indicadores (los parámetros son los sugeridos en la literatura)
	+ Diferencia de Aroon: 25 días de ventana de tiempo y precios de cierre ajustados.
	+ RSI con ventana de 14 días y precios de cierre ajustados.
	+ MFI (Money Flow Index) con ventana de 14 días.
	+ Williams %R con ventana de 14 días.
	+ Commodity Channel Index con ventana de 20 días y factorC igual a 0.015


