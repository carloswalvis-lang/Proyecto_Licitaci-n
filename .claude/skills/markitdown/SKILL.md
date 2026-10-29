---
name: markitdown
description: "Convierte archivos PDF, Word (.docx) y PowerPoint (.pptx) a Markdown con la librería MarkItDown de Microsoft y los deja en BD/ de la carpeta de contexto. Usa esta skill cuando el usuario diga \"ocupa markitdown\", \"usa markitdown\", \"convierte con markitdown\" o una variación similar, cuando entregue un PDF, DOCX o PPTX y pida pasarlo a Markdown o a texto plano, o cuando otra tarea necesite leer una referencia que aún no está en BD/."
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/convert.py *) Bash(python ${CLAUDE_SKILL_DIR}/scripts/convert.py *)
---

# MarkItDown — Convertidor a Markdown

Convierte archivos PDF, Word y PowerPoint a Markdown usando [MarkItDown](https://github.com/microsoft/markitdown) de Microsoft.

## Formatos soportados

| Extensión | Tipo de archivo |
|-----------|-----------------|
| `.pdf`    | PDF             |
| `.docx`   | Word            |
| `.pptx`   | PowerPoint      |

## Flujo de trabajo

### 1. Identificar el archivo de entrada

El archivo puede venir:
- **De la carpeta fuente del proceso** (línea "Carpeta fuente" de `proyecto/Proceso.md`).
- **Como ruta** que indique el usuario, dentro del repo o de una carpeta agregada con `/add-dir` o `additionalDirectories`.

Antes de convertir, revisa si ya existe el `.md` en `BD/`: reconvierte solo si el original es más reciente o si el usuario lo pide.

Si la extensión no es `.pdf`, `.docx` o `.pptx`, informa los formatos válidos y detente.

### 2. Convertir

Ejecuta el script incluido. Se encarga de verificar e instalar MarkItDown con sus extras (`markitdown[pdf,docx,pptx]`) si hace falta:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/convert.py" "<archivo_entrada>" "<carpeta de contexto>/BD/<nombre>.md" --origen
```

- Usa `python` si `python3` no existe (Windows).
- Por defecto el `.md` va a `BD/` de la carpeta de contexto (línea "Carpeta de contexto" de `proyecto/Proceso.md`; por defecto `proyecto/BD/`), con el mismo nombre base del original (`informe.docx` → `informe.md`).
- `--origen` agrega como primera línea el nombre y la ruta del original, como exige la regla de `BD/` en `docs/workflows.md`. Úsalo siempre que el destino sea `BD/`.
- Si MarkItDown no está disponible y no se puede instalar (sin acceso a internet), el script usa un respaldo con `python-docx`, `python-pptx` o `pdfplumber`/`pypdf`, según el formato. Informa al usuario que se usó el respaldo.

### 3. Entregar

- Si el usuario indicó otro destino, guárdalo ahí; si no, queda en `BD/`.
- Indica la ruta del `.md` generado y el método usado. Si el usuario lo pide, muestra un extracto.
- Ante dudas de conversión (tablas, celdas combinadas), verifica contra el original.

## Errores comunes

| Situación (código de salida) | Qué hacer |
|---|---|
| Archivo no encontrado (2) | Pedir que verifique la ruta o adjunte el archivo |
| Extensión no soportada (3) | Indicar los formatos válidos y detener |
| Sin MarkItDown ni respaldo disponible (4) | Explicar que falta MarkItDown y no se pudo instalar: instalarlo con `pip install "markitdown[pdf,docx,pptx]"` (o revisar el proxy o la red del equipo) |
| Error en la conversión (5) | Mostrar el error; sugerir verificar que el archivo no esté dañado ni protegido con contraseña |
| Contenido vacío (advertencia) | Probablemente es un PDF escaneado sin capa de texto; MarkItDown no hace OCR |

## Notas

- **No modificar el archivo original**: solo se lee.
- El Markdown refleja la estructura del documento (títulos, tablas, listas) en la medida en que MarkItDown la detecte.
- Para usarlo localmente en Windows: `conda activate markitdown` y luego `markitdown archivo.pdf -o archivo.md`.
