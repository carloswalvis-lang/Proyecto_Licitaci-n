# Costos_MO_Spot.csv: guía de lectura

Tabla de referencia de costo de mano de obra spot por cargo (separador `;`, UTF-8, valores en CLP). Cada fila lleva además `Proyecto_origen`, `Fuente` y `Fecha_carga`.

**Carga actual:** proyecto STL DRT Contrato Marco Obras Complementarias (LIC DRT-011-2026). Fuente: `RENTAS OBRAS COMPLEMENTARIAS CONTRATO MARCO DRT DIRECTOSKP.xlsx`, hoja "Costo Empresa", año 2026. 27 cargos directos de la zona Norte.

## Columnas
- **Cargo / Cargo_Homologado / Cantidad / Especialidad / Zona**: identificación del cargo. Cargo_Homologado es el nombre del cargo según las bases del cliente. Las especialidades son Construcción y Montaje, y las cuadrillas Eléctrica, Estructura, Mecánica, OOCC y Piping.
- **Liquido_Diario_Objetivo**: líquido diario pactado, que es la base de la renta.
- **Sueldo_Base, Bono_Parada_Planta, Asig_Pasajes, Asig_Colacion, Asig_Movilizacion**: haberes mensuales.
- **Total_Haberes_Mes**: suma de los haberes.
- **Leyes_Sociales_Empresa_Mes**: aportes que paga la empresa sobre el imponible (Sueldo base + Bono): Mutual 0,93%, SIS 1,78%, seguro de cesantía 3% y Ley 21.735 1,72%.
- **Costo_Empresa_Mes**: Total haberes + Leyes sociales.
- **Costo_Diario**: Costo empresa mes / 30.
- **Costo_Diario_con_Descanso**: Costo diario × 2, para un turno con descanso 1×1, donde cada día trabajado arrastra un día de descanso.
- **Valor_HH**: Costo empresa mes / 180 h.
- **Valor_HH_Extra**: Valor_HH × 1,5.
- **Liquido_Diario_Calculado**: líquido mensual / 15 días trabajados, una vez descontados AFP (11,44%), salud (7%) e impuesto único. Sirve para validar contra el objetivo.
- **Proyecto_origen / Fuente / Fecha_carga**: trazabilidad de la carga.

## Reglas de simplificación
- Se quitaron las columnas intermedias de cálculo tributario (imponible, no imponible, porcentajes, base tributable, factor, rebaja e impuesto). Se resumen en Liquido_Diario_Calculado.
- Los valores se redondearon a pesos enteros.
- El Alarife no tenía Valor HH en el origen. Se calculó con la misma fórmula y quedó anotado en Obs.
- La columna R ("Costos directos") se omitió porque es un valor fijo que no coincide con Costo_Empresa_Mes.

## Consulta
`python3 bd_precios.py mo --cargo "soldador" --zona Norte`
Son costos de un contrato y una zona específicos (año 2026). Para otra zona u otro año, se agregan filas con `cargar` y su propio `Proyecto_origen`.
