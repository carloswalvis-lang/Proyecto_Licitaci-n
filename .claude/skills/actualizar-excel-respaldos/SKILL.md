---
name: actualizar-excel-respaldos
description: Genera el Excel de cotizaciones del proyecto (hojas Listado y ECO) desde la base BD PRECIOS y copia a RESPALDO/ los originales de FSChile de cada PROV y las fuentes de cada MERC. Ejecutar solo cuando el usuario lo pida explícitamente.
disable-model-invocation: true
---

# Actualizar Excel y respaldos de cotizaciones

Ejecuta SOLO cuando el usuario lo solicita explícitamente (`/actualizar-excel-respaldos`), no automáticamente.

Las cotizaciones ya no viven en un registro por proyecto: están en la base general BD PRECIOS (ver skill `buscar-cotizaciones`). Esta skill toma las filas del proyecto actual y arma el Excel y los respaldos con `scripts/generar_excel.py`, que lee la base con `herramientas/bd_precios/bd_precios.py` del repo (misma carpeta de datos: `BD_PRECIOS_DIR` o `bd_precios` de `config/local.json`).

## Datos que necesita
- **Proyecto:** nombre tal como quedó en la columna `Proyecto_origen` de la base (por defecto, el título de `proyecto/Proceso.md`). Si no hay filas con ese nombre, muestra los proyectos de `python3 herramientas/bd_precios/bd_precios.py resumen` (`por_proyecto`) y pregunta cuál usar.
- **Destino:** carpeta `cotizaciones_salida` de `config/local.json` (por ejemplo `…\00_Bids\COT`); si no está definida, `OUTPUT/` de la carpeta de contexto. El Excel se llama `Registro_Cotizaciones - <proyecto>.xlsx` y los respaldos van a `<destino>/RESPALDO/`.
- **FSChile:** carpeta `fschile` de `config/local.json`, solo lectura.
- Si una carpeta está fuera del repo y de las carpetas permitidas, pide que se agregue con `/add-dir`.

## Proceso

1. Confirma en una línea proyecto, destino y si se copiarán respaldos; si el Excel ya existe, pregunta antes de reemplazarlo (`--sobrescribir`).
2. Ejecuta:
   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/generar_excel.py" --proyecto "<proyecto>" \
     --salida "<destino>/Registro_Cotizaciones - <proyecto>.xlsx" \
     --fschile "<raíz FSChile>" --respaldo "<destino>/RESPALDO"
   ```
   - Hoja **Listado:** tabla vertical con todas las columnas de la base.
   - Hoja **ECO:** matriz transpuesta (etiquetas en filas, cotizaciones en columnas).
   - Solo filas vigentes; agrega `--todas` si el usuario pide incluir las reemplazadas.
   - Respaldos: `PROV-NNNN_<archivo>` copiado desde FSChile (archivos planos, sin subcarpetas) y `MERC-NNNN_fuentes.txt` con las fuentes web de cada promedio de mercado. Nunca reemplaza archivos existentes.
3. Lee el JSON de salida y confirma.

## Output

```
✅ Actualización completada:
- Excel: Registro_Cotizaciones - <proyecto>.xlsx (Listado + ECO), N filas
- Respaldos copiados: X archivos
  - PROV-NNNN: X cotizaciones de proveedor
  - MERC-NNNN: X archivos de fuentes de mercado
- Ya existían (no se tocaron): X
- No encontrados en FSChile: X (lista de IDs y rutas)
```

## Notas
- Ejecutar SOLO cuando el usuario lo indique.
- No reemplazar archivos existentes sin confirmación.
- FSChile y BD PRECIOS son solo lectura para esta skill.
- Un solo guardado/copia por ejecución.
- El Excel queda como entregable: no se usa como referencia para otras tareas (regla de `OUTPUT/` en `docs/workflows.md`).
