"""Image item widget for QGraphicsScene."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QTransform,
)
from PySide6.QtWidgets import QGraphicsItem, QGraphicsObject

from beatboard.core.constants import (
    BEAT_SHADOW_OFFSET,
    BEAT_SHADOW_OPACITY,
    DEBUG_SHOW_Z_ORDER,
)
from beatboard.i18n import _tr

if TYPE_CHECKING:
    pass


class ImageItem(QGraphicsObject):
    """Graphics item for displaying images on the canvas."""

    item_moved = Signal(str, float, float)
    item_move_started = Signal(str, float, float)
    item_move_ended = Signal(str)
    item_selected = Signal(str)
    item_double_clicked = Signal(str)
    item_clicked = Signal(str)
    item_resized = Signal(str, float, float)

    RESIZE_HANDLE_SIZE = 8

    def __init__(
        self,
        image_path: str,
        parent: QGraphicsItem | None = None,
        position: QPointF | None = None,
        size: QPointF | None = None,
        image_id: str | None = None,
        rotation: float = 0.0,
        opacity: float = 1.0,
        fit_mode: str = "contain",
    ) -> None:
        super().__init__(parent)

        self._id = image_id if image_id is not None else str(id(self))
        self._image_path = image_path
        self._original_pixmap: Optional[QPixmap] = None
        self._is_hovering = False
        self._resizing = False
        self._resize_start_pos: Optional[QPointF] = None
        self._resize_start_size: Optional[QPointF] = None
        self._resize_handle: Optional[str] = None
        self._rotation = rotation
        self._opacity = opacity
        self._fit_mode = fit_mode

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self._load_image()

        if position:
            self.setPos(position)
        else:
            self.setPos(0, 0)

        if size:
            self._current_size = size
        elif self._original_pixmap:
            self._current_size = QPointF(
                self._original_pixmap.width(),
                self._original_pixmap.height(),
            )
        else:
            self._current_size = QPointF(200, 200)

        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self._update_pixmap()

    @property
    def image_id(self) -> str:
        return self._id

    @property
    def image_path(self) -> str:
        return self._image_path

    def _load_image(self) -> None:
        import sys
        debug = False
        if debug:
            print(f"[ImageItem] Loading image: {self._image_path}", file=sys.stderr)
        
        if Path(self._image_path).exists():
            if debug:
                print(f"[ImageItem]   Found at absolute path: {self._image_path}", file=sys.stderr)
            pix = QPixmap(self._image_path)
            if pix.isNull():
                if debug:
                    print(f"[ImageItem]   FAILED to load pixmap from {self._image_path}", file=sys.stderr)
            else:
                self._original_pixmap = pix
                if debug:
                    print(f"[ImageItem]   Pixmap loaded successfully", file=sys.stderr)
                return
        
        project_path = self._get_project_path()
        if debug:
            print(f"[ImageItem]   Project path: {project_path}", file=sys.stderr)
        
        if project_path:
            full_path = project_path / self._image_path
            if debug:
                print(f"[ImageItem]   Trying project_path/image_path: {full_path}", file=sys.stderr)
            if full_path.exists():
                pix = QPixmap(str(full_path))
                if pix.isNull():
                    if debug:
                        print(f"[ImageItem]   FAILED to load pixmap from {full_path}", file=sys.stderr)
                else:
                    self._original_pixmap = pix
                    if debug:
                        print(f"[ImageItem]   Found at project relative path", file=sys.stderr)
                    return
            
            for search_dir in [project_path / "media", project_path / "beats", project_path]:
                if debug:
                    print(f"[ImageItem]   Searching in: {search_dir}", file=sys.stderr)
                if search_dir.exists():
                    for item in search_dir.iterdir():
                        if item.is_file() and item.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                            if debug:
                                print(f"[ImageItem]     Checking: {item.name}", file=sys.stderr)
                            if item.stem in self._image_path or self._image_path in str(item):
                                pix = QPixmap(str(item))
                                if pix.isNull():
                                    if debug:
                                        print(f"[ImageItem]     FAILED to load pixmap from {item}", file=sys.stderr)
                                else:
                                    self._original_pixmap = pix
                                    if debug:
                                        print(f"[ImageItem]     Matched!", file=sys.stderr)
                                    return
        if debug:
            print(f"[ImageItem]   Image not found", file=sys.stderr)

    def _get_project_path(self) -> Optional[Path]:
        import sys
        debug = False
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if debug:
            print(f"[ImageItem] _get_project_path: app={app}", file=sys.stderr)
        if app and hasattr(app, "main_window"):
            main_window = app.main_window
            if debug:
                print(f"[ImageItem]   main_window={main_window}", file=sys.stderr)
            if hasattr(main_window, "_project") and main_window._project:
                project = main_window._project
                if debug:
                    print(f"[ImageItem]   project={project}", file=sys.stderr)
                if hasattr(project, "project_path") and project.project_path:
                    path = Path(project.project_path)
                    if debug:
                        print(f"[ImageItem]   project_path={path}", file=sys.stderr)
                    return path
        if debug:
            print(f"[ImageItem]   returning None", file=sys.stderr)
        return None

    def _get_current_size(self) -> QPointF:
        return self._current_size

    def _update_pixmap(self) -> None:
        if not self._original_pixmap or self._original_pixmap.isNull():
            return

        current_size = self._get_current_size()

        if self._fit_mode == "contain":
            scaled = self._original_pixmap.scaled(
                int(current_size.x()),
                int(current_size.y()),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._display_pixmap = scaled
        elif self._fit_mode == "cover":
            scaled = self._original_pixmap.scaled(
                int(current_size.x()),
                int(current_size.y()),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._display_pixmap = scaled
        else:
            self._display_pixmap = self._original_pixmap.scaled(
                int(current_size.x()),
                int(current_size.y()),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

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
        if not self._original_pixmap or self._original_pixmap.isNull():
            self._draw_placeholder(painter)
            return

        size = self._get_current_size()

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        shadow_color = QColor(0, 0, 0, int(255 * BEAT_SHADOW_OPACITY))
        shadow_rect = QRectF(
            BEAT_SHADOW_OFFSET,
            BEAT_SHADOW_OFFSET,
            size.x(),
            size.y(),
        )
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(shadow_rect)

        painter.setOpacity(self._opacity)

        if self._display_pixmap and not self._display_pixmap.isNull():
            pixmap_rect = QRectF(0, 0, size.x(), size.y())
            painter.drawPixmap(pixmap_rect.topLeft(), self._display_pixmap)

        if self.isSelected():
            pen = QPen(QColor("#1976D2"), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(0, 0, size.x(), size.y()))
            self._draw_resize_handles(painter)

        if DEBUG_SHOW_Z_ORDER:
            z = int(self.zValue())
            from PySide6.QtGui import QFont
            debug_font = QFont("Arial", 8)
            debug_font.setBold(True)
            painter.setFont(debug_font)
            painter.setPen(QColor("#FF0000"))
            painter.drawText(QRectF(5, 2, 30, 15), f"z:{z}")

    def _draw_placeholder(self, painter: QPainter) -> None:
        size = self._get_current_size()

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QBrush(QColor("#E0E0E0")))
        painter.setPen(QPen(QColor("#999999"), 1))
        painter.drawRect(QRectF(0, 0, size.x(), size.y()))

        from PySide6.QtGui import QFont
        placeholder_font = QFont("Arial", 10)
        painter.setFont(placeholder_font)
        painter.setPen(QColor("#666666"))

        text = _tr("image_not_found")
        painter.drawText(
            QRectF(0, 0, size.x(), size.y()),
            Qt.AlignmentFlag.AlignCenter,
            text,
        )

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
                self.item_clicked.emit(self._id)
                self.item_move_started.emit(self._id, self.x(), self.y())

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._resizing and self._resize_start_pos and self._resize_start_size:
            delta = event.scenePos() - self._resize_start_pos
            new_width = max(50, self._resize_start_size.x() + delta.x())
            new_height = max(50, self._resize_start_size.y() + delta.y())

            self._current_size = QPointF(new_width, new_height)
            self._update_pixmap()
            self.update()

            self.item_resized.emit(self._id, new_width, new_height)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._resizing:
            self._resizing = False
            self._resize_handle = None
            self._resize_start_pos = None
            self._resize_start_size = None
            self.item_resized.emit(self._id, self._current_size.x(), self._current_size.y())
        elif event.button() == Qt.MouseButton.LeftButton:
            self.item_move_ended.emit(self._id)

        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        self.item_double_clicked.emit(self._id)
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.item_moved.emit(self._id, value.x(), value.y())
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if value:
                self.item_selected.emit(self._id)
        return super().itemChange(change, value)

    def set_fit_mode(self, mode: str) -> None:
        self._fit_mode = mode
        self._update_pixmap()
        self.update()

    def set_opacity(self, opacity: float) -> None:
        self._opacity = max(0.0, min(1.0, opacity))
        self.update()

    def set_rotation(self, degrees: float) -> None:
        self._rotation = degrees
        self.setTransform(QTransform().rotate(degrees))
        self.update()

    def refresh(self) -> None:
        from PySide6.QtWidgets import QApplication

        self._load_image()
        self._update_pixmap()
        self.prepareGeometryChange()
        self.update()
        QApplication.processEvents()
