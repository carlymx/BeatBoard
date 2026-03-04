# BeatBoard - Estado del Desarrollo

## Fecha: 4 de Marzo de 2026

## Progreso Actual

### v1.0.17 - EN DESARROLLO

BeatBoard versión 1.0.17 con mejoras de visibilidad y contenido.

---

### Cambios v1.0.17

#### ✨ Mejoras en la Interfaz de Usuario
- [x] **Fix truncamiento de contenido en beats**:
  - Los beats ahora expanden su altura automáticamente para mostrar todo el contenido
  - Eliminada restricción de altura fija que causaba que el texto se cortara
  - La altura se ajusta dinámicamente al contenido del beat
- [x] **Bordes de selección más gruesos**:
  - Aumentado grosor de borde de selección de beats de 2px a 4px
  - Aumentado grosor de borde de selección de conexiones de 2px a 5px
  - Mejor visibilidad de elementos seleccionados
- [x] **Indicador de color en panel de propiedades**:
  - Nuevo widget que muestra el color actualmente seleccionado
  - Se actualiza en tiempo real al cambiar color con teclas numéricas
  - Ubicado junto al selector de color en el panel de propiedades

#### 🔧 Cambios Técnicos
- [x] **`beat_item.py`**:
  - Eliminada restricción de altura fija en `boundingRect()` y `paint()`
  - Ajuste dinámico de altura basado en contenido y título
  - Borde de selección más grueso (4px)
- [x] **`connection_item.py`**:
  - Borde de selección más grueso (5px) para mejor visibilidad
- [x] **`properties_panel.py`**:
  - Añadido widget indicador de color (`color_indicator`)
  - Función `_update_color_indicator()` para actualización en tiempo real
  - Conexión con señal de cambio de color del beat
- [x] **`beat_board_view.py`**:
  - Emitir señal `beat_color_changed` cuando se cambia color con teclas 1-0
  - Permite que el panel de propiedades actualice el indicador
- [x] **`main_window.py`**:
  - Conectar señal `beat_color_changed` al panel de propiedades

---

### v1.0.16 - RELEASE ✅

BeatBoard versión 1.0.16 con corrección de icono y mejoras varias.

---

### Cambios v1.0.16

#### ✨ Nuevas Funcionalidades
- [x] **Menú Preferencias**:
  - Nuevo menú "Preferencias" antes del menú "Ayuda"
  - Movidas las opciones de Tema, Recordar tamaño y color, Idioma y Corrección Ortográfica
- [x] **Opciones de Configuración de Backups**:
  - Backup al abrir proyecto (activado por defecto)
  - Máximo de backups (1-20, por defecto 10)
  - Intervalo de auto-guardado configurable (1, 2, 5, 10, 15, 30 minutos)
  - Auto-guardado habilitado (activado por defecto)
  - Botón para limpiar backups del proyecto actual
- [x] **Copias de seguridad diferenciadas**:
  - Los backups de auto-guardado se nombran con sufijo `_auto_`
  - Los backups al abrir se nombran con sufijo `_open_`
  - Persistencia de preferencias entre sesiones

#### 🔧 Cambios Técnicos
- [x] **`theme_manager.py`**:
  - Nuevas preferencias: `backup_on_open`, `max_backups`, `autosave_interval`, `autosave_enabled`
  - Getters y setters para las nuevas preferencias
  - Valores por defecto: backup_on_open=True, max_backups=10, autosave_interval=10min, autosave_enabled=True
- [x] **`autosave_service.py`**:
  - Carga de preferencias desde theme_manager
  - Métodos: `save_backup_on_open()`, `cleanup_all_backups()`, `set_max_backups()`, `set_backup_on_open()`, `set_enabled()`
  - Identificadores diferenciados para backups (auto vs open)
- [x] **`main_window.py`**:
  - Reestructuración de menús (Ver ahora solo tiene opciones de vista)
  - Menú Preferencias con todas las opciones
  - Nuevos métodos: `_load_backup_preferences()`, `_on_backup_on_open_changed()`, `_on_autosave_enabled_changed()`, `_on_autosave_interval_changed()`, `_on_max_backups_changed()`, `_on_cleanup_backups()`
  - Backup automático al abrir proyecto

#### 🌐 Internacionalización
- [x] Nuevas traducciones en los 4 idiomas:
  - `menu_preferences`: "Preferencias" / "Preferences" / "Préférences" / "Einstellungen"
  - `backup_options`: "Opciones de copia de seguridad" / "Backup Options" / "Options de sauvegarde" / "Sicherungsoptionen"
  - `backup_on_open`: "Crear backup al abrir proyecto"
  - `max_backups`: "Máximo de backups"
  - `autosave_enabled`: "Auto-guardado habilitado"
  - `autosave_interval`: "Intervalo de auto-guardado"
  - `cleanup_backups`: "Limpiar backups..."
  - Intervalos: 1, 2, 5, 10, 15, 30 minutos

#### 🔧 Traducciones de UI
- [x] **Etiquetas de beats traducidas**:
  - "Sin título" → "Untitled" / "Sans titre" / "Ohne Titel"
  - "Contenido del beat..." → "Beat content..." / "Contenu du beat..." / "Beat-Inhalt..."
- [x] **Etiquetas de colores traducidas**:
  - Panel de propiedades ahora muestra nombres de colores traducidos
  - Colores personalizados: "Custom {num} ({color})" en cada idioma
- [x] **Exportación**:
  - PDF y texto ahora usan traducciones para "Sin título"

#### 🔧 Icono de aplicación (Cross-platform)
- [x] **Fix icono en barra de tareas Windows**:
  - Añadido `AppUserModelID` con `ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID()`
  - Evita que Windows agrupe la app con otros procesos Python
- [x] **Carga explícita de icono**:
  - Nuevo módulo `beatboard/app/resources.py` con funciones `get_resource_path()`, `get_app_icon_path()`, `fix_windows_taskbar_icon()`
  - `MainWindow` ahora carga el icono explícitamente con `setWindowIcon()`
  - Funciona en desarrollo y en ejecutable (soporta `sys._MEIPASS`)
- [x] **Spec files actualizados**:
  - `beatboard-windows.spec`: Icono .ico y .png en datas
  - `beatboard-linux.spec`: Icono .png en datas
  - `beatboard-macos.spec`: Iconos .icns y .png en datas

---

### v1.0.14 - RELEASE ✅

BeatBoard versión 1.0.14 con mejoras en el sistema de colores personalizables.

---

### Cambios v1.0.14

#### ✨ Mejoras en la Interfaz de Usuario
- [x] **Eliminado botón "Más colores"**:
  - El botón no funcionaba correctamente y ha sido eliminado
  - Simplificación de la interfaz
- [x] **Cambiado Alt+Click a Doble-Click**:
  - Personalizar colores ahora con Doble-Click (mejor UX)
  - Tooltips actualizados para reflejar el cambio
- [x] **Etiqueta actualizada**:
  - "Personalizados:" → "Personalizados (Doble-Click para cambiar):"
  - Mejor indicación de la funcionalidad
- [x] **Dropdown del panel de propiedades mejorado**:
  - Ahora muestra colores personalizados reales con sus valores hexadecimales
  - Se actualiza dinámicamente cuando los colores cambian
  - Formato: "Personalizado 1 (#FF5733)"

#### 🔧 Cambios Técnicos
- [x] **`beat_editor_dialog.py`**:
  - Eliminado botón "Más colores" y función `_select_any_color`
  - Cambiado `mousePressEvent` a `mouseDoubleClickEvent`
  - Actualizados tooltips y etiquetas
- [x] **`properties_panel.py`**:
  - Función `_update_custom_colors_in_combo()` para actualización dinámica
  - ComboBox muestra valores hexadecimales reales
  - Actualización automática al establecer beat

#### ✨ Nuevas Funcionalidades
- [x] **Sistema de colores hexadecimales**:
  - Todos los colores ahora se manejan como hexadecimales (#FFFFFF)
  - Compatibilidad con beats antiguos (nombres → hexadecimales)
  - Función `get_valid_beat_color()` para conversión automática
- [x] **Botón "Más Colores..." corregido**:
  - Ahora funciona correctamente
  - Selecciona cualquier color hexadecimal
  - No guarda como color personalizado (es para color único)
- [x] **3 colores personalizables (8, 9, 0)**:
  - Inicialmente blancos (#FFFFFF)
  - Personalizables con Alt+Click
  - Guardados en `preferences.json`
  - Persistencia entre sesiones
- [x] **Atajos de teclado extendidos (1-0)**:
  - Teclas 1-7: colores predefinidos
  - Teclas 8, 9, 0: colores personalizables
  - Compatible con beats seleccionados múltiples
- [x] **Sistema de persistencia**:
  - Colores personalizados guardados en `preferences.json`
  - Cargados automáticamente al iniciar
  - Actualizados en tiempo real

#### 🔧 Cambios Técnicos
- [x] **`constants.py`**: Nuevo sistema de colores hexadecimales
- [x] **`beat_item.py`**: Renderizado desde hexadecimales
- [x] **`beat_editor_dialog.py`**: Diálogo con colores personalizables
- [x] **`beat_board_view.py`**: Atajos de teclado 1-0
- [x] **`theme_manager.py`**: Manejo de colores personalizados
- [x] **`properties_panel.py`**: ComboBox actualizado
- [x] **`beat_defaults.py`**: Color por defecto hexadecimal

#### 📦 Archivos Generados v1.0.14
- `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.14_portable` (58 MB)
- `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.14.AppImage` (72 MB)
- Compilar con GitHub Actions (workflow build-linux.yml) para máxima compatibilidad

---

### v1.0.13 - RELEASE ✅

BeatBoard versión 1.0.13 con indicador visual para modo conexión.

---

### Cambios v1.0.13

#### ✨ Nuevas Funcionalidades
- [x] **Indicador visual para Modo Conexión**:
  - Banner translúcido en la parte inferior del lienzo
  - Muestra mensaje "Modo 'Conexión' Activado. ESC para Salir"
  - Traducciones en 4 idiomas (ES, EN, FR, DE)
- [x] **Fix cursor en Modo Conexión**:
  - Usar `viewport().setCursor()` en lugar de `setCursor()`
  - El cursor cruz ahora tiene prioridad sobre los cursores de BeatItem
  - Se muestra correctamente cuando el modo conexión está activo

#### 📦 Archivos Generados v1.0.13
- `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.13_portable` (58 MB)
- `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.13.AppImage` (72 MB)
- Compilar con GitHub Actions (workflow build-linux.yml) para máxima compatibilidad

---

### v1.0.12 - RELEASE ✅

BeatBoard versión 1.0.12 con optimización de spellcheck y checkbox mostrar título.

---

### Cambios v1.0.12

#### ✨ Nuevas Funcionalidades
- [x] **Optimización de spellcheck**:
  - Carga diferida de diccionarios (lazy loading)
  - Los diccionarios solo se cargan cuando se habilita spellcheck
  - Mejor tiempo de inicio de la aplicación
- [x] **Checkbox "Mostrar título"**:
  - Checkbox en el panel de propiedades para mostrar/ocultar título de cada beat
  - Por defecto está activado
  - Se guarda con el proyecto

#### 📦 Archivos Generados v1.0.12
- `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.12_portable` (58 MB)
- `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.12.AppImage` (72 MB)
- Compilar con GitHub Actions (workflow build-linux.yml) para máxima compatibilidad

---

### Cambios v1.0.10

#### ✨ Nuevas Funcionalidades
- [x] **Corrección ortográfica**: 
  - Integración de diccionarios Hunspell (es_ES, en_US, fr_FR, de_DE)
  - Subrayado rojo en palabras mal escritas
  - Menú contextual con sugerencias
  - diccionarios de usuario por idioma
- [x] **Menú Ver > Corrección ortográfica**:
  - Habilitar/deshabilitar spellcheck
  - Selección de idioma de diccionario
- [x] **Diccionarios de usuario**: 
  - Ubicación: `~/.config/beatboard/user_dictionary_{idioma}.txt`
  - Separados por idioma

#### 📦 Archivos Generados v1.0.10
- `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.10_portable` (58 MB)
- `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.10.AppImage` (72 MB)
- Compilar con GitHub Actions (workflow build-linux.yml) para máxima compatibilidad

**IMPORTANTE: Compilar siempre con Python 3.10** para compatibilidad máxima con sistemas antiguos (GLIBC 2.31+).

---

### v1.0.7 - RELEASE ✅

BeatBoard versión 1.0.7 con icono personalizado y rutas cross-platform.

---

### Cambios v1.0.7

#### ✨ Nuevas Funcionalidades
- [x] **Icono personalizado**: Icono de aplicación embebido en el ejecutable Windows
- [x] **Rutas cross-platform**: 
  - Windows: `%APPDATA%\BeatBoard\`
  - macOS: `~/Library/Application Support/BeatBoard`
  - Linux: `~/.config/beatboard`
- [x] **Workflow CI**: Compilación automática de ejecutable Windows con GitHub Actions

#### 📦 Archivos Generados v1.0.7
- `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.7_portable` (58 MB)
- `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.7.AppImage` (58 MB)
- `dist/BeatBoard.exe` (Windows, vía GitHub Actions)

**Nota**: Compilados con Python 3.10 para máxima compatibilidad (GLIBC 2.31+)

---

### Cambios v1.0.1

#### 🔧 Correcciones
- [x] **Iconos de toolbar**: Ahora se cargan desde el proyecto en lugar de usar QIcon.fromTheme
- [x] **Iconos por tema**: Iconos claros para tema oscuro, iconos oscuros para tema claro
- [x] **Compatibilidad Linux**: Compilación con Ubuntu 22.04 (GLIBC 2.31) para máxima compatibilidad
  - Compatible con: Ubuntu 20.04+, Linux Mint 20+, Debian 11+, Fedora 34+
- [x] **Archivos generados**:
  - `dist/BeatBoard-x86_64-Ubuntu22-v5.AppImage` (57 MB)
  - `output/BeatBoard-ubuntu22` (ejecutable portable)

---

### Funcionalidades Implementadas (v1.0)

#### ✅ Setup y Estructura
- [x] Entorno configurado con PySide6
- [x] Estructura de proyecto completa
- [x] MainWindow con menú y toolbar
- [x] Sistema de logging

#### ✅ Canvas Básico
- [x] BeatBoardScene y BeatBoardView
- [x] BeatItem como QGraphicsObject
- [x] Zoom con scroll de ratón (Ctrl+Scroll)
- [x] Paneo con tecla Espacio
- [x] Creación de beat con doble clic
- [x] **Coordenadas del cursor**: El centro del lienzo es (0,0)
- [x] **Barra de estado**: Muestra coordenadas del cursor en tiempo real
- [x] **Punto central**: Guía visual en el centro (0,0)
- [x] **Botón centrar**: Toolbar para centrar vista en el origen

#### ✅ Interactividad
- [x] **Edición de beats**: Doble clic abre diálogo para editar título, contenido y color
- [x] **Drag & drop**: Arrastrar beats libremente
- [x] **Selección**: Selección única y múltiple
- [x] **Menú contextual**: Clic derecho con opciones editar/eliminar
- [x] **Eliminación**: Delete/Supr o menú contextual

#### ✅ Sistema de Conexiones
- [x] ConnectionItem (QGraphicsPathItem)
- [x] Modo de conexión en toolbar (botón "Conectar")
- [x] Líneas curvas bezier entre beats
- [x] Actualización automática de líneas al mover beats
- [x] Colores para conexiones

#### ✅ Tema y Personalización
- [x] Sistema de temas (claro/oscuro/sistema)
- [x] Detección automática del tema del sistema
- [x] **Temas múltiples**:
  - Claros: Claro, Solarized Light, GitHub Light, PaperColor
  - Oscuros: Oscuro, Dracula, Nord, One Dark, Material Dark
- [x] Paleta de colores predefinidos para beats
- [x] Color de fondo del canvas (predefinidos + personalizado)
- [x] Cuadrícula opcional
- [x] Tamaño de cuadrícula (50, 100, 150, 200, 250)
- [x] Color de cuadrícula (auto, predefinidos, personalizado)

#### ✅ Internacionalización (i18n)
- [x] **Sistema de traducciones**: Estructura en `beatboard/i18n/`
- [x] **Idiomas disponibles**: Inglés, Español, Francés, Alemán
- [x] **Detección de idioma del sistema**: QLocale para detectar idioma
- [x] **Menú de idioma**: En Ver > Idioma
- [x] **Preferencia persistente**: Se guarda en preferences.json
- [x] **Notificación de reinicio**: Al cambiar idioma

#### ✅ Deshacer/Rehacer
- [x] QUndoStack con comandos para:
  - [x] Crear beat
  - [x] Eliminar beat
  - [x] Mover beat
  - [x] Editar beat (título, contenido, color)
  - [x] Crear conexión
  - [x] Eliminar conexión

#### ✅ Atajos de Teclado
- [x] Ctrl+Z: Deshacer
- [x] Ctrl+Y: Rehacer
- [x] Ctrl+A: Seleccionar todo
- [x] Ctrl+C: Copiar beats seleccionados
- [x] Ctrl+X: Cortar beats seleccionados
- [x] Ctrl+V: Pegar beats copiados
- [x] Ctrl+Home: Traer al frente
- [x] Ctrl+End: Enviar al fondo
- [x] Ctrl+PageUp: Subir uno
- [x] Ctrl+PageDown: Bajar uno
- [x] Escape: Deseleccionar todo / Cancelar modo conexión
- [x] Delete/Supr: Eliminar beat o conexión seleccionada
- [x] Espacio: Modo paneo (mantener presionado)
- [x] Ctrl+0: Ajustar a contenido
- [x] Ctrl++: Acercar
- [x] Ctrl+-: Alejar
- [x] 1-8: Cambiar color de beat seleccionado
- [x] **Menú Ayuda → Atajos de teclado**: Ventana con lista completa

#### ✅ Configuración de Defaults
- [x] **Recordar tamaño y color**: Opción en menú Ver para activar/desactivar
  - Cuando está activado, el último beat creado/editado define el color y tamaño del siguiente
  - Se activa desde: Ver → Recordar tamaño y color del último beat
  - El tamaño se memoriza al redimensionar un beat
  - El color se memoriza al editar un beat (doble clic)

#### ✅ Persistencia y Exportación
- [x] Auto-guardado cada 5 minutos
- [x] Guardar/Cargar proyectos (.bbp)
- [x] Exportación PDF
- [x] Exportación texto plano

#### ✅ Preferencias de Usuario
- [x] **Configuración persistente**: Se guarda en `~/.config/beatboard/preferences.json`
- [x] Tema seleccionado
- [x] Color de fondo del canvas
- [x] Mostrar/ocultar cuadrícula
- [x] Tamaño de celda de cuadrícula
- [x] Color de cuadrícula (incluye personalizado)
- [x] Idioma seleccionado
- [x] Recordar tamaño y color del último beat

#### ✅ Panel de Propiedades
- [x] Panel lateral para editar beats
- [x] Sincronización con selección

---

### Tareas Pendientes para v1.0

#### 🔧 Bugs/Correcciones
- [x] Bug: Conexiones no se cargaban al abrir proyecto - FIXED
- [x] Bug: Z-order de beats no se guardaba/cargaba - FIXED

#### 📋 Mejoras
- [x] Actualizado "Acerca de" con info del autor
- [x] README.md y README_ES.md creados
- [x] Archivo .desktop creado
- [x] AppImage generado
- [x] Compilación Linux (AppImage/Package)
- [x] Compilación macOS (build/mac/)
- [x] Compilación Windows (build/win/)
- [x] Compilación Flatpak/Flathub (build/flatpak/)

#### 📦 Empaquetado
- [x] Ejecutable generado con PyInstaller (dist/BeatBoard)
- [x] Versión actualizada a 1.0.0
- [x] Icono de aplicación generado (beatboard/ui/icons/)
- [x] AppImage Linux (dist/BeatBoard-x86_64.AppImage)
- [x] README.md (inglés)
- [x] README_ES.md (español)
- [x] GitHub workflow para Windows

---

### Archivos del Proyecto

#### Core
| Archivo | Descripción |
|---------|-------------|
| `beatboard/core/beat.py` | Entidad Beat |
| `beatboard/core/connection.py` | Entidad Connection |
| `beatboard/core/project.py` | Entidad Project |
| `beatboard/core/constants.py` | Constantes globales |
| `beatboard/core/beat_defaults.py` | Valores por defecto |

#### UI
| Archivo | Descripción |
|---------|-------------|
| `beatboard/ui/main_window.py` | Ventana principal |
| `beatboard/ui/theme_manager.py` | Gestor de temas |
| `beatboard/ui/undo_commands.py` | Comandos undo/redo |
| `beatboard/ui/canvas/beat_board_view.py` | Vista del canvas |
| `beatboard/ui/canvas/beat_board_scene.py` | Escena del canvas |
| `beatboard/ui/canvas/beat_item.py` | Item de beat |
| `beatboard/ui/canvas/connection_item.py` | Item de conexión |
| `beatboard/ui/dialogs/beat_editor_dialog.py` | Editor de beat |
| `beatboard/ui/widgets/properties_panel.py` | Panel de propiedades |

#### Services
| Archivo | Descripción |
|---------|-------------|
| `beatboard/services/autosave_service.py` | Auto-guardado |
| `beatboard/services/export_service.py` | Exportación PDF/texto |

#### Tests
| Archivo | Tests |
|---------|-------|
| `beatboard/tests/test_beat.py` | 7 tests |
| `beatboard/tests/test_connection.py` | 4 tests |
| `beatboard/tests/test_project.py` | 11 tests |
| `beatboard/tests/test_undo.py` | 12 tests |
| **Total** | **34 tests** |

#### i18n (Internacionalización)
| Archivo | Descripción |
|---------|-------------|
| `beatboard/i18n/__init__.py` | Gestor de LocaleManager |
| `beatboard/i18n/locales/__init__.py` | Funciones de carga de locale |
| `beatboard/i18n/locales/en.py` | Traducciones inglés |
| `beatboard/i18n/locales/es.py` | Traducciones español |
| `beatboard/i18n/locales/fr.py` | Traducciones francés |
| `beatboard/i18n/locales/de.py` | Traducciones alemán |

---

## Cómo Ejecutar

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar aplicación
python -m beatboard.app.main

# Ejecutar tests
python -m pytest beatboard/tests/ -v
```

---

## Problemas Conocidos y Soluciones

### Error: GLIBC_ABI_GNU2_TLS not found

**Síntoma:**
```
[PYI-14896:ERROR] Failed to load Python shared library '/tmp/_MEIxxxxx/libpython3.14.so.1.0': 
/lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_ABI_GNU2_TLS' not found
```

**Causa:** Se compiló con Python 3.14 (versión muy reciente), que requiere GLIBC 2.34+.

**Solución:** Usar Python 3.10 o 3.11 para compilar. Actualizar el Dockerfile:

```dockerfile
# Usar Python 3.10 específico en lugar de python3 del sistema
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.10 python3.10-venv python3.10-dev
RUN ln -sf /usr/bin/python3.10 /usr/bin/python3
```

**Versiones compatibles:**
- Ubuntu 20.04+: Python 3.8-3.10
- Ubuntu 22.04: Python 3.10 (RECOMENDADO)
- Linux Mint 22.2: Python 3.11

**Regla:** Usar siempre Python 3.10 o 3.11 para máxima compatibilidad.

### Icono de AppImage no se muestra en el explorador

**Síntoma:** El icono no aparece en el explorador de archivos (Nemo, Dolphin, Nautilus).

**Solución probable:** Usar `linuxdeploy` en lugar de `appimagetool`:
```bash
./linuxdeploy-x86_64.AppImage --appdir AppDir -i beatboard.png -d beatboard.desktop --plugin qt --output appimage
```

**Estructura requerida del AppDir:**
```
AppDir/
├── AppRun                    # Script que lanza la app
├── beatboard.desktop         # Archivo de escritorio
├── beatboard.png             # Icono en raíz (OBLIGATORIO)
└── usr/share/icons/hicolor/  # Iconos en múltiples resoluciones
    ├── 256x256/apps/beatboard.png
    ├── 128x128/apps/beatboard.png
    ├── 64x64/apps/beatboard.png
    ├── 32x32/apps/beatboard.png
    └── 16x16/apps/beatboard.png
```

**Archivo `.desktop` debe tener:**
```ini
[Desktop Entry]
Name=BeatBoard
Exec=AppRun %U
Icon=beatboard
Type=Application
Categories=Office;
```

**Nota:** Algunos gestores de archivos (Nemo, Dolphin) pueden requerir daemon de integración como `appimageaged` o **AppImageLauncher** para mostrar el icono.

---

## Notas

- Los errores de LSP (type hints) son falsos positivos - el código funciona correctamente
- Tema oscuro detectado automáticamente del sistema
- Conexiones entre beats funcionan con líneas curvas bezier
- El foco de teclado está configurado para capturar Delete/Supr correctamente
- Configuración de usuario en `~/.config/beatboard/preferences.json`
- Iconos de toolbar embebidos en el ejecutable (`beatboard/ui/icons/toolbar_*`)
- Compilación con Ubuntu 22.04 para compatibilidad máxima
- Sistema i18n con soporte para EN, ES, FR, DE
- Idioma del sistema detectado automáticamente
- Grid color con opción de color personalizado
- Rutas cross-platform:
  - Windows: `%APPDATA%\BeatBoard\`
  - macOS: `~/Library/Application Support/BeatBoard`
  - Linux: `~/.config/beatboard`

---

## Compilación del Proyecto

### Requisitos

- **Sistema**: Ubuntu 22.04 LTS con Python 3.10
- **Herramientas**: Podman o Docker
- **Python**: 3.10 (IMPORTANTE: No usar 3.12+)

### GitHub Actions (Recomendado)

Para compilar automáticamente con GitHub Actions:

1. Ir a **Actions** en el repositorio
2. Ejecutar el workflow **Build Linux Executable**
3. Descargar los artefactos generados

Los workflows disponibles son:
- `build-linux.yml` - Linux (usa Docker con Python 3.10)
- `build-macos.yml` - macOS
- `build-windows.yml` - Windows

### Linux (AppImage/Package)

#### Método 1: GitHub Actions (Automático)

```bash
# En GitHub:
# 1. Ir a Actions > Build Linux Executable
# 2. Click en "Run workflow"
# 3. Descargar artefactos: BeatBoard-Linux
```

#### Método 2: Docker/Podman local

```bash
# 1. Navegar al directorio del proyecto
cd /path/to/BeatBoard

# 2. Construir la imagen
podman build -t beatboard-builder:latest -f build/Dockerfile .

# 3. Extraer los archivos generados
podman run --rm -v $(pwd)/build:/output:Z beatboard-builder:latest \
    cp -r /build/output/BeatBoard-portable /output/

# 4. Crear AppImage
cd build
wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
    -O appimagetool
chmod +x appimagetool
mkdir -p AppDir/usr/bin
cp ../dist/BeatBoard AppDir/usr/bin/beatboard
chmod +x AppDir/usr/bin/beatboard
# Crear AppRun, desktop file e icono...
./appimagetool AppDir BeatBoard-x86_64.AppImage
```

#### Método 2: Flatpak (para Flathub)

```bash
# Instalar Flatpak y SDK
sudo apt install flatpak flatpak-builder
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install flathub org.freedesktop.Platform//23.08 org.freedesktop.Sdk//23.08

# Compilar
cd BeatBoard/build/flatpak
flatpak-builder --user --install build com.beatboard.BeatBoard.json
```

Los archivos de configuración Flatpak están en `build/flatpak/`:
- `com.beatboard.BeatBoard.json` - Manifiesto
- `com.beatboard.BeatBoard.desktop` - Entrada de escritorio
- `com.beatboard.BeatBoard.metainfo.xml` - Metadatos AppStream
- `README_FLATPAK.md` - Instrucciones completas

### macOS

```bash
cd BeatBoard/build/mac
chmod +x build_mac.sh
./build_mac.sh
```

Salida: `build/mac/output/BeatBoard.app`

### Windows

```powershell
cd BeatBoard\build\win
.\build_win.ps1
```

Salida: `build\win\output\BeatBoard.exe`

### Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.5_portable` | Ejecutable portable Linux (58 MB) |
| `build/BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.5.AppImage` | AppImage Linux (58 MB) |
| `build/mac/output/BeatBoard.app` | Bundle macOS |
| `build/win/output/BeatBoard.exe` | Ejecutable Windows |
| `build/flatpak/` | Archivos para Flatpak/Flathub |

### Compatibilidad de Binarios

Los binarios compilados con Ubuntu 22.04 son compatibles con:

- Ubuntu 20.04+
- Linux Mint 20+
- Debian 11+
- Fedora 34+
- openSUSE 15.4+

### Notas sobre el Spec File

El archivo `beatboard.spec` está configurado para detectar automáticamente la estructura del proyecto:

- **Docker**: Copia `beatboard/` y `beatboard.spec` al contenedor
- **Local**: Usa la estructura del proyecto directamente

### Iconos de la Toolbar

Los iconos de la toolbar están embebidos en el proyecto:
- `beatboard/ui/icons/toolbar/` - Iconos originales
- `beatboard/ui/icons/toolbar_light/` - Iconos claros (para tema oscuro)
- `beatboard/ui/icons/toolbar_dark/` - Iconos oscuros (para tema claro)

El código en `main_window.py` detecta automáticamente el tema y usa los iconos apropiados.
