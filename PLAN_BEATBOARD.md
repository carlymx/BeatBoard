# BeatBoard - Plan de Desarrollo

## Info
- **App de escritorio**: Pizarra virtual de beats para guionistas (como Final Draft Beat Board)
- **Tech**: Python 3.10+ / PySide6 / Qt Graphics View
- **v1.0 COMPLETA** | Roadmap: v1.1→v1.2→v1.5→v2.0

---

## 📋 TODOList - Features Pendientes

### 🐛 BUGS/FIXES (Prioridad Alta)

#### 1. Fix Altura de Conexiones (z-order) ✅ COMPLETADO
**Descripción**: Las líneas de conexión no se actualizan correctamente cuando se cambia la altura de un beat. En ocasiones la conexión queda por detrás del beat o en una posición incorrecta.  
**Solución implementada**: 
- Sistema de z-order consecutivo: cada beat ocupa posición única (1, 2, 3...)
- Nuevo beat se crea en z = número total + 1
- Conexiones siempre se muestran sobre los beats que conectan (max_z + 1)
- Movimientos Z (subir/bajar/frente/fondo) reordenan toda la pila correctamente
**Archivo relacionado**: `connection_item.py`, `beat_item.py`, `beat_board_view.py`

#### 2. Arreglar Exportar PDF
**Descripción**: Los PDF no se generan correctamente.  
**Mejora adicional**: Generar PDF en una sola hoja del tamaño de la zona que ocupen todos los elementos más márgenes. Mantener elementos vectoriales (beats, conexiones, shapes) como vectores en el PDF.  
**Archivo relacionado**: `export_service.py`

---

### 🏗️ ARQUITECTURA (Base para otras features)

#### 3. Columna de Propiedades General ✅ COMPLETADO
**Descripción**: Transformar el panel lateral de propiedades específico de beats en una columna de propiedades genérica que funcione para cualquier tipo de elemento seleccionado (beats, conexiones, shapes, imágenes). Mostrar opciones únicas según el tipo de elemento seleccionado.  
**Cambios**:
- beats → título, contenido, color, mostrar título
- conexiones → grosor, color, forma nodos, texto
- shapes → forma, tamaño, color, translucidez
- Renombrar a "Propiedades" (sin "del Beat")  
**Prepara el terreno para**: shapes, imágenes, múltiples tipos de elementos  
**Archivos relacionados**: `properties_panel.py`, `main_window.py`

---

### 🎨 MEJORAS UI/UX

#### 4. Botón "Más Opciones" en Editor de Beats ✅ COMPLETADO
**Descripción**: Añadir un botón debajo del campo de texto "Contenido" en el diálogo de edición de beats que abra el Editor de Beats completo (igual que hace el doble clic). útil para usuarios que prefieran editar desde el panel de propiedades.  
**Archivos relacionados**: `properties_panel.py`, `beat_editor_dialog.py`

#### 5. Color de Fondo con Tema ✅ COMPLETADO
**Descripción**: Cada tema debe tener asociado un color de fondo y color de cuadrícula coherentes. Al seleccionar un tema, automáticamente cambiar el fondo del canvas y el color de la cuadrícula a los valores definidos para ese tema.  
**Archivos relacionados**: `theme_manager.py`, `beat_board_view.py`, `constants.py`

---

### 🔗 FEATURES DE CONEXIONES

#### 6. Grosor y Color de Líneas de Conexión ✅ COMPLETADO
**Descripción**: Permitir personalizar cada línea de conexión de forma independiente.  
**Implementado**:
- ✅ Nodos editables (arrastrar puntos de control)
- ✅ Porcentage de conexión configurable (default 25%)
- ✅ Ajuste proporcional al mover beats
- ✅ Panel propiedades: grosor, color, forma nodos
- ✅ Soporte para múltiples conexiones seleccionadas
- ✅ Renderizado de terminadores (arrows, circles, squares, none)
- ✅ Persistencia de configuración (guardar/cargar)

**Archivos relacionados**: `connection_item.py`, `properties_panel.py`, `constants.py`, `main_window.py`

#### 7. Texto en Conexiones ⚠️ PARCIAL
**Descripción**: Añadir la posibilidad de mostrar texto en el medio de las líneas de conexión. ⚠️ **Parcialmente implementado**: campo 'label' añadido en panel de propiedades y modelo Connection, pendiente renderizado en canvas.  
**Implementación**:
- Doble clic en conexión → abre diálogo de edición (como beats)
- Panel propiedades → campo de texto, configuración del contenedor:
  - Forma del contenedor: rectángulo, óvalo, diamante
  - Color de fondo
  - Color del texto
  - Grosor del borde
- El texto se renderiza centrado en la línea de conexión  
**Archivos relacionados**: `connection_item.py`, `beat_editor_dialog.py` (reutilizar)

---

### 📝 FEATURES DE BEATS

#### 8. Formato Markdown en Beats
**Descripción**: Permitir escribir contenido en formato Markdown en los beats y renderizarlo visualmente.  
**Implementación**:
- Toggle HTML/Markdown en editor de beats (default: Markdown)
- Renderizado en el beat: negrita, cursiva, listas, enlaces, headers
- Usar biblioteca como `markdown` o `mistune` para parsear  
**Preferencia usuario**: Markdown como predeterminado  
**Archivo relacionado**: `beat_item.py`, `beat_editor_dialog.py`

#### 9. Imágenes en Beats
**Descripción**: Soporte para插入 imágenes dentro de un beat o como elemento independiente en el canvas.  
**Beat con imagen**:
- Editor de beat → opción para añadir imagen
- Imagen se muestra dentro del beat (debajo del título o reemplazando contenido)
- Ajuste de tamaño: contener, cubrir, original  
**Imagen como elemento**:
- Nuevo tipo de elemento en el canvas
- Arrastrar imagen desde explorador de archivos
- Propiedades: ruta, tamaño, rotación, opacidad  
**Archivo relacionado**: `beat_item.py`, `beat_board_scene.py`

---

### 🛠️ NUEVAS FEATURES

#### 10. Barra de Herramientas de Dibujo (Shapes)
**Descripción**: Añadir toolbar para dibujar shapes vectoriales en el canvas.  
**Shapes disponibles**: rectángulo, círculo, elipse, flecha, línea.  
**Propiedades editables** (en panel de propiedades):
- Forma/tipo
- Grosor del trazo
- Color del trazo
- Color de relleno
- Translucidez (opacity 0-100%)
- Rotación
- Tamaño  
**Comportamiento**:
- Seleccionar shape → arrastrar para dibujar
- Seleccionar shape existente → mover/redimensionar
- Múltiples shapes seleccionables  
**Prepara para**: diagramas, storyboards, annotaciones  
**Archivos relacionados**: nuevo `shape_item.py`, toolbar en `main_window.py`

#### 11. Asociación de Tipo de Archivo ✅ COMPLETADO (v1.0.22)
**Descripción**: Registrar la aplicación como handler de archivos .bbp en el sistema operativo.  
**Funcionalidades implementadas**:
- Abrir archivo al invocar: `beatboard proyecto.bbp` (CLI args)
- Drag & drop de archivo .bbp a la ventana → cargar proyecto
- Menú Herramientas > Registrar asociaciones de archivo (diálogo)
- Linux: archivo .desktop con MimeType (en tools/)
- Windows/macOS: info en diálogo (se configura en instalación)

**Pendiente para futura versión**:
- Formato .bbp como carpeta comprimida (ZIP) para soportar imágenes/archivos adjuntos

**Archivos modificados**: `main.py`, `main_window.py`, `beat_board_view.py`, nuevo `file_association_dialog.py`, `tools/beatboard.desktop`

#### 12. Exportar a PNG
**Descripción**: Exportar el canvas completo o selección a imagen PNG.  
**Funcionalidades**:
- Diálogo de exportación con opciones de configuración
- Opciones del diálogo:
  - **Área a exportar**:
    - Todo el canvas (zona con contenido + márgenes)
    - Selección actual (solo elementos seleccionados)
    - Región visible (lo que se ve en pantalla)
  - **Resolución/Escala**:
    - 1x (original)
    - 2x (retina/doble densidad)
    - 3x (ultra alta)
    - Personalizado (0.5x a 5x)
  - **Fondo**:
    - Transparente
    - Color sólido (selector de color)
    - Mantener color actual del canvas
  - **Opciones de calidad**:
    - Compresión PNG (0-9)
    - Incluir/excluir grid
    - Incluir/excluir guías
- Vista previa en tiempo real en el diálogo
- Nombre de archivo sugerido: `{proyecto}_{fecha}_{escala}.png`
- Acceso desde: Menú Archivo > Exportar a PNG... (Ctrl+Shift+E)

**Algoritmo suggested**:
1. Calcular bounding box de elementos a exportar
2. Agregar márgenes configurables
3. Crear QImage del tamaño apropiado
4. Renderizar scene o selection con renderizador
5. Aplicar fondo si no es transparente
6. Guardar a PNG con compresión configurada

**Archivos relacionados**: `export_service.py` (nuevo método), `main_window.py` (menú)

---

## 📊 Orden de Implementación Recomendado

| Orden | Tipo | Feature | Estado |
|-------|------|---------|--------|
| 1 | Bug | Fix altura conexiones | ✅ Completado |
| 2 | Bug | Arreglar PDF | Pendiente |
| 3 | Arquitectura | Columna propiedades general | ✅ Completado |
| 4 | UI | Botón "Más opciones" | ✅ Completado |
| 5 | UI | Color fondo con tema | ✅ Completado |
| 6 | Conexiones | Grosor/color nodos | ✅ Completado |
| 7 | Conexiones | Texto en conexiones | ⚠️ Parcial |
| 8 | Beats | Markdown | Pendiente |
| 9 | Beats | Imágenes | Pendiente |
| 10 | Nueva | Shapes | Pendiente |
| 11 | Sistema | Asociar archivos | ✅ Completado v1.0.22 |
| 12 | Export | Exportar a PNG | Pendiente |

---

## Roadmap

### v1.0 ✅ (Core Beat Board)
- Canvas infinito, beats, conexiones bezier, temas, i18n (EN/ES/FR/DE), spellcheck, persistencia, exportación

### v1.1 (Outline Integration) - Pendiente
- Outline Editor jerárquico
- Estructura de actos
- Plantillas (Save the Cat, Trilogía...)
- Send to Script (exportar a guión)
- Page Goals
- Búsqueda avanzada

### v1.2 (Collaboration) - Pendiente
- Historial de versiones
- Imágenes en beats
- Integración FDX (Final Draft)
- Filtros por color
- Modo presentación

### v1.5 (Pro Features) - Pendiente
- Múltiples tableros por proyecto
- Story Map visual
- Estadísticas
- Macros
- Plugins/Scripts
- Exportación (MD, HTML, JSON)

### v2.0 (Cloud + AI) - Futuro
- Sincronización en nube
- Colaboración real-time
- AI Beat Suggestions
- AI Story Analysis
- App móvil / Web

---

## Arquitectura

```
beatboard/
├── app/          # main.py, application.py, resources.py
├── core/         # beat.py, connection.py, project.py, constants.py
├── ui/           # main_window.py, theme_manager.py, canvas/, dialogs/, widgets/
├── services/     # autosave_service.py, export_service.py
├── i18n/         # traducciones (en, es, fr, de)
└── tests/        # pytest (34 tests)
```

---

## Datos

### Beat
- id, title, content, color (hex), position, size, timestamps

### Connection
- id, source_beat_id, target_beat_id, color

### Project
- id, name, beats[], connections[], canvas_state

### Formato .bbp (JSON)
```json
{"version": "1.0", "project": {...}, "canvas": {...}, "beats": [...], "connections": [...]}
```

---

## Compilación
- **Python**: 3.10 (NO usar 3.12+ por GLIBC)
- **Docker**: Ubuntu 22.04 + Python 3.10
- **GitHub Actions**: workflows en .github/workflows/
- **Output**: `build/BeatBoard-*-portable`, `*.AppImage`

---

## Issues Conocidos
1. GLIBC error → usar Python 3.10
2. Icono AppImage no visible → usar linuxdeploy en lugar de appimagetool

---

## Ejecución
```bash
source .venv/bin/activate
python -m beatboard.app.main
pytest beatboard/tests/ -v
```
