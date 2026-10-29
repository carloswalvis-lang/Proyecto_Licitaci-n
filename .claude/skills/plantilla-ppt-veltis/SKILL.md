---
name: "plantilla-ppt-veltis"
description: "Al crear una presentación PowerPoint de licitación, comité o propuesta (Veltis, Berliam, Steel, Walvis, Quintrax), preguntar primero si usar la Plantilla Licitaciones Veltis incluida en plantillas/ppt/ del repositorio."
---

# Plantilla de presentaciones de licitación Veltis

Usar siempre que se pida crear o armar una presentación, ppt, pptx, deck o láminas relacionadas con una licitación, un comité de aprobación o una propuesta comercial de Veltis o de sus empresas operativas (Berliam, Steel, Walvis, Quintrax).

## 1. Preguntar antes de empezar

Antes de investigar o construir nada, preguntar con AskUserQuestion:

- ¿Quieres usar la plantilla Veltis de licitaciones? Opciones: Sí, versión Comité (con láminas financieras) / Sí, versión Comercial (para el cliente, sin cifras financieras) / Sí, versión completa (ambas, para elegir después) / No, diseño nuevo.

Si la respuesta es No, construir la presentación con la skill `pptx` (plugin `document-skills`) y el estilo corporativo (skill `estilo-veltis-ms365`), con Overpass como única fuente.

## 2. Ubicación de la plantilla

En el repositorio: `plantillas/ppt/` (se actualiza con `importar-plantillas-licitacion`).

Archivos: `Plantilla Licitaciones Veltis.potx` y `Plantilla Licitaciones Veltis.pptx` (mismo contenido).

Para usarla: copiar el `.pptx` a un directorio temporal (fuera del repo) y trabajar sobre la copia. **Nunca modificar la plantilla del repo**: si cambia, es una mejora global que se publica con `publicar-plantillas-licitacion`, no parte de una presentación. El resultado se guarda como archivo nuevo con el nombre de la licitación.

## 3. Estructura de la plantilla (9 láminas, en secciones de PowerPoint)

1. Portada (sección Portada)
2. Resumen de inversión, versión Comité (sección Resumen — Comité): 4 tarjetas con cifras financieras y tabla de 7 filas
3. Resumen comercial (sección Resumen — Comercial): tarjetas de plazo, dotación, equipos y disponibilidad, sin cifras financieras
4. Desafío (sección Contexto y alcance): cliente, operación, modalidad y alcance del servicio
5. Principales actividades (sección Contexto y alcance): 5 tarjetas con foto
6. KPI y Multas (sección Financiero — Comité): tablas de contrato, montos afectos, fórmula de descuento y KPI
7. P&L (sección Financiero — Comité): zona para pegar imagen del Excel
8. Cashflow (sección Financiero — Comité): zona para pegar imagen del Excel
9. Cierre (sección Cierre)

Todos los datos variables están como marcadores entre corchetes, por ejemplo [CLIENTE], [XX] meses, [XXX] MM CLP. Las notas del orador de cada lámina traen una guía de qué completar.

## 4. Cómo armar la presentación

1. Reunir los datos del proceso (bases, Excel de perfil, consultas) antes de tocar la plantilla.
2. Hacer primero todo el trabajo estructural: eliminar las secciones que no aplican (Comité: quitar Resumen — Comercial; Comercial: quitar Resumen — Comité y Financiero — Comité) y las tarjetas de actividades sobrantes completas (foto, recuadro y textos). Duplicar láminas con los scripts de la skill `pptx` (`add_slide.py`), nunca a mano.
3. Después reemplazar el contenido: cada texto entre corchetes por el dato real, conservando el formato de los runs (etiqueta en negrita y valor).
4. Fotos: reemplazar manteniendo tamaño y recorte; si no hay fotos disponibles, dejar la tarjeta fuera y avisar.
5. Logo: la plantilla trae el de Steel; cambiarlo por el de la empresa licitante si es otra operativa y avisar al usuario si no se dispone del archivo del logo.
6. P&L y Cashflow: insertar el rango del Excel como imagen estática (nunca como objeto vinculado, para no dejar la ruta de SharePoint ni pedir actualizar vínculos). Si no hay datos, eliminar esas láminas.
7. Tipografía: solo Overpass (regular, negrita y cursiva donde corresponda). No introducir otras fuentes.
8. Antes de entregar, verificar con markitdown que no queden corchetes sin completar, datos de otra licitación ni textos de guía; validar con validate.py usando --original con la plantilla; renderizar las láminas y revisar desbordes de texto.

## 5. Entrega

Guardar el `.pptx` final en `OUTPUT/` de la carpeta de contexto (línea "Carpeta de contexto" de `proyecto/Proceso.md`) con el nombre `<licitación> - <Comité|Comercial> - AAAA-MM-DD.pptx`, sin sobrescribir uno existente, e indicar la ruta. Avisar que quien lo abra necesita Overpass instalada (gratis en Google Fonts) o incrustarla desde Archivo → Opciones → Guardar → Incrustar fuentes en el archivo.

Si la skill `pptx` no está disponible, indicar que se instala con `/plugin marketplace add anthropics/skills` y `/plugin install document-skills@anthropic-agent-skills`.