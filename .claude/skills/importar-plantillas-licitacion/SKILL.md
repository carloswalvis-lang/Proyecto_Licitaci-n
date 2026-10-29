---
name: importar-plantillas-licitacion
description: Trae a este clon lo último publicado de la base de licitaciones en GitHub (git fetch + pull controlado), muestra qué cambió y crea en proyecto/ las plantillas crear-si-falta que falten, sin tocar lo propio del proyecto. Usar para actualizar instrucciones, skills o plantillas desde el repositorio.
---

# Importar (actualizar) la base desde GitHub

Actualiza los archivos globales de este clon con lo publicado en el repositorio remoto. La lista de documentos NO está en esta skill: sale de `docs/INDICE_PLANTILLAS.md`. Lo que hay en `proyecto/` (y en `BD/`, `OUTPUT/`, `CLAUDE.local.md`, `config/local.json`) está ignorado por git y **nunca** se toca.

## Pasos

1. **Verificar el repositorio.** `git rev-parse --show-toplevel`, `git remote -v` y la rama actual (`git branch --show-current`). La rama principal está en `config/local.json` (`rama_principal`, por defecto `main`). Si no hay remoto, deténte y explica cómo agregarlo (`git remote add origin <url>`). Si no estás en la rama principal, pregunta antes de cambiar.
2. **Traer sin aplicar.** `git fetch origin --tags`. Calcula lo entrante:
   - `git log --oneline HEAD..origin/<rama>` (commits nuevos).
   - `git diff --stat HEAD...origin/<rama>` (archivos cambiados).
   - `git show origin/<rama>:VERSION` y la sección nueva de `CHANGELOG.md`.
   Si no hay commits entrantes, ve al paso 6 (solo revisa plantillas faltantes) y di que la base ya está al día.
3. **Revisar cambios locales.** `git status --porcelain` (los archivos ignorados no aparecen, y así debe ser). Si hay cambios locales en archivos versionados o archivos nuevos sin seguimiento:
   - Muéstralos y pregunta con `AskUserQuestion`: **Publicar primero** (ejecuta `publicar-plantillas-licitacion` y vuelve aquí) / **Conservarlos sin publicar** (se aplican encima de lo nuevo con `git pull --rebase --autostash`) / **Descartarlos** (solo los archivos que el usuario confirme, con `git restore <archivo>`; nunca `git reset --hard` ni `git clean`).
   - Si un cambio local en un documento global era solo para este proceso, sugiere moverlo a `proyecto/Contexto_y_Acuerdos_del_Proyecto.md` antes de descartarlo.
4. **Aplicar.** Sin cambios locales: `git pull --ff-only origin <rama>`. Con cambios que el usuario decidió conservar: `git pull --rebase --autostash origin <rama>`.
   - Si hay conflictos, no los resuelvas en silencio: muestra cada archivo en conflicto con las dos versiones, propone la resolución y aplícala solo con confirmación. Si el usuario prefiere no seguir, `git rebase --abort` y avisa que el clon quedó como estaba.
5. **Revisar el índice nuevo.** Relee `docs/INDICE_PLANTILLAS.md`. Toma los perfiles del proyecto de la línea "Perfiles" de `proyecto/Proceso.md` (si no existe `proyecto/Proceso.md`, el clon no está configurado: sugiere `crear-proyecto-licitacion` al final). Separa las filas activas en alcance, las `retirado` y las de otros perfiles.
6. **Crear plantillas faltantes.** Solo si el clon ya está configurado (existe `proyecto/Proceso.md`; si no, omite este paso: lo hace `crear-proyecto-licitacion`, que además completa la ficha). Para cada fila activa y en alcance en modo `crear-si-falta`, si su destino en `proyecto/` no existe, cópiala desde el repo tal cual. Si existe, **no la toques**, aunque la plantilla haya cambiado y aunque el usuario pida forzar: guarda contenido propio del proyecto. Si la plantilla cambió, menciona en el resumen qué cambió para que el usuario decida si ajusta su copia a mano.
7. **Mantener `CLAUDE.local.md`.** Si existe, agrega una línea `@<destino>` por cada destino `.md` nuevo creado en el paso 6. No cambies las demás líneas.
8. **Verificar.** `git status` limpio (salvo los cambios locales conservados), `HEAD` igual a `origin/<rama>` o adelante con los commits locales conservados, y `git status --porcelain` sin archivos de `proyecto/`.
9. **Confirmar al usuario** en pocas líneas: versión anterior → versión nueva (`VERSION`), resumen del `CHANGELOG.md`, archivos actualizados (documentos, skills, plantillas), plantillas creadas en `proyecto/`, plantillas que cambiaron pero no se tocaron porque ya existían, filas retiradas y fuera de alcance. Si cambiaron `CLAUDE.md`, skills o `.claude/settings.json`, recuerda reiniciar la sesión de Claude Code para que se carguen.

## Reglas
- Nunca uses `git reset --hard`, `git clean`, `git push --force` ni `git checkout` sobre `proyecto/`.
- Nunca borres archivos de `proyecto/`; los documentos retirados solo se avisan.
- Nunca sobrescribas un destino `crear-si-falta` que ya existe.
- No hagas push: importar solo trae.
- Si no hay red o el remoto pide credenciales, deténte y explica qué falta (por ejemplo `gh auth login` o el administrador de credenciales de Git); no pidas ni escribas contraseñas o tokens.
