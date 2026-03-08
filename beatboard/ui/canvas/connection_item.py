"""Connection item for drawing lines between beats."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QPointF, QRectF, Signal, Qt
from PySide6.QtGui import (QPainterPath, QPainterPathStroker, QPen, QColor, 
                          QPainter, QBrush, QTransform, QPolygonF)
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem, QApplication
import math

from beatboard.core.connection import Connection
from beatboard.core.constants import (
    CONNECTION_COLORS,
    CONNECTION_LINE_WIDTH,
    CONNECTION_OFFSET_PERCENT,
    CONNECTION_OFFSET_MIN,
    DEBUG_SHOW_Z_ORDER,
)

if TYPE_CHECKING:
    from beatboard.ui.canvas.beat_item import BeatItem


class ConnectionItem(QGraphicsPathItem):
    connection_deleted = Signal(str)
    connection_control_points_changed = Signal(str, object, object)
    
    HANDLE_SIZE = 14
    HANDLE_HIT_SIZE = 30
    HANDLE_COLOR = QColor("#1976D2")
    HANDLE_HOVER_COLOR = QColor("#FF5722")
    LINE_COLOR = QColor("#1976D2")
    
    def __init__(self, connection: Connection, parent: QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        
        self._connection = connection
        self._source_item: BeatItem | None = None
        self._target_item: BeatItem | None = None
        
        self._custom_cp1: Optional[QPointF] = None  # cached absolute position
        self._custom_cp2: Optional[QPointF] = None  # cached absolute position
        self._custom_factor1: Optional[tuple[float, float]] = None  # (factor_x, factor_y) relative to source
        self._custom_factor2: Optional[tuple[float, float]] = None  # (factor_x, factor_y) relative to target
        self._dragging_handle: Optional[int] = None
        self._hovering_handle: Optional[int] = None
        self._source_pos_start: Optional[QPointF] = None
        self._target_pos_start: Optional[QPointF] = None
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        self._update_pen()
        self._update_path()
        
        if connection.control_factor1 is not None:
            self._custom_factor1 = connection.control_factor1
        if connection.control_factor2 is not None:
            self._custom_factor2 = connection.control_factor2
    
    def _get_offset_percent(self) -> float:
        app = QApplication.instance()
        if app and hasattr(app, 'theme_manager'):
            return app.theme_manager.get_connection_offset_percent()
        return CONNECTION_OFFSET_PERCENT
    
    def _get_offset_distance(self, rect: QRectF) -> float:
        percent = self._get_offset_percent()
        distance = rect.width() * percent
        return max(distance, CONNECTION_OFFSET_MIN)
    
    def _update_pen(self) -> None:
        color = CONNECTION_COLORS.get(self._connection.color, CONNECTION_COLORS["blue"])
        line_width = self._connection.line_width if hasattr(self._connection, 'line_width') else CONNECTION_LINE_WIDTH
        pen = QPen(QColor(color), line_width)
        pen.setStyle(Qt.PenStyle.SolidLine)
        self.setPen(pen)
    
    def _update_path(self) -> None:
        if not self._source_item or not self._target_item:
            return
            
        path = QPainterPath()
        
        source_rect = self._source_item.boundingRect()
        target_rect = self._target_item.boundingRect()
        source_pos = self._source_item.scenePos()
        target_pos = self._target_item.scenePos()
        
        source_center_y = source_pos.y() + source_rect.height() / 2
        target_center_y = target_pos.y() + target_rect.height() / 2
        
        source_right = source_pos.x() + source_rect.width()
        source_left = source_pos.x()
        target_right = target_pos.x() + target_rect.width()
        target_left = target_pos.x()
        
        offset1 = self._get_offset_distance(source_rect)
        offset2 = self._get_offset_distance(target_rect)
        
        if target_pos.x() > source_pos.x():
            start_x = source_right - offset1
            end_x = target_left + offset2
        else:
            start_x = source_left + offset1
            end_x = target_right - offset2
        
        start = QPointF(start_x, source_center_y)
        end = QPointF(end_x, target_center_y)
        
        cp1 = self._compute_control_point(1)
        cp2 = self._compute_control_point(2)
        
        path.moveTo(start)
        path.cubicTo(cp1, cp2, end)
        
        self.setPath(path)
        self._update_z_value()
    
    def _update_z_value(self) -> None:
        if self._source_item and self._target_item:
            source_z = self._source_item.zValue()
            target_z = self._target_item.zValue()
            max_z = max(source_z, target_z)
            self.setZValue(max_z + 1)
    
    def refresh(self) -> None:
        """Actualizar apariencia después de cambios en propiedades."""
        self._update_pen()
        self._update_path()
        self.update()
    
    def _draw_terminations(self, painter: QPainter) -> None:
        """Dibujar formas en las terminaciones de la línea (flechas, círculos, cuadrados)."""
        if not self._source_item or not self._target_item:
            return
        
        # Obtener forma de nodos de la conexión
        node_shape = self._connection.node_shape if hasattr(self._connection, 'node_shape') else "circle"
        if node_shape == "none":
            return
        
        path = self.path()
        if path.isEmpty():
            return
        
        # Obtener puntos de inicio y fin
        start_point = path.pointAtPercent(0.0)
        end_point = path.pointAtPercent(1.0)
        
        # Calcular ángulos de tangente en los extremos
        # Usar puntos cercanos para estimar la dirección
        start_angle = self._get_angle_at_percent(path, 0.0)
        end_angle = self._get_angle_at_percent(path, 1.0)
        
        # Grosor de línea para dimensionar las formas
        line_width = self._connection.line_width if hasattr(self._connection, 'line_width') else 2.0
        size = max(8.0, line_width * 3)  # Tamaño base proporcional al grosor
        
        # Color de la línea
        color = self.pen().color()
        
        # Dibujar terminación inicial (opcional, podríamos solo dibujar la final)
        # Por ahora dibujamos ambas
        self._draw_termination_shape(painter, start_point, start_angle, size, color, node_shape)
        self._draw_termination_shape(painter, end_point, end_angle, size, color, node_shape)
    
    def _get_angle_at_percent(self, path: QPainterPath, percent: float) -> float:
        """Calcular ángulo de la tangente en un punto del path."""
        # Usar un delta pequeño para calcular derivada
        delta = 0.01
        if percent == 0.0:
            p1 = path.pointAtPercent(percent)
            p2 = path.pointAtPercent(percent + delta)
        elif percent == 1.0:
            p1 = path.pointAtPercent(percent - delta)
            p2 = path.pointAtPercent(percent)
        else:
            p1 = path.pointAtPercent(percent - delta/2)
            p2 = path.pointAtPercent(percent + delta/2)
        
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        
        # Calcular ángulo en radianes, luego convertir a grados
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        return angle_deg
    
    def _draw_termination_shape(self, painter: QPainter, point: QPointF, angle: float, 
                               size: float, color: QColor, shape: str) -> None:
        """Dibujar una forma geométrica en un punto con orientación."""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Mover al punto y rotar según el ángulo
        painter.translate(point)
        painter.rotate(angle)
        
        # Configurar pincel y lapiz
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(150), 1))
        
        half = size / 2
        
        if shape == "circle":
            painter.drawEllipse(QPointF(0, 0), half, half)
        elif shape == "square":
            painter.drawRect(QRectF(-half, -half, size, size))
        elif shape == "arrow":
            # Triángulo apuntando hacia la dirección positiva del eje X
            arrow_size = size * 1.2
            arrow_height = arrow_size * 0.6
            polygon = QPolygonF()
            polygon.append(QPointF(arrow_size/2, 0))  # Punta
            polygon.append(QPointF(-arrow_size/2, -arrow_height/2))
            polygon.append(QPointF(-arrow_size/2, arrow_height/2))
            painter.drawPolygon(polygon)
        
        painter.restore()
    
    def _get_connection_geometry(self) -> tuple[float, float, float, float, float, float, float]:
        """Returns (start_x, end_x, source_center_y, target_center_y, dx, dy, curvature)."""
        if not self._source_item or not self._target_item:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        source_rect = self._source_item.boundingRect()
        target_rect = self._target_item.boundingRect()
        source_pos = self._source_item.scenePos()
        target_pos = self._target_item.scenePos()
        
        source_center_y = source_pos.y() + source_rect.height() / 2
        target_center_y = target_pos.y() + target_rect.height() / 2
        
        offset1 = self._get_offset_distance(source_rect)
        offset2 = self._get_offset_distance(target_rect)
        
        if target_pos.x() > source_pos.x():
            start_x = source_pos.x() + source_rect.width() - offset1
            end_x = target_pos.x() + offset2
        else:
            start_x = source_pos.x() + offset1
            end_x = target_pos.x() + target_rect.width() - offset2
        
        dx = abs(end_x - start_x)
        dy = target_center_y - source_center_y
        curvature = min(dx * 1.0, 200)      # Default: (dx * 0.4, 120)
        
        return start_x, end_x, source_center_y, target_center_y, dx, dy, curvature
    
    def _compute_control_point(self, handle_num: int) -> QPointF:
        """Compute absolute position of control point (handle_num 1 or 2)."""
        if not self._source_item or not self._target_item:
            return QPointF(0, 0)
        
        start_x, end_x, source_center_y, target_center_y, dx, dy, curvature = self._get_connection_geometry()
        
        if handle_num == 1:
            factor = self._custom_factor1
            base_x = start_x
            base_y = source_center_y
            default = QPointF(start_x + curvature, source_center_y + dy * 0.1)  # Default: 0.4
        else:
            factor = self._custom_factor2
            base_x = end_x
            base_y = target_center_y
            default = QPointF(end_x - curvature, target_center_y - dy * 0.1)    # Default: 0.4
        
        if factor is None:
            return default
        
        factor_x, factor_y = factor
        
        # For handle 1: position relative to source
        # For handle 2: position relative to target
        # The factor represents relative position within the connection's dimensions
        # factor_x: 0 = base_x, 1 = other_beat's x (but we'll use dx for scaling)
        # factor_y: 0 = base_y, 1 = other_beat's y (using dy)
        # Note: dx is always positive (absolute distance)
        # We need to consider direction (start_x may be > end_x)
        if handle_num == 1:
            # CP1 moves relative to source
            cp_x = start_x + factor_x * dx if start_x <= end_x else start_x - factor_x * dx
            cp_y = source_center_y + factor_y * dy
        else:
            # CP2 moves relative to target
            cp_x = end_x + factor_x * dx if end_x <= start_x else end_x - factor_x * dx
            cp_y = target_center_y + factor_y * dy
        
        return QPointF(cp_x, cp_y)
    
    def _update_factors_from_position(self, handle_num: int, scene_pos: QPointF) -> None:
        """Update factor for given handle based on absolute scene position."""
        if not self._source_item or not self._target_item:
            return
        
        start_x, end_x, source_center_y, target_center_y, dx, dy, _ = self._get_connection_geometry()
        
        if handle_num == 1:
            base_x = start_x
            base_y = source_center_y
            other_x = end_x
        else:
            base_x = end_x
            base_y = target_center_y
            other_x = start_x
        
        # Compute factor_x relative to dx (always positive)
        if dx > 0:
            # Determine direction: if base_x <= other_x, positive direction
            if base_x <= other_x:
                factor_x = (scene_pos.x() - base_x) / dx
            else:
                factor_x = (base_x - scene_pos.x()) / dx
        else:
            factor_x = 0.0
        
        # Compute factor_y relative to dy
        if dy != 0:
            factor_y = (scene_pos.y() - base_y) / dy
        else:
            factor_y = 0.0
        
        # Clamp factors to reasonable range? Maybe allow any value for flexibility
        # but we can limit to e.g., [-2, 2] to prevent extreme curves
        factor_x = max(min(factor_x, 2.0), -2.0)
        factor_y = max(min(factor_y, 2.0), -2.0)
        
        if handle_num == 1:
            self._custom_factor1 = (factor_x, factor_y)
            self._custom_cp1 = scene_pos  # cache
            self._connection.control_factor1 = (factor_x, factor_y)
        else:
            self._custom_factor2 = (factor_x, factor_y)
            self._custom_cp2 = scene_pos  # cache
            self._connection.control_factor2 = (factor_x, factor_y)
    
    def set_source_item(self, item: BeatItem) -> None:
        self._source_item = item
        self._update_path()
    
    def set_target_item(self, item: BeatItem) -> None:
        self._target_item = item
        self._update_path()
    
    def update_positions(self) -> None:
        self._update_path()
    
    def update_positions_with_delta(self, beat_id: str, delta_x: float, delta_y: float) -> None:
        # No-op: factors maintain relative position automatically
        pass
    
    def save_start_positions(self, beat_id: str, pos: QPointF) -> None:
        if beat_id == self._connection.source_beat_id:
            self._source_pos_start = pos
        elif beat_id == self._connection.target_beat_id:
            self._target_pos_start = pos
    
    def apply_delta_to_custom_points(self, beat_id: str, delta: QPointF) -> None:
        # No-op: factors maintain relative position automatically
        pass
    
    @property
    def connection_id(self) -> str:
        return self._connection.id
    
    def set_control_points(self, cp1: Optional[QPointF], cp2: Optional[QPointF]) -> None:
        if cp1 is not None and self._source_item and self._target_item:
            self._update_factors_from_position(1, cp1)
        else:
            self._custom_factor1 = None
            self._custom_cp1 = cp1
        
        if cp2 is not None and self._source_item and self._target_item:
            self._update_factors_from_position(2, cp2)
        else:
            self._custom_factor2 = None
            self._custom_cp2 = cp2
        
        self._update_path()
    
    def reset_control_points(self) -> None:
        self._custom_factor1 = None
        self._custom_factor2 = None
        self._custom_cp1 = None
        self._custom_cp2 = None
        self._connection.control_factor1 = None
        self._connection.control_factor2 = None
        self._update_path()
    
    def _get_handle_position(self, handle_num: int) -> QPointF:
        return self._compute_control_point(handle_num)
    
    def _get_handle_at(self, scene_pos: QPointF) -> Optional[int]:
        if not self.isSelected():
            return None
        
        half_hit = self.HANDLE_HIT_SIZE / 2
        
        for handle_num in [1, 2]:
            handle_pos = self._get_handle_position(handle_num)
            handle_rect = QRectF(
                handle_pos.x() - half_hit,
                handle_pos.y() - half_hit,
                self.HANDLE_HIT_SIZE,
                self.HANDLE_HIT_SIZE
            )
            if handle_rect.contains(scene_pos):
                return handle_num
        
        return None
    
    def boundingRect(self) -> QRectF:
        rect = super().boundingRect()
        if not self._source_item or not self._target_item:
            return rect
        
        half_hit = self.HANDLE_HIT_SIZE / 2
        for handle_num in [1, 2]:
            handle_pos_scene = self._get_handle_position(handle_num)
            handle_pos = self.mapFromScene(handle_pos_scene)
            handle_rect = QRectF(
                handle_pos.x() - half_hit,
                handle_pos.y() - half_hit,
                self.HANDLE_HIT_SIZE,
                self.HANDLE_HIT_SIZE
            )
            rect = rect.united(handle_rect)
        
        return rect
    
    def shape(self) -> QPainterPath:
        path = self.path()
        if path.isEmpty():
            return super().shape()
        stroker = QPainterPathStroker()
        stroker.setWidth(12)
        shape_path = stroker.createStroke(path)
        
        if not self._source_item or not self._target_item:
            return shape_path
        
        half_hit = self.HANDLE_HIT_SIZE / 2
        for handle_num in [1, 2]:
            handle_pos_scene = self._get_handle_position(handle_num)
            handle_pos = self.mapFromScene(handle_pos_scene)
            handle_rect = QRectF(
                handle_pos.x() - half_hit,
                handle_pos.y() - half_hit,
                self.HANDLE_HIT_SIZE,
                self.HANDLE_HIT_SIZE
            )
            handle_path = QPainterPath()
            handle_path.addRect(handle_rect)
            shape_path = shape_path.united(handle_path)
        
        return shape_path
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            handle = self._get_handle_at(scene_pos)
            if handle:
                self._dragging_handle = handle
                event.accept()
                return
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event) -> None:
        if self._dragging_handle:
            scene_pos = self.mapToScene(event.pos())
            self._update_factors_from_position(self._dragging_handle, scene_pos)
            self._update_path()
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        if self._dragging_handle:
            self._dragging_handle = None
            event.accept()
            return
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            handle = self._get_handle_at(scene_pos)
            if handle:
                if handle == 1:
                    self._custom_factor1 = None
                    self._custom_cp1 = None
                else:
                    self._custom_factor2 = None
                    self._custom_cp2 = None
                self._update_path()
                self.update()
                event.accept()
                return
        super().mouseDoubleClickEvent(event)
    
    def hoverEnterEvent(self, event) -> None:
        scene_pos = self.mapToScene(event.pos())
        self._hovering_handle = self._get_handle_at(scene_pos)
        if self._hovering_handle:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        super().hoverEnterEvent(event)
    
    def hoverMoveEvent(self, event) -> None:
        scene_pos = self.mapToScene(event.pos())
        handle = self._get_handle_at(scene_pos)
        if handle:
            self.setCursor(Qt.CursorShape.SizeAllCursor)
            self._hovering_handle = handle
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self._hovering_handle = None
        self.update()
        super().hoverMoveEvent(event)
    
    def hoverLeaveEvent(self, event) -> None:
        self._hovering_handle = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)
    
    def paint(self, painter: QPainter, option, widget=None) -> None:
        if self.isSelected():
            pen = self.pen()
            pen.setWidth(int(pen.widthF() + 3))
            pen.setColor(QColor("#1976D2"))
            painter.setPen(pen)
        else:
            painter.setPen(self.pen())
        
        painter.drawPath(self.path())
        
        # Dibujar terminaciones (flechas, círculos, cuadrados)
        self._draw_terminations(painter)
        
        if self.isSelected():
            self._draw_control_handles(painter)
    
    def _draw_control_handles(self, painter: QPainter) -> None:
        if not self._source_item or not self._target_item:
            return
        
        # Los handles de control siempre son círculos (independientes de node_shape)
        
        source_rect = self._source_item.boundingRect()
        target_rect = self._target_item.boundingRect()
        source_pos = self._source_item.scenePos()
        target_pos = self._target_item.scenePos()
        
        offset1 = self._get_offset_distance(source_rect)
        offset2 = self._get_offset_distance(target_rect)
        
        source_center_y = source_pos.y() + source_rect.height() / 2
        target_center_y = target_pos.y() + target_rect.height() / 2
        
        if target_pos.x() > source_pos.x():
            start_x = source_pos.x() + source_rect.width() - offset1
            end_x = target_pos.x() + offset2
        else:
            start_x = source_pos.x() + offset1
            end_x = target_pos.x() + target_rect.width() - offset2
        
        start_point = QPointF(start_x, source_center_y)
        end_point = QPointF(end_x, target_center_y)
        
        cp1_pos = self._get_handle_position(1)
        cp2_pos = self._get_handle_position(2)
        
        dashed_pen = QPen(self.LINE_COLOR, 1)
        dashed_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(dashed_pen)
        painter.drawLine(start_point, cp1_pos)
        painter.drawLine(end_point, cp2_pos)
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for i, cp_pos in enumerate([cp1_pos, cp2_pos], 1):
            if self._hovering_handle == i:
                color = self.HANDLE_HOVER_COLOR
            else:
                color = self.HANDLE_COLOR
            
            half = self.HANDLE_SIZE / 2
            rect = QRectF(cp_pos.x() - half, cp_pos.y() - half, self.HANDLE_SIZE, self.HANDLE_SIZE)
            
            # Dibujar handle de control (siempre círculo)
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
            painter.drawEllipse(cp_pos, half, half)
            
            painter.setPen(QPen(color, 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)
            
            # DEBUG: dibujar zona de colisión (transparente, 30x30)
            debug_size = 30
            half_debug = debug_size / 2
            painter.setPen(QPen(QColor(0, 0, 0, 0), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(cp_pos.x() - half_debug, cp_pos.y() - half_debug, 
                                   debug_size, debug_size))
        
        if DEBUG_SHOW_Z_ORDER and self._source_item and self._target_item:
            z = int(self.zValue())
            path = self.path()
            if not path.isEmpty():
                point = path.pointAtPercent(0.5)
                from PySide6.QtGui import QFont
                debug_font = QFont("Arial", 8)
                debug_font.setBold(True)
                painter.setFont(debug_font)
                painter.setPen(QColor("#FF0000"))
                painter.drawText(QRectF(point.x() - 15, point.y() - 8, 30, 16), f"z:{z}")

