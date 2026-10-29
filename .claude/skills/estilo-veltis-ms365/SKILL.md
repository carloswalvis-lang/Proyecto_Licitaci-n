---
name: "estilo-veltis-ms365"
description: "Aplica el estilo corporativo Veltis (paleta con Énfasis 1-6 y sus tonalidades como referencias + Overpass regular/bold/italic) a Word, PowerPoint, Excel y páginas HTML, nuevos o existentes. Úsalo siempre que se pida un documento, presentación, planilla, página o dashboard de Veltis, Berliam, Steel, Walvis o Quintrax, o 'aplicar el estilo/colores/fuente de la empresa'."
---

# Estilo corporativo Veltis (MS365 y HTML)

Deja cualquier archivo Word (.docx/.docm/.dotx), PowerPoint (.pptx/.pptm/.potx), Excel (.xlsx/.xlsm/.xltx), o página HTML (.html/.htm) con la identidad de Veltis y sus operativas (Berliam, Steel, Walvis, Quintrax). Hace cuatro cosas:

1. **Tema**: carga los 12 colores y Overpass en el tema del archivo (en HTML: variables CSS en `:root`). En Office la paleta Veltis aparece en el selector de colores.
2. **Colores como referencias al tema, nunca hex fijos**: cada elemento se pinta con una variable de la paleta (`ENFASIS_1`, `ENFASIS_2_CLARO_80`, `ENFASIS_1_OSCURO_25`, ...), que en el archivo queda como referencia a "Énfasis N" con su tonalidad, igual que si se eligiera en el selector de Office. En HTML queda como `var(--enfasis-1)`, `var(--enfasis-2-claro-80)`, etc. Si mañana cambia el tema, el documento cambia con él.
3. **Tamaños de texto por elemento** (tablas abajo).
4. **Tipografía**: todo el texto pasa a Overpass; negrita y cursiva se conservan (Overpass Bold / Italic).

Por qué importa usar referencias: un color fijo (#FC5E24) queda congelado; una referencia (Énfasis 1) se actualiza con el tema y Office la muestra como color del tema en el selector, manteniendo la coherencia de marca.

## Paleta del tema

Estos son los únicos hex del skill y solo se escriben dentro del tema del archivo (diccionario `TEMA`; en HTML, las variables base de `:root`).

| Slot | Nombre en Office | Variable base | Variable CSS | Hex en el tema |
|---|---|---|---|---|
| dk1 | Texto/fondo - Oscuro 1 | `OSCURO_1` | `--oscuro-1` | 000000 |
| lt1 | Texto/fondo - Claro 1 | `CLARO_1` | `--claro-1` | FFFFFF |
| dk2 | Texto/fondo - Oscuro 2 | `OSCURO_2` | `--oscuro-2` | 3F3F3F |
| lt2 | Texto/fondo - Claro 2 | `CLARO_2` | `--claro-2` | D8D8D8 |
| accent1 | Énfasis 1 | `ENFASIS_1` | `--enfasis-1` | FC5E24 |
| accent2 | Énfasis 2 | `ENFASIS_2` | `--enfasis-2` | F0AE94 |
| accent3 | Énfasis 3 | `ENFASIS_3` | `--enfasis-3` | D7D7D7 |
| accent4 | Énfasis 4 | `ENFASIS_4` | `--enfasis-4` | D7D7D7 |
| accent5 | Énfasis 5 | `ENFASIS_5` | `--enfasis-5` | A02B93 |
| accent6 | Énfasis 6 | `ENFASIS_6` | `--enfasis-6` | 4EA72E |
| hlink | Hipervínculo | `HIPERVINCULO` | `--hipervinculo` | 467886 |
| folHlink | Hipervínculo visitado | `HIPERVINCULO_VISITADO` | `--hipervinculo-visitado` | 96607D |

## Variables de tonalidad

Cada variable base tiene las mismas tonalidades que muestra el selector de Office:

| Sufijo | Tonalidad en Office | Word | PowerPoint / gráficos | Excel | CSS |
|---|---|---|---|---|---|
| (ninguno) | Color del tema | `themeColor="accent1"` | `<a:schemeClr val="accent1"/>` | `theme="4"` | `var(--enfasis-1)` |
| `_CLARO_80` | Más claro 80% | `themeTint="33"` | `lumMod 20000 + lumOff 80000` | `tint="0.8"` | `--enfasis-1-claro-80` |
| `_CLARO_60` | Más claro 60% | `themeTint="66"` | `lumMod 40000 + lumOff 60000` | `tint="0.6"` | `--enfasis-1-claro-60` |
| `_CLARO_40` | Más claro 40% | `themeTint="99"` | `lumMod 60000 + lumOff 40000` | `tint="0.4"` | `--enfasis-1-claro-40` |
| `_OSCURO_25` | Más oscuro 25% | `themeShade="BF"` | `lumMod 75000` | `tint="-0.25"` | `--enfasis-1-oscuro-25` |
| `_OSCURO_50` | Más oscuro 50% | `themeShade="80"` | `lumMod 50000` | `tint="-0.5"` | `--enfasis-1-oscuro-50` |

Ejemplos: `ENFASIS_1`, `ENFASIS_1_OSCURO_25`, `ENFASIS_2_CLARO_80`, `ENFASIS_2_OSCURO_50`, `ENFASIS_5_CLARO_60`.

Word exige además un hex en `w:val` como caché; el script lo calcula desde el tema y la tonalidad, pero lo que manda es la referencia (`themeColor` + `themeTint/themeShade`). En CSS las tonalidades se derivan de la variable base con color relativo, igual que Office (misma tonalidad y saturación, solo cambia la luminosidad): `--enfasis-2-oscuro-50: hsl(from var(--enfasis-2) h s calc(l * 0.5))`.

## Elementos: color y tamaño

Énfasis 2 puro tiene poco contraste como letra sobre blanco, así que en texto se usa su tonalidad `ENFASIS_2_OSCURO_50` y el tono puro se usa en líneas y rellenos.

### Word

| Elemento (estilo) | Color | Tamaño | Formato |
|---|---|---|---|
| Título | `ENFASIS_1` | 26 pt | Negrita, línea inferior `ENFASIS_1` |
| Subtítulo | `ENFASIS_2_OSCURO_50` | 14 pt | Cursiva |
| Título 1 | `ENFASIS_1` | 18 pt | Negrita |
| Título 2 | `ENFASIS_2_OSCURO_50` | 14 pt | Negrita, línea inferior `ENFASIS_2` |
| Título 3 | `ENFASIS_1_OSCURO_25` | 12 pt | Negrita |
| Normal (cuerpo) | (texto del tema) | 11 pt | — |
| Cita | `OSCURO_2` | 11 pt | Cursiva, barra izquierda `ENFASIS_2` |
| Cita destacada | `ENFASIS_1_OSCURO_25` | 12 pt | Negrita cursiva, barra izquierda `ENFASIS_1` |
| Descripción (pie de figura) | `ENFASIS_2_OSCURO_50` | 9 pt | Cursiva |
| Tabla: encabezado | Fondo `ENFASIS_1`, texto `CLARO_1` | 10 pt | Negrita |
| Tabla: filas alternas | Fondo `ENFASIS_2_CLARO_80` | 10 pt | — |

### PowerPoint (patrón de diapositivas)

| Elemento | Color | Tamaño |
|---|---|---|
| Títulos | `ENFASIS_1`, negrita | 36 pt |
| Texto nivel 1 / 2 / 3 / 4+ | (texto del tema) | 20 / 18 / 16 / 14 pt |
| Viñetas nivel 1 | `ENFASIS_1` | — |
| Viñetas nivel 2+ | `ENFASIS_2_OSCURO_25` | — |

### Excel

La mayoría de las planillas no usan "Tablas" formales de Excel, sino rangos con un título y una fila de encabezados. Por eso el script detecta ambos casos en cada hoja:

| Elemento | Color | Tamaño |
|---|---|---|
| Fuente del libro (estilo Normal) | (texto del tema) | 10 pt |
| Rango normal: fila de título (una sola celda con texto sobre los encabezados) | Texto `ENFASIS_1`, negrita | 14 pt |
| Rango normal: fila de encabezados (primera fila con 2+ celdas con datos) | Fondo `ENFASIS_1`, texto `CLARO_1`, negrita | 10 pt |
| Rango normal: filas de datos alternas | Fondo `ENFASIS_2_CLARO_80` | — |
| Tabla formal de Excel | Estilo `TableStyleMedium2` (encabezado Énfasis 1 y bandas, por tema) | — |

Las hojas que ya tienen tablas formales no se pintan celda a celda (las estiliza el estilo de tabla). Los ajustes están en el diccionario `EXCEL` del script.

### HTML

El bloque CSS Veltis (`<style id="veltis-tema">` + enlace a Overpass en Google Fonts) trae las variables de la paleta, modo claro y oscuro, y reglas base por elemento:

| Elemento | Color modo claro | Color modo oscuro | Tamaño |
|---|---|---|---|
| `h1` | `--enfasis-1` | `--enfasis-1` | 2.25rem, 700 |
| `h2` | `--enfasis-2-oscuro-50`, línea inferior `--enfasis-2` | `--enfasis-2` | 1.5rem, 700 |
| `h3` | `--enfasis-1-oscuro-25` | `--enfasis-1-claro-40` | 1.25rem, 700 |
| `h4` | `--oscuro-2` | `--claro-2` | 1rem, 700 |
| Cuerpo | `--oscuro-1` sobre `--claro-1` | `--claro-1` sobre fondo oscuro derivado de `--oscuro-2` | 1rem |
| `blockquote` | `--oscuro-2`, barra `--enfasis-2` | `--claro-2` | 1rem, cursiva |
| `figcaption`, `caption` | `--enfasis-2-oscuro-50` | `--enfasis-2` | 0.8125rem, cursiva |
| `th` | Fondo `--enfasis-1`, texto `--claro-1` | igual | 0.875rem, 700 |
| Filas pares de tabla | `--enfasis-2-claro-80` | mezcla tenue de `--enfasis-2` | — |
| Enlaces | `--hipervinculo` / `--hipervinculo-visitado` | sus `-claro-40` | — |
| Viñetas (`li::marker`), `hr`, botones | `--enfasis-1` | igual | — |
| Gráficos | `--serie-1` … `--serie-6` = `--enfasis-1` … `--enfasis-6` | igual | — |

El modo oscuro usa `@media (prefers-color-scheme: dark)` con `:root:not([data-theme="light"])` y también `:root[data-theme="dark"]`. Los ajustes están en `HTML_ROLES` y `build_css()` del script.

### Todos los formatos
- Gráficos: las series toman `ENFASIS_1`…`ENFASIS_6` desde el tema.
- Colores por defecto de Office escritos a mano (azul 4472C4, naranjo ED7D31 y sus tonalidades, de Office 2007/2013/2023) se reemplazan por la **referencia** equivalente (por ejemplo 2F5496 → `ENFASIS_1_OSCURO_25`, FBE4D5 → `ENFASIS_2_CLARO_80`; en HTML → `var(--enfasis-1-oscuro-25)`).
- En títulos se quita el tamaño y color puestos a mano para que manden los del estilo (desactivable con `--keep-direct`).

Para otra combinación edita en el script `WORD_ROLES`, `WORD_TABLA`, `PPT_ROLES`, `EXCEL` o `HTML_ROLES` usando siempre nombres de variables de la paleta, nunca hex.

## Flujo de trabajo

### 1. Preparar el script
El script viene con la skill: `${CLAUDE_SKILL_DIR}/scripts/apply_veltis_theme.py` (en los ejemplos de abajo, `apply_veltis_theme.py` se refiere a esa ruta). No lo copies al proceso. Requiere `lxml` (`pip install lxml` si falta; usa `python` en vez de `python3` si es lo que hay en Windows).

### 2a. Documento o página existente
1. Ubica el archivo (ruta que indique el usuario o `OUTPUT/` del proceso). Si está fuera del repo y de las carpetas permitidas, pide que se agregue con `/add-dir`.
2. Ejecuta `python apply_veltis_theme.py "archivo.xlsx"` (o `.docx`, `.pptx`, `.html`) → genera `archivo_veltis.ext` junto al original. `--inplace` solo si el usuario pide reemplazar el original; `-o` para otro nombre; acepta varios archivos.
3. Opciones (Office):
   - `--colors-only`: no cambia fuentes.
   - `--fonts-only`: solo Overpass.
   - `--theme-only`: carga tema y fuente, sin pintar ni redimensionar elementos.
   - `--no-sizes`: aplica colores pero no cambia tamaños.
   - `--keep-direct`: respeta tamaño/color puestos a mano en títulos.
4. En HTML el script inserta (o reemplaza, si ya existe) el bloque `veltis-tema` antes de `</head>` (o al inicio si es un fragmento sin `<head>`) y cambia los hex por defecto de Office del CSS por `var(--...)`. Después revisa el CSS propio de la página: los colores fijos que no son de Office conviene reemplazarlos a mano por variables de la paleta.

### 2b. Documento o página nuevo
- **Office**: crea el archivo con la skill del formato (`docx`, `pptx` o `xlsx`, del plugin `document-skills`) usando los estilos integrados (Título, Título 1-3, Cita, Descripción, tablas) en vez de formato manual, y fuente "Overpass". En Excel deja un título en una celda sola y la fila de encabezados justo debajo, para que el script los reconozca. Cuando la librería permita colores del tema, usa referencias: python-docx `font.color.theme_color = MSO_THEME_COLOR.ACCENT_1` (+ `brightness` para tonalidades), python-pptx `font.color.theme_color` y `.brightness`, openpyxl `Color(theme=4, tint=-0.25)`. Evita `RGBColor`/hex. Al terminar, ejecuta el script con `--inplace`.
- **HTML**: obtén el bloque con `python apply_veltis_theme.py --css` y pégalo al inicio del archivo. Escribe todo el CSS propio con las variables (`var(--enfasis-1)`, `var(--enfasis-2-claro-80)`, `var(--fondo)`, `var(--borde)`, `var(--serie-N)` para gráficos…), nunca con hex. Usa los elementos semánticos (`h1`-`h4`, `table/th`, `blockquote`, `figcaption`) para que tomen el estilo solos. Para gráficos en canvas (Chart.js, etc.) lee las variables en JS con `getComputedStyle(document.documentElement).getPropertyValue('--serie-1')`.

### 3. Verificar
- Office: abre el resultado con python-docx / python-pptx / openpyxl para confirmar que no está corrupto, y revisa que los colores sean referencias: en Word `themeColor=` en `word/styles.xml`; en PowerPoint `schemeClr` en el patrón; en Excel `theme=` en `xl/styles.xml` (con openpyxl: `ws['A1'].fill.fgColor.theme` debe ser 4 en el encabezado).
- HTML: abre la página con Playwright en modo claro y oscuro (`color_scheme`) y revisa contraste y que no queden hex fijos (`grep -E '#[0-9A-Fa-f]{6}'` fuera del bloque `veltis-tema`).
- Si generas vista previa con LibreOffice: Overpass puede no estar instalada (se verá otra fuente) y LibreOffice no dibuja estilos de tabla formal de Excel; no son errores del archivo.

### 4. Entregar
Los archivos nuevos van a `OUTPUT/` de la carpeta de contexto; un archivo existente queda junto al original como `archivo_veltis.ext` (o reemplazado, si el usuario pidió `--inplace`). Indica la ruta. Para Office recuerda en una línea que quien abra el archivo necesita Overpass instalada (gratis en Google Fonts); en HTML la fuente se carga sola desde Google Fonts.

## Límites
- .doc/.ppt/.xls antiguos: convertir antes con LibreOffice (`--convert-to docx|pptx|xlsx`).
- Colores personalizados fuera de las paletas por defecto de Office no se tocan (no se sabe su intención); si el usuario lo pide, agrégalos a `DEFAULT_MAP` apuntando a una variable de la paleta.
- Excel: solo se analiza el primer bloque de cada hoja (título + encabezado en las primeras 30 filas y los datos contiguos debajo). Hojas con varios bloques o encabezados en otra posición pueden necesitar ajuste manual.
- HTML: las reglas base son de selector de elemento; clases o estilos en línea de la página pueden ganarles y hay que ajustarlos a mano. Las tonalidades CSS usan color relativo (`hsl(from …)`), soportado por Chrome/Edge 119+, Safari 16.4+ y Firefox 128+.
- Imágenes y logos no se modifican.
- Los hex del tema se midieron desde el selector de Office; si hay manual de marca con otros valores, actualiza solo `TEMA`.

## Script

El script está en `scripts/apply_veltis_theme.py` de esta skill (`${CLAUDE_SKILL_DIR}/scripts/apply_veltis_theme.py`). Para cambiar la paleta o los roles por elemento se edita ese archivo (`TEMA`, `WORD_ROLES`, `WORD_TABLA`, `PPT_ROLES`, `EXCEL`, `HTML_ROLES`, `DEFAULT_MAP`) y el cambio se publica con `publicar-plantillas-licitacion`.
