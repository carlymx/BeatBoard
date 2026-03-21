# BeatBoard - Estado del Desarrollo

**Fecha**: 15 Marzo 2026  
**Versión**: 1.0.29 - RELEASE ✅

---
## v1.0.28 - RELEASE ✅

### Cambios
- ✅ **Fix alineación vertical panel de propiedades**:
  - Los widgets del panel de beats ahora se alinean en la parte superior (igual que conexiones)
  - Agregado `addStretch()` en layouts para empujar widgets hacia arriba

- ✅ **Confirmación de cambios no guardados en Nuevo Proyecto**:
  - El botón "Nuevo" (Ctrl+N) ahora pregunta si guardar cambios antes de crear nuevo proyecto
  - Refactorizado método `_confirm_unsaved_changes()` reutilizable
  - También aplicado a Abrir, Cerrar y Abrir reciente

- ✅ **Eliminación de email por privacidad**:
  - Removida dirección de email del diálogo "Acerca de"
  - Eliminadas referencias a email en README.md y README_ES.md

- ✅ **Fix menú "Archivos recientes"**:
  - Ahora muestra los archivos guardados al iniciar la aplicación
  - Corregido orden de inicialización: `_load_recent_files()` después de `_setup_menus()`

- ✅ **Nuevo menú "Manual" en Ayuda**:
  - Opción "Abrir Manual" que abre documentación en el idioma actual
  - Submenú "Manual (Otros Idiomas)" con enlaces a español, inglés, francés y alemán
  - URLs apuntan a GitHub: `https://github.com/carlymx/BeatBoard/blob/main/doc/manual_md/MANUAL_[lang].md`

### Archivos modificados
- `beatboard/ui/widgets/properties_panel.py` – Añadido `addStretch()` para alineación vertical
- `beatboard/ui/main_window.py` – Confirmación cambios no guardados, fix archivos recientes, nuevo menú manual
- `beatboard/i18n/locales/*.py` – Nuevas traducciones para menú manual
- `README.md`, `README_ES.md` – Eliminación de email

---
## v1.0.29 - RELEASE ✅

### Cambios
- ✅ **Sistema ZIP para proyectos (.bbp)**: Formato de archivo cambiado de JSON plano a ZIP, permitiendo almacenar imágenes y recursos
- ✅ **Imágenes en canvas**: Nuevo tipo de elemento ImageItem para insertar imágenes en el lienzo
- ✅ **Persistencia de imágenes**: Las imágenes se guardan en `media/` dentro del ZIP y cargan correctamente
- ✅ **Carpetas temporales ocultas**: Las carpetas de datos del proyecto ahora son ocultas (`.{proyecto}_data`)
- ✅ **Limpieza automática**: Eliminación automática de carpetas temporales al cerrar proyecto/abrir nuevo/cerrar app
- ✅ **Bug fixes generales**: Corrección de rutas de imágenes, duplicación de UUIDs, consistencia de image_id
- ✅ **Integración con beats**: Las imágenes embebidas en beats también se guardan en `beats/{id}/`
- ✅ **Compatibilidad con versiones anteriores**: Los proyectos JSON antiguos se cargan correctamente
- ✅ **FIX bugs críticos del sistema de imágenes**:
  - **Copy/paste bug**: Las imágenes mostraban "Imagen no encontrada" al copiar después de guardar/cerrar/reabrir proyecto
    - Solución: Nuevo método `_resolve_image_path()` en `beat_board_view.py` que busca imágenes en `media/`, `beats/` y directorio base del proyecto
  - **WYSIWYG resize bug**: Los cambios de tamaño en el diálogo de propiedades de imágenes incrustadas no persistían (volvían al tamaño original al reeditar)
    - Solución: Corregido `mouseDoubleClickEvent()` en `rich_text_editor.py` usando `cursorForPosition(event.pos())`, añadido `document().setModified(True)` y señales de cambio de contenido
  - **Undo bug**: Eliminar una imagen y pulsar Ctrl+Z no hacía nada (undo no funcionaba)
    - Solución: Modificado `delete_selected_beats()` en `beat_board_view.py` para usar `DeleteImageCommand` cuando existe un stack de undo
  - **LSP errors**: Corregidos usando `isinstance(item, ImageItem)` con type hints en lugar de `hasattr(item, 'image_id')`

### Archivos modificados
- `beatboard/core/project_packager.py` – Nueva clase para empaquetar/desempaquetar proyectos ZIP
- `beatboard/ui/canvas/image_item.py` – Nuevo widget para imágenes en canvas
- `beatboard/ui/canvas/beat_board_view.py` – Gestión de imágenes, carga/guardado, señales + nuevos métodos `_resolve_image_path()`, fix undo para imágenes, corrección LSP errors
- `beatboard/core/project.py` – Nuevo campo `canvas_images`
- `beatboard/ui/main_window.py` – Lógica de limpieza de carpetas temporales
- `beatboard/ui/widgets/rich_text_editor.py` – Fix bug WYSIWYG resize, diálogo de propiedades de imágenes
- `beatboard/i18n/locales/*.py` – Traducciones para imágenes y diálogo de propiedades (image_properties, width, height, keep_aspect_ratio)
- `beatboard/ui/undo_commands.py` – Comandos `DeleteImageCommand` y `CreateImageCommand` ya existentes, ahora utilizados correctamente

---
## v1.0.27 - RELEASE ✅

### Cambios
- ✅ **Zoom de selección de área**:
  - Nuevo modo de zoom que permite dibujar un rectángulo para hacer zoom al área seleccionada
  - Activación: botón en toolbar (entre zoom-in y fit) o tecla "Z" (cuando no hay selección)
  - Banner visual indicando el modo activo
  - Rectángulo semitransparente azul durante la selección
  - Margen del 5% aplicado para mejor visualización

- ✅ **Fix banner modo conexión**:
  - Arreglado el banner que no se mostraba al activar el modo conexión

- ✅ **Atajos de teclado actualizados**:
  - Añadido atajo "Z" para zoom de selección en el diálogo de atajos
  - Añadido atajo "Ctrl+W" para cerrar proyecto
  - Actualizada descripción de "Crear nuevo beat" (doble clic en lienzo)
  - Actualizada descripción de "Editar beat" (doble clic en beat)
  - Actualizada descripción de "Modo paneo" (Espacio o botón central del ratón)

- ✅ **Fix paneo con teclado (Espacio)**:
  - Arreglado el problema por el cual el paneo con Espacio no funcionaba correctamente
  - Añadido flag `_pan_started_with_space` para gestionar el primer movimiento del ratón
  - Ahora el paneo empieza sin desplazamiento no deseado

### Archivos modificados
- `beatboard/ui/canvas/beat_board_view.py` – Nueva lógica de zoom de selección, fix paneo
- `beatboard/ui/main_window.py` – Nuevo botón toolbar, diálogo de atajos actualizado
- `beatboard/i18n/locales/*.py` – Nuevas traducciones para zoom selection, paneo, atajos

---
## v1.0.26 - RELEASE ✅

### Cambios
- ✅ **Corrección de bugs en propiedades de conexión**:
  - Solucionado problema donde la selección múltiple de conexiones no aplicaba cambios
  - El handler `_on_multiple_connections_updated` ahora incluye el parámetro `label` faltante

- ✅ **Atajos de teclado extendidos para conexiones**:
  - Teclas 1-0 ahora cambian colores tanto para beats como para conexiones
  - Nueva señal `connection_updated` en `BeatBoardView` para notificar actualizaciones
  - Método `_change_selected_connection_color()` para manejar cambios de color por teclado

- ✅ **Personalización de colores de conexión**:
  - Añadidos colores personalizados (8, 9, 0) a los widgets de propiedades de conexión
  - Función `get_valid_connection_color()` para manejar colores hex y nombres predefinidos

- ✅ **Nuevo color de conexión**:
  - Añadido 7º color predefinido "dark_gray" (#616161) a `CONNECTION_COLORS`
  - Traducciones en los 4 idiomas para "Gris Oscuro"/"Dark Gray"

- ✅ **Atajo para modo conexión**:
  - Tecla "C" activa/desactiva modo conexión cuando no hay nada seleccionado
  - Integración con el método existente `toggle_connection_mode()`

- ✅ **Actualizaciones de interfaz**:
  - Cambiado "Cambiar color del beat" a "Cambiar color de la selección" en todos los idiomas
  - Panel de propiedades de conexión se actualiza en tiempo real con atajos de teclado
  - Actualizado diálogo de atajos de teclado para mostrar "1-0" y "C"

### Archivos modificados
- `beatboard/ui/widgets/properties_panel.py` – Soporte para colores personalizados en conexiones, fix multiselección
- `beatboard/ui/main_window.py` – Handlers actualizados, conexión de señales, diálogo de atajos
- `beatboard/ui/canvas/beat_board_view.py` – Nueva señal `connection_updated`, método `_change_selected_connection_color()`, atajo "C"
- `beatboard/core/constants.py` – Añadido color `dark_gray`, función `get_valid_connection_color()`
- `beatboard/ui/canvas/connection_item.py` – Usa `get_valid_connection_color()` para renderizado correcto
- `beatboard/i18n/locales/*.py` – Nuevas traducciones para atajos y color gris oscuro
- `beatboard/__init__.py` y `pyproject.toml` – Versión actualizada a 1.0.26

---
## v1.0.24 - RELEASE ✅

### Cambios
- ✅ **Reorganizado menú Archivo**:
  - "Abrir recientes" ahora aparece debajo de "Abrir proyecto"
  - "Cerrar" con atajo Ctrl+W

### Archivos modificados
- `beatboard/ui/main_window.py`

---
## v1.0.25 - RELEASE ✅

### Cambios
- ✅ **Columna de propiedades general**:
  - Panel de propiedades ahora funciona para beats, conexiones y selección múltiple
  - Nuevos campos para conexiones: color, grosor de línea (0.5-10px), forma de terminadores (círculo, cuadrado, flecha, ninguno)
  - Soporte para cambiar propiedades comunes en selección múltiple (beats y conexiones)
  - Estados mixtos cuando valores difieren (combo sin selección, checkbox tri-state)
  - Actualización en tiempo real al usar atajos de teclado (1-0)

- ✅ **Renderizado de terminadores en conexiones**:
  - Terminadores visuales en extremos de líneas según forma seleccionada
  - Flechas, círculos, cuadrados o ninguno
  - Tamaño proporcional al grosor de línea

- ✅ **Persistencia de propiedades de conexión**:
  - Los campos `line_width` y `node_shape` se guardan en archivos .bbp
  - Compatibilidad con versiones anteriores (valores por defecto)

### Archivos modificados
- `beatboard/core/constants.py` – añadidas constantes para grosores y formas de nodo
- `beatboard/core/connection.py` – nuevos campos `line_width` y `node_shape`
- `beatboard/ui/widgets/properties_panel.py` – **REFACTOR COMPLETO**: widgets separados para beats, conexiones, múltiples beats, múltiples conexiones
- `beatboard/ui/main_window.py` – handlers para selección múltiple, actualización de colores
- `beatboard/ui/canvas/connection_item.py` – método `_draw_terminations()`
- `beatboard/i18n/locales/*.py` – nuevas traducciones para propiedades de conexión

---
## v1.0.23 - RELEASE ✅

### Cambios
- ✅ **Menú Archivo > Cerrar (Ctrl+W)**:
  - Cierra el proyecto actual
  - Pregunta si desea guardar cambios sin guardar
  
- ✅ **Menú Archivo > Abrir recientes**:
  - Lista de los 10 últimos archivos abiertos
  - Guarda la lista en config/recent_files.json
  - Si un archivo no existe, muestra diálogo para eliminarlo de la lista

- ✅ **Arreglado: Guardado de forma de conexiones**:
  - Ahora se guardan los puntos de control personalizados de las conexiones
  - Los factores de control (control_factor1, control_factor2) se almacenan en el JSON
  - Al cargar un proyecto, las conexiones mantienen la forma de curva personalizada

### Archivos modificados
- `beatboard/core/connection.py`: nuevos campos control_factor1 y control_factor2
- `beatboard/ui/canvas/connection_item.py`: carga y guardado de factores de control
- `beatboard/ui/main_window.py`: nuevos menús y métodos para archivos recientes
- `beatboard/i18n/locales/*.py`: nuevas traducciones

---
## v1.0.22 - RELEASE ✅

### Cambios
- ✅ **Asociación de archivos .bbp**:
  - Soporte para CLI args: `beatboard archivo.bbp` abre el proyecto
  - Drag & drop de archivos .bbp al canvas carga el proyecto
  - Nuevo menú "Herramientas > Registrar asociaciones de archivo..."
  - Diálogo que permite configurar asociaciones según el SO detectado
  - Archivo .desktop para Linux (en tools/) con MimeType

### Archivos modificados
- `beatboard/app/main.py`: manejo de argumentos CLI
- `beatboard/ui/main_window.py`: 
  - Nuevo parámetro `file_to_open_on_start` en constructor
  - Nuevo menú Herramientas
  - Drag & drop habilitado
- `beatboard/ui/canvas/beat_board_view.py`:
  - Métodos dragEnterEvent, dragMoveEvent, dropEvent
  - setAcceptDrops(True)
- Nuevo `beatboard/ui/dialogs/file_association_dialog.py`: diálogo de configuración
- `beatboard/i18n/locales/*.py`: nuevas traducciones
- `tools/beatboard.desktop`: archivo .desktop para Linux

### Pendiente (futura versión)
- Formato .bbp como ZIP para soportar imágenes/archivos adjuntos

---
## v1.0.21 - RELEASE ✅

### Cambios
- ✅ **Botón "Abrir editor completo" en Panel de Propiedades**:
  - Nuevo botón debajo del campo de contenido en el panel de propiedades
  - Solo visible cuando hay un beat seleccionado
  - Abre el diálogo de edición completa (igual que doble clic)
  - Los cambios se aplican automáticamente al beat
  - Traducciones en los 4 idiomas

### Archivos modificados
- `beatboard/ui/widgets/properties_panel.py`:
  - Añadido QPushButton "_open_editor_btn"
  - Nuevo método "_open_full_editor()"
  - set_beat() muestra/oculta el botón según selección
- `beatboard/i18n/locales/*.py`: nueva traducción "open_full_editor"

---
## v1.0.20 - RELEASE ✅

### Cambios
- ✅ **Color de fondo con Tema**:
  - Cada tema ahora tiene colores de fondo y cuadrícula asociados
  - Al cambiar de tema se aplican automáticamente los colores del tema (solo si el usuario no los ha personalizado)
  - Banderas para rastrear si el usuario ha personalizado fondo/grid
  - Nueva opción "Restablecer colores del tema" en menú Preferencias > Fondo del Canvas
  - Traducciones en los 4 idiomas

### Archivos modificados
- `beatboard/core/constants.py`: añadido THEME_CANVAS_COLORS con colores por tema
- `beatboard/ui/theme_manager.py`:
  - Nuevas señales: grid_color_changed
  - Banderas: _user_customized_background, _user_customized_grid
  - Métodos: reset_to_theme_colors(), is_background_customized(), is_grid_color_customized()
  - _apply_theme_canvas_colors() aplicado en set_theme()
- `beatboard/ui/canvas/beat_board_scene.py`: conexión de señal grid_color_changed
- `beatboard/ui/main_window.py`: nueva opción de menú y handler
- `beatboard/i18n/locales/*.py`: nueva traducción "reset_theme_colors"

---
## v1.0.19 - RELEASE ✅

### Cambios
- ✅ **Sistema de Z-Order corregido**:
  - Cada beat nuevo se crea con z = número total de beats + 1
  - Los beats ocupan posiciones únicas y consecutivas (1, 2, 3...)
  - Subir beat (Ctrl+PageUp): intercambia posición con el beat que está encima
  - Bajar beat (Ctrl+PageDown): intercambia posición con el beat que está debajo
  - Traer al frente (Ctrl+Home): mueve a posición máxima, reordena los demás
  - Enviar al fondo (Ctrl+End): mueve a posición 1, reordena los demás
  - Al cargar proyecto: normaliza z-orders a números consecutivos
  - Debug visual: muestra "z:X" sobre cada objeto (constante DEBUG_SHOW_Z_ORDER en constants.py)
- ✅ **Barra de estado informativa**:
  - Muestra beats seleccionados con altura Z (z-order)
  - Para múltiples beats: cantidad y rango de alturas (z1, z2)
  - Conexiones seleccionadas también muestran altura Z
  - Objetos mixtos (beats + conexiones) muestran cantidad y rango
  - Se actualiza al subir/bajar beats (Ctrl+Home/Ctrl+End, Ctrl+PageUp/Ctrl+PageDown)
- ✅ **Selección múltiple mejorada**:
  - La barra de estado distingue entre beats, conexiones y objetos mixtos
  - Traducciones para nuevos mensajes en todos los idiomas

### Archivos modificados
- `beatboard/core/constants.py`: añadida constante DEBUG_SHOW_Z_ORDER
- `beatboard/ui/canvas/beat_item.py`: debug visual z-order en paint()
- `beatboard/ui/canvas/connection_item.py`: debug visual z-order en paint()
- `beatboard/ui/canvas/beat_board_view.py`: 
  - _add_beat_item: nuevo beat recibe z = max + 1
  - _normalize_z_order: reordena todos los z-orders a consecutivos
  - _get_max_z_order, _get_beat_by_z_order: helpers para gestión de z
  - bring_selected_beats_to_front, send_selected_beats_to_back: reordenan toda la pila
  - move_selected_beats_up, move_selected_beats_down: intercambian posiciones
  - _load_beats: normaliza al cargar proyecto

### Archivos modificados
- `beatboard/ui/canvas/beat_board_view.py`: señal selection_changed ahora emite dict con beats y connections, nuevo método _get_current_selection, actualización de barra de estado en movimientos Z
- `beatboard/ui/main_window.py`: nueva lógica en _on_selection_changed para mostrar información de altura Z
- `beatboard/i18n/locales/*.py`: nuevas claves de traducción (selected_connection_status, multiple_connections_status, mixed_objects_status)
- `beatboard/core/constants.py`, `beatboard/__init__.py`, `pyproject.toml`: versión actualizada a 1.0.19

---
## v1.0.18 - RELEASE ✅

### Cambios
- ✅ **Handles de conexión mejorados**:
  - Hitbox aumentada a 30x30 (antes 60x60) para mejor precisión
  - Rectángulos debug transparentes de 30x30
  - Interacción solo cuando conexión está seleccionada
  - Doble clic en handle para resetear a curvatura predeterminada
- ✅ **Curvas proporcionales**:
  - Sistema de factores relativos mantiene forma al mover beats
  - No más deformación exponencial al mover beats después de ajustar handles
  - Puntos de control almacenan posición relativa, no absoluta
- ✅ **Mejoras de interacción**:
  - Handles visibles solo al seleccionar conexión
  - Cursor cambia a cruz al pasar sobre handles
  - Debug prints eliminados para terminal limpia

### Archivos modificados
- `beatboard/ui/canvas/connection_item.py`: Lógica completa de handles, factores relativos, doble clic

---
## v1.0.17 - RELEASE ✅

### Cambios
- ✅ Fix truncamiento: beats expanden altura automáticamente
- ✅ Bordes selección más gruesos (4px beats, 5px conexiones)
- ✅ Indicador de color en panel de propiedades
- ✅ Fix z-order conexiones
- ✅ Curvas de conexión mejoradas:
  - **Offset configurable**: Preferencias > Punto de conexión (0%-50% desde el borde)
  - **Segmentos horizontales**: La curva ahora tiene entrada/salida recta horizontal antes de la curva
  - **Nodos editables**: Al seleccionar conexión aparecen manejadores conectados por líneas discontinuas
  - **Ajuste proporcional**: Al mover beats los puntos de control se ajustan automáticamente

### Archivos modificados
- `beat_item.py`: altura dinámica, borde 4px
- `connection_item.py`: curva con segmentos horizontales, nodos editables
- `properties_panel.py`: widget color_indicator
- `beat_board_view.py`: actualización de conexiones
- `theme_manager.py`: preferencia connection_offset_percent
- `constants.py`: CONNECTION_OFFSET_PERCENT, CONNECTION_OFFSET_MIN
- `main_window.py`: menú de conexiones, traducciones

---
## v1.0.16 - RELEASE ✅

### Features
- Menú Preferencias (backup config: on_open, max, interval)
- Backups diferenciados (_auto_ vs _open_)
- Traducciones completas (UI, beats, colores)
- Fix icono Windows (AppUserModelID)

### Tech
- `theme_manager.py`: nuevas preferencias
- `autosave_service.py`: métodos de backup
- `resources.py`: carga cross-platform de iconos

---
## v1.0.14 - RELEASE ✅

### Features
- Sistema colores hexadecimales
- 3 colores personalizables (teclas 8,9,0)
- Dropdown panel propiedades con hex reales
- Fix botón "Más Colores..."

---
## v1.0.13 - RELEASE ✅
- Indicador visual Modo Conexión (banner)
- Fix cursor cruz en Modo Conexión

---
## v1.0.12 - RELEASE ✅
- Spellcheck lazy loading
- Checkbox "Mostrar título"

---
## v1.0.10 - RELEASE ✅
- Spellcheck Hunspell (es, en, fr, de)
- Diccionarios de usuario

---
## v1.0.7 - RELEASE ✅
- Icono personalizado embebido
- Rutas cross-platform

---
## Funcionalidades v1.0 (COMPLETO- BeatBoardScene)

### Canvas
/View, BeatItem
- Zoom (Ctrl+Scroll), Paneo (Espacio)
- Coordenadas cursor, punto central (0,0)

### Interactividad
- Crear (doble clic), Editar, Mover, Eliminar
- Selección única/múltiple
- Menú contextual

### Conexiones
- ConnectionItem, líneas bezier
- Modo conexión (toolbar)
- Actualización automática

### Tema
- 9 temas (claro/oscuro)
- Fondo/grid personalizable

### i18n
- EN, ES, FR, DE
- Detección sistema

### Otros
- Undo/Redo completo
- Atajos teclado
- Panel propiedades
- Persistencia (.bbp), auto-guardado
- Export PDF/texto
- 34 tests

---
## 📋 Tareas Pendientes (Futuras Versiones)

### Formato .bbp como ZIP (para imágenes/archivos adjuntos)
**Descripción**: Cambiar el formato de archivo .bbp de JSON plano a carpeta comprimida (ZIP) renombrada, permitiendo:
- Almacenar imágenes embebidas en beats
- Adjuntar archivos adicionales a beats
- Mejor organización de recursos

**Implementación sugerida**:
1. Crear clase `ProjectPackager` con métodos:
   - `pack(project: Project, output_path: Path)`: comprime proyecto a ZIP
   - `unpack(zip_path: Path) -> Project`: descomprime y carga proyecto
2. Estructura interna del ZIP:
   ```
   proyecto.bbp/
   ├── project.json      # Datos del proyecto
   ├── beats/
   │   ├── {beat_id}/
   │   │   ├── image.png
   │   │   └── attachments/
   │   │       └── file.pdf
   └── thumbnails/       # (opcional) miniaturas
   ```
3. Detectar formato al cargar (JSON plano vs ZIP)
4. Guardar siempre en nuevo formato ZIP
5. Migración automática de archivos antiguos

**Archivos a crear**:
- `beatboard/core/project_packager.py` (nuevo)

**Archivos a modificar**:
- `beatboard/ui/main_window.py`: lógica de carga/guardado
- `beatboard/core/project.py`: integración con packager
- Spec files: actualizar para incluir recursos

---
## Archivos Clave

| Módulo | Archivo |
|--------|---------|
| Core | beat.py, connection.py, project.py, constants.py |
| UI | main_window.py, theme_manager.py, undo_commands.py |
| Canvas | beat_board_view.py, beat_board_scene.py, beat_item.py, connection_item.py |
| Dialogs | beat_editor_dialog.py |
| Widgets | properties_panel.py |
| Services | autosave_service.py, export_service.py |
| i18n | beatboard/i18n/ (en, es, fr, de) |

---
## Ejecución
```bash
source .venv/bin/activate
python -m beatboard.app.main
pytest beatboard/tests/ -v
```

---
## Notas
- Python 3.10 para compilar (no 3.12+)
- Errores LSP son falsos positivos
- Config: ~/.config/beatboard/preferences.json