# Control de proyectos de licitación — Veltis Latam

Base de Claude Code para gestionar licitaciones: criterios, seguimiento, cotizaciones, nóminas técnicas y decisiones de evaluación.

Cada licitación es un **clon local** de este repositorio. Lo global (instrucciones, flujo, skills y plantillas) se versiona en GitHub y se comparte entre todos los proyectos. Lo propio de cada licitación vive en `proyecto/` y **nunca** se sube.

## Contexto de la organización
- Empresa principal: **Veltis**.
- Empresas operativas que también pueden aparecer en los proyectos: **Berliam**, **Steel**, **Walvis** y **Quintrax**.
- Idioma de trabajo: español.

## Preferencias de salida
- Botón de copiar solo para texto generado: cuando entregues texto para trasladar a otro documento, ponlo en un bloque cercado que contenga solo ese texto, sin elementos adicionales.

## Qué es global y qué es propio del proyecto

| Contenido | Ubicación | ¿Se sube a GitHub? |
|---|---|---|
| Instrucciones generales | `CLAUDE.md` | Sí, con `publicar-plantillas-licitacion` |
| Flujo, skills disponibles, consultas base e índice | `docs/` | Sí |
| Skills | `.claude/skills/` | Sí |
| Plantillas vacías y presentación Veltis | `plantillas/` | Sí |
| Herramientas (por ejemplo `bd_precios.py`) | `herramientas/` | Sí |
| Datos del proceso, contexto específico y acuerdos | `proyecto/` | **Nunca** |
| Referencias (`BD/`) y entregables (`OUTPUT/`) | raíz de la carpeta de contexto (por defecto `proyecto/`) | **Nunca** |
| Rutas y usuario de cada equipo | `config/local.json`, `CLAUDE.local.md`, `.claude/settings.local.json` | **Nunca** |

`.gitignore` excluye todo lo marcado como "Nunca". Aun así, antes de cualquier commit se revisa que no vaya contenido propio de un proceso (ver la skill de publicar).

## Al iniciar una sesión
1. Si no existe `proyecto/Proceso.md`, este clon aún no está configurado: ofrece `crear-proyecto-licitacion` antes de trabajar un proceso.
2. `CLAUDE.local.md` (lo crea `crear-proyecto-licitacion`) carga el proceso, el contexto específico y los acuerdos del proyecto. Sus acuerdos y criterios prevalecen sobre los supuestos generales, pero no sobre las bases, aclaraciones y adendas del cliente.
3. Las rutas de cada equipo (BD PRECIOS, FSChile, carpeta de cotizaciones) están en `config/local.json`. Si falta y una tarea las necesita, pide los datos y créalo a partir de `config/local.example.json`. Nunca escribas rutas personales en archivos versionados.

## Documentos globales
- La lista oficial de documentos compartidos está en **`docs/INDICE_PLANTILLAS.md`**. Es el único lugar donde se agregan, retiran o cambian de ámbito. Las skills de plantillas leen esa tabla y no llevan listas propias.
- Cada documento tiene un **ámbito**: `global` (todos los proyectos) o `perfil:<NOMBRE>` (solo proyectos que declaran ese perfil en la línea "Perfiles" de `proyecto/Proceso.md`). Hoy todos los documentos activos son `global`.
- Cada documento lleva su versión y fecha en el índice; las actualiza la skill de publicar. No editarlas a mano.
- **Proyecto nuevo:** `crear-proyecto-licitacion`. Pregunta los datos del proceso y los perfiles, crea `proyecto/` desde `plantillas/` y genera `CLAUDE.local.md`.
- **Traer lo último de GitHub:** `importar-plantillas-licitacion` (`git pull` controlado, sin tocar `proyecto/`).
- **Subir cambios globales:** `publicar-plantillas-licitacion`. Sube solo lo global que cambió, actualiza versiones, `CHANGELOG.md` y `VERSION`.
- **Documento nuevo compartido:** crearlo en `docs/` (o `plantillas/` si cada proyecto debe tener su copia) y agregar su fila al índice. Con eso las skills lo toman solas.
- **`proyecto/Contexto_y_Acuerdos_del_Proyecto.md`**: se crea vacío desde `plantillas/` y guarda el contexto y los acuerdos propios del proceso. Se lee antes de responder y se revisa al cierre de cada etapa (ver `docs/workflows.md`). Su contenido nunca se publica.
- `proyecto/Proceso.md`, `proyecto/Contexto_Especifico.md` y todo lo que haya en `proyecto/` son propios del proceso: nunca se publican ni se copian a otros proyectos.

## Reglas generales para Claude
1. Antes de responder sobre un proceso, considera los documentos activos del índice que apliquen (ámbito global o de sus perfiles) y los propios del proyecto en `proyecto/`.
2. Registra las decisiones y criterios que se acuerden en `proyecto/Contexto_y_Acuerdos_del_Proyecto.md`: propón la entrada al usuario y escríbela al confirmar.
3. Ante una licitación nueva, sigue el flujo de `docs/workflows.md`.
4. Cuando falte información para evaluar, indícalo explícitamente en vez de asumir valores.
5. Al crear un documento que deba compartirse entre proyectos, agrégalo a `docs/INDICE_PLANTILLAS.md` indicando su ámbito.
6. **Referencias solo desde `BD/`:** toda referencia se lee en `.md` desde la carpeta `BD/` de la carpeta de contexto. Si se necesita un PDF u otro documento de otra carpeta, se convierte primero a `.md` en `BD/` (skill `markitdown`) y se lee desde ahí.
7. **Entregables en `OUTPUT/`:** todo documento nuevo que Claude cree se guarda en `OUTPUT/` y no se usa como referencia para otras actividades, salvo que el usuario lo indique; en ese caso se crea su `.md` en `BD/`.
8. **Git:** no hagas commit, push ni cambies de rama fuera de las skills `importar-plantillas-licitacion` y `publicar-plantillas-licitacion`. Nunca agregues a git archivos de `proyecto/`, `BD/`, `OUTPUT/`, `config/local.json`, `CLAUDE.local.md` ni documentos de clientes, CVs o precios.
9. Cambios a documentos globales que solo valen para este proceso no se hacen en el documento global: van a `proyecto/Contexto_y_Acuerdos_del_Proyecto.md`.
10. Nunca escribas a mano en la base BD PRECIOS ni en las carpetas de FSChile: solo mediante las skills correspondientes.

## Pendiente de definir
Estos puntos siguen abiertos. No inventes valores: si una tarea los necesita, pregunta.
- [ ] Criterios de evaluación técnica y económica y sus ponderaciones.
- [ ] Escala de puntajes y umbrales de aprobación / descarte.
- [ ] Roles y responsables por etapa (quién revisa, quién aprueba).
- [ ] Formato estándar de informe de evaluación.
- [ ] Fuentes de información oficiales (portales, carpetas, bases).

## Flujo de trabajo
@docs/workflows.md
