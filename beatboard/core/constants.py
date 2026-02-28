"""Global constants for BeatBoard application."""

from PySide6.QtCore import QSizeF, QPointF
from PySide6.QtGui import QColor

APP_NAME = "BeatBoard"
APP_VERSION = "1.0.5"
APP_ORGANIZATION = "BeatBoard"

BEAT_DEFAULT_WIDTH = 200.0
BEAT_DEFAULT_HEIGHT = 150.0
BEAT_MIN_WIDTH = 100.0
BEAT_MIN_HEIGHT = 80.0

BEAT_COLOR_DEFAULT = "yellow"

BEAT_MEMORIZE_LAST = False
BEAT_LAST_COLOR = BEAT_COLOR_DEFAULT
BEAT_LAST_SIZE = QSizeF(BEAT_DEFAULT_WIDTH, BEAT_DEFAULT_HEIGHT)
BEAT_CORNER_RADIUS = 8.0
BEAT_SHADOW_OFFSET = 4.0
BEAT_SHADOW_BLUR = 8.0
BEAT_SHADOW_OPACITY = 0.2

BEAT_DEFAULT_SIZE = QSizeF(BEAT_DEFAULT_WIDTH, BEAT_DEFAULT_HEIGHT)

BEAT_COLORS: dict[str, QColor] = {
    "yellow": QColor("#FFF59D"),
    "blue": QColor("#90CAF9"),
    "green": QColor("#A5D6A7"),
    "red": QColor("#EF9A9A"),
    "orange": QColor("#FFCC80"),
    "purple": QColor("#CE93D8"),
    "gray": QColor("#E0E0E0"),
}

CONNECTION_LINE_WIDTH = 2.0

CONNECTION_COLORS: dict[str, QColor] = {
    "red": QColor("#EF5350"),
    "blue": QColor("#42A5F5"),
    "green": QColor("#66BB6A"),
    "yellow": QColor("#FFEE58"),
    "orange": QColor("#FFA726"),
    "purple": QColor("#AB47BC"),
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
