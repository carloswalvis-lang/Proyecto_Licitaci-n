# BD PRECIOS: base general de cotizaciones

Base única de Veltis y sus empresas operativas (Berliam, Steel, Walvis, Quintrax). Reemplaza al registro que cada proyecto guardaba por separado. La escribe y consulta la skill `buscar-cotizaciones`; también se puede abrir en Excel para analizarla.

> **En el repositorio `licitaciones-base`** se versionan solo `bd_precios.py` y estas guías (`herramientas/bd_precios/`). Los CSV siguen en la carpeta compartida BD PRECIOS y nunca se suben a GitHub. El script busca la carpeta de datos en `BD_PRECIOS_DIR` o en la clave `bd_precios` de `config/local.json`. Desde la raíz del repo, los comandos de abajo se ejecutan como `python3 herramientas/bd_precios/bd_precios.py <comando>`.

## Archivos
- `Cotizaciones.csv`: una fila por cotización (separador `;`, UTF-8).
- `Busquedas_sin_precio.csv`: ítems que se buscaron y no tenían precio público.
- `bd_precios.py`: único punto de lectura y escritura (Python 3, sin instalar nada). No editar los CSV a mano mientras haya una sesión de Claude trabajando.

## Columnas de Cotizaciones.csv
- **ID**: `PROV-NNNN` (cotización de un tercero encontrada en FSChile) o `MERC-NNNN` (promedio de mercado). Correlativos para toda la empresa, no por proyecto.
- **Tipo / Familia**: PROV o MERC; familia en MAYÚSCULAS sin tildes (ELECTRODO, PLANCHA, EXTINTOR…).
- **Fecha_cotizacion**: fecha del precio (AAAA-MM-DD). Con ella se calcula la antigüedad (90 días).
- **Fecha_registro**: día en que se escribió la fila.
- **Descripcion**: nombre canónico (Tipo + Subtipo + Material/Grado + Medida + Formato + Norma + Marca si se pidió).
- **Unidad / Precio_neto_CLP**: unidad de venta y precio neto sin IVA, entero.
- **Proveedor_Fuentes / Link_o_Ruta_FS / Ubicacion_Detalle**: de dónde sale el precio. En PROV, la ruta relativa en FSChile y la página u hoja.
- **Notas**: etiquetas fijas (`Marca:`, `Alcance:`, `Moneda orig:`, `IVA no especificado, se asume neto`, `Mín. compra:`, `Entrega:`, `Baja confianza (1 fuente)`, `Convertido desde <ID>`, `Reemplaza <ID>`).
- **Proyecto_origen / Empresa_operativa / GC / Zona / Usuario**: contexto de quién cotizó y para qué. GC es el Grupo de Costo (GC_01 a GC_18) del Perfil Base. Sirven para analizar por proyecto, zona o grupo de costo.
- **Estado**: `vigente`, o `reemplazada por <ID>` cuando una cotización nueva del mismo ítem la sustituye. Las reemplazadas se conservan como historial de precios.

## Conjuntos de datos de referencia
Además de las cotizaciones, la carpeta guarda tablas de referencia con estructura propia, que pueden recibir datos de varios proyectos. Cada fila lleva `Proyecto_origen`, `Fuente` (archivo de origen) y `Fecha_carga`.

- `Arriendo_Equipos.csv`: valor hora de arriendo de equipos y maquinarias en UF, por proveedor y plazo (P1 = 1-3 meses, P2 = 4-6, P3 = 7-9, P4 = 10-12). Guía: `LEEME_Arriendo_Equipos.md`.
- `Costos_MO_Spot.csv`: costo empresa de mano de obra spot por cargo, en CLP (haberes, leyes sociales, costo diario, valor HH). Guía: `LEEME_Costos_MO_Spot.md`. Son valores por cargo, no por persona; contienen sueldos base, así que cuida con quién se comparte la carpeta.

Los materiales, insumos y servicios sueltos siguen en `Cotizaciones.csv`. Estas tablas no se mezclan con ella porque sus unidades (UF por hora, costo mensual por cargo) y sus volúmenes no calzan con un precio unitario en CLP.

```
python3 bd_precios.py arriendo --equipo "pluma|grua" --capacidad "10" --horas 180 --plazo P1   # proveedores, mediana y rango en UF/h
python3 bd_precios.py mo --cargo "soldador" --zona Norte                                       # costo empresa, diario y HH
python3 bd_precios.py cargar --dataset mo --archivo nuevo.csv --proyecto "Nombre" --fuente "archivo.xlsx"
```
`cargar` reemplaza solo las filas del mismo `Proyecto_origen` y conserva las de otros proyectos, así que repetir una carga no duplica. El archivo debe traer las mismas columnas que la tabla (sin las tres de control). En `arriendo`, los valores marcados "REVISAR valor atipico" se excluyen del resumen salvo que se use `--con-atipicos`.

## Comandos útiles (para análisis a mano o desde Claude)
```
python3 bd_precios.py resumen                       # filas por familia, antiguas y por proyecto
python3 bd_precios.py buscar --familia ELECTRODO --texto "e6011&3,2"
python3 bd_precios.py historial --texto "plancha|lamina&a36"
python3 bd_precios.py verificar                     # revisa IDs, fechas y precios
python3 bd_precios.py duplicados --archivo candidatos.json   # compara candidatos con la base y sugiere agregar, reemplazar u omitir
```
En `--texto`, `&` separa condiciones que deben cumplirse todas y `|` separa sinónimos de una misma condición.

## Reglas
- Precio siempre neto (sin IVA), regular (nunca oferta), en CLP entero.
- PROV solo con cotizaciones emitidas por terceros; los documentos propios de Veltis y sus empresas nunca son referencia.
- Una cotización de más de 90 días no se reutiliza sola: el skill pregunta si usarla o actualizarla.
- **Prioridad ante duplicados** (carga de archivos y carpetas): la cotización de proveedor (PROV) prevalece sobre el promedio de mercado (MERC). Entre filas del mismo tipo, reemplaza la de fecha más reciente y la anterior queda como historial (`reemplazada por <ID>`). Si llega un MERC y existe un PROV de más de 90 días, decide el usuario.
- **Carga de archivos y carpetas**: el skill lee los archivos, descarta los documentos propios de Veltis y sus empresas, y confirma con el usuario ítem por ítem antes de escribir en la base.
- La escritura usa un bloqueo (`.bd_precios.lock`) para que dos sesiones no escriban a la vez. Si queda un bloqueo viejo, se libera solo a los 60 segundos.
- Si una sesión no puede alcanzar esta carpeta, guarda las filas como pendientes en el proyecto (`proyecto/cotizaciones/PENDIENTE_SYNC.md`) y se cargan después con `pendientes-sync`, sin duplicar.
- Los datos de esta carpeta no forman parte de la base compartida: `publicar-plantillas-licitacion` e `importar-plantillas-licitacion` solo mueven el script y estas guías, nunca los CSV.

## Registro de cambios
- 2026-10-26: creación de la base general. Parte vacía: los proyectos no tenían registro previo que migrar.
- 2026-10-26: nuevo comando `duplicados` y regla de prioridad PROV sobre MERC para la carga de archivos y carpetas.
- 2026-10-26: se cargan `Arriendo_Equipos.csv` (2.619 filas) y `Costos_MO_Spot.csv` (27 cargos) del proyecto STL DRT Contrato Marco Obras Complementarias (LIC DRT-011-2026); nuevos comandos `arriendo`, `mo` y `cargar`.
- 2026-10-29: el script pasa al repositorio `licitaciones-base` (`herramientas/bd_precios/`) y toma la carpeta de datos de `BD_PRECIOS_DIR` o `config/local.json`; junto a los CSV sigue funcionando como antes.
