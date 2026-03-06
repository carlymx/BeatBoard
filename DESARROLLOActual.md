# BeatBoard - Estado del Desarrollo

**Fecha**: 6 Marzo 2026  
**Versión**: 1.0.19 - RELEASE ✅

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
