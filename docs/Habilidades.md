# Habilidades — Skills disponibles en este repositorio

Las skills viven en `.claude/skills/` y Claude Code las carga solas al abrir el repositorio. Se invocan escribiendo `/<nombre>` o, salvo excepción indicada, Claude las usa cuando la solicitud coincide con su descripción.

## Skills de apoyo a licitaciones (Veltis)
| Skill | Uso en este proyecto |
|---|---|
| `consultor-bases-tecnicas` | Responder consultas sobre requerimientos, aclaraciones, adendas y ofertas ECO/TEC a partir de las referencias del proceso en `BD/`. |
| `resumen-ejecutivo-licitacion` | Resumen ejecutivo gerencial (Word) a partir de bases, anexos y consultas; se guarda en `OUTPUT/`. |
| `tec-nomina` | Procesar CVs de postulantes contra las Bases Técnicas (BBTT) y llenar la nómina de personal técnico en el Excel del proceso. Se activa solo con `/tec-nomina`. |
| `buscar-cotizaciones` | Cotizar, buscar y cargar precios con la base general BD PRECIOS (materiales, insumos, servicios, arriendo de equipos y MO spot): base → FSChile → mercado. |
| `actualizar-excel-respaldos` | Generar el Excel de cotizaciones del proyecto (hojas Listado y ECO) desde BD PRECIOS y copiar los respaldos de FSChile a la carpeta RESPALDO. Solo con `/actualizar-excel-respaldos`. |

## Skills de formato de salida
| Skill | Uso |
|---|---|
| `estilo-veltis-ms365` | Aplicar el estilo corporativo Veltis a Word, PowerPoint, Excel y páginas HTML. Trae su script en `scripts/apply_veltis_theme.py`. |
| `plantilla-ppt-veltis` | Antes de crear una presentación de licitación, comité o propuesta, ofrecer la Plantilla Licitaciones Veltis de `plantillas/ppt/`. |
| `markitdown` | Convertir PDF, Word o PowerPoint de bases y ofertas a Markdown en `BD/`. |
| `docx` / `xlsx` / `pptx` / `pdf` | No vienen en el repo. Se instalan una vez por equipo con el plugin oficial: `/plugin marketplace add anthropics/skills` y luego `/plugin install document-skills@anthropic-agent-skills`. |

## Gestión de la base compartida (GitHub)
| Skill | Uso |
|---|---|
| `crear-proyecto-licitacion` | Configurar este clon para una licitación: pregunta los datos del proceso y los **perfiles** (si el índice define alguno), crea `proyecto/` desde `plantillas/`, genera `CLAUDE.local.md` y, si la carpeta de contexto es externa, la agrega a `.claude/settings.local.json`. |
| `importar-plantillas-licitacion` | Traer lo último publicado en GitHub (`git fetch` + `git pull` controlado), mostrar qué cambió y crear las plantillas `crear-si-falta` que falten en `proyecto/`. Nunca toca `proyecto/`. |
| `publicar-plantillas-licitacion` | Subir a GitHub solo los cambios globales de este clon: verifica que no vaya nada propio del proceso, sube versión (`VERSION`, índice, `CHANGELOG.md`), hace commit y push (o pull request) y etiqueta la versión. |

**Cómo deciden qué mover estas skills:**
- La lista de documentos sale solo de `docs/INDICE_PLANTILLAS.md`; nunca de una lista fija dentro de la skill. Un documento nuevo se agrega editando únicamente el índice.
- Un documento aplica si su estado es `activo` y su ámbito es `global` o un perfil declarado en la línea "Perfiles" de `proyecto/Proceso.md`.
- Todo lo que está en `proyecto/` (y en `BD/` y `OUTPUT/`) nunca se sube: está en `.gitignore` y la skill de publicar lo verifica antes del commit.
- Orden recomendado en un clon nuevo: `crear-proyecto-licitacion`. Para recibir cambios de otros proyectos: `importar-plantillas-licitacion`. Para compartir cambios: `publicar-plantillas-licitacion`.

## Skills que no se incluyeron en esta base
| Skill | Motivo |
|---|---|
| `organigrama` | Depende de un artefacto de claude.ai ("Organigrama Profesional") y su base de datos, que no existen en Claude Code. Se puede reescribir para generar el organigrama como archivo en `OUTPUT/`. |
| `llenado-perfil-veltis` | Pertenece al desarrollo de costos, que se retiró de esta base en la versión 3.0.0. |
| `cotizacion-mercado-cl` | Ya no existe como skill separada: su función está en `buscar-cotizaciones` (FASE 3B). |
| `deep-research`, `dataviz` | Son skills de Cowork / claude.ai; no forman parte de Claude Code. |

## Pendiente
- [ ] Confirmar qué skills se usarán en cada etapa del flujo (ver `docs/workflows.md`).
- [ ] Identificar si se necesitan skills nuevas (por ejemplo, evaluación económica, informe de adjudicación u organigrama en archivo).
