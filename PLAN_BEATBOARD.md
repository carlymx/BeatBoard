# BeatBoard - Plan de Desarrollo Completo

## 1. Resumen del Proyecto

BeatBoard es una aplicación de escritorio desarrollada en Python utilizando PySide6 (Qt for Python) que replica la funcionalidad del Beat Board de Final Draft. Esta herramienta está diseñada para escritores de guiones, cineastas y narradores que necesitan organizar visualmente los puntos de historia (beats) de sus proyectos antes de escribir el guión final.

### 1.1 Objetivos Principales

- Crear una pizarra virtual interactiva donde los usuarios puedan crear, mover y organizar tarjetas (beats)
- Permitir la conexión visual entre beats mediante líneas de flujo codificadas por colores
- Integrar un sistema de esquema jerárquico
- Facilitar la exportación de trabajo a formatos estándar de guión

### 1.2 Alcance Inicial

La primera versión (v1.0) se centrará en replicar las funcionalidades core del Beat Board:
- Creación y edición de beats
- Arrastrar y soltar en pizarra infinita
- Conexiones entre beats
- Paleta de colores
- Persistencia de proyectos
- Exportación básica

---

## 2. Análisis de Requisitos

### 2.1 Requisitos Funcionales

#### 2.1.1 Gestión de Beats

| Requisito | Descripción | Prioridad |
|-----------|-------------|-----------|
| Crear beat | Doble clic en el canvas crea un nuevo beat vacío | Alta |
| Editar título | Campo de título editable en cada beat | Alta |
| Editar contenido | Área de texto para descripción del beat | Alta |
| Eliminar beat | Selección y eliminación de beats | Alta |
| Mover beat | Arrastrar y soltar libre en el canvas | Alta |
| Color de beat | Asignar color desde paleta predefinida | Media |
| Imagen en beat | Insertar imagen de referencia en beat | Baja |
| Redimensionar beat | Ajustar tamaño del beat | Media |

#### 2.1.2 Conexiones entre Beats

| Requisito | Descripción | Prioridad |
|-----------|-------------|-----------|
| Crear conexión | Dibujar línea entre dos beats | Alta |
| Color de conexión | Diferentes colores para tipos de relación | Media |
| Eliminar conexión | Eliminar línea de conexión | Alta |
| Mover conexión | Las líneas se actualizan al mover beats | Alta |

#### 2.1.3 Gestión de Proyectos

| Requisito | Descripción | Prioridad |
|-----------|-------------|-----------|
| Nuevo proyecto | Crear proyecto vacío | Alta |
| Guardar proyecto | Persistir a archivo .bbp (BeatBoard Project) | Alta |
| Cargar proyecto | Recuperar proyecto desde archivo | Alta |
| Auto-guardado | Guardado automático periódicamente | Media |
| Proyecto reciente | Lista de proyectos abiertos recientemente | Baja |

#### 2.1.4 Canvas e Interfaz

| Requisito | Descripción | Prioridad |
|-----------|-------------|-----------|
| Canvas infinito | Área de trabajo sin límites visibles | Alta |
| Zoom | Ampliar/reducir vista del canvas | Alta |
| Panorámica | Desplazarse por el canvas | Alta |
| Cuadrícula | Mostrar guía visual opcional | Baja |
| Modo enfoque | Ocultar todo excepto beat seleccionado | Baja |

#### 2.1.5 Exportación

| Requisito | Descripción | Prioridad |
|-----------|-------------|-----------|
| Exportar a PDF | Generar documento PDF del Beat Board | Media |
| Exportar a texto | Exportar lista de beats como texto | Baja |
| Exportar a FDX | Exportar a formato Final Draft | Baja |

### 2.2 Requisitos No Funcionales

#### 2.2.1 Rendimiento

- La aplicación debe manejar al menos 500 beats sin degradación perceptible
- Tiempo de inicio menor a 3 segundos
- Operaciones de guardado/carga menores a 2 segundos para proyectos medianos

#### 2.2.2 Compatibilidad

- Windows 10/11
- macOS 11+
- Linux (Ubuntu 20.04+)

#### 2.2.3 Usabilidad

- Curva de aprendizaje mínima para usuarios de Final Draft
- Atajos de teclado para operaciones frecuentes
- Interface responsiva (mantener 60 FPS durante interacciones)

---

## 3. Arquitectura Técnica

### 3.1 Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Framework UI | PySide6 (Qt for Python) | 6.5+ |
| Lenguaje | Python | 3.10+ |
| Serialización | JSON + recursos embebidos | - |
| Testing | pytest + pytest-qt | - |
| Virtual Environment | uv | - |

### 3.2 Arquitectura de Capas

```
┌─────────────────────────────────────────┐
│           Capa de Presentación         │
│  (Widgets, Vistas, Dialogs, Menús)     │
├─────────────────────────────────────────┤
│           Capa de Lógica               │
│  (Controladores, Señales, Slots)       │
├─────────────────────────────────────────┤
│           Capa de Datos                │
│  (Modelos, Persistencia, Archivos)      │
├─────────────────────────────────────────┤
│           Capa Core                    │
│  (Entidades, Utilidades, Constantes)   │
└─────────────────────────────────────────┘
```

### 3.3 Estructura de Módulos

```
beatboard/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada
│   ├── application.py          # QApplication principal
│   └── resources.py           # Recursos embebidos
├── core/
│   ├── __init__.py
│   ├── beat.py                # Entidad Beat
│   ├── connection.py           # Entidad Connection
│   ├── project.py              # Entidad Project
│   └── constants.py            # Constantes globales
├── data/
│   ├── __init__.py
│   ├── project_repository.py   # Carga/Guardado
│   └── file_handler.py         # Manejo de archivos
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Ventana principal
│   ├── canvas/
│   │   ├── __init__.py
│   │   ├── beat_board_view.py  # QGraphicsView principal
│   │   ├── beat_board_scene.py # QGraphicsScene
│   │   └── beat_item.py        # QGraphicsItem para Beat
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── beat_card.py        # Widget de tarjeta
│   │   ├── toolbar.py          # Barra de herramientas
│   │   └── color_palette.py    # Selector de colores
│   └── dialogs/
│       ├── __init__.py
│       ├── new_beat_dialog.py  # Diálogo nuevo beat
│       └── export_dialog.py    # Diálogo exportación
├── services/
│   ├── __init__.py
│   ├── export_service.py       # Exportación PDF/Texto
│   └── autosave_service.py     # Auto-guardado
└── tests/
    ├── __init__.py
    ├── test_beat.py
    ├── test_project.py
    └── test_integration.py
```

---

## 4. Diseño de Interfaz

### 4.1 Layout Principal

```
┌──────────────────────────────────────────────────────────────┐
│  Archivo  Editar  Ver  Beat  Ayuda                           │
├──────────────────────────────────────────────────────────────┤
│  [+Nuevo] [Guardar] [Zoom+] [Zoom-] [Ajustar] │ [Colores]  │
├────────────────────────────────────────┬─────────────────────┤
│                                        │                     │
│                                        │   Panel de          │
│         Beat Board Canvas              │   Propiedades      │
│         (QGraphicsView)                │                     │
│                                        │   - Título          │
│         ┌────────┐    ┌────────┐       │   - Contenido      │
│         │ Beat 1 │───>│ Beat 2 │       │   - Color          │
│         └────────┘    └────────┘       │   - Notas          │
│                                        │                     │
│                    ┌────────┐          │                     │
│                    │ Beat 3 │          │                     │
│                    └────────┘          │                     │
│                                        │                     │
├────────────────────────────────────────┴─────────────────────┤
│  Beats: 3  │  Zoom: 100%  │  Modificado                      │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Componentes de Interfaz

#### 4.2.1 Beat Card (Tarjeta de Beat)

- Dimensiones: 200x150 píxeles (ajustable)
- Estados: Normal, Seleccionado, Hover, Editando
- Elementos: Título, Contenido, Color indicator, Handle de conexión
- Sombra: 4px offset, 8px blur, 20% opacity

#### 4.2.2 Conexiones (Flow Lines)

- Estilo: Línea curva bezier o línea recta
- Grosor: 2px
- Colores disponibles: Rojo, Azul, Verde, Amarillo, Naranja, Púrpura
- Animación: Opcional - flujo suave al seleccionar

#### 4.2.3 Toolbar

- Estilo: Iconos + texto emergente
- Posición: Superior, debajo del menú
- Grupos: Archivo, Vista, Beat, Herramientas

#### 4.2.4 Panel de Propiedades

- Visible: Solo cuando un beat está seleccionado
- Campos: Título (QLineEdit), Contenido (QTextEdit), Color (QComboBox)

### 4.3 Paleta de Colores

Colores predefinidos para beats (inspirados en Final Draft):

| Nombre | Hex | Uso recomendado |
|--------|-----|------------------|
| Amarillo | #FFF59D | Beat general |
| Azul | #90CAF9 | Personaje |
| Verde | #A5D6A7 | Plot |
| Rojo | #EF9A9A | Conflicto |
| Naranja | #FFCC80 | Acción |
| Púrpura | #CE93D8 | Subplot |
| Gris | #E0E0E0 | Nota/Borrador |

---

## 5. Modelo de Datos

### 5.1 Entidad Beat

```python
class Beat:
    id: str                      # UUID único
    title: str                   # Título del beat
    content: str                 # Descripción/detalles
    color: str                   # Color hex o nombre
    position: QPointF            # Posición en canvas
    size: QSizeF                 # Dimensiones
    created_at: datetime         # Timestamp creación
    modified_at: datetime        # Timestamp modificación
    image_path: str | None       # Ruta de imagen (opcional)
    connections: list[str]        # IDs de beats conectados
```

### 5.2 Entidad Connection

```python
class Connection:
    id: str                      # UUID único
    source_beat_id: str          # ID beat origen
    target_beat_id: str         # ID beat destino
    color: str                   # Color de la línea
    label: str | None            # Etiqueta opcional
```

### 5.3 Entidad Project

```python
class Project:
    id: str                      # UUID único
    name: str                    # Nombre del proyecto
    created_at: datetime         # Timestamp creación
    modified_at: datetime        # Timestamp modificación
    beats: list[Beat]            # Lista de beats
    connections: list[Connection] # Lista de conexiones
    canvas_state: dict            # Estado del canvas (zoom, posición)
    metadata: dict                # Metadatos adicionales
```

### 5.4 Formato de Archivo .bbp

Formato JSON con estructura:

```json
{
  "version": "1.0",
  "project": {
    "id": "uuid",
    "name": "Mi Guión",
    "created_at": "2024-01-01T00:00:00Z",
    "modified_at": "2024-01-01T00:00:00Z"
  },
  "canvas": {
    "zoom": 1.0,
    "pan_x": 0,
    "pan_y": 0
  },
  "beats": [
    {
      "id": "uuid",
      "title": "Inicio",
      "content": "El protagonista aparece...",
      "color": "#FFF59D",
      "position": {"x": 100, "y": 100},
      "size": {"width": 200, "height": 150},
      "created_at": "2024-01-01T00:00:00Z",
      "modified_at": "2024-01-01T00:00:00Z"
    }
  ],
  "connections": [
    {
      "id": "uuid",
      "source_beat_id": "uuid1",
      "target_beat_id": "uuid2",
      "color": "#2196F3"
    }
  ]
}
```

---

## 6. Plan de Implementación

### 6.1 Fase 1: Fundamentos (Semanas 1-2)

#### Semana 1: Setup y Estructura

**Objetivos:**
- Configurar entorno de desarrollo
- Crear estructura de proyecto
- Implementar aplicación básica con ventana principal

**Tareas:**
1. [ ] Crear entorno virtual con uv
2. [ ] Instalar PySide6 y dependencias
3. [ ] Configurar proyecto con pyproject.toml
4. [ ] Crear estructura de directorios
5. [ ] Implementar Application y MainWindow básicos
6. [ ] Configurar sistema de logging

**Entregable:** Ventana principal funcional con menú básico

#### Semana 2: Canvas Básico

**Objetivos:**
- Implementar QGraphicsScene y QGraphicsView
- Permitir creación de beats básicos
- Implementar zoom y paneo

**Tareas:**
1. [ ] Crear BeatBoardScene personalizado
2. [ ] Crear BeatBoardView personalizado
3. [ ] Implementar BeatItem como QGraphicsWidget
4. [ ] Habilitar zoom con scroll de ratón
5. [ ] Habilitar paneo con tecla Espacio
6. [ ] Implementar creación de beat con doble clic

**Entregable:** Canvas donde se pueden crear y visualizar beats

### 6.2 Fase 2: Interactividad (Semanas 3-4)

#### Semana 3: Drag & Drop y Edición

**Objetivos:**
- Implementararrastrar y soltar de beats
- Permitir edición de beats
- Selecciones múltiples

**Tareas:**
1. [ ] Implementar drag & drop de beats
2. [ ] Crear editor inline para título
3. [ ] Crear editor inline para contenido
4. [ ] Implementar selección única y múltiple
5. [ ] Agregar menú contextual (clic derecho)
6. [ ] Implementar eliminación de beats

**Entregable:** Beats completamente editables y movibles

#### Semana 4: Conexiones

**Objetutos:**
- Implementar sistema de conexiones
- Crear líneas de flujo entre beats
- Permitir edición de conexiones

**Tareas:**
1. [ ] Crear ConnectionItem (QGraphicsPathItem)
2. [ ] Implementar modo de conexión (botón toolbar)
3. [ ] Dibujar línea al arrastrar desde un beat
4. [ ] Actualizar posición de líneas al mover beats
5. [ ] Implementar eliminación de conexiones
6. [ ] Agregar colores a conexiones

**Entregable:** Beats conectables con líneas visuales

### 6.3 Fase 3: Datos y Persistencia (Semanas 5-6)

#### Semana 5: Sistema de Archivos

**Objetivos:**
- Implementar guardado y carga de proyectos
- Crear formato .bbp
- Manejar auto-guardado

**Tareas:**
1. [ ] Implementar ProjectRepository
2. [ ] Crear serialización JSON de beats y conexiones
3. [ ] Implementar diálogo guardar/guardar como
4. [ ] Implementar diálogo abrir proyecto
5. [ ] Agregar manejo de archivos recientes
6. [ ] Implementar auto-guardado (cada 5 minutos)

**Entregable:** Proyectos guardables y cargables

#### Semana 6: Exportación

**Objetivos:**
- Implementar exportación a PDF
- Agregar opciones de exportación

**Tareas:**
1. [ ] Implementar ExportService
2. [ ] Crear diálogo de exportación
3. [ ] Exportar a PDF (lista de beats)
4. [ ] Exportar a texto plano
5. [ ] Implementar vista previa de exportación

**Entregable:** Capacidad de exportar trabajo

### 6.4 Fase 4: UI/UX Avanzado (Semanas 7-8)

#### Semana 7: Panel de Propiedades y Toolbar

**Objetivos:**
- Agregar panel de propiedades
- Mejorar toolbar
- Agregar más opciones de vista

**Tareas:**
1. [ ] Crear panel de propiedades lateral
2. [ ] Sincronizar selección con panel
3. [ ] Implementar editor de color
4. [ ] Agregar más controles de zoom
5. [ ] Implementar ajuste automático a contenido
6. [ ] Agregar modo de cuadrícula

**Entregable:** Interfaz pulida y funcional

#### Semana 8: Atajos y Mejoras UX

**Objetivos:**
- Agregar atajos de teclado
- Mejorar feedback visual
- Optimizar rendimiento

**Tareas:**
1. [ ] Implementar atajos de teclado (Ctrl+N, Ctrl+S, Delete, etc.)
2. [ ] Agregar animaciones de transición
3. [ ] Mejorar estilos visuales (tema)
4. [ ] Optimizar rendimiento con muchos beats
5. [ ] Agregar deshacer/rehacer básico
6. [ ] Testing y bug fixing

**Entregable:** Aplicación lista para uso

### 6.5 Fase 5: Polish y Distribución (Semanas 9-10)

#### Semana 9: Estilos y Temas

**Objetivos:**
- Implementar sistema de temas
- Crear tema oscuro y claro
- Mejorar iconografía

**Tareas:**
1. [ ] Crear sistema de QSS (Qt Style Sheets)
2. [ ] Implementar tema claro
3. [ ] Implementar tema oscuro
4. [ ] Agregar toggle de tema
5. [ ] Mejorar iconos del toolbar
6. [ ] Agregar splash screen

#### Semana 10: Empaquetado

**Objetivos:**
- Preparar para distribución
- Crear ejecutables
- Documentación

**Tareas:**
1. [ ] Configurar PyInstaller o cx_Freeze
2. [ ] Crear ejecutable para Windows
3. [ ] Crear executable para macOS
4. [ ] Crear paquete para Linux
5. [ ] Escribir README
6. [ ] Crear CHANGELOG

---

## 7. Detalles de Implementación

### 7.1 Graphics View - Concepts Clave

El framework Graphics View de Qt es ideal para el Beat Board:

- **QGraphicsScene**: El área lógica donde viven los items
- **QGraphicsView**: El viewport que muestra la scene
- **QGraphicsItem**: Items individuales (beats, conexiones)

```python
# Ejemplo básico de BeatItem
from PySide6.QtWidgets import QGraphicsWidget
from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QPen, QBrush, QColor

class BeatItem(QGraphicsWidget):
    clicked = Signal(str)  # signal con beat id
    
    def __init__(self, beat_id, title="", parent=None):
        super().__init__(parent)
        self.beat_id = beat_id
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.setPreferredSize(200, 150)
```

### 7.2 Drag & Drop Implementación

```python
def mousePressEvent(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
    super().mousePressEvent(event)

def mouseReleaseEvent(self, event):
    self.setCursor(Qt.CursorShape.OpenHandCursor)
    super().mouseReleaseEvent(event)
```

### 7.3 Conexiones con Líneas Curvas

```python
from PySide6.QtGui import QPainterPath

def update_connection_path(self):
    path = QPainterPath()
    start = self.source_item.scenePos() + self.source_item.boundingRect().center()
    end = self.target_item.scenePos() + self.target_item.boundingRect().center()
    
    # Curva bezier horizontal
    control_offset = abs(end.x() - start.x()) / 2
    path.moveTo(start)
    path.cubicTo(
        start.x() + control_offset, start.y(),
        end.x() - control_offset, end.y(),
        end.x(), end.y()
    )
    self.setPath(path)
```

---

## 8. Testing

### 8.1 Estrategia de Testing

- **Unit Tests**: Para lógica de negocio (Beat, Connection, Project)
- **Widget Tests**: Para componentes de UI individuales
- **Integration Tests**: Para flujos completos de usuario

### 8.2 Frameworks

```bash
pytest
pytest-qt        # Para testing de widgets Qt
pytest-cov       # Para coverage
```

### 8.3 Ejemplo de Test

```python
import pytest
from beatboard.core.beat import Beat

def test_beat_creation():
    beat = Beat(title="Test Beat", content="Test content")
    assert beat.title == "Test Beat"
    assert beat.content == "Test content"
    assert beat.color == "#FFF59D"  # Default color

def test_beat_position():
    beat = Beat()
    beat.setPosition(100, 200)
    assert beat.position.x() == 100
    assert beat.position.y() == 200
```

---

## 9. Dependencias

### 9.1 Dependencias de Proyecto

```toml
[project]
name = "beatboard"
version = "1.0.10"
description = "A virtual beat board for screenwriters"
requires-python = ">=3.10"
dependencies = [
    "pyside6>=6.5.0",
    "spylls>=0.0.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-qt>=4.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]
```

### 9.2 Instalación

```bash
# Crear entorno virtual
uv venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\Activate.ps1  # Windows

# Instalar dependencias
uv pip install pyside6
uv pip install pytest pytest-qt pytest-cov
```

---

## 10. Guía de Contribución

### 10.1 Estilo de Código

- Seguir PEP 8
- Usar type hints
- Nombres en inglés para código
- Nombres en español para UI visible (opcional)
- Máximo 100 líneas por función

### 10.2 Commits

```
feat: add beat color customization
fix: resolve connection update on beat move
docs: update README with installation instructions
test: add unit tests for Beat class
refactor: extract connection logic to separate module
```

---

## 11. Roadmap Completo

### 11.1 Visión General del Roadmap

```
═══════════════════════════════════════════════════════════════════════════════════
                              BEATBOARD ROADMAP
═══════════════════════════════════════════════════════════════════════════════════

  v1.0              v1.1              v1.2              v2.0
  ████████          ████████          ████████          ████████
  Core Beat         Outline           Collaboration     Cloud + AI
  Board             Integration       Sync              Mobile

  ════════════════════════════════════════════════════════════════════════════════
  Timeline: 12-18 meses (desarrollo activo)
  ════════════════════════════════════════════════════════════════════════════════
```

### 11.2 Fases de Desarrollo Detalladas

#### ═══════════════════════════════════════════════════════════════════════════════
FASE 1: FUNDAMENTOS (Meses 1-2)
══════════════════════════════════════════════════════════════════════════════

| Semana | Sprint | Entregables | Milestone |
|--------|--------|-------------|-----------|
| 1-2    | S1     | Entorno configurado, estructura de proyecto, MainWindow básico | ✅ Project Setup |
| 3-4    | S2     | GraphicsView/Scene, BeatItem básico, canvas infinito | ✅ Canvas Core |
| 5-6    | S3     | Drag & drop beats, edición inline, selección | ✅ Beat Interaction |
| 7-8    | S4     | Sistema de conexiones, líneas de flujo | ✅ Connections |

**Objetivo de Fase:** MVP funcional con operaciones core de beats y conexiones

---

#### ═══════════════════════════════════════════════════════════════════════════════
FASE 2: PERSISTENCIA Y EXPORTACIÓN (Meses 3-4)
══════════════════════════════════════════════════════════════════════════════

| Semana | Sprint | Entregables | Milestone |
|--------|--------|-------------|-----------|
| 9-10   | S5     | Sistema de archivos .bbp, guardar/cargar proyectos | ✅ Data Persistence |
| 11-12  | S6     | Auto-guardado, archivos recientes | ✅ Auto-save |
| 13-14  | S7     | Exportación PDF, exportación texto | ✅ Export |
| 15-16  | S8     | Panel de propiedades, toolbar completo | ✅ UI Polish |

**Objetivo de Fase:** Aplicación completamente utilizable con persistencia

---

#### ═══════════════════════════════════════════════════════════════════════════════
FASE 3: ESTABILIZACIÓN V1.0 (Meses 5-6)
══════════════════════════════════════════════════════════════════════════════

| Semana | Sprint | Entregables | Milestone |
|--------|--------|-------------|-----------|
| 17-18  | S9     | Atajos de teclado, deshacer/rehacer | ✅ UX Enhancement |
| 19-20  | S10    | Tema claro/oscuro, estilos QSS | ✅ Theming |
| 21-22  | S11    | Testing completo, bug fixing | ✅ Quality |
| 23-24  | S12    | Empaquetado, distribución, release v1.0 | 🎉 v1.0 RELEASE |

**Objetivo de Fase:** Release estable v1.0 listo para producción

---

### 11.3 Roadmap por Versión

#### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERSION 1.0 - "Core Beat Board" (Mes 6)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Fecha Estimada:** Agosto 2026

**Características:**
- ✅ Crear, editar, eliminar beats
- ✅ Arrastrar y soltar beats en canvas infinito
- ✅ Conexiones visuales entre beats (líneas de flujo)
- ✅ Paleta de colores para beats
- ✅ Guardar/Cargar proyectos (.bbp)
- ✅ Auto-guardado
- ✅ Zoom y paneo
- ✅ Exportar a PDF
- ✅ Tema claro/oscuro
- ✅ Atajos de teclado básicos

**Criterios de Release:**
- [ ] Aplicación inicia sin errores
- [ ] CRUD de beats funciona correctamente
- [ ] Conexiones se actualizan al mover beats
- [ ] Proyectos se guardan y cargan sin pérdida de datos
- [ ] Exportación a PDF genera documento legible
- [ ] Tests unitarios pasan (>80% coverage)
- [ ] Ejecutable funciona en Windows, macOS, Linux

**dependencias:**
- PySide6 6.5+
- Python 3.10+

---

#### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERSION 1.1 - "Outline Integration" (Mes 9)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Fecha Estimada:** Noviembre 2026

**Características:**
- [x] **MultiIdioma** - Traducir menús y textos a los principales idiomas en, sp, fr, ge
- [x] **SpellCheck** - Agregar uso de diccionarios .OXT de LibreOffice
- [ ] **Outline Editor** - Vista de esquema jerárquico de beats
- [ ] **Estructura de actos** - Agrupar beats en actos/secuencias
- [ ] **Drag to Outline** - Arrastrar beats desde canvas a outline
- [ ] **Send to Script** - Exportar beats como elementos de guión
- [ ] **Plantillas de estructura** - Save the Cat, Trilogía,etc.
- [ ] **Page Goals** - Asignar rango de páginas a beats
- [ ] **Búsqueda avanzada** - Buscar beats por título/contenido/color
- [ ] **Ajustar a contenido** - Zoom automático para ver todos los beats

**Criterios de Release:**
- [ ] Outline muestra beats en estructura jerárquica
- [ ] Beats se pueden arrastrar de canvas a outline
- [ ] Plantillas predefinidas cargan estructura correcta
- [ ] Exportación a guión mantiene formato

**dependencias:**
- Todo lo de v1.0
- spylls>=0.0.4

---

#### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERSION 1.1.0 - "Outline Integration" (Mes 9)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Fecha Estimada:** Noviembre 2026

**Características:**
- [ ] **Outline Editor** - Vista de esquema jerárquico de beats
- [ ] **Estructura de actos** - Agrupar beats en actos/secuencias
- [ ] **Drag to Outline** - Arrastrar beats desde canvas a outline
- [ ] **Send to Script** - Exportar beats como elementos de guión
- [ ] **Plantillas de estructura** - Save the Cat, Trilogía,etc.
- [ ] **Page Goals** - Asignar rango de páginas a beats
- [ ] **Búsqueda avanzada** - Buscar beats por título/contenido/color
- [ ] **Ajustar a contenido** - Zoom automático para ver todos los beats

**Criterios de Release:**
- [ ] Outline muestra beats en estructura jerárquica
- [ ] Beats se pueden arrastrar de canvas a outline
- [ ] Plantillas predefinidas cargan estructura correcta
- [ ] Exportación a guión mantiene formato

**dependencias:**
- Todo lo de v1.0.10
- (Sin nuevas dependencias)

---

#### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERSION 1.2 - "Collaboration" (Mes 12)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Fecha Estimada:** Febrero 2027

**Características:**
- [ ] **Historial de versiones** - Guardar y restaurar versiones
- [ ] **Marcadores** - Marcar beats importantes
- [ ] **Notas en beats** - Notas adicionales independientes del contenido
- [ ] **Imágenes en beats** - Adjuntar imágenes de referencia
- [ ] **Integración FDX** - Importar/Exportar .fdx (Final Draft)
- [ ] **Filtros por color** - Mostrar solo beats de cierto color
- [ ] **Agrupación de beats** - Crear grupos/álbumes de beats
- [ ] **Modo presentación** - Ver beats en pantalla completa

**Criterios de Release:**
- [ ] Historial permite restaurar versiones anteriores
- [ ] Imágenes se muestran en beats
- [ ] FDX import/export mantiene estructura
- [ ] Filtros funcionan correctamente

**dependencias:**
- Todo lo de v1.1
- xml.etree.ElementTree (stdlib)

---

#### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERSION 1.5 - "Pro Features" (Mes 15)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Fecha Estimada:** Mayo 2027

**Características:**
- [ ] **Múltiples Beat Boards** - Varios tableros por proyecto
- [ ] **Story Map** - Vista visual de estructura de acto
- [ ] **Statistics** - Estadísticas del proyecto (beats por color, etc.)
- [ ] **Keyboard shortcuts personalizables** - Configurar atajos
- [ ] **Macros** - Secuencias de acciones automáticas
- [ ] **Plugins/Scripts** - Sistema de extensiones básico
- [ ] **Dark mode mejorado** - Temas adicionales
- [ ] **Exportación avanzada** - Markdown, HTML, JSON

**Criterios de Release:**
- [ ] Múltiples tableros funcionan independientemente
- [ ] Story Map representa estructura visualmente
- [ ] Macros se pueden grabar y reproducir

**dependencias:**
- Todo lo de v1.2
- Importlib (stdlib) para plugins

---

#### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERSION 2.0 - "Cloud & AI" (Mes 18)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Fecha Estimada:** Agosto 2027

**Características:**
- [ ] **Sincronización en la nube** - Guardar en servidor
- [ ] **Colaboración en tiempo real** - Múltiples usuarios editando
- [ ] **AI Beat Suggestions** - Generación de beats con IA
- [ ] **AI Story Analysis** - Análisis de estructura narrativa
- [ ] **AI Writing Assistant** - Asistencia para diálogos
- [ ] **Aplicación móvil** - iOS/Android
- [ ] **Web App** - Versión navegador
- [ ] **API REST** - Integración con otros servicios

**Criterios de Release:**
- [ ] Sincronización funciona sin conflictos
- [ ] IA genera beats relevantes
- [ ] App móvil funcional (MVP)
- [ ] Web app permite edición básica

**dependencias:**
- Todo lo de v1.5
- Servidor backend (FastAPI/Node.js)
- Base de datos (PostgreSQL/MongoDB)
- OpenAI API u otro provider de IA
- Flutter (para móvil)

---

### 11.4 Milestones y Entregas

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CALENDARIO DE ENTREGAS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  2026                                                                        │
│  ═══                                                                        │
│  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec                    │
│  ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───                          │
│  ████                                                                       
│  Phase 1                                                                    
│  ████████████████                                                           
│  Phase 2                                                                    
│              ████████████████                                               
│              Phase 3                                                         │
│                            🎉 v1.0                                           
│  ─────────────────────────────────────────────────▶                       
│                                    ████████ v1.1                           
│                                    ██████████████ v1.2                      
│                                                      █████ v1.5            
│                                                                  ████ v2.0  
│                                                                             
│  Entregas:                                                                  │
│  ├─ v1.0: Agosto 2026 (Release estable)                                    │
│  ├─ v1.1: Noviembre 2026 (Outline)                                        │
│  ├─ v1.2: Febrero 2027 (Collaboration)                                     │
│  ├─ v1.5: Mayo 2027 (Pro)                                                  │
│  └─ v2.0: Agosto 2027 (Cloud + AI)                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.5 Gestión de Dependencias entre Features

```
┌────────────────────┐     ┌────────────────────┐
│     BEAT BOARD     │     │    OUTLINE VIEW    │
│      (v1.0)        │────▶│      (v1.1)        │
└────────────────────┘     └────────────────────┘
         │                            │
         │                            ▼
         │                   ┌────────────────────┐
         │                   │   SEND TO SCRIPT   │
         └──────────────────▶│      (v1.1)        │
                             └────────────────────┘
                                       │
                                       ▼
                             ┌────────────────────┐
                             │  FDX INTEGRATION   │
                             │      (v1.2)        │
                             └────────────────────┘

┌────────────────────┐     ┌────────────────────┐
│   LOCAL STORAGE    │     │   CLOUD SYNC        │
│      (v1.0)        │────▶│      (v2.0)         │
└────────────────────┘     └────────────────────┘
         │                            │
         ▼                            ▼
┌────────────────────┐     ┌────────────────────┐
│    VERSIONS       │     │  COLLABORATION      │
│     (v1.2)        │────▶│      (v2.0)         │
└────────────────────┘     └────────────────────┘
```

### 11.6 Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Retrasos en desarrollo | Alta | Medio | Iteraciones cortas, milestones frecuentes |
| Complejidad de Qt Graphics | Media | Alto | Prototipos tempranos, documentación Qt |
| IA no cumple expectativas | Media | Medio | Fallback a features manuales, prompts iterativos |
|scope creep | Alta | Alto | Feature freezing en cada fase |
| Compatibilidad cross-platform | Baja | Alto | Testing temprano en todos los OS |

### 11.7 Recursos Estimados

| Fase | Semanas | Esfuerzo (developer-months) |
|------|---------|----------------------------|
| Fase 1: Fundamentos | 8 | 4-6 |
| Fase 2: Persistencia | 8 | 4-6 |
| Fase 3: Estabilización | 8 | 3-4 |
| v1.1 | 12 | 4-6 |
| v1.2 | 12 | 4-6 |
| v1.5 | 12 | 5-7 |
| v2.0 | 12 | 8-10 |
| **Total** | **72** | **32-45** |

---

### 11.8 Priorización de Features (MoSCoW)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PRIORIZACIÓN                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MUST HAVE (v1.0) - Critical                                                │
│  ════════════════════                                                       │
│  ✓ Crear/editar/eliminar beats                                             │
│  ✓ Drag & drop                                                             │
│  ✓ Conexiones                                                               │
│  ✓ Persistencia                                                             │
│  ✓ Zoom/pan                                                                 │
│                                                                             │
│  SHOULD HAVE (v1.1) - Important                                             │
│  ══════════════════════════                                                 │
│  ○ Outline editor                                                           │
│  ○ Plantillas                                                               │
│  ○ Búsqueda                                                                 │
│                                                                             │
│  COULD HAVE (v1.2) - Nice to have                                           │
│  ═══════════════════════════                                               │
│  ○ Versiones                                                                │
│  ○ Imágenes                                                                 │
│  ○ FDX integration                                                          │
│                                                                             │
│  WON'T HAVE (v2.0+) - Future                                                │
│  ══════════════════════                                                     │
│  □ Cloud sync                                                               │
│  □ AI features                                                              │
│  □ Mobile app                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Referencias

- [Qt Graphics View Framework](https://doc.qt.io/qtforpython-6/overviews/graphicsview.html)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Final Draft Beat Board](https://www.finaldraft.com/blog/how-to-use-final-draft-the-beat-board)
- [Arc Studio Plot Board](https://www.arcstudiopro.com/)

---

*Documento generado como plan de desarrollo para BeatBoard*
*Versiones: 1.0 - 2.0*
*Fecha: Febrero 2026*
*Última actualización: Febrero 2026*
