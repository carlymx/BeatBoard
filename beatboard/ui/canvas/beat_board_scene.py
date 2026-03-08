"""Custom QGraphicsScene for the Beat Board."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QGraphicsScene

from beatboard.core.constants import (
    CANVAS_BACKGROUND_COLORS,
    CANVAS_BACKGROUND_DEFAULT,
    CANVAS_SCENE_SIZE,
    GRID_ENABLED_DEFAULT,
    GRID_SIZE,
    GRID_COLOR_DEFAULT,
    GRID_COLOR_DARK_DEFAULT,
)
from beatboard.core.project import Project

if TYPE_CHECKING:
    pass


class BeatBoardScene(QGraphicsScene):
    beat_created = Signal(str)
    beat_deleted = Signal(str)
    beat_moved = Signal(str)
    scene_clicked = Signal(QPointF)

    def __init__(self, project: Project, parent=None) -> None:
        super().__init__(parent)
        
        self._project = project
        self._grid_enabled = GRID_ENABLED_DEFAULT
        self._grid_size = GRID_SIZE
        self._grid_color = GRID_COLOR_DEFAULT
        
        half_size = CANVAS_SCENE_SIZE / 2
        self.setSceneRect(-half_size, -half_size, CANVAS_SCENE_SIZE, CANVAS_SCENE_SIZE)
        
        self._apply_canvas_background()
        
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            app.theme_manager.canvas_background_changed.connect(self._on_canvas_background_changed)
            app.theme_manager.grid_color_changed.connect(self._on_grid_color_changed)
            self._grid_color = app.theme_manager.get_grid_color()
    
    def _apply_canvas_background(self) -> None:
        app = QApplication.instance()
        bg_key = CANVAS_BACKGROUND_DEFAULT
        if app and hasattr(app, "theme_manager"):
            bg_key = app.theme_manager.get_canvas_background()
        
        bg_color = self._get_bg_color(bg_key)
        self.setBackgroundBrush(QBrush(QColor(bg_color)))
    
    def _get_bg_color(self, bg_key: str) -> str:
        if bg_key.startswith("#"):
            return bg_key
        return CANVAS_BACKGROUND_COLORS.get(bg_key, CANVAS_BACKGROUND_DEFAULT)
    
    def _on_canvas_background_changed(self, color_key: str) -> None:
        bg_color = self._get_bg_color(color_key)
        self.setBackgroundBrush(QBrush(QColor(bg_color)))
    
    def _on_grid_color_changed(self, color: str) -> None:
        self._grid_color = color
        self.update()
    
    def set_project(self, project: Project) -> None:
        self._project = project
        self.clear()
    
    def get_project(self) -> Project:
        return self._project
    
    def set_grid_enabled(self, enabled: bool) -> None:
        self._grid_enabled = enabled
        self.update()
    
    def is_grid_enabled(self) -> bool:
        return self._grid_enabled
    
    def toggle_grid(self) -> None:
        self._grid_enabled = not self._grid_enabled
        self.update()
    
    def set_grid_size(self, size: int) -> None:
        self._grid_size = size
        self.update()
    
    def get_grid_size(self) -> int:
        return self._grid_size
    
    def set_grid_color(self, color: str) -> None:
        self._grid_color = color
        self.update()
    
    def get_grid_color(self) -> str:
        return self._grid_color
    
    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawBackground(painter, rect)
        
        center_pen = QPen(QColor("#FF5722"))
        center_pen.setWidth(2)
        painter.setPen(center_pen)
        
        painter.drawLine(QPointF(-50, 0), QPointF(50, 0))
        painter.drawLine(QPointF(0, -50), QPointF(0, 50))
        
        painter.setBrush(QBrush(QColor("#FF5722")))
        painter.drawEllipse(QPointF(0, 0), 5, 5)
        
        if not self._grid_enabled:
            return
        
        bg_key = CANVAS_BACKGROUND_DEFAULT
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            bg_key = app.theme_manager.get_canvas_background()
        
        bg_color = self._get_bg_color(bg_key)
        
        if self._grid_color == "auto":
            is_dark = self._is_dark_color(bg_color)
            grid_color = GRID_COLOR_DARK_DEFAULT if is_dark else GRID_COLOR_DEFAULT
        else:
            grid_color = self._grid_color
        
        pen = QPen(QColor(grid_color))
        pen.setWidth(1)
        painter.setPen(pen)
        
        grid_size = self._grid_size
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        
        x = left
        while x < rect.right():
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            x += grid_size
        
        y = top
        while y < rect.bottom():
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            y += grid_size
    
    def _is_dark_color(self, hex_color: str) -> bool:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return False
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            brightness = (r * 299 + g * 587 + b * 114) / 1000
            return brightness < 128
        except ValueError:
            return False
