# licitaciones-base — Control de proyectos de licitación (Claude Code)

Base de Claude Code para trabajar licitaciones de Veltis Latam (Veltis, Berliam, Steel, Walvis, Quintrax): instrucciones, flujo de evaluación, skills y plantillas compartidas.

**Modelo de trabajo:** un solo repositorio en GitHub. Cada licitación es un **clon local** de este repo. En el clon se trabaja el proceso; lo propio de la licitación queda en `proyecto/` (ignorado por git) y las mejoras globales se suben al repo para que las reciban los demás clones.

```
GitHub: licitaciones-base  (instrucciones, skills, plantillas)
   │  git clone / importar          ▲  publicar (solo lo global)
   ▼                                │
Clon "LIC Aseo Caletones"     Clon "LIC DRT Obras"     ...
   └── proyecto/  (propio, nunca se sube)
```

## Requisitos (una vez por equipo)
- [Claude Code](https://code.claude.com) (terminal, VS Code o app de escritorio).
- Git y Python 3. En Windows, Git for Windows (Claude Code usa su Git Bash).
- Acceso al repositorio privado en GitHub (y, opcional, `gh` autenticado si se publicará por pull request).
- Plugin de documentos (Word, Excel, PowerPoint, PDF), desde Claude Code:
  ```
  /plugin marketplace add anthropics/skills
  /plugin install document-skills@anthropic-agent-skills
  ```
- Fuente Overpass instalada (gratis en Google Fonts) para ver bien los archivos con estilo Veltis.

## Subir esta base a GitHub (una sola vez)
1. Crear en GitHub un repositorio **privado** vacío, por ejemplo `veltis/licitaciones-base`.
2. En esta carpeta:
   ```
   git init -b main
   git add .
   git commit -m "Base de licitaciones 4.0.0"
   git remote add origin https://github.com/<organizacion>/licitaciones-base.git
   git push -u origin main
   git tag v4.0.0 && git push origin v4.0.0
   ```
3. Antes del primer commit, `git status` no debe mostrar nada de `proyecto/`, `config/local.json` ni documentos de clientes.

## Empezar una licitación nueva
1. Clonar en una carpeta local, **fuera de OneDrive** (OneDrive y la carpeta `.git` se llevan mal):
   ```
   git clone https://github.com/<organizacion>/licitaciones-base.git "LIC <nombre corto>"
   cd "LIC <nombre corto>"
   ```
2. Copiar `config/local.example.json` como `config/local.json` y completar tus rutas (BD PRECIOS, FSChile, carpeta de cotizaciones). Si no lo haces, Claude te las pedirá la primera vez que las necesite.
3. Abrir Claude Code en esa carpeta y ejecutar `/crear-proyecto-licitacion`. Pregunta los datos del proceso, crea `proyecto/` y `CLAUDE.local.md`.
4. Dejar las bases y antecedentes en la carpeta fuente (por defecto `proyecto/fuentes/`, o una carpeta compartida que indiques al crear el proyecto).

## Día a día
| Quiero… | Uso |
|---|---|
| Traer las mejoras que otros publicaron | `/importar-plantillas-licitacion` |
| Compartir una mejora global (regla, consulta base, skill) | `/publicar-plantillas-licitacion` |
| Preguntar algo de las bases | Preguntar directo (skill `consultor-bases-tecnicas`) |
| Resumen ejecutivo | `/resumen-ejecutivo-licitacion` |
| Cotizar ítems | `/buscar-cotizaciones` |
| Nómina técnica desde CVs | `/tec-nomina` |
| Presentación de comité o propuesta | Pedir la presentación (skill `plantilla-ppt-veltis`) |

Detalle de cada skill en `docs/Habilidades.md` y del flujo en `docs/workflows.md`.

## Estructura
| Ruta | Contenido | ¿Se versiona? |
|---|---|---|
| `CLAUDE.md` | Instrucciones generales (Claude Code lo carga al iniciar e importa `docs/workflows.md`). | Sí |
| `docs/` | Flujo, skills disponibles, consultas base e índice de plantillas. | Sí |
| `.claude/skills/` | Skills de licitación. | Sí |
| `.claude/settings.json` | Permisos compartidos (lecturas de git permitidas; push forzado, `git clean` y `git add -f` bloqueados). | Sí |
| `plantillas/` | Plantillas vacías que se copian a `proyecto/` y la presentación Veltis. | Sí |
| `herramientas/bd_precios/` | `bd_precios.py` y sus guías. Los CSV de la base no. | Sí |
| `VERSION`, `CHANGELOG.md` | Versión del conjunto e historial. Los mantiene la skill de publicar. | Sí |
| `config/local.example.json` | Ejemplo de configuración local. | Sí |
| `proyecto/` | Ficha del proceso, contexto, acuerdos, `BD/`, `OUTPUT/`, fuentes. | **No** |
| `config/local.json`, `CLAUDE.local.md`, `.claude/settings.local.json` | Rutas y configuración de cada equipo y clon. | **No** |

## Confidencialidad
- El repositorio debe ser **privado**.
- Nunca se suben bases de clientes, CVs, precios de proveedores ni datos personales. `.gitignore` excluye `proyecto/`, `BD/`, `OUTPUT/` y los formatos de documentos típicos fuera de `plantillas/`, y la skill de publicar revisa el commit antes de subirlo. La revisión final es de quien publica.
- Las tablas de BD PRECIOS (arriendo, MO spot) contienen sueldos y precios: siguen en su carpeta compartida, no en el repo.

## Qué cambió respecto de la versión en OneDrive (3.2.0)
| Antes (proyecto de Claude + OneDrive) | Ahora (Claude Code + GitHub) |
|---|---|
| Carpeta `Plantillas Licitaciones` en OneDrive | Este repositorio |
| `Instrucciones.md` | `CLAUDE.md` |
| `claude/*.md` en el proyecto de Claude | `docs/*.md` en el repo |
| `manifest.json` | `VERSION`, `CHANGELOG.md` y etiquetas `vX.Y.Z` |
| `Version_plantillas.md` | La versión la da git; los perfiles van en `proyecto/Proceso.md` |
| Importar con el conector de Microsoft 365 | `git pull` controlado |
| Publicar copiando a OneDrive | Commit + push (o pull request) |
| Rutas `C:\Users\carlos.armas\...` dentro de las skills | `config/local.json` de cada equipo |
| `project_read` / `project_write` | Archivos en `proyecto/`, cargados por `CLAUDE.local.md` |

## Pendientes
Los criterios de evaluación, ponderaciones, roles y formato de informe aún no están definidos (ver "Pendiente de definir" en `CLAUDE.md`).
