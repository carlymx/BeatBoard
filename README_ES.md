# BeatBoard

[📖 Read in English](./README.md)

<!-- Sección de Badges -->
![Licencia](https://img.shields.io/badge/licencia-MIT%20(NC)-blue.svg)
![Documentación](https://img.shields.io/badge/docs-CC%20BY--NC--SA%204.0-green.svg)
![Versión](https://img.shields.io/badge/versión-1.0.29-green.svg)
![Plataforma](https://img.shields.io/badge/plataforma-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)
![Qt](https://img.shields.io/badge/Qt-PySide6-purple.svg)

![main](./imgs/beatboard_002.png)

## Descripción

BeatBoard es una aplicación de escritorio de pizarra virtual para escritores, inspirada en el Beat Board de Final Draft. Ya seas guionista, escritor de relatos o novelas, BeatBoard te proporciona un lienzo infinito donde puedes crear, organizar y conectar "beats" - los bloques fundamentales de construcción de una historia.

Ya sea que estés delineando un guión cinematográfico, novela, relato corto o serie de TV, BeatBoard te ayuda a visualizar la estructura de tu historia con tarjetas de colores y líneas de flujo.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Instalación](#instalación)
- [Uso](#uso)
- [Manual de Usuario](./doc/manual_md/MANUAL_es.md)
- [Atajos de Teclado](#atajos-de-teclado)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Contribuir](#contribuir)
- [Licencia](#licencia)
- [Agradecimientos](#agradecimientos)

## Características

### Características Principales
- **Lienzo Infinito** - Desplazamiento y zoom en un espacio de trabajo ilimitado
- **Tarjetas de Beat** - Crea tarjetas coloreadas con título y contenido
- **Conexiones** - Une beats con líneas de flujo curvas bezier
- **Arrastrar y Soltar** - Organiza libremente los beats en el lienzo

### Productividad
- **Deshacer/Rehacer** - Soporte completo de historial para todas las operaciones
- **Copiar/Pegar** - Duplica beats con Ctrl+C / Ctrl+V
- **Orden Z** - Traer al frente, enviar atrás, mover arriba/abajo
- **Selección Múltiple** - Selecciona y mueve varios beats a la vez

### Personalización
- **9 Temas** - Temas claros y oscuros (Nord, Dracula, One Dark, etc.)
- **10 Colores de Beat** - 7 colores predefinidos + 3 colores personalizables
- **Colores Personalizados** - Doble-click para personalizar colores (teclas 8, 9, 0)
- **Fondo Personalizado** - Elige entre colores predefinidos o personalizados
- **Cuadrícula Opcional** - Mostrar/ocultar cuadrícula de alineación con tamaño y color personalizables

### Internacionalización
- **Soporte Multiidioma** - Disponible en Inglés, Español, Francés y Alemán
- **Detección de Idioma del Sistema** - Detecta automáticamente el idioma de tu sistema
- **Preferencia de Idioma Persistente** - Recuerda tu elección de idioma

### Exportar y Guardar
- **Archivos de Proyecto** - Guarda y carga archivos de proyecto .bbp
- **Auto-guardado** - Guardado automático cada 5 minutos
- **Exportar PDF** - Genera documentos PDF de tu beat board
- **Exportar Texto** - Exporta beats como texto plano

### Adicionales
- **Panel de Propiedades** - Edita propiedades del beat seleccionado
- **Barra de Estado** - Coordenadas del cursor en tiempo real
- **Punto Central** - Guía visual en el origen (0,0)

## Instalación

### Requisitos Previos
- Python 3.10 o superior
- PySide6

### Desde el Código Fuente

```bash
# Clonar el repositorio
git clone https://github.com/carlymx/BeatBoard.git
cd BeatBoard

# Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Instalar dependencias
pip install pyside6

# Ejecutar la aplicación
python -m beatboard.app.main
```

### Ejecutables Pre-construidos

Descarga desde la página de [Lanzamientos](https://github.com/carlymx/BeatBoard/releases) o compila desde el código fuente (ver abajo):

| Plataforma | Tipo | Archivo |
|------------|------|---------|
| Linux | AppImage | `BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.7.AppImage` |
| Linux | Portable | `BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.7_portable` |
| Windows | Ejecutable | `BeatBoard.exe` (vía GitHub Actions) |

### Requisitos del Sistema

- **Linux**: Ubuntu 20.04+, Linux Mint 20+, Debian 11+, Fedora 34+ (GLIBC 2.31+)

### Compilar desde el Código Fuente

Para compilar el ejecutable y AppImage tú mismo:

```bash
# 1. Navegar al directorio del proyecto
cd BeatBoard

# 2. Compilar con Docker/Podman (recomendado para máxima compatibilidad)
podman build -t beatboard-builder:latest -f build/Dockerfile .

# 3. Extraer los archivos generados
podman run --rm -v $(pwd)/build:/output:Z beatboard-builder:latest \
    cp -r /build/AppDir /output/ && cp /build/output/BeatBoard-portable /output/

# 4. Crear AppImage (requiere FUSE)
cd build
wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
chmod +x appimagetool
./appimagetool -s AppDir BeatBoard-x86_64.AppImage
```

Los archivos generados estarán en `build/`:
- `BeatBoard-portable` - Ejecutable portable
- `BeatBoard-x86_64.AppImage` - AppImage autocontenido

Ver `DESARROLLOActual.md` para instrucciones detalladas de compilación.

### Ejecutar AppImage (Linux)

```bash
chmod +x BeatBoard-x86_64.AppImage
./BeatBoard-x86_64.AppImage
```

## Uso

### Primeros Pasos

1. **Crear un Beat** - Doble clic en cualquier lugar del lienzo
2. **Editar un Beat** - Doble clic en un beat para abrir el editor
3. **Mover un Beat** - Clic y arrastra para reposicionar
4. **Conectar Beats** - Clic en "Conectar" en la barra de herramientas, luego clic en beat origen y destino

### Gestión de Beats

- **Eliminar**: Selecciona beat(s) y presiona Delete/Supr
- **Copiar**: Ctrl+C para copiar beats seleccionados
- **Pegar**: Ctrl+V para pegar beats copiados
- **Seleccionar Todo**: Ctrl+A para seleccionar todos los beats

### Trabajando con Conexiones

1. Clic en el botón "Conectar" en la barra de herramientas
2. Clic en el beat origen
3. Clic en el beat destino
4. Presiona Escape para salir del modo conexión

### Manual de Usuario

Para una guía completa de uso, consulta el manual en tu idioma:

- [Español](./doc/manual_md/MANUAL_es.md)
- [English](./doc/manual_md/MANUAL_en.md)
- [Français](./doc/manual_md/MANUAL_fr.md)
- [Deutsch](./doc/manual_md/MANUAL_de.md)

## Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| Ctrl+Z | Deshacer |
| Ctrl+Y | Rehacer |
| Ctrl+A | Seleccionar Todo |
| Ctrl+C | Copiar |
| Ctrl+X | Cortar |
| Ctrl+V | Pegar |
| Delete | Eliminar seleccionado |
| Ctrl+Home | Traer al Frente |
| Ctrl+End | Enviar al Fondo |
| Ctrl+PageUp | Mover Arriba |
| Ctrl+PageDown | Mover Abajo |
| Ctrl+0 | Ajustar al Contenido |
| Ctrl++ | Acercar |
| Ctrl+- | Alejar |
| Espacio | Modo desplazamiento (mantener) |
| Escape | Cancelar / Deseleccionar |
| 1-0 | Cambia el color de selección |
| C | Activa/desactiva modo conexión (sin selección) |

## Estructura del Proyecto

```
BeatBoard/
├── beatboard/
│   ├── app/              # Punto de entrada de la aplicación
│   │   ├── main.py
│   │   └── application.py
│   ├── core/             # Modelos de datos principales
│   │   ├── beat.py
│   │   ├── connection.py
│   │   ├── project.py
│   │   └── constants.py
│   ├── ui/               # Interfaz de usuario
│   │   ├── main_window.py
│   │   ├── theme_manager.py
│   │   ├── canvas/       # Componentes de vista gráfica
│   │   ├── dialogs/      # Ventanas de diálogo
│   │   └── widgets/      # Widgets personalizados
│   ├── services/         # Lógica de negocio
│   │   ├── autosave_service.py
│   │   └── export_service.py
│   └── tests/            # Pruebas unitarias
├── dist/                 # Ejecutables compilados
├── beatboard.spec        # Spec de PyInstaller
└── README.md
```

## Ejecutar Pruebas

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ejecutar todas las pruebas
python -m pytest beatboard/tests/ -v

# Ejecutar archivo de prueba específico
python -m pytest beatboard/tests/test_beat.py -v
```

## Contribuir

¡Las contribuciones son bienidas! Por favor, sigue estos pasos:

1. Haz fork del repositorio
2. Crea una rama de funcionalidad (`git checkout -b feature/funcionalidad-increible`)
3. Haz commit de tus cambios (`git commit -m 'Añadir funcionalidad increíble'`)
4. Haz push a la rama (`git push origin feature/funcionalidad-increible`)
5. Abre un Pull Request

## Licencia

Este proyecto utiliza **licencia dual**:

- **Código**: [Licencia MIT (No Comercial)](./LICENSE) - Ver archivo LICENSE
- **Documentación**: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) - Ver archivo LICENSE-DOCS

**Eres libre de:**
- Compartir — copiar y redistribuir el material
- Adaptar — remezclar, transformar y crear a partir del material

**Bajo los siguientes términos:**
- Atribución — Debes dar crédito apropiado
- NoComercial — No puedes usar el material para fines comerciales
- CompartirIgual — Si remezclas o transformas el material, debes distribuir tu contribución bajo la misma licencia

## Registro de Cambios

### v1.0.29 (2026-03-14)
- **Sistema ZIP para proyectos**: Formato .bbp cambiado de JSON plano a ZIP, permitiendo almacenar imágenes y recursos
- **Imágenes en canvas**: Nuevo tipo de elemento para insertar imágenes en el lienzo con movimiento y redimensionamiento
- **Carpetas temporales ocultas**: Datos del proyecto almacenados en carpetas `.{proyecto}_data` con limpieza automática
- **Persistencia de imágenes**: Las imágenes se guardan en `media/` dentro del ZIP y cargan correctamente al reabrir
- **Compatibilidad con versiones anteriores**: Los proyectos JSON antiguos se cargan automáticamente
- **Bug fixes**: Corrección de rutas de imágenes, duplicación de UUIDs, consistencia de identificadores

### v1.0.28 (2026-03-12)
- **Fix alineación vertical panel de propiedades**: Los widgets del panel de beats ahora se alinean en la parte superior (igual que conexiones)
- **Confirmación cambios no guardados en Nuevo Proyecto**: El botón "Nuevo" (Ctrl+N) ahora pregunta si guardar cambios antes de crear nuevo proyecto
- **Fix menú "Archivos recientes"**: Ahora muestra los archivos guardados al iniciar la aplicación
- **Nuevo menú "Manual" en Ayuda**: Opción "Abrir Manual" que abre documentación en el idioma actual, con submenú para otros idiomas

### v1.0.27 (2026-03-09)
- **Zoom de selección de área**: Nuevo modo de zoom que permite dibujar un rectángulo para hacer zoom al área seleccionada
- **Botón toolbar para zoom**: Nuevo icono "Zoom" entre zoom-in y fit
- **Atajo de teclado "Z"**: Activa el modo zoom de selección cuando no hay nada seleccionado
- **Fix banner modo conexión**: Arreglado el problema por el cual el banner no se mostraba
- **Atajos actualizados**: Añadidos "Z" (zoom) y "Ctrl+W" (cerrar proyecto) al diálogo de atajos
- **Descripciones de atajos corregidas**: Ahora indican "doble clic" para crear/editar beats
- **Fix paneo con teclado**: Arreglado el problema por el cual el paneo con Espacio no funcionaba correctamente

### v1.0.26 (2026-03-09)
- **Corrección de bugs en propiedades de conexión**: Solucionado problema donde la selección múltiple de conexiones no aplicaba cambios
- **Atajos de teclado extendidos**: Teclas 1-0 ahora cambian colores tanto para beats COMO para conexiones
- **Personalización de colores de conexión**: Añadidos colores personalizados (8, 9, 0) a los widgets de propiedades de conexión
- **Nuevo color de conexión**: Añadido 7º color predefinido "Gris Oscuro" (#616161)
- **Atajo para modo conexión**: Añadida tecla "C" para activar/desactivar modo conexión cuando no hay nada seleccionado
- **Descripciones de atajos actualizadas**: Cambiado "Cambiar color del beat" a "Cambiar color de la selección" en todos los idiomas
- **Actualizaciones en tiempo real de propiedades**: El panel de propiedades de conexión se actualiza al usar atajos de teclado
- **Renderizado de colores mejorado**: Corregida visualización de colores hexadecimales para conexiones personalizadas

### v1.0.25 (2026-03-08)
- **Columna de propiedades general**: El panel de propiedades ahora funciona para beats, conexiones y selección múltiple
- **Propiedades de conexión**: Nuevos campos para color de línea, grosor (0.5-10px) y formas de terminadores (círculo, cuadrado, flecha, ninguno)
- **Soporte para selección múltiple**: Cambiar propiedades comunes para múltiples beats o conexiones simultáneamente
- **Visualización de estados mixtos**: Combos sin selección y checkboxes parcialmente marcados cuando los valores difieren
- **Renderizado de terminadores**: Terminadores visuales en extremos de líneas según la forma seleccionada
- **Actualizaciones en tiempo real**: Los indicadores de color se actualizan al usar atajos de teclado (1-0)

### v1.0.21 (2026-03-08)
- **Botón "Abrir editor completo"**: Nuevo botón en el panel de propiedades para abrir el editor de beats completo con formato rico

### v1.0.20 (2026-03-08)
- **Color de fondo con Tema**: Cada tema ahora tiene colores de fondo y cuadrícula asociados que se aplican automáticamente

### v1.0.19 (2026-03-06)
- **Sistema de Z-Order corregido**: Cada beat nuevo se crea con z = número total de beats + 1
- **Posiciones Z únicas y consecutivas**: Los beats ocupan posiciones únicas (1, 2, 3...)
- **Movimiento Z mejorado**: Subir/bajar beats ahora intercambia posiciones con los beats adyacentes
- **Traer al frente/fondo**: Reordena toda la pila de beats correctamente
- **Debug visual de Z**: Muestra "z:X" sobre cada objeto (constante DEBUG_SHOW_Z_ORDER en constants.py)

### v1.0.17 (2026-03-04)
- **Mejor visibilidad de selección**: Bordes de selección más gruesos (4px beats, 5px conexiones) para mejor visibilidad
- **Contenido completo visible**: Los beats ahora expanden su altura automáticamente para mostrar todo el contenido sin truncar
- **Indicador de color en propiedades**: Nuevo widget que muestra el color actualmente seleccionado en tiempo real
- **Fix actualización de indicador**: El indicador de color se actualiza correctamente al usar teclas numéricas (1-0)

### v1.0.16 (2026-03-04)
- **Nuevo menú Preferencias**: Menú reorganizado con opciones de preferencias antes de Ayuda
- **Opciones de backup configurables**: Backup al abrir proyecto, máximo de backups, intervalo de auto-guardado
- **Traducciones completas**: Etiquetas de beats y colores traducidas a los 4 idiomas
- **Icono de aplicación corregido**: Solucionado problema de icono en barra de tareas/título de Windows

### v1.0.15 (2026-03-04)
- **Reestructuración completa del sistema de colores**: Todos los colores ahora usan formato hexadecimal (#FFFFFF)
- **Corregido botón "Más Colores..."**: Ahora funciona correctamente con colores personalizados
- **Añadidos 3 colores personalizables**: Colores personalizables 8, 9, 0 (inicialmente blancos)
- **Atajos de teclado extendidos**: Teclas 1-0 ahora cambian colores (1-7 predefinidos, 8-0 personalizables)
- **Compatibilidad con versiones anteriores**: Beats antiguos con nombres de color (amarillo, azul, etc.) siguen funcionando
- **Colores personalizados persistentes**: Guardados en preferences.json
- **Personalización de colores**: Alt+Click en colores personalizables para cambiarlos

### v1.0.13 (2026-03-03)
- Añadido indicador visual para Modo Conexión (banner translúcido en la parte inferior del lienzo)
- Corregido cursor que no se mostraba como cruz en Modo Conexión (prioridad de cursor del viewport)
- Añadidas traducciones para el banner de modo conexión en los 4 idiomas

### v1.0.12 (2026-03-03)
- Añadida casilla para mostrar/ocultar títulos de beats
- Corregida carga diferida del corrector ortográfico (diccionarios se cargan solo cuando se necesitan)
- Corregida comparación de estado de casillas en panel de propiedades

### v1.0.11 (2026-03-03)
- Optimizado el rendimiento del spellcheck con carga diferida de diccionarios
- Mejorado el tiempo de inicio al no cargar diccionarios hasta que se habilita el spellcheck
- Añadido checkbox "Mostrar título" en el panel de propiedades para beats individuales

### v1.0.10 (2026-02-28)
- Añadido soporte de corrección ortográfica para el contenido de beats
- Integrados diccionarios Hunspell (en, es, fr, de)
- Añadido menú de spellcheck en el menú Ver
- Añadida opción para diccionarios de usuario en ~/.config/beatboard/dictionaries/
- Añadido menú contextual con sugerencias al hacer clic derecho
- Añadido SpellCheckService para gestión de diccionarios
- Añadido SpellCheckHighlighter para marcado visual de errores

### v1.0.7 (2026-02-28)
- Añadido icono de aplicación personalizado para ejecutable Windows
- Añadidas rutas de configuración cross-platform (Windows: %APPDATA%, macOS: Application Support, Linux: .config)
- Añadido workflow de GitHub Actions para compilación en Windows

### v1.0.5 (2026-02-27)
- Añadido soporte multiidioma (Inglés, Español, Francés, Alemán)
- Añadida detección de idioma del sistema al primer inicio
- Añadido color de cuadrícula personalizable con selector de color
- Añadida opción de color de cuadrícula personalizado en ajustes de cuadrícula
- Cambiados valores de tamaño de cuadrícula a: 50, 100, 150, 200, 250
- Corregidos iconos de toolbar embebidos en el ejecutable
- Corregida la creación de preferences.json al primer inicio
- Añadida notificación de reinicio al cambiar de idioma

### v1.0.1 (2026-02-27)
- Corregidos iconos de toolbar (ahora embebidos en la app en lugar de depender del sistema)
- Añadidos iconos por tema (iconos claros para tema oscuro, iconos oscuros para tema claro)
- Compilado con Ubuntu 22.04 para máxima compatibilidad con distribuciones Linux

### v1.0.0 (2026-02-27)
- Lanzamiento inicial
- Lienzo infinito con desplazamiento y zoom
- Tarjetas de beat con título y contenido
- Conexiones entre beats con curvas bezier
- 9 temas (claros y oscuros)
- 8 colores de beat
- Sistema deshacer/rehacer
- Copiar/pegar beats
- Gestión de orden z
- Atajos de teclado
- Auto-guardado
- Exportar PDF/Texto
- Persistencia de preferencias
- Panel de propiedades
- Cuadrícula y fondo personalizable
- Correcciones: carga de conexiones, guardado de z-order

## Agradecimientos

- Inspirado en [Final Draft Beat Board](https://www.finaldraft.com/)
- Construido con [PySide6](https://www.qt.io/qt-for-python)
- Diseño de icono por CarlyMx

---

**Autor:** CarlyMx  
**GitHub:** https://github.com/carlymx/BeatBoard
