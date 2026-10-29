# Arriendo_Equipos.csv: guía de lectura

Tabla de referencia de arriendo de equipos y maquinarias (separador `;`, UTF-8). Una fila por equipo, capacidad, horas mínimas y proveedor. Cada fila lleva además `Proyecto_origen`, `Fuente` y `Fecha_carga`.

**Carga actual:** proyecto STL DRT Contrato Marco Obras Complementarias (LIC DRT-011-2026). Fuente: `Maestro _Licitación Arriendo Equipos y Maquinarias.xlsx` (29 hojas ECO-01 por equipo). 2.619 filas, 21 proveedores.

## Columnas
- **Equipo / Tipo / Capacidad_Modelo / Horas_Min_Mes / Requiere_Cert**: identificación del ítem (las horas mínimas al mes son 180–400, FULL HORAS, etc.).
- **Proveedor**: Finning, Komatsu Arrienda, Trektrading, TYC, Transmac, Getram, Rent Maq, Salfa Rent, entre otros.
- **Hora_UF_P1..P4**: valor por hora en UF según el plazo del contrato. P1 = 1-3 meses, P2 = 4-6, P3 = 7-9 y P4 = 10-12 o anual. Las etiquetas originales del proveedor están en `Periodos_Origen` (por ejemplo, Alo Rental cotiza 1-5 / 6-8 / 9-11 / 12).
- **HoraAdic_UF_P1..P4**: valor de la hora adicional por sobre el mínimo.
- **Rank_P1**: ranking de precio entre proveedores para el mismo ítem en P1 (1 = más barato). Corresponde a la carga original de ese proyecto.
- **Oferta**: de qué oferta se tomó el valor. Se usa la última disponible (2da > 1ra). "Única" significa que el proveedor no tenía ronda.
- **Moneda_Origen / Obs**: alertas de calidad.
- **Proyecto_origen / Fuente / Fecha_carga**: trazabilidad de la carga.

## Reglas de simplificación
- Se eliminaron Día, Semana, Quincena y Mes porque se derivan de la hora: Día = Hora × 6; Mes = Hora × Horas_Min_Mes.
- Cuando el proveedor solo informó Mes, la hora se calculó como Mes / Horas (Obs: "Hora derivada").
- Valores en CLP (sobre todo Transmac y Cota Cero) se convirtieron a UF con UF = 39.485,65 (valor que aparece en el maestro).
- "REVISAR valor atipico" marca las horas que superan 3 veces la mediana del equipo. La mayoría son de Transmac, cuyo valor hora crece con las horas mínimas, lo que sugiere un error de origen. El comando `arriendo` los excluye del resumen por defecto.
- Descuento de referencia en la hoja Tracto + Cama Baja: 10% (no aplicado).

## Consulta
`python3 bd_precios.py arriendo --equipo "lubricador" --capacidad "estandar" --horas 180 --plazo P1`
Devuelve las filas ordenadas por precio y un resumen (n, mínimo, mediana, promedio, máximo) en UF por hora. Son precios de una licitación específica: sirven de referencia, no reemplazan una cotización vigente.
