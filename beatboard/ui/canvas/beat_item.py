"""Beat item widget for QGraphicsScene."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QPainter,
    QPainterPath,
    QPen,
    QTextDocument,
    QTextOption,
)
from PySide6.QtWidgets import QGraphicsItem, QGraphicsObject

from beatboard.core.beat import Beat
from beatboard.core.constants import (
    BEAT_CORNER_RADIUS,
    BEAT_DEFAULT_HEIGHT,
    BEAT_DEFAULT_WIDTH,
    BEAT_MIN_HEIGHT,
    BEAT_MIN_WIDTH,
    BEAT_SHADOW_OFFSET,
    BEAT_SHADOW_OPACITY,
    get_beat_qcolor,
)
from beatboard.i18n import _tr

if TYPE_CHECKING:
    pass


class BeatItem(QGraphicsObject):
    item_moved = Signal(str, float, float)
    item_move_started = Signal(str, float, float)
    item_move_ended = Signal(str)
    item_selected = Signal(str)
    item_double_clicked = Signal(str)
    item_clicked = Signal(str)
    item_resized = Signal(str, float, float)

    RESIZE_HANDLE_SIZE = 8

    def __init__(self, beat: Beat, parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        
        self._beat = beat
        self._is_hovering = False
        self._resizing = False
        self._resize_start_pos: Optional[QPointF] = None
        self._resize_start_size: Optional[QPointF] = None
        self._resize_handle = None
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        self.setPos(beat.position)
        
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        
        width = beat.size.width() if beat.size else BEAT_DEFAULT_WIDTH
        height = beat.size.height() if beat.size else BEAT_DEFAULT_HEIGHT
        self._rect = QRectF(0, 0, width, height)
    
    @property
    def beat(self) -> Beat:
        return self._beat
    
    @property
    def beat_id(self) -> str:
        return self._beat.id
    
    def _get_current_size(self) -> QPointF:
        if self._beat.size:
            return QPointF(self._beat.size.width(), self._beat.size.height())
        return QPointF(BEAT_DEFAULT_WIDTH, BEAT_DEFAULT_HEIGHT)
    
    def boundingRect(self) -> QRectF:
        size = self._get_current_size()
        return QRectF(0, 0, size.x(), size.y())
    
    def _get_resize_handle_rects(self) -> dict:
        size = self._get_current_size()
        h = self.RESIZE_HANDLE_SIZE
        return {
            "bottom_right": QRectF(size.x() - h, size.y() - h, h, h),
        }
    
    def _get_resize_handle_at(self, pos: QPointF) -> Optional[str]:
        if not self.isSelected():
            return None
        handles = self._get_resize_handle_rects()
        for handle_name, rect in handles.items():
            if rect.contains(pos):
                return handle_name
        return None
    
    def paint(self, painter: QPainter, option, widget=None) -> None:
        size = self._get_current_size()
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        shadow_color = QColor(0, 0, 0, int(255 * BEAT_SHADOW_OPACITY))
        shadow_rect = QRectF(
            BEAT_SHADOW_OFFSET,
            BEAT_SHADOW_OFFSET,
            size.x(),
            size.y(),
        )
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(shadow_rect, BEAT_CORNER_RADIUS, BEAT_CORNER_RADIUS)
        
        beat_color = get_beat_qcolor(self._beat.color)
        
        if self.isSelected():
            beat_color = beat_color.lighter(110)
        
        if self._is_hovering:
            beat_color = beat_color.lighter(105)
        
        painter.setBrush(QBrush(beat_color))
        
        if self.isSelected():
            pen = QPen(QColor("#1976D2"), 2)
        else:
            pen = QPen(QColor("#E0E0E0"), 1)
        painter.setPen(pen)
        
        beat_rect = QRectF(0, 0, size.x(), size.y())
        painter.drawRoundedRect(beat_rect, BEAT_CORNER_RADIUS, BEAT_CORNER_RADIUS)
        
        color_bar_rect = QRectF(0, 0, 8, size.y())
        accent_color = beat_color.darker(120)
        painter.setBrush(QBrush(accent_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(color_bar_rect, BEAT_CORNER_RADIUS, BEAT_CORNER_RADIUS)
        
        if self._beat.show_title:
            title_font = QFont()
            title_font.setPointSize(11)
            title_font.setBold(True)
            painter.setFont(title_font)
            painter.setPen(QColor("#333333"))
            
            title_rect = QRectF(15, 10, size.x() - 25, 25)
            title = self._beat.title or _tr("no_title")
            title_option = QTextOption(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            painter.drawText(title_rect, title, title_option)
            
            content_rect = QRectF(15, 40, size.x() - 25, size.y() - 50)
        else:
            content_rect = QRectF(15, 15, size.x() - 25, size.y() - 30)
        
        content = self._beat.content or ""
        
        if content:
            if "<" in content and ">" in content:
                styled_content = f'<style>body {{ color: #333333; }}</style>{content}'
                text_doc = QTextDocument()
                text_doc.setHtml(styled_content)
                text_doc.setDefaultFont(QFont("Arial", 9))
                text_doc.setTextWidth(content_rect.width())
                
                painter.save()
                painter.translate(content_rect.topLeft())
                painter.setClipRect(QRectF(0, 0, content_rect.width(), content_rect.height()))
                text_doc.drawContents(painter)
                painter.restore()
            else:
                content_font = QFont("Arial", 9)
                painter.setFont(content_font)
                painter.setPen(QColor("#333333"))
                
                if len(content) > 100:
                    content = content[:97] + "..."
                
                content_option = QTextOption(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                content_option.setWrapMode(QTextOption.WrapMode.WordWrap)
                painter.drawText(content_rect, content, content_option)
        else:
            placeholder_font = QFont("Arial", 9)
            painter.setFont(placeholder_font)
            painter.setPen(QColor("#999999"))
            placeholder_option = QTextOption(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            painter.drawText(content_rect, _tr("beat_content_placeholder_canvas"), placeholder_option)
        
        if self.isSelected():
            self._draw_resize_handles(painter)
    
    def _draw_resize_handles(self, painter: QPainter) -> None:
        size = self._get_current_size()
        h = self.RESIZE_HANDLE_SIZE
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        handle_color = QColor("#1976D2")
        painter.setBrush(QBrush(handle_color))
        painter.setPen(QPen(handle_color, 1))
        
        path = QPainterPath()
        path.moveTo(size.x() - h, size.y())
        path.lineTo(size.x(), size.y())
        path.lineTo(size.x(), size.y() - h)
        path.closeSubpath()
        
        painter.drawPath(path)
    
    def hoverEnterEvent(self, event) -> None:
        self._is_hovering = True
        self.update()
        super().hoverEnterEvent(event)
    
    def hoverMoveEvent(self, event) -> None:
        pos = event.pos()
        handle = self._get_resize_handle_at(pos)
        
        if handle == "bottom_right":
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif handle in ("right", "bottom"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        
        super().hoverMoveEvent(event)
    
    def hoverLeaveEvent(self, event) -> None:
        self._is_hovering = False
        if not self._resizing:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.update()
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            handle = self._get_resize_handle_at(pos)
            
            if handle:
                self._resizing = True
                self._resize_handle = handle
                self._resize_start_pos = event.scenePos()
                self._resize_start_size = self._get_current_size()
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.item_clicked.emit(self._beat.id)
                self.item_move_started.emit(self._beat.id, self._beat.position.x(), self._beat.position.y())
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event) -> None:
        if self._resizing and self._resize_start_pos and self._resize_start_size:
            delta = event.scenePos() - self._resize_start_pos
            new_width = max(BEAT_MIN_WIDTH, self._resize_start_size.x() + delta.x())
            new_height = max(BEAT_MIN_HEIGHT, self._resize_start_size.y() + delta.y())
            
            self._beat.set_size(new_width, new_height)
            self.update()
            
            self.item_resized.emit(self._beat.id, new_width, new_height)
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        if self._resizing:
            self._resizing = False
            self._resize_handle = None
            self._resize_start_pos = None
            self._resize_start_size = None
            self.item_resized.emit(self._beat.id, self._beat.size.width(), self._beat.size.height())
        elif event.button() == Qt.MouseButton.LeftButton:
            self.item_move_ended.emit(self._beat.id)
        
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event) -> None:
        self.item_double_clicked.emit(self._beat.id)
        super().mouseDoubleClickEvent(event)
    
    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self._beat.set_position(value.x(), value.y())
            self.item_moved.emit(self._beat.id, value.x(), value.y())
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if value:
                self.item_selected.emit(self._beat.id)
        return super().itemChange(change, value)
    
    def update_from_beat(self) -> None:
        self.setPos(self._beat.position)
        self.update()
    
    def refresh(self) -> None:
        from PySide6.QtWidgets import QApplication
        self.prepareGeometryChange()
        self.update()
        QApplication.processEvents()
