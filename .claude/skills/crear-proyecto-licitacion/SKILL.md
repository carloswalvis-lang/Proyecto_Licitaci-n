---
name: crear-proyecto-licitacion
description: Configura este clon del repositorio para una licitación nueva — pregunta los datos del proceso y los perfiles, crea proyecto/ desde las plantillas del índice, genera CLAUDE.local.md y registra la carpeta fuente y la carpeta de contexto. Usar cuando el usuario pida crear, iniciar o configurar un proyecto de licitación.
---

# Crear proyecto de licitación

Prepara **este clon** del repositorio para trabajar una licitación. No crea repositorios ni clones: el usuario ya clonó la base (ver `README.md`) y abrió Claude Code en esa carpeta. Todo lo que crea esta skill queda en archivos ignorados por git (`proyecto/`, `CLAUDE.local.md`, `.claude/settings.local.json`), así que nunca se sube a GitHub.

Los documentos se dividen en dos grupos:
- **Globales:** los que lista `docs/INDICE_PLANTILLAS.md` en modo `reemplazar`. Se usan directo desde el repo; esta skill no los copia.
- **Propios del proyecto:** las filas en modo `crear-si-falta` del índice (por ejemplo `Proceso.md`, `Contexto_Especifico.md`, `Contexto_y_Acuerdos_del_Proyecto.md`). Se copian desde `plantillas/` a su "Destino en el proyecto". **Esta skill no lleva ninguna lista fija de documentos**: si se agrega una fila `crear-si-falta` al índice, esta skill la crea sin cambios.

## Pasos

1. **Verificar el clon.** Confirma que estás en la raíz del repositorio (`git rev-parse --show-toplevel` y que existen `docs/INDICE_PLANTILLAS.md` y `plantillas/`). Si ya existe `proyecto/Proceso.md`, avisa que el clon ya está configurado (muestra nombre y fecha de creación) y pregunta si continúa (solo completa lo que falta) o cancela. Nunca sobrescribas archivos de `proyecto/`.
2. **Comprobar que la base está al día.** Ejecuta `git fetch` y compara `HEAD` con la rama remota. Si hay cambios publicados que este clon no tiene, ofrece correr primero `importar-plantillas-licitacion`. Si no hay red o remoto, sigue y avísalo en el resumen.
3. **Leer el índice.** Lee `docs/INDICE_PLANTILLAS.md` y arma la lista de filas `activo`. Obtén los perfiles distintos del ámbito (`perfil:<NOMBRE>`) con su descripción de "Perfiles disponibles". Si no hay ninguno, no preguntes por perfiles y usa `ninguno`.
4. **Reunir los datos del proceso** en una sola ronda de `AskUserQuestion` (o un solo mensaje si son campos de texto): nombre de la licitación, entidad o cliente (empresa y división), empresa operativa (Veltis, Berliam, Steel, Walvis, Quintrax u otra), fecha de cierre, **carpeta fuente** (dónde están las bases y antecedentes originales; por defecto `proyecto/fuentes`), **carpeta de contexto** (dónde vivirán `BD/` y `OUTPUT/`; por defecto `proyecto`, o una carpeta compartida del equipo, por ejemplo `…\2.1. Estudio`) y, solo si el índice define perfiles, **perfiles que aplican** (se acepta "ninguno"). Si el usuario no conoce un dato, anótalo como "Pendiente"; no lo inventes ni supongas un perfil.
5. **Validar rutas externas.** Si la carpeta fuente o la de contexto están fuera del repo, comprueba que existan (`ls`). Si no existen, pregunta antes de crear nada fuera del repo. Nunca crees carpetas dentro de carpetas compartidas sin confirmación.
6. **Crear las plantillas propias.** Para cada fila activa y en alcance (ámbito `global` o perfil declarado) en modo `crear-si-falta`: si su destino no existe, copia el archivo del repo tal cual (`cp`, sin resumir ni reformular). Si existe, déjalo y anótalo como "ya existía".
7. **Completar `proyecto/Proceso.md`.** Reemplaza los marcadores `<…>` con los datos del paso 4, la fecha de hoy, el contenido de `VERSION` y el commit corto (`git rev-parse --short HEAD`). En `proyecto/Contexto_Especifico.md` reemplaza solo la fecha de "Historial". No agregues otro contenido.
8. **Crear carpetas de trabajo.** En la carpeta de contexto crea `BD/` y `OUTPUT/` si no existen. Si la carpeta fuente es `proyecto/fuentes`, créala también.
9. **Generar `CLAUDE.local.md`** en la raíz del repo (está en `.gitignore`), para que cada sesión cargue el contexto del proyecto:

```
# Proyecto: <nombre de la licitación>

Contexto propio de este clon. No se sube a GitHub.

@proyecto/Proceso.md
@proyecto/Contexto_Especifico.md
@proyecto/Contexto_y_Acuerdos_del_Proyecto.md
```

   Agrega una línea `@<destino>` por cada otra fila `crear-si-falta` en alcance cuyo destino sea un `.md`. Si `CLAUDE.local.md` ya existe, agrega solo las líneas que falten.
10. **Dar acceso a carpetas externas.** Si la carpeta fuente o la de contexto están fuera del repo, agrégalas a `permissions.additionalDirectories` en `.claude/settings.local.json` (créalo si no existe; si existe, léelo y agrega sin borrar lo que tenga). Avisa que el acceso rige desde la próxima sesión, o en esta con `/add-dir <ruta>`.
11. **Configuración local.** Si no existe `config/local.json`, avisa que conviene crearlo desde `config/local.example.json` (rutas de BD PRECIOS, FSChile y carpeta de cotizaciones) y ofrece completarlo ahora con los datos que entregue el usuario.
12. **Verificar.** Confirma que existen `proyecto/Proceso.md`, cada destino `crear-si-falta` en alcance, `CLAUDE.local.md`, `BD/` y `OUTPUT/`. Ejecuta `git status --porcelain` y confirma que **ningún** archivo creado aparece como cambio (todos deben estar ignorados; compruébalo con `git check-ignore -v <ruta>`). Si alguno aparece, deténte y avisa: el `.gitignore` está incompleto.
13. **Confirmar al usuario** en pocas líneas: proyecto configurado, perfiles, versión de la base, archivos creados (y cuáles ya existían), carpetas fuente y de contexto, datos pendientes, y que debe reiniciar la sesión (o usar `/memory`) para que `CLAUDE.local.md` se cargue.

## Reglas
- No hagas commit, push ni cambies de rama.
- No escribas fuera del repo sin confirmación del usuario.
- Nunca leas ni copies archivos de una carpeta `.IGNORE`.
- No cambies un proyecto ya configurado sin confirmación explícita y nunca sobrescribas archivos de `proyecto/`.
- No asumas ni agregues documentos por nombre: la lista de plantillas sale siempre del índice.
