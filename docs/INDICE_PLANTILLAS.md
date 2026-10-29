# Índice de plantillas

Único documento que define qué archivos forman la base compartida y cómo los tratan las skills `crear-proyecto-licitacion`, `importar-plantillas-licitacion` y `publicar-plantillas-licitacion`. Para agregar, retirar o cambiar un documento, se edita solo esta tabla; las skills no se tocan y no llevan listas propias de documentos.

La base vive en el repositorio de GitHub. Cada licitación es un clon local: lo que está en esta tabla se versiona y se comparte; lo que está en `proyecto/` es propio del clon y nunca se sube.

## Documentos

| Archivo (ruta en el repo) | Destino en el proyecto | Ámbito | Modo | Estado | Versión | Actualizado | Descripción |
|---|---|---|---|---|---|---|---|
| docs/INDICE_PLANTILLAS.md | — | global | reemplazar | activo | — | — | Este índice. Se publica siempre; no lleva versión propia. |
| CLAUDE.md | — | global | reemplazar | activo | 4.0.0 | 2026-10-29 | Instrucciones generales (antes `Instrucciones.md`). Claude Code lo carga al iniciar. |
| docs/workflows.md | — | global | reemplazar | activo | 4.0.0 | 2026-10-29 | Flujo de evaluación y enrutamiento de consultas. |
| docs/Habilidades.md | — | global | reemplazar | activo | 4.0.0 | 2026-10-29 | Skills disponibles y su uso. |
| docs/Consultas_Base.md | — | global | reemplazar | activo | 3.1.0 | 2026-10-26 | Listado estándar de consultas base para procesos de licitación, por categoría. |
| .claude/skills/ | — | global | reemplazar | activo | 4.0.0 | 2026-10-29 | Skills de licitación (detalle en `docs/Habilidades.md`). Una sola fila para toda la carpeta. |
| herramientas/ | — | global | reemplazar | activo | 4.0.0 | 2026-10-29 | Herramientas compartidas: `bd_precios/bd_precios.py` y sus guías. Los datos de la base no se versionan. |
| plantillas/ppt/ | — | global | reemplazar | activo | 4.0.0 | 2026-10-29 | Plantilla Licitaciones Veltis (.potx y .pptx) que usa `plantilla-ppt-veltis`. |
| plantillas/Contexto_y_Acuerdos_del_Proyecto.md | proyecto/Contexto_y_Acuerdos_del_Proyecto.md | global | crear-si-falta | activo | 3.0.0 | 2026-10-26 | Plantilla vacía de contexto y acuerdos propios de cada proyecto. El repo guarda solo la plantilla vacía. |
| plantillas/Contexto_Especifico.md | proyecto/Contexto_Especifico.md | global | crear-si-falta | activo | 4.0.0 | 2026-10-29 | Plantilla de definiciones, supuestos y decisiones propias del proyecto (antes estaba escrita dentro de la skill de crear). |
| plantillas/Proceso.md | proyecto/Proceso.md | global | crear-si-falta | activo | 4.0.0 | 2026-10-29 | Ficha del proceso: datos, perfiles, carpeta fuente y carpeta de contexto. La completa `crear-proyecto-licitacion`. |

`—` en Versión significa "sin versión propia" (solo el índice) o "aún sin publicar".

## Perfiles disponibles

Un perfil agrupa documentos que solo aplican a cierto tipo de proyecto. Un perfil nuevo se crea escribiéndolo en la columna Ámbito (y, si se quiere, describiéndolo aquí); no requiere cambiar skills.

| Perfil | Para qué proyectos | Documentos que aporta |
|---|---|---|
| — | Por ahora no hay documentos con ámbito de perfil: todos los activos son `global`. | — |

## Cómo se lee la tabla
- **Archivo (ruta en el repo):** ruta relativa a la raíz del repositorio. Una ruta que termina en `/` representa toda la carpeta.
- **Destino en el proyecto:** solo para el modo `crear-si-falta`: dónde se crea la copia propia del proyecto (siempre dentro de `proyecto/`).
- **Ámbito:** a qué proyectos aplica el documento.
  - `global`: a todos los proyectos.
  - `perfil:<NOMBRE>`: solo a proyectos que declaran ese perfil en la línea "Perfiles" de `proyecto/Proceso.md`. El archivo existe en todos los clones (git trae todo), pero Claude solo lo usa en los proyectos de ese perfil y la skill de publicar no toca sus filas desde otros proyectos.
- **Modo:**
  - `reemplazar`: el archivo se usa directamente desde el repo y se actualiza con `git pull` (skill de importar). No se edita para un solo proyecto: lo propio va a `proyecto/`.
  - `crear-si-falta`: el archivo del repo es una plantilla vacía. Al crear el proyecto (o al importar, si falta) se copia a su destino en `proyecto/`; si ya existe, no se toca. Al publicar, se sube solo la plantilla vacía, nunca la copia del proyecto.
- **Estado:**
  - `activo`: forma parte de la base.
  - `retirado`: ya no se usa; las skills no borran nada, solo avisan. Para quitar el archivo del repo se hace un commit explícito con la skill de publicar.
- **Versión y Actualizado:** versión (semver) del conjunto en que el documento cambió por última vez y la fecha de ese cambio. La skill de publicar las actualiza sola; no se editan a mano.

## Cómo procesan las skills este índice (contrato)

**Qué filas se consideran.** Una fila entra si su Estado es `activo` y su Ámbito es `global` o un perfil que el proyecto declara en `proyecto/Proceso.md`. Las filas de otros perfiles no se modifican. Las filas `retirado` se avisan, nunca se borran.

**Crear** (`crear-proyecto-licitacion`): copia cada fila `crear-si-falta` en alcance a su destino en `proyecto/` (si no existe), completa `proyecto/Proceso.md` con los datos del proceso y genera `CLAUDE.local.md`.

**Importar** (`importar-plantillas-licitacion`):
1. `git fetch` y muestra lo que llegó (`VERSION`, `CHANGELOG.md` y archivos cambiados).
2. Si hay cambios locales sin publicar en archivos versionados, pregunta antes: publicar primero, conservarlos (rebase con autostash) o descartarlos.
3. `git pull` (solo avance rápido o rebase; nunca merge silencioso con conflictos).
4. Crea las plantillas `crear-si-falta` en alcance que falten en `proyecto/`. Nunca toca las que ya existen.

**Publicar** (`publicar-plantillas-licitacion`):
1. Detecta los archivos versionados que cambiaron (y los nuevos sin seguimiento fuera de `proyecto/`).
2. Verifica que nada propio del proceso vaya en el commit y que las plantillas `crear-si-falta` sigan vacías.
3. Sube la versión del conjunto (`VERSION`), actualiza Versión y Actualizado de las filas que cambiaron, agrega la entrada en `CHANGELOG.md` y en el registro de cambios de este índice.
4. Commit, `git pull --rebase`, push (o rama + pull request, según `config/local.json`) y etiqueta `vX.Y.Z`.

**Qué debe pasar cuando se agrega un documento nuevo.** Se agrega su fila aquí (con ruta, ámbito y modo) y se crea el archivo en el repo. La próxima publicación lo sube; la próxima importación lo trae a los demás clones (y, si es `crear-si-falta`, crea su copia en `proyecto/`). Si la skill de publicar encuentra un archivo nuevo fuera de `proyecto/` que no está cubierto por una fila, pregunta si debe agregarse.

## Fuera del índice (por diseño)
- Todo `proyecto/`: `Proceso.md`, `Contexto_Especifico.md`, `Contexto_y_Acuerdos_del_Proyecto.md` con contenido, `cotizaciones/` y cualquier documento propio del proceso. Está en `.gitignore`.
- Las carpetas de trabajo `BD/` y `OUTPUT/` de cada proceso (ver `docs/workflows.md`), estén dentro de `proyecto/` o en una carpeta de contexto externa.
- La configuración local: `config/local.json`, `CLAUDE.local.md` y `.claude/settings.local.json`.
- Los datos de BD PRECIOS (CSV): viven en la carpeta configurada en `config/local.json`, no en el repo.
- `VERSION` y `CHANGELOG.md`: los mantiene la skill de publicar; no son plantillas.
- El rol del Consultor de procesos: vive en la skill `consultor-bases-tecnicas`.

## Registro de cambios del índice
- 08-10-2026: versión inicial del índice.
- 08-10-2026: se agregaron las columnas Ámbito, Versión y Actualizado.
- 13-10-2026: se agregan las secciones "Perfiles disponibles", "Cómo procesan las skills este índice" y "Formatos que las skills leen y escriben".
- 13-10-2026: se agrega Contexto_y_Acuerdos_del_Proyecto.md (global, crear-si-falta).
- 13-10-2026: publicación del conjunto 2.4.0.
- 26-10-2026: publicación del conjunto 3.0.0: se retira todo lo relacionado con costos, que pertenece a otro desarrollo.
- 26-10-2026: publicación del conjunto 3.1.0: se agrega Consultas_Base.md (global, reemplazar).
- 29-10-2026: publicación del conjunto 3.2.0 desde STL DCH ING Y SOPORTE INFRA: regla de carpetas `BD/` y `OUTPUT/`.
- 29-10-2026: conjunto 4.0.0, migración a GitHub. La columna "Archivo" pasa a ser la ruta en el repo y "Ruta en el proyecto" pasa a "Destino en el proyecto" (solo para `crear-si-falta`). `Instrucciones.md` pasa a `CLAUDE.md`. Se agregan las filas de skills, herramientas, plantilla PPT, `Contexto_Especifico.md` y `Proceso.md`. Se eliminan `manifest.json` (reemplazado por `VERSION`, `CHANGELOG.md` y etiquetas de git) y `Version_plantillas.md` (los perfiles pasan a `proyecto/Proceso.md`; la versión la da git).
