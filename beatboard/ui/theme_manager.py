"""Theme manager for BeatBoard application."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

from beatboard.core.constants import (
    CANVAS_BACKGROUND_COLORS,
    CANVAS_BACKGROUND_DEFAULT,
    SPELLCHECK_ENABLED_DEFAULT,
    SPELLCHECK_DICTIONARY_DEFAULT,
    BEAT_CUSTOM_COLORS,
    AUTOSAVE_INTERVAL_MS,
)
from beatboard.core.paths import get_config_dir


class ThemeMode(Enum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"
    SOLARIZED_LIGHT = "solarized_light"
    GITHUB_LIGHT = "github_light"
    PAPERCOLOR = "papercolor"
    DRACULA = "dracula"
    NORD = "nord"
    ONE_DARK = "one_dark"
    MATERIAL_DARK = "material_dark"


THEME_PALETTES = {
    ThemeMode.LIGHT: {
        "window": "#f5f5f5",
        "window_text": "#333333",
        "base": "#ffffff",
        "alternate_base": "#f0f0f0",
        "tooltip_base": "#ffffff",
        "tooltip_text": "#333333",
        "text": "#333333",
        "button": "#ffffff",
        "button_text": "#333333",
        "bright_text": "#ffffff",
        "highlight": "#1976D2",
        "highlighted_text": "#ffffff",
    },
    ThemeMode.DARK: {
        "window": "#1e1e1e",
        "window_text": "#ffffff",
        "base": "#2d2d2d",
        "alternate_base": "#3d3d3d",
        "tooltip_base": "#3d3d3d",
        "tooltip_text": "#ffffff",
        "text": "#ffffff",
        "button": "#3d3d3d",
        "button_text": "#ffffff",
        "bright_text": "#ffffff",
        "highlight": "#1976D2",
        "highlighted_text": "#ffffff",
    },
    ThemeMode.SOLARIZED_LIGHT: {
        "window": "#fdf6e3",
        "window_text": "#657b83",
        "base": "#eee8d5",
        "alternate_base": "#fdf6e3",
        "tooltip_base": "#fdf6e3",
        "tooltip_text": "#657b83",
        "text": "#657b83",
        "button": "#93a1a1",
        "button_text": "#fdf6e3",
        "bright_text": "#fdf6e3",
        "highlight": "#268bd2",
        "highlighted_text": "#fdf6e3",
    },
    ThemeMode.GITHUB_LIGHT: {
        "window": "#ffffff",
        "window_text": "#24292e",
        "base": "#ffffff",
        "alternate_base": "#f6f8fa",
        "tooltip_base": "#ffffff",
        "tooltip_text": "#24292e",
        "text": "#24292e",
        "button": "#f6f8fa",
        "button_text": "#24292e",
        "bright_text": "#ffffff",
        "highlight": "#0969da",
        "highlighted_text": "#ffffff",
    },
    ThemeMode.PAPERCOLOR: {
        "window": "#eeeeee",
        "window_text": "#444444",
        "base": "#dddddd",
        "alternate_base": "#eeeeee",
        "tooltip_base": "#eeeeee",
        "tooltip_text": "#444444",
        "text": "#444444",
        "button": "#cccccc",
        "button_text": "#444444",
        "bright_text": "#444444",
        "highlight": "#0088aa",
        "highlighted_text": "#eeeeee",
    },
    ThemeMode.DRACULA: {
        "window": "#282a36",
        "window_text": "#f8f8f2",
        "base": "#383a59",
        "alternate_base": "#44475a",
        "tooltip_base": "#44475a",
        "tooltip_text": "#f8f8f2",
        "text": "#f8f8f2",
        "button": "#44475a",
        "button_text": "#f8f8f2",
        "bright_text": "#f8f8f2",
        "highlight": "#bd93f9",
        "highlighted_text": "#282a36",
    },
    ThemeMode.NORD: {
        "window": "#2e3440",
        "window_text": "#eceff4",
        "base": "#3b4252",
        "alternate_base": "#434c5e",
        "tooltip_base": "#3b4252",
        "tooltip_text": "#eceff4",
        "text": "#eceff4",
        "button": "#4c566a",
        "button_text": "#eceff4",
        "bright_text": "#eceff4",
        "highlight": "#88c0d0",
        "highlighted_text": "#2e3440",
    },
    ThemeMode.ONE_DARK: {
        "window": "#282c34",
        "window_text": "#abb2bf",
        "base": "#21252b",
        "alternate_base": "#282c34",
        "tooltip_base": "#21252b",
        "tooltip_text": "#abb2bf",
        "text": "#abb2bf",
        "button": "#3e4451",
        "button_text": "#abb2bf",
        "bright_text": "#abb2bf",
        "highlight": "#61afef",
        "highlighted_text": "#282c34",
    },
    ThemeMode.MATERIAL_DARK: {
        "window": "#263238",
        "window_text": "#eceff1",
        "base": "#37474f",
        "alternate_base": "#455a64",
        "tooltip_base": "#455a64",
        "tooltip_text": "#eceff1",
        "text": "#eceff1",
        "button": "#455a64",
        "button_text": "#eceff1",
        "bright_text": "#eceff1",
        "highlight": "#80deea",
        "highlighted_text": "#263238",
    },
}


class ThemeManager(QObject):
    theme_changed = Signal(str)
    canvas_background_changed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._current_mode: ThemeMode = ThemeMode.SYSTEM
        self._canvas_background: str = CANVAS_BACKGROUND_DEFAULT
        self._grid_enabled: bool = False
        self._grid_size: int = 25
        self._grid_color: str = "auto"
        self._memorize_defaults: bool = False
        self._spellcheck_enabled: bool = SPELLCHECK_ENABLED_DEFAULT
        self._spellcheck_dictionary: str = SPELLCHECK_DICTIONARY_DEFAULT
        self._app = QApplication.instance()
        
        # Colores personalizados
        self._custom_colors = BEAT_CUSTOM_COLORS.copy()
        
        # Preferencias de backup
        self._backup_on_open: bool = True
        self._max_backups: int = 10
        self._autosave_interval: int = AUTOSAVE_INTERVAL_MS
        self._autosave_enabled: bool = True
        
        self._load_preference()

    def _get_config_path(self) -> Path:
        config_dir = get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "preferences.json"

    def _load_preference(self) -> None:
        config_path = self._get_config_path()
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text(encoding="utf-8"))
                mode = data.get("theme_mode", "system")
                self._current_mode = ThemeMode(mode)
                self._canvas_background = data.get("canvas_background", CANVAS_BACKGROUND_DEFAULT)
                self._grid_enabled = data.get("grid_enabled", False)
                self._grid_size = data.get("grid_size", 25)
                self._grid_color = data.get("grid_color", "auto")
                self._memorize_defaults = data.get("memorize_defaults", False)
                self._spellcheck_enabled = data.get("spellcheck_enabled", SPELLCHECK_ENABLED_DEFAULT)
                self._spellcheck_dictionary = data.get("spellcheck_dictionary", SPELLCHECK_DICTIONARY_DEFAULT)
                
                # Cargar colores personalizados
                saved_custom_colors = data.get("custom_colors")
                if isinstance(saved_custom_colors, list) and len(saved_custom_colors) == 3:
                    self._custom_colors = saved_custom_colors
                
                # Cargar preferencias de backup
                self._backup_on_open = data.get("backup_on_open", True)
                self._max_backups = data.get("max_backups", 10)
                self._autosave_interval = data.get("autosave_interval", AUTOSAVE_INTERVAL_MS)
                self._autosave_enabled = data.get("autosave_enabled", True)
            except (json.JSONDecodeError, KeyError, ValueError):
                self._current_mode = ThemeMode.SYSTEM
                self._canvas_background = CANVAS_BACKGROUND_DEFAULT
                self._grid_enabled = False
                self._grid_size = 25
                self._grid_color = "auto"
                self._memorize_defaults = False
                self._spellcheck_enabled = SPELLCHECK_ENABLED_DEFAULT
                self._spellcheck_dictionary = SPELLCHECK_DICTIONARY_DEFAULT
                self._backup_on_open = True
                self._max_backups = 10
                self._autosave_interval = AUTOSAVE_INTERVAL_MS
                self._autosave_enabled = True
        else:
            self._current_mode = ThemeMode.SYSTEM
            self._canvas_background = CANVAS_BACKGROUND_DEFAULT
            self._grid_enabled = False
            self._grid_size = 25
            self._grid_color = "auto"
            self._memorize_defaults = False
            self._spellcheck_enabled = SPELLCHECK_ENABLED_DEFAULT
            self._spellcheck_dictionary = SPELLCHECK_DICTIONARY_DEFAULT
            self._backup_on_open = True
            self._max_backups = 10
            self._autosave_interval = AUTOSAVE_INTERVAL_MS
            self._autosave_enabled = True
        self._save_preference()

    def _save_preference(self, language: str | None = None) -> None:
        config_path = self._get_config_path()
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            data = {}
        data["theme_mode"] = self._current_mode.value
        data["canvas_background"] = self._canvas_background
        data["grid_enabled"] = self._grid_enabled
        data["grid_size"] = self._grid_size
        data["grid_color"] = self._grid_color
        data["memorize_defaults"] = self._memorize_defaults
        data["spellcheck_enabled"] = self._spellcheck_enabled
        data["spellcheck_dictionary"] = self._spellcheck_dictionary
        if language is not None:
            data["language"] = language
        
        # Guardar colores personalizados
        data["custom_colors"] = self._custom_colors
        
        # Guardar preferencias de backup
        data["backup_on_open"] = self._backup_on_open
        data["max_backups"] = self._max_backups
        data["autosave_interval"] = self._autosave_interval
        data["autosave_enabled"] = self._autosave_enabled
        
        config_path.write_text(json.dumps(data, indent=2))

    def get_canvas_background(self) -> str:
        return self._canvas_background

    def set_canvas_background(self, color_key: str) -> None:
        if color_key in CANVAS_BACKGROUND_COLORS:
            self._canvas_background = color_key
            self._save_preference()
            self.canvas_background_changed.emit(color_key)
    
    def set_custom_canvas_background(self, hex_color: str) -> None:
        self._canvas_background = hex_color
        self._save_preference()
        self.canvas_background_changed.emit(hex_color)
    
    def get_grid_enabled(self) -> bool:
        return self._grid_enabled
    
    def set_grid_enabled(self, enabled: bool) -> None:
        self._grid_enabled = enabled
        self._save_preference()
    
    def get_grid_size(self) -> int:
        return self._grid_size
    
    def set_grid_size(self, size: int) -> None:
        self._grid_size = size
        self._save_preference()
    
    def get_grid_color(self) -> str:
        return self._grid_color
    
    def set_grid_color(self, color: str) -> None:
        self._grid_color = color
        self._save_preference()
    
    def get_memorize_defaults(self) -> bool:
        return self._memorize_defaults
    
    def set_memorize_defaults(self, enabled: bool) -> None:
        self._memorize_defaults = enabled
        self._save_preference()
    
    def get_spellcheck_enabled(self) -> bool:
        return self._spellcheck_enabled
    
    def set_spellcheck_enabled(self, enabled: bool) -> None:
        self._spellcheck_enabled = enabled
        self._save_preference()
    
    def get_spellcheck_dictionary(self) -> str:
        return self._spellcheck_dictionary
    
    def set_spellcheck_dictionary(self, dictionary: str) -> None:
        self._spellcheck_dictionary = dictionary
        self._save_preference()

    def is_dark_mode(self) -> bool:
        if self._current_mode == ThemeMode.SYSTEM:
            return self._detect_system_theme()
        dark_modes = {
            ThemeMode.DARK, ThemeMode.DRACULA, ThemeMode.NORD,
            ThemeMode.ONE_DARK, ThemeMode.MATERIAL_DARK
        }
        return self._current_mode in dark_modes

    def _detect_system_theme(self) -> bool:
        app = QApplication.instance()
        if app:
            try:
                hints = app.styleHints()
                is_dark = hints.colorScheme() == Qt.ColorScheme.Dark
                return is_dark
            except Exception:
                pass
        return False

    def get_current_mode(self) -> ThemeMode:
        return self._current_mode

    def set_theme(self, mode: ThemeMode) -> None:
        self._current_mode = mode
        self._save_preference()
        self.apply_theme()

    def apply_theme(self) -> None:
        if not self._app:
            return

        if self._current_mode == ThemeMode.SYSTEM:
            is_dark = self._detect_system_theme()
            if is_dark:
                self._apply_dark_theme()
            else:
                self._apply_light_theme()
        else:
            theme_key = self._current_mode
            if theme_key in [ThemeMode.LIGHT, ThemeMode.SOLARIZED_LIGHT, ThemeMode.GITHUB_LIGHT, ThemeMode.PAPERCOLOR]:
                self._apply_theme_palette(theme_key, False)
            else:
                self._apply_theme_palette(theme_key, True)

        self.theme_changed.emit(self._current_mode.value)

    def _apply_light_theme(self) -> None:
        self._apply_theme_palette(ThemeMode.LIGHT, False)

    def _apply_dark_theme(self) -> None:
        self._apply_theme_palette(ThemeMode.DARK, True)

    def _apply_theme_palette(self, mode: ThemeMode, is_dark: bool) -> None:
        if not self._app:
            return

        self._app.setStyle("Fusion")
        self._app.setStyleSheet(self._get_stylesheet(mode))
        
        palette = self._app.palette()
        colors = THEME_PALETTES.get(mode, THEME_PALETTES[ThemeMode.LIGHT])
        
        palette.setColor(QPalette.ColorRole.Window, QColor(colors["window"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["window_text"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors["base"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["alternate_base"]))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["tooltip_base"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["tooltip_text"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors["text"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors["button"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["button_text"]))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors["bright_text"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["highlight"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["highlighted_text"]))
        self._app.setPalette(palette)

    def _get_stylesheet(self, mode: ThemeMode) -> str:
        stylesheets = {
            ThemeMode.LIGHT: self._light_stylesheet,
            ThemeMode.DARK: self._dark_stylesheet,
            ThemeMode.SOLARIZED_LIGHT: self._solarized_light_stylesheet,
            ThemeMode.GITHUB_LIGHT: self._github_light_stylesheet,
            ThemeMode.PAPERCOLOR: self._papercolor_stylesheet,
            ThemeMode.DRACULA: self._dracula_stylesheet,
            ThemeMode.NORD: self._nord_stylesheet,
            ThemeMode.ONE_DARK: self._one_dark_stylesheet,
            ThemeMode.MATERIAL_DARK: self._material_dark_stylesheet,
        }
        return stylesheets.get(mode, self._light_stylesheet)

    _light_stylesheet = """
        QMainWindow { background-color: #f5f5f5; }
        QToolBar { background-color: #ffffff; border-bottom: 1px solid #e0e0e0; spacing: 4px; padding: 4px; }
        QToolBar QToolButton { background-color: #ffffff; color: #000000; border: none; padding: 6px 12px; border-radius: 3px; }
        QToolBar QToolButton:hover { background-color: #e0e0e0; }
        QToolBar QToolButton:pressed { background-color: #cccccc; }
        QStatusBar { background-color: #ffffff; border-top: 1px solid #e0e0e0; color: #333333; }
        QMenuBar { background-color: #ffffff; color: #333333; }
        QMenuBar::item:selected { background-color: #e0e0e0; }
        QMenu { background-color: #ffffff; color: #333333; border: 1px solid #e0e0e0; }
        QMenu::item:selected { background-color: #e0e0e0; }
        QLabel { color: #333333; }
        QPushButton { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; padding: 5px 15px; border-radius: 3px; }
        QPushButton:hover { background-color: #f0f0f0; border-color: #999999; }
        QPushButton:pressed { background-color: #e0e0e0; }
        QComboBox { background-color: #ffffff; color: #333333; border: 1px solid #cccccc; padding: 4px; border-radius: 3px; }
        QComboBox:hover { border-color: #999999; }
        QComboBox::drop-down { border: none; }
        QLineEdit { background-color: #ffffff; color: #333333; border: 1px solid #cccccc; padding: 4px; border-radius: 3px; }
        QLineEdit:focus { border-color: #1976D2; }
        QTextEdit { background-color: #ffffff; color: #333333; border: 1px solid #cccccc; border-radius: 3px; }
        QCheckBox { color: #333333; }
        QRadioButton { color: #333333; }
        QDialog { background-color: #f5f5f5; }
        QSplitter::handle { background-color: #e0e0e0; }
    """

    _dark_stylesheet = """
        QMainWindow { background-color: #1e1e1e; }
        QToolBar { background-color: #2d2d2d; border-bottom: 1px solid #3d3d3d; spacing: 4px; padding: 4px; }
        QStatusBar { background-color: #2d2d2d; border-top: 1px solid #3d3d3d; color: #ffffff; }
        QMenuBar { background-color: #2d2d2d; color: #ffffff; }
        QMenuBar::item:selected { background-color: #4d4d4d; }
        QMenu { background-color: #2d2d2d; color: #ffffff; border: 1px solid #4d4d4d; }
        QMenu::item:selected { background-color: #4d4d4d; }
        QLabel { color: #ffffff; }
        QPushButton { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555555; padding: 5px 15px; border-radius: 3px; }
        QPushButton:hover { background-color: #4d4d4d; }
        QPushButton:pressed { background-color: #2d2d2d; }
        QComboBox { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555555; padding: 4px; border-radius: 3px; }
        QComboBox:hover { border-color: #777777; }
        QComboBox::drop-down { border: none; }
        QLineEdit { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555555; padding: 4px; border-radius: 3px; }
        QLineEdit:focus { border-color: #1976D2; }
        QTextEdit { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555555; border-radius: 3px; }
        QCheckBox { color: #ffffff; }
        QRadioButton { color: #ffffff; }
        QDialog { background-color: #2d2d2d; }
        QSplitter::handle { background-color: #3d3d3d; }
    """

    _solarized_light_stylesheet = """
        QMainWindow { background-color: #fdf6e3; }
        QToolBar { background-color: #eee8d5; border-bottom: 1px solid #d5c4a1; spacing: 4px; padding: 4px; }
        QToolBar QToolButton { background-color: #eee8d5; color: #073642; border: none; padding: 6px 12px; border-radius: 3px; }
        QToolBar QToolButton:hover { background-color: #d5c4a1; }
        QToolBar QToolButton:pressed { background-color: #b58900; color: #fdf6e3; }
        QStatusBar { background-color: #eee8d5; border-top: 1px solid #d5c4a1; color: #073642; }
        QMenuBar { background-color: #eee8d5; color: #073642; }
        QMenuBar::item:selected { background-color: #d5c4a1; }
        QMenu { background-color: #eee8d5; color: #073642; border: 1px solid #d5c4a1; }
        QMenu::item:selected { background-color: #d5c4a1; }
        QLabel { color: #073642; }
        QPushButton { background-color: #93a1a1; color: #073642; border: 1px solid #839496; padding: 5px 15px; border-radius: 3px; }
        QPushButton:hover { background-color: #839496; }
        QPushButton:pressed { background-color: #657b83; color: #fdf6e3; }
        QComboBox { background-color: #93a1a1; color: #073642; border: 1px solid #839496; padding: 4px; border-radius: 3px; }
        QComboBox QAbstractItemView { background-color: #eee8d5; color: #073642; }
        QLineEdit { background-color: #eee8d5; color: #073642; border: 1px solid #d5c4a1; padding: 4px; border-radius: 3px; }
        QTextEdit { background-color: #eee8d5; color: #073642; border: 1px solid #d5c4a1; border-radius: 3px; }
        QCheckBox { color: #073642; }
        QDialog { background-color: #fdf6e3; }
        QSplitter::handle { background-color: #d5c4a1; }
    """

    _github_light_stylesheet = """
        QMainWindow { background-color: #ffffff; }
        QToolBar { background-color: #f6f8fa; border-bottom: 1px solid #d0d7de; spacing: 4px; padding: 4px; }
        QToolBar QToolButton { background-color: #f6f8fa; color: #1f2328; border: none; padding: 6px 12px; border-radius: 6px; }
        QToolBar QToolButton:hover { background-color: #e8eaef; }
        QToolBar QToolButton:pressed { background-color: #d0d7de; }
        QStatusBar { background-color: #f6f8fa; border-top: 1px solid #d0d7de; color: #24292f; }
        QMenuBar { background-color: #f6f8fa; color: #24292f; }
        QMenuBar::item:selected { background-color: #d0d7de; }
        QMenu { background-color: #ffffff; color: #24292f; border: 1px solid #d0d7de; }
        QMenu::item:selected { background-color: #f6f8fa; }
        QLabel { color: #24292f; }
        QPushButton { background-color: #f6f8fa; color: #1f2328; border: 1px solid #d0d7de; padding: 5px 15px; border-radius: 6px; }
        QPushButton:hover { background-color: #e8eaef; border-color: #8c959f; }
        QPushButton:pressed { background-color: #d0d7de; }
        QComboBox { background-color: #f6f8fa; color: #24292f; border: 1px solid #d0d7de; padding: 4px; border-radius: 6px; }
        QLineEdit { background-color: #ffffff; color: #24292f; border: 1px solid #d0d7de; padding: 4px; border-radius: 6px; }
        QTextEdit { background-color: #ffffff; color: #24292f; border: 1px solid #d0d7de; border-radius: 6px; }
        QCheckBox { color: #24292f; }
        QDialog { background-color: #ffffff; }
        QSplitter::handle { background-color: #d0d7de; }
    """

    _papercolor_stylesheet = """
        QMainWindow { background-color: #eeeeee; }
        QToolBar { background-color: #dddddd; border-bottom: 1px solid #bbbbbb; spacing: 4px; padding: 4px; }
        QStatusBar { background-color: #dddddd; border-top: 1px solid #bbbbbb; color: #444444; }
        QMenuBar { background-color: #dddddd; color: #444444; }
        QMenuBar::item:selected { background-color: #bbbbbb; }
        QMenu { background-color: #dddddd; color: #444444; border: 1px solid #bbbbbb; }
        QMenu::item:selected { background-color: #bbbbbb; }
        QLabel { color: #444444; }
        QPushButton { background-color: #cccccc; color: #444444; border: 1px solid #999999; padding: 5px 15px; border-radius: 3px; }
        QPushButton:hover { background-color: #bbbbbb; }
        QPushButton:pressed { background-color: #aaaaaa; }
        QComboBox { background-color: #cccccc; color: #444444; border: 1px solid #999999; padding: 4px; border-radius: 3px; }
        QLineEdit { background-color: #dddddd; color: #444444; border: 1px solid #bbbbbb; padding: 4px; border-radius: 3px; }
        QTextEdit { background-color: #dddddd; color: #444444; border: 1px solid #bbbbbb; border-radius: 3px; }
        QCheckBox { color: #444444; }
        QDialog { background-color: #eeeeee; }
        QSplitter::handle { background-color: #bbbbbb; }
    """

    _dracula_stylesheet = """
        QMainWindow { background-color: #282a36; }
        QToolBar { background-color: #383a59; border-bottom: 1px solid #44475a; spacing: 4px; padding: 4px; }
        QStatusBar { background-color: #383a59; border-top: 1px solid #44475a; color: #f8f8f2; }
        QMenuBar { background-color: #383a59; color: #f8f8f2; }
        QMenuBar::item:selected { background-color: #44475a; }
        QMenu { background-color: #383a59; color: #f8f8f2; border: 1px solid #44475a; }
        QMenu::item:selected { background-color: #44475a; }
        QLabel { color: #f8f8f2; }
        QPushButton { background-color: #44475a; color: #f8f8f2; border: 1px solid #6272a4; padding: 5px 15px; border-radius: 3px; }
        QPushButton:hover { background-color: #6272a4; }
        QPushButton:pressed { background-color: #282a36; }
        QComboBox { background-color: #44475a; color: #f8f8f2; border: 1px solid #6272a4; padding: 4px; border-radius: 3px; }
        QLineEdit { background-color: #44475a; color: #f8f8f2; border: 1px solid #6272a4; padding: 4px; border-radius: 3px; }
        QTextEdit { background-color: #44475a; color: #f8f8f2; border: 1px solid #6272a4; border-radius: 3px; }
        QCheckBox { color: #f8f8f2; }
        QDialog { background-color: #282a36; }
        QSplitter::handle { background-color: #44475a; }
    """

    _nord_stylesheet = """
        QMainWindow { background-color: #2e3440; }
        QToolBar { background-color: #3b4252; border-bottom: 1px solid #434c5e; spacing: 4px; padding: 4px; }
        QStatusBar { background-color: #3b4252; border-top: 1px solid #434c5e; color: #eceff4; }
        QMenuBar { background-color: #3b4252; color: #eceff4; }
        QMenuBar::item:selected { background-color: #434c5e; }
        QMenu { background-color: #3b4252; color: #eceff4; border: 1px solid #434c5e; }
        QMenu::item:selected { background-color: #434c5e; }
        QLabel { color: #eceff4; }
        QPushButton { background-color: #4c566a; color: #eceff4; border: 1px solid #5e81ac; padding: 5px 15px; border-radius: 3px; }
        QPushButton:hover { background-color: #5e81ac; }
        QPushButton:pressed { background-color: #3b4252; }
        QComboBox { background-color: #4c566a; color: #eceff4; border: 1px solid #5e81ac; padding: 4px; border-radius: 3px; }
        QLineEdit { background-color: #4c566a; color: #eceff4; border: 1px solid #5e81ac; padding: 4px; border-radius: 3px; }
        QTextEdit { background-color: #4c566a; color: #eceff4; border: 1px solid #5e81ac; border-radius: 3px; }
        QCheckBox { color: #eceff4; }
        QDialog { background-color: #2e3440; }
        QSplitter::handle { background-color: #434c5e; }
    """

    _one_dark_stylesheet = """
        QMainWindow { background-color: #282c34; }
        QToolBar { background-color: #21252b; border-bottom: 1px solid #181a1f; spacing: 4px; padding: 4px; }
        QStatusBar { background-color: #21252b; border-top: 1px solid #181a1f; color: #abb2bf; }
        QMenuBar { background-color: #21252b; color: #abb2bf; }
        QMenuBar::item:selected { background-color: #3e4451; }
        QMenu { background-color: #21252b; color: #abb2bf; border: 1px solid #3e4451; }
        QMenu::item:selected { background-color: #3e4451; }
        QLabel { color: #abb2bf; }
        QPushButton { background-color: #3e4451; color: #abb2bf; border: 1px solid #528bff; padding: 5px 15px; border-radius: 3px; }
        QPushButton:hover { background-color: #528bff; color: #282c34; }
        QPushButton:pressed { background-color: #21252b; }
        QComboBox { background-color: #3e4451; color: #abb2bf; border: 1px solid #528bff; padding: 4px; border-radius: 3px; }
        QLineEdit { background-color: #3e4451; color: #abb2bf; border: 1px solid #528bff; padding: 4px; border-radius: 3px; }
        QTextEdit { background-color: #3e4451; color: #abb2bf; border: 1px solid #528bff; border-radius: 3px; }
        QCheckBox { color: #abb2bf; }
        QDialog { background-color: #282c34; }
        QSplitter::handle { background-color: #3e4451; }
    """

    _material_dark_stylesheet = """
        QMainWindow { background-color: #263238; }
        QToolBar { background-color: #37474f; border-bottom: 1px solid #455a64; spacing: 4px; padding: 4px; }
        QStatusBar { background-color: #37474f; border-top: 1px solid #455a64; color: #eceff1; }
        QMenuBar { background-color: #37474f; color: #eceff1; }
        QMenuBar::item:selected { background-color: #455a64; }
        QMenu { background-color: #37474f; color: #eceff1; border: 1px solid #455a64; }
        QMenu::item:selected { background-color: #455a64; }
        QLabel { color: #eceff1; }
        QPushButton { background-color: #455a64; color: #eceff1; border: 1px solid #80deea; padding: 5px 15px; border-radius: 3px; }
        QPushButton:hover { background-color: #80deea; color: #263238; }
        QPushButton:pressed { background-color: #37474f; }
        QComboBox { background-color: #455a64; color: #eceff1; border: 1px solid #80deea; padding: 4px; border-radius: 3px; }
        QLineEdit { background-color: #455a64; color: #eceff1; border: 1px solid #80deea; padding: 4px; border-radius: 3px; }
        QTextEdit { background-color: #455a64; color: #eceff1; border: 1px solid #80deea; border-radius: 3px; }
        QCheckBox { color: #eceff1; }
        QDialog { background-color: #263238; }
        QSplitter::handle { background-color: #455a64; }
    """
    
    # Métodos para colores personalizados
    def get_custom_colors(self) -> list[str]:
        """Obtener la lista de colores personalizados."""
        return self._custom_colors.copy()
    
    def set_custom_color(self, index: int, hex_color: str) -> None:
        """Establecer un color personalizado."""
        if 0 <= index < 3 and hex_color.startswith("#") and len(hex_color) == 7:
            self._custom_colors[index] = hex_color
            self._save_preference()
    
    def update_custom_colors(self, colors: list[str]) -> None:
        """Actualizar todos los colores personalizados."""
        if len(colors) == 3:
            for i, color in enumerate(colors):
                if color.startswith("#") and len(color) == 7:
                    self._custom_colors[i] = color
            self._save_preference()
    
    # Getters y setters para preferencias de backup
    def get_backup_on_open(self) -> bool:
        return self._backup_on_open
    
    def set_backup_on_open(self, enabled: bool) -> None:
        self._backup_on_open = enabled
        self._save_preference()
    
    def get_max_backups(self) -> int:
        return self._max_backups
    
    def set_max_backups(self, count: int) -> None:
        self._max_backups = max(1, min(count, 20))
        self._save_preference()
    
    def get_autosave_interval(self) -> int:
        return self._autosave_interval
    
    def set_autosave_interval(self, interval_ms: int) -> None:
        self._autosave_interval = interval_ms
        self._save_preference()
    
    def get_autosave_enabled(self) -> bool:
        return self._autosave_enabled
    
    def set_autosave_enabled(self, enabled: bool) -> None:
        self._autosave_enabled = enabled
        self._save_preference()
