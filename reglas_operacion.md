# **Reglas de compra**
1. Si $\Delta P_{t}^{open}, \Delta P_{t-1}^{open}, \Delta P_{t-2}^{open}$ son positivos (tres días
consecutivos a la alza) $\wedge$ se tienen acciones, entonces *compra*.

  + *El razonamiento de esta regla se basa en el supuesto de que la tendencia
  alcista se va a conservar en el futuro cercano*.

2. Si $\Delta P_{t - 2}^{open} < 0, \, \Delta P_{t - 1} ^ {open} > 0, \, \Delta P_{t}^{open} >0$ y además $\Delta P_{t - 1} ^ {open} + \Delta P_{t}^{open} > |\Delta P_{t - 2}^{open}|$, entonce *compra*
  + *El razonamiento de esta regla se basa en que la tendencia a la baja se ha terminado y ahora empieza un periodo a la alza*


# **Reglas de venta**
1. Si $P_{t}^{open} \in [BS - \epsilon, \infty)$, en donde $BS$ es una banda
superior establecida por el usuario y $\epsilon$ es una tolerancia también definida
por el usuario $\wedge$ se tienen acciones, entonces *vende*.

  + *El razonamiento de esta regla se basa en el supuesto de que existe ciertos
  niveles en los que el inversionista está satisfecho con la ganancia que puede
  obtener y decide vender en lugar de arriesgarse esperando a que el precio siga
  creciendo*
