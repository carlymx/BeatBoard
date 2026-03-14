"""Global constants for BeatBoard application."""

from PySide6.QtCore import QSizeF, QPointF
from PySide6.QtGui import QColor

APP_NAME = "BeatBoard"
APP_VERSION = "1.0.29"
APP_ORGANIZATION = "BeatBoard"

BEAT_DEFAULT_WIDTH = 200.0
BEAT_DEFAULT_HEIGHT = 150.0
BEAT_MIN_WIDTH = 100.0
BEAT_MIN_HEIGHT = 80.0

BEAT_COLOR_DEFAULT = "#FFF59D"  # Amarillo por defecto

BEAT_MEMORIZE_LAST = False
BEAT_LAST_COLOR = BEAT_COLOR_DEFAULT
BEAT_LAST_SIZE = QSizeF(BEAT_DEFAULT_WIDTH, BEAT_DEFAULT_HEIGHT)
BEAT_CORNER_RADIUS = 8.0
BEAT_SHADOW_OFFSET = 4.0
BEAT_SHADOW_BLUR = 8.0
BEAT_SHADOW_OPACITY = 0.2

BEAT_DEFAULT_SIZE = QSizeF(BEAT_DEFAULT_WIDTH, BEAT_DEFAULT_HEIGHT)

# Colores predefinidos (teclas 1-7)
BEAT_PREDEFINED_COLORS = [
    "#FFF59D",  # 1 - Amarillo
    "#90CAF9",  # 2 - Azul
    "#A5D6A7",  # 3 - Verde
    "#EF9A9A",  # 4 - Rojo
    "#FFCC80",  # 5 - Naranja
    "#CE93D8",  # 6 - Púrpura
    "#E0E0E0",  # 7 - Gris
]

BEAT_PREDEFINED_NAMES = [
    "Amarillo",  # 1
    "Azul",      # 2
    "Verde",     # 3
    "Rojo",      # 4
    "Naranja",   # 5
    "Púrpura",   # 6
    "Gris",      # 7
]

# Colores personalizables (teclas 8, 9, 0) - inicialmente blancos
BEAT_CUSTOM_COLORS = [
    "#FFFFFF",  # 8 - Personalizado 1
    "#FFFFFF",  # 9 - Personalizado 2
    "#FFFFFF",  # 0 - Personalizado 3
]

# Mapa de compatibilidad para beats antiguos (nombres -> hexadecimal)
BEAT_COLOR_COMPATIBILITY_MAP: dict[str, str] = {
    "yellow": "#FFF59D",
    "blue": "#90CAF9",
    "green": "#A5D6A7",
    "red": "#EF9A9A",
    "orange": "#FFCC80",
    "purple": "#CE93D8",
    "gray": "#E0E0E0",
}

# Función para obtener color válido desde cualquier formato
def get_valid_beat_color(color_str: str) -> str:
    """Convert any color string to valid hex color."""
    # Si ya es hexadecimal válido
    if color_str.startswith("#") and len(color_str) == 7:
        try:
            # Verificar que sea un color válido
            QColor(color_str)
            return color_str
        except:
            pass
    
    # Si es nombre de color antiguo
    if color_str in BEAT_COLOR_COMPATIBILITY_MAP:
        return BEAT_COLOR_COMPATIBILITY_MAP[color_str]
    
    # Fallback a color por defecto
    return BEAT_COLOR_DEFAULT

# Función para obtener QColor desde cualquier formato
def get_beat_qcolor(color_str: str) -> QColor:
    """Get QColor from any color string format."""
    hex_color = get_valid_beat_color(color_str)
    return QColor(hex_color)

# Función para obtener color válido para conexiones
def get_valid_connection_color(color_str: str) -> QColor:
    """Get valid QColor for connections from any color string format."""
    # Si ya es un nombre de color predefinido
    if color_str in CONNECTION_COLORS:
        return CONNECTION_COLORS[color_str]
    
    # Si es un color hexadecimal válido
    if color_str.startswith("#") and len(color_str) == 7:
        try:
            return QColor(color_str)
        except:
            pass
    
    # Fallback a color por defecto
    return CONNECTION_COLORS[CONNECTION_COLOR_DEFAULT]

CONNECTION_LINE_WIDTH = 2.0
CONNECTION_LINE_WIDTH_OPTIONS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
CONNECTION_LINE_WIDTH_DEFAULT = 2.0

CONNECTION_NODE_SHAPES = ["circle", "square", "arrow", "none"]
CONNECTION_NODE_SHAPE_DEFAULT = "circle"

CONNECTION_OFFSET_PERCENT = 0.25
CONNECTION_OFFSET_MIN = 20.0

CONNECTION_COLORS: dict[str, QColor] = {
    "red": QColor("#EF5350"),
    "blue": QColor("#42A5F5"),
    "green": QColor("#66BB6A"),
    "yellow": QColor("#FFEE58"),
    "orange": QColor("#FFA726"),
    "purple": QColor("#AB47BC"),
    "dark_gray": QColor("#616161"),  # 7º color - gris oscuro
}

CONNECTION_COLOR_DEFAULT = "blue"

CANVAS_SCENE_SIZE = 100000
CANVAS_SCENE_RECT_OFFSET = QPointF(-CANVAS_SCENE_SIZE / 2, -CANVAS_SCENE_SIZE / 2)

ZOOM_MIN = 0.1
ZOOM_MAX = 5.0
ZOOM_DEFAULT = 1.0
ZOOM_STEP = 0.1

GRID_SIZE = 20
GRID_SIZE_OPTIONS = [50, 100, 150, 200, 250]
GRID_ENABLED_DEFAULT = False
GRID_COLOR_DEFAULT = "#CCCCCC"
GRID_COLOR_DARK_DEFAULT = "#444444"

AUTOSAVE_INTERVAL_MS = 300000
PROJECT_FILE_EXTENSION = ".bbp"
PROJECT_FILE_FILTER = f"BeatBoard Project (*{PROJECT_FILE_EXTENSION})"

CANVAS_BACKGROUND_COLORS: dict[str, str] = {
    "white": "#ffffff",
    "light_gray": "#f0f0f0",
    "gray": "#e0e0e0",
    "dark_gray": "#cccccc",
    "cream": "#fffef5",
    "dark": "#2d2d2d",
    "black": "#1e1e1e",
}

CANVAS_BACKGROUND_DEFAULT = "light_gray"

# Colores de fondo y grid asociados a cada tema
THEME_CANVAS_COLORS: dict[str, dict[str, str]] = {
    "system": {"background": "light_gray", "grid": "auto"},
    "light": {"background": "#f5f5f5", "grid": "#CCCCCC"},
    "dark": {"background": "#1e1e1e", "grid": "#444444"},
    "solarized_light": {"background": "#fdf6e3", "grid": "#d5c4a1"},
    "github_light": {"background": "#ffffff", "grid": "#d0d7de"},
    "papercolor": {"background": "#eeeeee", "grid": "#bbbbbb"},
    "dracula": {"background": "#282a36", "grid": "#44475a"},
    "nord": {"background": "#2e3440", "grid": "#434c5e"},
    "one_dark": {"background": "#282c34", "grid": "#3e4451"},
    "material_dark": {"background": "#263238", "grid": "#455a64"},
}

SPELLCHECK_ENABLED_DEFAULT = False
SPELLCHECK_DICTIONARY_DEFAULT = "es_ES"
SPELLCHECK_RESOURCES_PATH = "resources/dictionaries"

DEBUG_SHOW_Z_ORDER = False
