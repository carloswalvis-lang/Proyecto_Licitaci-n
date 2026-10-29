---
name: tec-nomina
description: "Procesa CVs de postulantes contra las Bases Técnicas (BBTT) de un proceso o licitación, y llena una nómina de personal técnico directamente en el Excel de la misma carpeta. Se ejecuta ÚNICAMENTE cuando el usuario invoca explícitamente /tec-nomina — no se activa automáticamente porque el usuario mencione CVs, currículums, nóminas o un Excel."
disable-model-invocation: true
---

# /tec-nomina — Nómina técnica de postulantes vs. Bases Técnicas

## Qué hace

Este skill arma la "nómina de personal" que se anexa a una propuesta técnica o licitación: toma los CVs de los postulantes a un cargo, los compara contra las Bases Técnicas (BBTT) del proceso, y deja una fila por candidato en el Excel de la carpeta, con 11 columnas fijas listas para revisar y presentar.

Solo se ejecuta cuando el usuario invoca `/tec-nomina` explícitamente. Si en otra conversación alguien sube CVs o pide "arma una nómina" sin invocar el comando, no actives este skill por tu cuenta — esa es una tarea distinta hasta que el usuario lo pida por nombre.

## Paso 0: Ubicar la carpeta de trabajo

El usuario llama a este skill estando sobre un Excel (o una carpeta que contiene un Excel). Esa carpeta es la fuente de todo:

- Usa la carpeta que indique el usuario o, si no indica ninguna, la carpeta fuente del proceso (línea "Carpeta fuente" de `proyecto/Proceso.md`). Lista el contenido primero, excluyendo `.IGNORE` y `OUTPUT/`.
- Si la carpeta está fuera del repo y de las carpetas permitidas, pide al usuario que la agregue con `/add-dir` antes de seguir.
- Si hay más de un `.xlsx` candidato y no es obvio cuál es el destino, pregunta cuál usar antes de seguir — escribir en el archivo equivocado es más costoso que una pregunta.

## Paso 1: Verificar que estén los insumos mínimos antes de procesar nada

Antes de leer o calcular cualquier cosa, confirma que la carpeta tiene lo necesario. Esto evita procesar a medias y generar resultados basura.

Busca por nombre de archivo (sin distinguir mayúsculas ni tildes):

- **Archivo de Bases Técnicas (BBTT):** el nombre contiene algo como "bbtt", "bases tecnicas", "terminos de referencia", "tdr" o "especificaciones tecnicas".
- **CVs:** un archivo por candidato, con nombres que contienen "cv", "curriculum", "currículo" u "hoja de vida". Formatos esperados: PDF o Word (.docx).

Si falta alguno de los dos grupos, **detente y avisa con un mensaje claro**, por ejemplo:

- "No encontré un archivo de Bases Técnicas (BBTT) en esta carpeta. Necesito ese documento para saber el cargo y los requisitos exigidos — ¿puedes indicarme cuál archivo es o en qué carpeta está?"
- "No encontré archivos de CV en esta carpeta (busqué nombres con 'cv', 'curriculum' u 'hoja de vida'). ¿Los postulantes están en otra carpeta o con otro nombre?"

No sigas adivinando ni proceses con supuestos — sin BBTT no hay contexto para evaluar cumplimiento, y sin CVs no hay nada que procesar.

Si el nombre del archivo no es concluyente (por ejemplo, todos los archivos se llaman "Documento1.pdf"), ábrelos y decide por contenido: la BBTT es un documento normativo/técnico del proceso (menciona el cargo, requisitos, funciones); un CV es la trayectoria de una persona.

## Paso 2: Leer la BBTT y definir el contexto del proceso

Lee la BBTT desde su `.md` en `BD/` de la carpeta de contexto (regla de `docs/workflows.md`). Si aún no está convertida, conviértela primero con la skill `markitdown` a `BD/`. De ahí identifica:

- **CARGO A DESEMPEÑAR**: el nombre exacto del cargo que se está licitando/contratando.
- **Requisitos de experiencia**: años mínimos de experiencia general y/o específica exigidos, si la BBTT los indica.
- **Funciones específicas del cargo**: qué se espera que la persona haga en el servicio (esto es lo que define qué cuenta como "experiencia específica" más adelante).
- **Formación o certificaciones exigidas**, si las hay.

Este contexto se usa para dos cosas: (a) filtrar y resumir la información de cada CV para que sea relevante al cargo, y (b) evaluar objetivamente si cada candidato cumple o no con lo exigido. Si la BBTT no da un mínimo numérico de años, evalúa cumplimiento en base a la coherencia entre la trayectoria del candidato y las funciones descritas.

## Paso 3: Procesar cada CV

Extrae el texto de cada CV (PDF o Word) y completa estos 11 campos. Los primeros 10 van siempre en este orden exacto; toda la información de resumen debe estar filtrada y ser altamente relevante al CARGO A DESEMPEÑAR — no copies el CV completo, resume con criterio.

| # | Campo | Cómo se obtiene |
|---|-------|------------------|
| 1 | NOMBRE COMPLETO | Tal como aparece en el CV. |
| 2 | CARGO A DESEMPEÑAR | El mismo para todos los CVs de esta corrida: el que identificaste en la BBTT (Paso 2). |
| 3 | TÍTULO PROFESIONAL | El título universitario de mayor nivel que tenga el candidato. |
| 4 | A (años exp. general) | Años totales de experiencia general, contados desde la fecha en que obtuvo su título profesional hasta hoy (o hasta el fin de su último trabajo si ya no está activo). Solo el número entero (ej: 5). |
| 5 | B (años exp. específica) | Años totales de experiencia directamente relacionada con las funciones del CARGO A DESEMPEÑAR según la BBTT. Solo el número entero (ej: 3). Nunca puede ser mayor que A. |
| 6 | CURSOS DE ESPECIALIZACIÓN | Certificaciones, diplomados o postítulos relevantes al cargo, separados por comas. Si no hay ninguno relevante, usa "N/A". |
| 7 | EXPERIENCIA GENERAL (RESUMEN) | Listado cronológico de las experiencias relevantes, cada una separada por punto y coma (;). Cada experiencia debe incluir: fechas (ej: 2018-2022 o 2018-Actual); empresa/mandante; cargo; funciones relevantes al rol general. |
| 8 | EXPERIENCIA ESPEC (RESUMEN) | Resumen (máx. ~250 palabras) de la experiencia directamente ligada a las funciones específicas del cargo, según la BBTT. |
| 9 | OTRAS EXPERIENCIA GENERAL (RESUMEN) | Otra experiencia que aporte valor (docencia, publicaciones, gremios, etc.). Si no hay, usa "NA". |
| 10 | ANTECEDENTES ACADÉMICOS | Estudios de postgrado con año y organización acreditadora (ej: "2025 Magíster, Universidad USACH; 2020 Doctorado, Universidad de Viña"). Si no tiene postgrados, deja el grado universitario base con su año. |
| 11 | CUMPLE BBTT | Ver más abajo. |

### CUMPLE BBTT (columna 11)

Evalúa de forma objetiva si el candidato cumple **estrictamente** los requisitos de la BBTT (años de experiencia general/específica, título exigido, funciones esperadas). Escribe un veredicto corto en la celda:

- Si cumple: `✔️ Cumple` (puedes agregar una frase muy breve si aporta, ej: `✔️ Cumple (supera años mínimos)`).
- Si NO cumple estrictamente algún requisito: empieza con `✖️` y en pocas palabras di por qué (ej: `✖️ No cumple — 4 años exp. específica, se exigen 6`).

No suavices el veredicto para quedar bien con el candidato: el objetivo de esta columna es que quien arma la propuesta detecte de inmediato a quién le falta algo antes de presentar la nómina.

## Paso 4: Escribir los resultados en el Excel

El Excel encontrado en el Paso 0 es el destino final — no generes un archivo aparte.

1. Si ya existe una hoja con estos 11 encabezados exactos, agrega las filas nuevas al final de esa tabla.
2. Si no existe, crea una hoja (o usa la hoja activa si está vacía) y escribe primero la fila de encabezados, luego las filas de datos.
3. Antes de agregar un candidato, revisa si su NOMBRE COMPLETO ya está en la tabla (comparación sin distinguir mayúsculas/espacios). Si ya está, no lo dupliques — sáltalo y menciónalo en tu resumen final.
4. Nunca borres ni reordenes filas que ya estaban en el Excel; este skill solo agrega.

Trabaja directamente sobre el archivo en su ruta. El Excel debe estar **cerrado** al momento de escribir (si está abierto, el usuario perderá el cambio al guardar encima): dilo antes de escribir. Los CVs se leen directo desde su carpeta; no se copian a `BD/` ni al repo, porque contienen datos personales.

Usa el script incluido (ajusta las rutas y guarda antes las filas ya calculadas en un JSON temporal, fuera del repo y de las carpetas del proceso):

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/write_nomina.py" "ruta/Nomina.xlsx" "Nomina" "rows.json"
```

Donde `rows.json` es una lista de objetos con las 11 llaves de `HEADERS` (definidas en el script). Responde con un JSON con las filas agregadas y los duplicados saltados. Borra el JSON temporal al terminar: contiene datos personales. Si `openpyxl` no está instalado en ese entorno, instálalo (`pip install openpyxl` o, en el shell local del usuario, según lo que permita su conexión de red) antes de correr el script.

Para extraer texto de los CVs y la BBTT, usa `pdfplumber` (o `PyPDF2`) para PDF y `python-docx` para `.docx`; instálalos si faltan.

## Paso 5: Si no puedes escribir en el Excel

Puede pasar que el archivo esté abierto y bloqueado, que no haya Excel disponible en la carpeta, o que el usuario solo haya indicado CVs sin un Excel de destino. En ese caso, no te bloquees: entrega el mismo resultado como texto plano en el chat, listo para pegar.

Formato de respaldo: una línea por candidato, con los 11 campos (mismo orden de la tabla, sin encabezados) separados estrictamente por `/`. Así el usuario lo puede pegar en Excel y usar "Texto en columnas" separando por `/`.

Ejemplo de una línea:

```
Carlos Muñoz Rojas/Líder de Proyecto BIM/Arquitecto/15/8/Certificación Autodesk Professional, Diplomado en Gestión de la Construcción/2018-Actual; Constructora Zenith; Jefe de Proyectos; Liderazgo de equipos multidisciplinarios, coordinación BIM nivel 300, gestión de presupuesto y plazos en obras viales.; 2010-2018; Estudio de Arquitectura Alpha; Arquitecto Senior; Diseño arquitectónico y supervisión de proyectos residenciales, utilizando Revit y coordinación de modelos estructurales./8 años de experiencia liderando la implementación y estandarización de flujos de trabajo BIM para proyectos de infraestructura civil mayor y sistemas MEP en entornos ISO 19650./Miembro activo del Colegio de Arquitectos; Publicación en Revista de Construcción./Magíster/✔️ Cumple
```

## Paso 6: Resumen final para el usuario

No repitas toda la tabla en el chat si ya quedó escrita en el Excel — el usuario la va a abrir ahí. Cierra con un resumen breve: cuántos CVs procesaste, para qué cargo, cuántas filas nuevas agregaste (y a qué hoja/archivo), cuántos candidatos no cumplen estrictamente (✖️) y sus nombres, y si saltaste algún duplicado.