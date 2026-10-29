---
name: publicar-plantillas-licitacion
description: Publica en GitHub los cambios globales de este clon (CLAUDE.md, docs, skills, plantillas, herramientas) sin subir nada propio del proyecto — revisa el commit, sube la versión en VERSION, el índice y CHANGELOG.md, hace commit y push (o pull request) y etiqueta vX.Y.Z. Usar cuando el usuario pida publicar, guardar o subir cambios a la base compartida.
---

# Publicar cambios globales en GitHub

Sube a la base compartida lo que cambió en los archivos **versionados** de este clon. Lo propio del proceso (`proyecto/`, `BD/`, `OUTPUT/`, `CLAUDE.local.md`, `config/local.json`, `.claude/settings.local.json`) está ignorado por git y además se verifica que no se cuele. La lista de documentos y su versión salen de `docs/INDICE_PLANTILLAS.md`; esta skill no lleva listas propias.

## Pasos

1. **Preparar.** Confirma la raíz del repo, el remoto y la rama (`rama_principal` y `publicacion` de `config/local.json`; por defecto `main` y `main`). Si no estás en la rama principal y el modo es `main`, pregunta antes de seguir.
2. **Estar al día con el remoto.** `git fetch origin --tags`. Si `origin/<rama>` tiene commits que este clon no tiene, deténte y ejecuta primero `importar-plantillas-licitacion` (otro proyecto publicó; hay que partir de su versión). Luego vuelve aquí.
3. **Listar candidatos.** `git status --porcelain`: archivos versionados modificados, eliminados o renombrados, y archivos nuevos sin seguimiento. Si no hay nada, di que no hay cambios para publicar y termina.
4. **Revisar que nada sea propio del proceso.** Para cada candidato, deténte y avisa si:
   - Está en `proyecto/`, `BD/`, `OUTPUT/`, o es `config/local.json`, `CLAUDE.local.md` o `.claude/settings.local.json` (además, `git ls-files proyecto config/local.json CLAUDE.local.md` debe estar vacío; si no, alguien los forzó al repo: avisa y no publiques).
   - Es un documento o planilla (`.pdf .doc .docx .xls .xlsx .xlsm .csv .msg .eml .zip`) fuera de `plantillas/`, o pesa más de 5 MB.
   - Su diferencia (`git diff -- <archivo>`, o el contenido si es nuevo) contiene: rutas personales (`C:\Users\…`, `/Users/…`), correos o RUT de personas, montos o precios de un proceso, o el nombre del proceso, del cliente o de la división registrados en `proyecto/Proceso.md`. Muestra las líneas y pregunta: quitar el dato del documento global (y, si corresponde, moverlo a `proyecto/Contexto_y_Acuerdos_del_Proyecto.md`) o confirmar que es una regla general.
   - Es una plantilla `crear-si-falta` (`plantillas/…` con modo `crear-si-falta` en el índice) que ya no está vacía: solo debe tener encabezados, comentarios, instrucciones y marcadores `<…>`. Si tiene entradas de un proyecto, no se publica.
5. **Revisar cobertura del índice.** Cada candidato debe estar cubierto por una fila del índice (ruta exacta, o una fila de carpeta terminada en `/` que la contenga). Para los que no lo están, pregunta si se agregan al índice (ruta, ámbito, modo, descripción) o se excluyen de esta publicación. Si un candidato pertenece a una fila `perfil:<X>` que este proyecto no declara, pregunta antes de incluirlo.
6. **Elegir qué publicar.** Muestra la lista final (archivo, tipo de cambio, fila del índice) y confirma con `AskUserQuestion`: publicar todo / elegir archivos / cancelar. Lo que el usuario deje fuera queda como cambio local.
7. **Definir la versión nueva.** Lee `VERSION`. `major` si cambia la estructura, los roles o se eliminan documentos; `minor` si se agregan o reemplazan reglas, criterios, procesos, documentos o skills; `patch` si son correcciones de redacción. Si no es evidente, pregunta. Redacta un resumen corto del cambio y confírmalo.
8. **Actualizar versiones.**
   - `VERSION`: la versión nueva.
   - `docs/INDICE_PLANTILLAS.md`: en cada fila que cubre un archivo publicado, Versión = versión nueva y Actualizado = fecha de hoy. Agrega las filas nuevas acordadas en el paso 5 y una línea en "Registro de cambios del índice" (`DD-MM-AAAA: conjunto X.Y.Z desde <proyecto>: <resumen>`). No toques filas que no cambiaron ni filas de perfiles que este proyecto no declara.
   - `CHANGELOG.md`: nueva sección arriba de la anterior: `## X.Y.Z — AAAA-MM-DD — <nombre del proyecto de proyecto/Proceso.md>`, el resumen y la lista de archivos.
9. **Commit.** Agrega **solo los archivos aprobados** más `VERSION`, `CHANGELOG.md` y `docs/INDICE_PLANTILLAS.md`, con rutas explícitas (`git add -- <ruta> …`; nunca `git add .`, `-A` ni `-f`). Revisa `git diff --cached --stat` y confirma que coincide con lo aprobado. Mensaje: `vX.Y.Z: <resumen> (desde <proyecto>)`.
10. **Subir**, según `publicacion`:
    - `main`: `git pull --rebase origin <rama>` (si alguien publicó entretanto y hay conflicto en `VERSION`, `CHANGELOG.md` o el índice, `git rebase --abort`, `git reset --soft HEAD~1`, ejecuta `importar-plantillas-licitacion` y repite desde el paso 7), luego `git push origin <rama>`, `git tag -a vX.Y.Z -m "<resumen>"` y `git push origin vX.Y.Z`.
    - `pr`: crea la rama `publicar/<proyecto-en-minusculas-con-guiones>-<AAAAMMDD>`, haz push de la rama y abre el pull request con `gh pr create --title "vX.Y.Z: <resumen>" --body "<resumen, archivos y proyecto>"`. Si `gh` no está disponible o no está autenticado, entrega la URL para abrirlo en GitHub. La etiqueta `vX.Y.Z` se crea al aprobar el PR (indícalo).
11. **Verificar.** `git status` limpio respecto de lo publicado, `git log -1 --stat`, y en modo `main` que `origin/<rama>` apunte al commit nuevo y que la etiqueta exista en el remoto (`git ls-remote --tags origin vX.Y.Z`).
12. **Confirmar al usuario** en pocas líneas: versión publicada, archivos subidos, archivos que quedaron como cambios locales, filas nuevas del índice y, en modo `pr`, el enlace del pull request. Recuerda que los demás clones reciben el cambio con `importar-plantillas-licitacion`.

## Reglas
- Nunca uses `git push --force`, `git add -f`, `git add .` ni `git add -A`.
- Nunca subas contenido propio de un proceso; ante la duda, pregunta y deja el archivo fuera.
- Nunca borres archivos del repo sin confirmación explícita; una fila `retirado` se avisa y, si el usuario lo pide, el archivo se elimina con `git rm` en esta misma publicación.
- Si un paso de git falla, no sigas con el siguiente: muestra el error, deja el clon en un estado limpio (abortar rebase, sin etiquetas a medias) y explica qué hacer.
- No pidas ni escribas contraseñas o tokens. Si el push pide credenciales, indica cómo autenticarse (`gh auth login` o el administrador de credenciales de Git).
