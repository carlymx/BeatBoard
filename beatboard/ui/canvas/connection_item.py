"""Connection item for drawing lines between beats."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Signal
from PySide6.QtGui import QPainterPath, QPen, QColor, QPainter
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem

from beatboard.core.connection import Connection
from beatboard.core.constants import CONNECTION_COLORS, CONNECTION_LINE_WIDTH

if TYPE_CHECKING:
    from beatboard.ui.canvas.beat_item import BeatItem


class ConnectionItem(QGraphicsPathItem):
    connection_deleted = Signal(str)
    
    def __init__(self, connection: Connection, parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        
        self._connection = connection
        self._source_item: BeatItem | None = None
        self._target_item: BeatItem | None = None
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        
        self._update_pen()
        self._update_path()
    
    def _update_pen(self) -> None:
        color = CONNECTION_COLORS.get(self._connection.color, CONNECTION_COLORS["blue"])
        pen = QPen(QColor(color), CONNECTION_LINE_WIDTH)
        pen.setStyle(Qt.PenStyle.SolidLine)
        self.setPen(pen)
    
    def _update_path(self) -> None:
        if self._source_item and self._target_item:
            path = QPainterPath()
            
            start = self._source_item.scenePos() + self._source_item.boundingRect().center()
            end = self._target_item.scenePos() + self._target_item.boundingRect().center()
            
            control_offset = abs(end.x() - start.x()) / 2
            if control_offset < 50:
                control_offset = 50
            
            path.moveTo(start)
            path.cubicTo(
                QPointF(start.x() + control_offset, start.y()),
                QPointF(end.x() - control_offset, end.y()),
                end
            )
            
            self.setPath(path)
    
    def set_source_item(self, item: BeatItem) -> None:
        self._source_item = item
        self._update_path()
    
    def set_target_item(self, item: BeatItem) -> None:
        self._target_item = item
        self._update_path()
    
    def update_positions(self) -> None:
        self._update_path()
    
    @property
    def connection_id(self) -> str:
        return self._connection.id
    
    def paint(self, painter: QPainter, option, widget=None) -> None:
        if self.isSelected():
            pen = self.pen()
            pen.setWidth(CONNECTION_LINE_WIDTH + 1)
            pen.setColor(QColor("#1976D2"))
            painter.setPen(pen)
        else:
            painter.setPen(self.pen())
        
        painter.drawPath(self.path())


from PySide6.QtCore import Qt