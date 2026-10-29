# Workflows — Evaluación de proyectos de licitación

Borrador del flujo general. Las etapas y responsables se completarán con las indicaciones detalladas que se entreguen en las próximas conversaciones.

## Paso 0 — Enrutamiento de la consulta

Antes de cualquier etapa, clasifica la solicitud recibida:

**Consulta a los documentos → skill `consultor-bases-tecnicas`**
Usar el Consultor de procesos cuando la pregunta pueda responderse con la documentación del proceso, por ejemplo:
- Requerimientos, cantidades, especificaciones, plazos, valores o condiciones exigidas por el cliente.
- Aclaraciones, preguntas y respuestas o adendas.
- Qué presentó la empresa propia (ECO o TEC) o cómo se compara con lo requerido.
- Identificación de la empresa o división solicitante y del origen de un documento.

**Proyecto nuevo o base compartida → skills de plantillas**
- Configurar este clon para una licitación nueva: `crear-proyecto-licitacion` (pregunta los datos del proceso y los perfiles, si el índice define alguno, y crea `proyecto/` desde `plantillas/`).
- Traer lo último publicado en GitHub: `importar-plantillas-licitacion`.
- Subir a GitHub los cambios globales hechos en este clon: `publicar-plantillas-licitacion`.
- Estas skills toman la lista de documentos solo de `docs/INDICE_PLANTILLAS.md`; no hay que nombrar documentos en la solicitud.

**Otras solicitudes → etapas de este flujo**
- Registrar o actualizar un proceso (Etapa 1).
- Análisis de bases para extraer requisitos y generar listados (Etapa 2).
- Resumen ejecutivo de una licitación (Etapa 2, skill `resumen-ejecutivo-licitacion`).
- Buscar o cotizar precios de ítems (Etapa 3, skill `buscar-cotizaciones`).
- Nómina técnica desde CVs (Etapa 3, skill `tec-nomina`, solo por invocación explícita).
- Evaluación, informe o decisión (Etapas 4 y 5).
- Presentación de comité o propuesta (Etapa 5, skill `plantilla-ppt-veltis`).
- Seguimiento de resultados (Etapa 6).

**Casos mixtos o ambiguos.** Si la solicitud combina consulta y acción (por ejemplo, "¿qué exige el cliente en camionetas y cotiza ese ítem?"), responde primero la consulta con el Consultor y luego ejecuta la acción. Si no queda claro, formula una sola pregunta antes de decidir.

**Confirmar la carpeta fuente.** El Consultor solo usa la carpeta del proceso activo, registrada en `proyecto/Proceso.md` (líneas "Carpeta fuente" y "Carpeta de contexto"). Si no está definida, pídela antes de responder.

**Leer el contexto del proyecto.** Antes de responder o ejecutar una etapa, considera `proyecto/Contexto_y_Acuerdos_del_Proyecto.md` (se carga solo a través de `CLAUDE.local.md`): sus acuerdos y criterios propios prevalecen sobre los supuestos generales. Si el archivo no existe, avisa y propón crearlo con `importar-plantillas-licitacion` (crea las plantillas `crear-si-falta` que falten) o configurar el proyecto con `crear-proyecto-licitacion`.

## Carpetas de trabajo: BD (referencias) y OUTPUT (entregables)

Ambas carpetas viven en la raíz de la **carpeta de contexto** del proceso, registrada en `proyecto/Proceso.md`. Por defecto es `proyecto/` dentro de este clon (`proyecto/BD`, `proyecto/OUTPUT`). Si el equipo trabaja el proceso en una carpeta compartida (por ejemplo `2.1. Estudio/` en OneDrive o SharePoint), la carpeta de contexto puede ser esa, y `crear-proyecto-licitacion` la agrega a `additionalDirectories` en `.claude/settings.local.json`. Si `BD/` u `OUTPUT/` no existen, crearlas al primer uso.

**BD — única fuente de lectura de referencias.**
- Toda referencia que se necesite leer (bases, anexos, aclaraciones, adendas, formularios, antecedentes) se lee **solo desde `BD/`, en formato Markdown**.
- Si la referencia necesaria es un PDF, Word, PowerPoint u otro documento ubicado en cualquier otra carpeta, primero se convierte a `.md` (skill `markitdown` o conversión equivalente que conserve títulos y tablas), se guarda en `BD/` con el mismo nombre base del original y recién entonces se lee desde ahí.
- Antes de convertir, revisar si ya existe el `.md` en `BD/`. Se reconvierte solo si el original es más reciente que el `.md` o si el usuario lo pide.
- El `.md` lleva al inicio una línea con el nombre y la ubicación del archivo original, para trazabilidad. Ante dudas de conversión (tablas, celdas combinadas), se verifica contra el original.
- No se leen referencias directamente desde otras carpetas, salvo para convertirlas a `BD/`.

**OUTPUT — destino de lo que Claude genera.**
- Todo documento nuevo creado en el proceso (informes, listados, planillas, resúmenes, borradores de consultas, etc.) se guarda en `OUTPUT/`.
- Lo que está en `OUTPUT/` **no se usa como referencia** para otras actividades.
- Excepción: si el usuario indica expresamente que un documento de `OUTPUT/` debe usarse como referencia, se crea su versión `.md` en `BD/` (con la línea de origen) y desde entonces se lee desde `BD/`.

**BD y OUTPUT nunca se publican.**
- El contenido de `BD/` y de `OUTPUT/` es propio de cada proceso: está en `.gitignore`, nunca se agrega a un commit, no se agrega a `docs/INDICE_PLANTILLAS.md` y no se copia a otros proyectos.
- Lo único que se comparte entre proyectos es esta regla (en este documento y en `CLAUDE.md`), no los archivos.

## Revisión de contexto del proyecto (al cierre de cada etapa y de cada consulta)

`proyecto/Contexto_y_Acuerdos_del_Proyecto.md` se crea vacío en todos los proyectos y guarda solo lo propio de este proceso. Al terminar cada etapa, y cada vez que el usuario fije algo en la conversación, preguntarse si hay algo que deba quedar registrado:

- **Sí corresponde si es:** un acuerdo o decisión, un criterio o supuesto que vale solo para este proyecto, una corrección del usuario a un dato o clasificación, una particularidad del cliente o del alcance, o una duda abierta relevante.
- **No corresponde si es:** una regla general válida para todos los proyectos (va al documento global que corresponda, se agrega al índice si es nuevo y se sube con `publicar-plantillas-licitacion`), un dato ya presente en los documentos del proceso, o un comentario pasajero.

Cómo registrarlo: proponer al usuario la entrada, en una línea, con la sección donde iría (Contexto, Acuerdos, Criterios o Pendientes) y fecha; escribirla recién cuando confirme (o si el usuario pidió expresamente "registra"). Si no hay nada que registrar, no decir nada. Nunca reescribir ni borrar entradas previas sin que el usuario lo pida. Este documento nunca se sube a GitHub.

## Flujo base (borrador)

### Etapa 1 — Recepción y registro del proceso
- Configurar el clon con `crear-proyecto-licitacion`: nombre, entidad, empresa operativa (Veltis, Berliam, Steel, Walvis o Quintrax), fechas clave, carpeta fuente y carpeta de contexto quedan en `proyecto/Proceso.md`.
- Guardar las Bases Técnicas y Administrativas en la carpeta fuente del proceso.
- Crear `BD/` y `OUTPUT/` en la carpeta de contexto si no existen.
- **Pendiente:** campos obligatorios adicionales del registro.

### Etapa 2 — Análisis de bases
- Convertir a `.md` en `BD/` las bases, aclaraciones y adendas que se vayan a usar, y leerlas desde ahí.
- Extraer requisitos técnicos, administrativos y económicos de las bases, considerando primero las aclaraciones y adendas.
- Identificar requisitos excluyentes y plazos.
- Si se pide, generar el resumen ejecutivo (`resumen-ejecutivo-licitacion`) y el borrador de consultas a partir de `docs/Consultas_Base.md`.
- **Pendiente:** plantilla de extracción de requisitos.

### Etapa 3 — Levantamiento de información
- Buscar y cotizar ítems con `buscar-cotizaciones` (BD PRECIOS → FSChile → mercado).
- Preparar la nómina técnica a partir de CVs (`tec-nomina`), si aplica.
- **Pendiente:** fuentes oficiales y responsables.

### Etapa 4 — Evaluación
- Aplicar criterios de evaluación técnica y económica.
- Registrar puntajes y justificación por criterio.
- **Pendiente:** criterios, ponderaciones y escala (ver `CLAUDE.md`).

### Etapa 5 — Informe y decisión
- Generar el informe de evaluación en el formato estándar y guardarlo en `OUTPUT/`.
- Si se requiere presentación de comité o propuesta, usar `plantilla-ppt-veltis`.
- Registrar la decisión (participar / no participar / observaciones) y el responsable de aprobación.
- **Pendiente:** formato del informe y niveles de aprobación.

### Etapa 6 — Seguimiento
- Registrar resultado de la adjudicación y lecciones aprendidas en `proyecto/Contexto_y_Acuerdos_del_Proyecto.md`.
- Si una lección aplica a todos los proyectos, proponer el cambio en el documento global correspondiente y publicarlo.
- **Pendiente:** indicadores a seguir en el panel de control.

## Registro de cambios
- Versión 1.0.0: borrador inicial creado en la primera sesión del proyecto.
- Versión 1.1.0: se agregó el Paso 0 de enrutamiento hacia el rol Consultor de procesos.
- Versión 2.0.0: el rol del Consultor pasó a ser la skill `consultor-bases-tecnicas` y se eliminó `Rol_Consultor_de_procesos.md`.
- 13-10-2026 (3): se agregó la lectura del contexto del proyecto en el Paso 0 y la sección "Revisión de contexto del proyecto" (al cierre de cada etapa) con el nuevo `Contexto_y_Acuerdos_del_Proyecto.md`.
- 13-10-2026 (2): se agregó al Paso 0 la ruta "Proyecto nuevo o plantillas" hacia las skills de crear, importar y publicar plantillas.
- Versión 3.0.0 (26-10-2026): se retira todo lo relacionado con costos, que pertenece a otro desarrollo.
- Versión 3.2.0 (29-10-2026, desde STL DCH ING Y SOPORTE INFRA): se agrega la sección "Carpetas de trabajo: BD y OUTPUT" y se ajustan las Etapas 1, 2 y 5.
- Versión 4.0.0 (29-10-2026): migración a repositorio de Claude Code en GitHub. La base compartida deja de vivir en OneDrive: se actualiza con `git pull` y se publica con commit y push. Lo propio de cada proceso vive en `proyecto/` (ignorado por git). La carpeta de contexto queda registrada en `proyecto/Proceso.md`. Se quita la referencia a `cotizacion-mercado-cl` (integrada en `buscar-cotizaciones`) y se agregan al flujo `resumen-ejecutivo-licitacion` y `plantilla-ppt-veltis`.
