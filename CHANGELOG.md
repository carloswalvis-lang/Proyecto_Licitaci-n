# Changelog

Versiones del conjunto de la base compartida (semver). La versión vigente está en `VERSION` y cada publicación se etiqueta en git como `vX.Y.Z`. La skill `publicar-plantillas-licitacion` agrega una entrada por publicación, con la fecha y el proyecto desde el que se publicó.

- **major**: cambia la estructura, los roles o se eliminan documentos.
- **minor**: se agregan o reemplazan reglas, criterios, procesos, documentos o skills.
- **patch**: correcciones de redacción.

## 4.0.0 — 2026-10-29 — CONTROL - PROYECTOS DE LICITACIONES
Migración a repositorio de Claude Code en GitHub.
- La base compartida deja de vivir en la carpeta Plantillas Licitaciones de OneDrive: se actualiza con `git pull` y se publica con commit y push.
- `Instrucciones.md` pasa a `CLAUDE.md`; `workflows.md`, `Habilidades.md`, `Consultas_Base.md` e `INDICE_PLANTILLAS.md` pasan a `docs/`.
- Lo propio de cada proceso vive en `proyecto/` (ignorado por git) y se carga con `CLAUDE.local.md`.
- `manifest.json` se reemplaza por `VERSION`, este archivo y las etiquetas de git. `Version_plantillas.md` desaparece: los perfiles pasan a `proyecto/Proceso.md`.
- Skills de plantillas reescritas para git. Las demás skills quedan sin rutas personales, sin conector de Microsoft 365 y sin herramientas de Cowork; las rutas de cada equipo van en `config/local.json`.
- Se incluyen la plantilla PPT Veltis (`plantillas/ppt/`) y `bd_precios.py` (`herramientas/bd_precios/`); los datos de BD PRECIOS siguen fuera del repo.
- No se incluyen `organigrama` (depende de un artefacto de claude.ai) ni `llenado-perfil-veltis` (desarrollo de costos).

## 3.2.0 — 2026-10-29 — STL DCH ING Y SOPORTE INFRA
Instrucciones y workflows agregan la regla de carpetas BD (referencias solo en .md, convirtiendo PDFs u otros documentos a BD) y OUTPUT (entregables, no se usan como referencia salvo indicación). El contenido de BD y OUTPUT nunca se publica ni se importa.

## 3.1.0 — 2026-10-26 — CONTROL - PROYECTOS DE LICITACIONES
Se agrega Consultas_Base.md (listado estándar de consultas base por categoría), global y en modo reemplazar.

## 3.0.0 — 2026-10-26 — CONTROL - PROYECTOS DE LICITACIONES
Se retira todo lo relacionado con costos, que pertenece a otro desarrollo: se eliminan de la carpeta y del índice los documentos de costos. Instrucciones y workflows se ajustan en consecuencia.

## 2.5.0 — 2026-10-26 — STL - DRT OBRAS MISCELANEAS
Actualización de documentos de la carpeta.

## 2.4.0 — 2026-10-13 — DET ASEO CALETONES
Nueva plantilla vacía Contexto_y_Acuerdos_del_Proyecto.md (global, crear-si-falta); workflows.md agrega la lectura del contexto del proyecto y la revisión de contexto al cierre de cada etapa.

## 2.3.0 — 2026-10-13 — DET ASEO CALETONES
Actualización de documentos de la carpeta.

## 2.2.0 — 2026-10-08 — DET ASEO CALETONES
Se agregó INDICE_PLANTILLAS.md (lista de documentos que publican e importan las skills, con ámbito y versión por documento).

## 2.1.0 — 2026-10-08 — CONTROL - PROYECTOS DE LICITACIONES
Habilidades.md: se agregó la sección Gestión de plantillas.

## 2.0.0 — 2026-10-08 — CONTROL - PROYECTOS DE LICITACIONES
El rol Consultor de procesos pasó a la skill consultor-bases-tecnicas.

## 1.0.0 — 2026-10-08 — CONTROL - PROYECTOS DE LICITACIONES
Versión inicial de la carpeta base.
