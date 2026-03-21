"""Custom QGraphicsView for the Beat Board canvas."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QGraphicsView, QLabel, QWidget
from PySide6.QtWidgets import QVBoxLayout

from beatboard.core.beat import Beat
from beatboard.core.beat_defaults import BeatDefaults
from beatboard.core.constants import (
    CANVAS_SCENE_SIZE,
    GRID_ENABLED_DEFAULT,
    GRID_SIZE,
    ZOOM_DEFAULT,
    ZOOM_MAX,
    ZOOM_MIN,
    ZOOM_STEP,
)
from beatboard.core.project import Project
from beatboard.ui.canvas.beat_board_scene import BeatBoardScene
from beatboard.ui.canvas.beat_item import BeatItem
from beatboard.ui.canvas.connection_item import ConnectionItem
from beatboard.ui.canvas.image_item import ImageItem

if TYPE_CHECKING:
    from beatboard.ui.canvas.image_item import ImageItem


class BeatBoardView(QGraphicsView):
    beat_created = Signal(str)
    beat_deleted = Signal(str)
    beat_moved = Signal(str)
    connection_updated = Signal(str, str, float, str, str)  # connection_id, color, line_width, node_shape, label
    selection_changed = Signal(dict)
    zoom_changed = Signal(float)
    mouse_moved = Signal(int, int)

    def __init__(self, project: Project, parent: QWidget | None = None, undo_stack=None) -> None:
        super().__init__(parent)
        
        self._project = project
        self._undo_stack = undo_stack
        self._zoom_level = ZOOM_DEFAULT
        self._pan_mode = False
        self._pan_started_with_space = False
        self._last_pan_point = QPoint()
        self._grid_enabled = GRID_ENABLED_DEFAULT
        self._beat_items: dict[str, BeatItem] = {}
        self._connection_items: dict[str, ConnectionItem] = {}
        self._image_items: dict[str, 'ImageItem'] = {}
        self._connection_mode = False
        self._image_mode = False
        self._connection_start_beat: str | None = None
        self._temp_connection_line = None
        self._clipboard_items: list[dict] = []
        self._zoom_selection_mode = False
        self._zoom_selection_start: QPointF | None = None
        self._zoom_selection_rect_item = None
        
        self._setup_scene()
        self._setup_view()
        
        self._load_beats()
        self._load_connections()
        self._load_canvas_images()
        
        self._create_connection_mode_banner()
        self._create_zoom_selection_banner()
        self._create_image_mode_banner()
        
        self.viewport().installEventFilter(self)
    
    def eventFilter(self, obj, event) -> bool:
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.Type.MouseMove:
            pos = self.mapToScene(event.pos())
            x = int(pos.x())
            y = int(-pos.y())
            self.mouse_moved.emit(x, y)
        return super().eventFilter(obj, event)
    
    def _setup_scene(self) -> None:
        self._scene = BeatBoardScene(self._project, self)
        self.setScene(self._scene)
        
        self._scene.scene_clicked.connect(self._on_scene_clicked)
        self._scene.selectionChanged.connect(self._on_selection_changed)
    
    def _setup_view(self) -> None:
        self.setRenderHint(self.renderHints().Antialiasing)
        self.setRenderHint(self.renderHints().SmoothPixmapTransform)
        self.setViewportUpdateMode(self.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(self.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(self.DragMode.RubberBandDrag)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAcceptDrops(True)
        
        half_size = CANVAS_SCENE_SIZE / 2
        self.centerOn(0, 0)
    
    def _load_beats(self) -> None:
        for beat in self._project.beats:
            item = self._add_beat_item(beat)
        
        self._normalize_z_order()
        for beat in self._project.beats:
            item = self._beat_items.get(beat.id)
            if item:
                item.setZValue(beat.z_order)
    
    def _load_connections(self) -> None:
        for connection in self._project.connections:
            self._add_connection_item(connection)
    
    def _load_canvas_images(self) -> None:
        """Load canvas images from project data."""
        import sys
        from PySide6.QtCore import QPointF
        from pathlib import Path
        
        debug = False
        if debug:
            print(f"[BeatBoardView] Loading canvas images, count: {len(self._project.canvas_images)}", file=sys.stderr)
            print(f"[BeatBoardView] Project path: {self._project.project_path}", file=sys.stderr)
        
        for idx, image_data in enumerate(self._project.canvas_images):
            image_id = image_data.get("image_id")
            image_path = image_data.get("image_path")
            if not image_path:
                continue
            
            if debug:
                print(f"[BeatBoardView] Image {idx}: id={image_id}, path={image_path}", file=sys.stderr)
            
            # Intentar resolver ruta absoluta
            absolute_path = None
            if self._project.project_path:
                # Primero intentar ruta relativa al project_path
                candidate = self._project.project_path / image_path
                if debug:
                    print(f"[BeatBoardView]   Candidate: {candidate}", file=sys.stderr)
                if candidate.exists():
                    absolute_path = str(candidate)
                    if debug:
                        print(f"[BeatBoardView]   Found at candidate", file=sys.stderr)
                else:
                    # Buscar en subdirectorios comunes
                    for subdir in ["media", "beats"]:
                        candidate = self._project.project_path / subdir / Path(image_path).name
                        if debug:
                            print(f"[BeatBoardView]   Searching in {subdir}: {candidate}", file=sys.stderr)
                        if candidate.exists():
                            absolute_path = str(candidate)
                            if debug:
                                print(f"[BeatBoardView]   Found in {subdir}", file=sys.stderr)
                            break
            
            position_data = image_data.get("position", {"x": 0, "y": 0})
            size_data = image_data.get("size", {"width": 200, "height": 200})
            rotation = image_data.get("rotation", 0.0)
            opacity = image_data.get("opacity", 1.0)
            fit_mode = image_data.get("fit_mode", "contain")
            
            position = QPointF(position_data.get("x", 0), position_data.get("y", 0))
            size = QPointF(size_data.get("width", 200), size_data.get("height", 200))
            
            # Usar ruta absoluta si se encontró, sino la relativa
            effective_path = absolute_path if absolute_path else image_path
            if debug:
                print(f"[BeatBoardView]   Effective path: {effective_path}", file=sys.stderr)
            
            item = ImageItem(
                image_path=effective_path,
                position=position,
                size=size,
                image_id=image_id,
                rotation=rotation,
                opacity=opacity,
                fit_mode=fit_mode,
            )
            
            self._scene.addItem(item)
            # Usar image_id como clave (si existe), sino el id generado
            key = image_id if image_id else item.image_id
            self._image_items[key] = item
            if debug:
                print(f"[BeatBoardView]   Added item with key: {key}", file=sys.stderr)
            
            # Conectar señales para actualizar proyecto
            item.item_moved.connect(self._on_image_moved)
            item.item_resized.connect(self._on_image_resized)
            
            # Establecer z-order
            z_order = image_data.get("z_order")
            if z_order is not None:
                item.setZValue(z_order)
            else:
                # Asignar z_order secuencial
                z_order = idx + 1
                item.setZValue(z_order)
                # Guardar en datos del proyecto
                self._project.canvas_images[idx]["z_order"] = z_order
    
    def _add_connection_item(self, connection) -> None:
        from beatboard.ui.canvas.connection_item import ConnectionItem
        
        item = ConnectionItem(connection)
        
        source_item = self._beat_items.get(connection.source_beat_id)
        target_item = self._beat_items.get(connection.target_beat_id)
        
        if source_item and target_item:
            item.set_source_item(source_item)
            item.set_target_item(target_item)
            self._scene.addItem(item)
            self._connection_items[connection.id] = item
    
    def toggle_connection_mode(self) -> None:
        self._connection_mode = not self._connection_mode
        if self._connection_mode:
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)
            self._show_connection_mode_banner()
        else:
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            self._hide_connection_mode_banner()
            self._connection_start_beat = None
    
    def is_connection_mode(self) -> bool:
        return self._connection_mode
    
    def toggle_image_mode(self) -> None:
        self._image_mode = not self._image_mode
        if self._image_mode:
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)
            self._show_image_mode_banner()
        else:
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            self._hide_image_mode_banner()
    
    def is_image_mode(self) -> bool:
        return self._image_mode
    
    def _show_image_mode_banner(self) -> None:
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app and hasattr(app, 'locale_manager'):
            from beatboard.i18n.locales import get_locale
            locale_dict = get_locale()
            message = locale_dict.get(
                'image_mode_active',
                "Modo 'Imagen' Activado. Click para añadir imagen. ESC para salir."
            )
            self._image_banner.setText(message)
        else:
            self._image_banner.setText("Modo 'Imagen' Activado. Click para añadir imagen. ESC para salir.")
        
        banner_width = 400
        self._image_banner.setFixedWidth(banner_width)
        x = (self.viewport().width() - banner_width) // 2
        y = self.viewport().height() - 60
        self._image_banner.move(x, y)
        self._image_banner.raise_()
        self._image_banner.show()
    
    def _hide_image_mode_banner(self) -> None:
        if hasattr(self, '_image_banner'):
            self._image_banner.hide()
    
    def _create_image_mode_banner(self) -> None:
        self._image_banner = QLabel(self.viewport())
        self._image_banner.setText("Modo 'Imagen' Activado. Click para añadir imagen. ESC para salir")
        self._image_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_banner.setStyleSheet("""
            QLabel {
                background-color: rgba(156, 39, 176, 220);
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self._image_banner.setFixedHeight(40)
        self._image_banner.hide()
    
    def _create_connection_mode_banner(self) -> None:
        self._connection_banner = QLabel(self.viewport())
        self._connection_banner.setText("Modo 'Conexión' Activado. ESC para Salir")
        self._connection_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._connection_banner.setStyleSheet("""
            QLabel {
                background-color: rgba(33, 150, 243, 220);
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self._connection_banner.setFixedHeight(40)
        self._connection_banner.hide()
    
    def _show_connection_mode_banner(self) -> None:
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app and hasattr(app, 'locale_manager'):
            from beatboard.i18n.locales import get_locale
            locale_dict = get_locale()
            message = locale_dict.get(
                'connection_mode_active',
                "Modo 'Conexión' Activado. ESC para Salir"
            )
            self._connection_banner.setText(message)
        else:
            self._connection_banner.setText("Modo 'Conexión' Activado. ESC para Salir")
        
        banner_width = 350
        self._connection_banner.setFixedWidth(banner_width)
        x = (self.viewport().width() - banner_width) // 2
        y = self.viewport().height() - 60
        self._connection_banner.move(x, y)
        self._connection_banner.raise_()
        self._connection_banner.show()
    
    def _create_zoom_selection_banner(self) -> None:
        self._zoom_selection_banner = QLabel(self.viewport())
        self._zoom_selection_banner.setText("Modo 'Zoom' Activado. Arrastra para seleccionar área. ESC para salir.")
        self._zoom_selection_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._zoom_selection_banner.setStyleSheet("""
            QLabel {
                background-color: rgba(76, 175, 80, 220);
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self._zoom_selection_banner.setFixedHeight(40)
        self._zoom_selection_banner.hide()
    
    def _show_zoom_selection_banner(self) -> None:
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app and hasattr(app, 'locale_manager'):
            from beatboard.i18n.locales import get_locale
            locale_dict = get_locale()
            message = locale_dict.get(
                'zoom_selection_mode_active',
                "Modo 'Zoom' Activado. Arrastra para seleccionar área. ESC para salir."
            )
            self._zoom_selection_banner.setText(message)
        else:
            self._zoom_selection_banner.setText("Modo 'Zoom' Activado. Arrastra para seleccionar área. ESC para salir.")
        
        banner_width = 450
        self._zoom_selection_banner.setFixedWidth(banner_width)
        x = (self.viewport().width() - banner_width) // 2
        y = self.viewport().height() - 60
        self._zoom_selection_banner.move(x, y)
        self._zoom_selection_banner.raise_()
        self._zoom_selection_banner.show()
    
    def _hide_zoom_selection_banner(self) -> None:
        self._zoom_selection_banner.hide()
    
    def _update_zoom_selection_banner_position(self):
        if not hasattr(self, '_zoom_selection_banner'):
            return
        banner_width = self._zoom_selection_banner.width()
        x = (self.viewport().width() - banner_width) // 2
        y = self.viewport().height() - 60
        self._zoom_selection_banner.move(x, y)
    
    def toggle_zoom_selection_mode(self) -> None:
        self._zoom_selection_mode = not self._zoom_selection_mode
        if self._zoom_selection_mode:
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)
            self._show_zoom_selection_banner()
        else:
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            self._hide_zoom_selection_banner()
            self._clear_zoom_selection_rect()
    
    def is_zoom_selection_mode(self) -> bool:
        return self._zoom_selection_mode
    
    def _clear_zoom_selection_rect(self) -> None:
        if self._zoom_selection_rect_item:
            self._scene.removeItem(self._zoom_selection_rect_item)
            self._zoom_selection_rect_item = None
        self._zoom_selection_start = None
    
    def _update_zoom_selection_rect(self, current_pos: QPointF) -> None:
        from PySide6.QtGui import QPen, QBrush, QColor, QPainter
        from PySide6.QtCore import QRectF
        
        if self._zoom_selection_rect_item:
            self._scene.removeItem(self._zoom_selection_rect_item)
        
        x1 = self._zoom_selection_start.x()
        y1 = self._zoom_selection_start.y()
        x2 = current_pos.x()
        y2 = current_pos.y()
        
        rect = QRectF(x1, y1, x2 - x1, y2 - y1)
        
        from PySide6.QtWidgets import QGraphicsRectItem
        self._zoom_selection_rect_item = QGraphicsRectItem(rect)
        self._zoom_selection_rect_item.setPen(QPen(QColor(33, 150, 243), 2))
        self._zoom_selection_rect_item.setBrush(QBrush(QColor(33, 150, 243, 50)))
        self._scene.addItem(self._zoom_selection_rect_item)
    
    def _apply_zoom_to_selection(self, rect: QPointF) -> None:
        if not self._zoom_selection_start:
            return
        
        from PySide6.QtCore import QRectF
        x1 = min(self._zoom_selection_start.x(), rect.x())
        y1 = min(self._zoom_selection_start.y(), rect.y())
        x2 = max(self._zoom_selection_start.x(), rect.x())
        y2 = max(self._zoom_selection_start.y(), rect.y())
        
        selection_rect = QRectF(x1, y1, x2 - x1, y2 - y1)
        
        if selection_rect.width() < 10 or selection_rect.height() < 10:
            self._clear_zoom_selection_rect()
            return
        
        margin_factor = 0.05
        margin_x = selection_rect.width() * margin_factor
        margin_y = selection_rect.height() * margin_factor
        selection_rect.adjust(-margin_x, -margin_y, margin_x, margin_y)
        
        self.fitInView(selection_rect, Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_level = self.transform().m11()
        
        if self._zoom_level < ZOOM_MIN:
            self._zoom_level = ZOOM_MIN
            self._set_zoom(self._zoom_level)
        elif self._zoom_level > ZOOM_MAX:
            self._zoom_level = ZOOM_MAX
            self._set_zoom(self._zoom_level)
        
        self.zoom_changed.emit(self._zoom_level)
        self._clear_zoom_selection_rect()
        
        if self._zoom_selection_mode:
            self.toggle_zoom_selection_mode()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_connection_banner') and self._connection_banner.isVisible():
            self._update_banner_position()
        if hasattr(self, '_zoom_selection_banner') and self._zoom_selection_banner.isVisible():
            self._update_zoom_selection_banner_position()
    
    def _update_banner_position(self):
        if not hasattr(self, '_connection_banner'):
            return
        banner_width = self._connection_banner.width()
        x = (self.viewport().width() - banner_width) // 2
        y = self.viewport().height() - 60
        self._connection_banner.move(x, y)
    
    def _hide_connection_mode_banner(self) -> None:
        self._connection_banner.hide()
    
    def _on_beat_clicked_for_connection(self, beat_id: str) -> None:
        if not self._connection_mode:
            return
        
        if self._connection_start_beat is None:
            self._connection_start_beat = beat_id
        else:
            if self._connection_start_beat != beat_id:
                self._create_connection(self._connection_start_beat, beat_id)
            self._connection_start_beat = None
    
    def _create_connection(self, source_id: str, target_id: str) -> None:
        from beatboard.core.connection import Connection
        
        connection = Connection(source_beat_id=source_id, target_beat_id=target_id)
        
        if self._undo_stack:
            from beatboard.ui.undo_commands import CreateConnectionCommand
            cmd = CreateConnectionCommand(self._project, self, connection)
            self._undo_stack.push(cmd)
        else:
            self._project.add_connection(connection)
            self._add_connection_item(connection)
    
    def _on_beat_move_started(self, beat_id: str, x: float, y: float) -> None:
        self._move_start_positions = getattr(self, '_move_start_positions', {})
        self._move_start_positions[beat_id] = QPointF(x, y)
        
        if self._undo_stack:
            from beatboard.ui.undo_commands import MoveBeatCommand
            
            self._current_move_command = MoveBeatCommand(
                self._project, self, beat_id,
                QPointF(x, y), QPointF(x, y)
            )
    
    def _add_beat_item(self, beat: Beat) -> BeatItem:
        project_path = self._project.project_path if self._project else None
        item = BeatItem(beat, project_path=project_path)
        self._scene.addItem(item)
        self._beat_items[beat.id] = item
        
        max_z = self._get_max_z_order()
        beat.z_order = max_z + 1
        item.setZValue(beat.z_order)
        
        item.item_moved.connect(self._on_beat_moved)
        item.item_move_started.connect(self._on_beat_move_started)
        item.item_move_ended.connect(self._on_beat_move_ended)
        item.item_selected.connect(self._on_beat_selected)
        item.item_double_clicked.connect(self._on_beat_double_clicked)
        item.item_clicked.connect(self._on_beat_clicked_for_connection)
        item.item_resized.connect(self._on_beat_resized)
        
        return item
    
    def _get_max_z_order(self) -> int:
        max_z = 0
        if self._project.beats:
            max_z = max(beat.z_order for beat in self._project.beats)
        for item in self._image_items.values():
            z = item.zValue()
            if z > max_z:
                max_z = z
        return max_z
    
    def _get_beat_by_z_order(self, z_order: int) -> Beat | None:
        for beat in self._project.beats:
            if beat.z_order == z_order:
                return beat
        return None
    
    def _normalize_z_order(self) -> None:
        # Recopilar todos los elementos con su z actual
        elements = []
        
        # Beats
        for beat in self._project.beats:
            elements.append(("beat", beat, beat.z_order))
        
        # Imágenes
        for image_data in self._project.canvas_images:
            z = image_data.get("z_order")
            if z is None:
                item = self._image_items.get(image_data.get("image_id"))
                if item:
                    z = item.zValue()
                else:
                    z = 0
            elements.append(("image", image_data, z))
        
        # Ordenar por z
        elements.sort(key=lambda x: x[2])
        
        # Reasignar z secuencialmente
        for i, (elem_type, elem, _) in enumerate(elements, start=1):
            if elem_type == "beat":
                elem.z_order = i
                item = self._beat_items.get(elem.id)
                if item:
                    item.setZValue(i)
            else:  # image
                elem["z_order"] = i
                item = self._image_items.get(elem.get("image_id"))
                if item:
                    item.setZValue(i)
    
    def _on_beat_resized(self, beat_id: str, width: float, height: float) -> None:
        if BeatDefaults.is_memorize_enabled():
            BeatDefaults.set_last_size(width, height)
        self._update_connections_for_beat(beat_id)
    
    def _get_item_by_beat_id(self, beat_id: str) -> BeatItem | None:
        return self._beat_items.get(beat_id)
    
    def _on_scene_clicked(self, pos: QPointF) -> None:
        pass
    
    def _on_selection_changed(self) -> None:
        selected_items = self._scene.selectedItems()
        beat_ids = []
        connection_ids = []
        for item in selected_items:
            if isinstance(item, BeatItem):
                beat_ids.append(item.beat_id)
            elif isinstance(item, ConnectionItem):
                connection_ids.append(item._connection.id)
        self.selection_changed.emit({
            'beats': beat_ids,
            'connections': connection_ids
        })
    
    def _on_beat_moved(self, beat_id: str, x: float, y: float) -> None:
        new_pos = QPointF(x, y)
        
        if self._undo_stack and hasattr(self, '_current_move_command'):
            cmd = self._current_move_command
            if cmd and cmd._beat_id == beat_id:
                old_pos = cmd._new_pos
                cmd._new_pos = new_pos
                beat = self._project.get_beat_by_id(beat_id)
                if beat:
                    beat.set_position(x, y)
        
        start_positions = getattr(self, '_move_start_positions', {})
        old_pos = start_positions.get(beat_id)
        
        self._update_connections_for_beat(beat_id, old_pos, new_pos)
        self.beat_moved.emit(beat_id)
    
    def _on_beat_move_ended(self, beat_id: str) -> None:
        if self._undo_stack and hasattr(self, '_current_move_command'):
            cmd = self._current_move_command
            if cmd and cmd._beat_id == beat_id and cmd._old_pos != cmd._new_pos:
                self._undo_stack.push(cmd)
            self._current_move_command = None
    
    def _update_connections_for_beat(self, beat_id: str, old_pos: QPointF | None = None, new_pos: QPointF | None = None) -> None:
        for conn_id, item in self._connection_items.items():
            connection = self._project.get_connection_by_id(conn_id)
            if not connection:
                continue
            
            if old_pos and new_pos:
                delta = new_pos - old_pos
                if hasattr(item, 'apply_delta_to_custom_points'):
                    item.apply_delta_to_custom_points(beat_id, delta)
            
            if hasattr(item, 'update_positions'):
                item.update_positions()
    
    def _on_beat_selected(self, beat_id: str) -> None:
        pass
    
    def _on_beat_double_clicked(self, beat_id: str) -> None:
        beat = self._project.get_beat_by_id(beat_id) if self._project else None
        
        if beat:
            from beatboard.ui.dialogs.beat_editor_dialog import BeatEditorDialog
            dialog = BeatEditorDialog(beat, self)
            if dialog.exec():
                title, content, color, content_mode, content_markdown, embedded_images = dialog.get_beat_data()
                
                old_data = {
                    "title": beat.title,
                    "content": beat.content,
                    "color": beat.color,
                }
                new_data = {
                    "title": title,
                    "content": content,
                    "color": color,
                }
                
                if self._undo_stack:
                    from beatboard.ui.undo_commands import EditBeatCommand
                    cmd = EditBeatCommand(self._project, self, beat_id, old_data, new_data)
                    self._undo_stack.push(cmd)
                
                beat.title = title
                beat.content = content
                beat.color = color
                beat.content_mode = content_mode
                beat.content_markdown = content_markdown
                beat.embedded_images = embedded_images
                BeatDefaults.update_from_beat(beat)
                
                item = self._get_item_by_beat_id(beat_id)
                if item:
                    item.update()
                
                self.beat_moved.emit(beat_id)
                self.selection_changed.emit({'beats': [beat_id], 'connections': []})
    
    def set_project(self, project: Project) -> None:
        self._project = project
        self._beat_items.clear()
        self._connection_items.clear()
        # Eliminar imágenes existentes de la escena
        for item in list(self._image_items.values()):
            self._scene.removeItem(item)
        self._image_items.clear()
        self._scene.set_project(project)
        self._load_beats()
        self._load_connections()
        self._load_canvas_images()
        self.centerOn(0, 0)
    
    @property
    def zoom_level(self) -> float:
        return self._zoom_level
    
    def zoom_in(self) -> None:
        new_zoom = self._zoom_level + ZOOM_STEP
        if new_zoom <= ZOOM_MAX:
            self._set_zoom(new_zoom)
    
    def zoom_out(self) -> None:
        new_zoom = self._zoom_level - ZOOM_STEP
        if new_zoom >= ZOOM_MIN:
            self._set_zoom(new_zoom)
    
    def _set_zoom(self, level: float) -> None:
        self._zoom_level = level
        self.resetTransform()
        self.scale(level, level)
        self.zoom_changed.emit(level)
    
    def fit_to_contents(self) -> None:
        items = self._scene.items()
        if not items:
            self.centerOn(0, 0)
            return
        
        bounding_rect = self._scene.itemsBoundingRect()
        if bounding_rect.isValid():
            self.fitInView(bounding_rect, Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom_level = self.transform().m11()
            self.zoom_changed.emit(self._zoom_level)
    
    def center_on_origin(self) -> None:
        self.centerOn(0, 0)
    
    def create_beat_at(self, pos: QPointF) -> BeatItem | None:
        from beatboard.ui.undo_commands import CreateBeatCommand
        
        beat = Beat()
        beat.set_position(pos.x() - 100, pos.y() - 75)
        
        beat.color = BeatDefaults.get_default_color()
        default_size = BeatDefaults.get_default_size()
        beat.set_size(default_size.width(), default_size.height())
        
        if self._undo_stack:
            cmd = CreateBeatCommand(self._project, self, beat)
            self._undo_stack.push(cmd)
            return self._beat_items.get(beat.id)
        else:
            self._project.add_beat(beat)
            item = self._add_beat_item(beat)
            self.beat_created.emit(beat.id)
            return item
    
    def copy_selected_beats(self) -> None:
        from beatboard.ui.canvas.beat_item import BeatItem
        from beatboard.ui.canvas.image_item import ImageItem
        
        selected_items = self._scene.selectedItems()
        items_to_copy = []
        
        for item in selected_items:
            if isinstance(item, BeatItem):
                beat = self._project.get_beat_by_id(item.beat_id)
                if beat:
                    items_to_copy.append({
                        "type": "beat",
                        "data": beat.to_dict()
                    })
            elif isinstance(item, ImageItem):
                image_id = item.image_id
                for img_data in self._project.canvas_images:
                    if img_data.get("image_id") == image_id:
                        items_to_copy.append({
                            "type": "image",
                            "data": img_data.copy()
                        })
                        break
        
        self._clipboard_items = items_to_copy
    
    def cut_selected_beats(self) -> None:
        from beatboard.ui.canvas.beat_item import BeatItem
        from beatboard.ui.canvas.image_item import ImageItem
        
        self.copy_selected_beats()
        
        if self._clipboard_items:
            selected_items = self._scene.selectedItems()
            beats_to_delete = []
            images_to_delete = []
            
            for item in selected_items:
                if isinstance(item, BeatItem):
                    beat = self._project.get_beat_by_id(item.beat_id)
                    if beat:
                        beats_to_delete.append((item, beat))
                elif isinstance(item, ImageItem):
                    image_id = item.image_id
                    images_to_delete.append((item, image_id))
            
            # Eliminar beats
            for item, beat in beats_to_delete:
                beat_id = beat.id
                self._scene.removeItem(item)
                self._project.remove_beat(beat_id)
                if beat_id in self._beat_items:
                    del self._beat_items[beat_id]
                self.beat_deleted.emit(beat_id)
            
            # Eliminar imágenes
            for item, image_id in images_to_delete:
                self._scene.removeItem(item)
                if image_id in self._image_items:
                    del self._image_items[image_id]
                # Eliminar del proyecto
                self._project.canvas_images = [
                    img for img in self._project.canvas_images
                    if img.get("image_id") != image_id
                ]
                self._project.update_modified()
    
    def paste_beats(self) -> None:
        if not self._clipboard_items:
            return
        
        import uuid
        beat_id_mapping = {}
        image_id_mapping = {}
        
        for item_data in self._clipboard_items:
            item_type = item_data["type"]
            data = item_data["data"]
            
            if item_type == "beat":
                old_id = data["id"]
                new_id = str(uuid.uuid4())
                beat_id_mapping[old_id] = new_id
                
                new_beat_data = data.copy()
                new_beat_data["id"] = new_id
                
                pos = data.get("position", {"x": 0, "y": 0})
                new_beat_data["position"] = {
                    "x": pos.get("x", 0) + 30,
                    "y": pos.get("y", 0) + 30
                }
                
                from beatboard.core.beat import Beat
                new_beat = Beat.from_dict(new_beat_data)
                
                self._project.add_beat(new_beat)
                item = self._add_beat_item(new_beat)
                self.beat_created.emit(new_beat.id)
                
            elif item_type == "image":
                old_id = data["image_id"]
                new_id = str(uuid.uuid4())
                image_id_mapping[old_id] = new_id
                
                new_image_data = data.copy()
                new_image_data["image_id"] = new_id
                
                pos = data.get("position", {"x": 0, "y": 0})
                new_image_data["position"] = {
                    "x": pos.get("x", 0) + 30,
                    "y": pos.get("y", 0) + 30
                }
                
                # Agregar al proyecto
                self._project.canvas_images.append(new_image_data)
                self._project.update_modified()
                
                # Crear item
                item = self._add_image_item(new_image_data)
                item.setSelected(True)
        
        self._scene.clearSelection()
        
        # Seleccionar nuevos elementos
        for item_data in self._clipboard_items:
            item_type = item_data["type"]
            data = item_data["data"]
            if item_type == "beat":
                old_id = data["id"]
                new_id = beat_id_mapping.get(old_id)
                if new_id and new_id in self._beat_items:
                    self._beat_items[new_id].setSelected(True)
            elif item_type == "image":
                old_id = data["image_id"]
                new_id = image_id_mapping.get(old_id)
                if new_id and new_id in self._image_items:
                    self._image_items[new_id].setSelected(True)
    
    def delete_selected_beats(self) -> None:
        selected_items = self._scene.selectedItems()
        beats_to_delete = []
        connections_to_delete = []
        images_to_delete = []
        
        for item in selected_items:
            if isinstance(item, BeatItem):
                beats_to_delete.append((item, self._project.get_beat_by_id(item.beat_id)))
            elif hasattr(item, 'connection_id'):
                connections_to_delete.append(item)
            elif hasattr(item, 'image_id'):
                images_to_delete.append(item)
        
        total_to_delete = len(beats_to_delete) + len(connections_to_delete) + len(images_to_delete)
        
        if total_to_delete > 1:
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Eliminar {total_to_delete} elementos seleccionados?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Eliminar imágenes
        if self._undo_stack and images_to_delete:
            from beatboard.ui.undo_commands import DeleteImageCommand
            for img_item in images_to_delete:
                img_id = img_item.image_id
                # Buscar datos de imagen
                image_data = None
                for img in self._project.canvas_images:
                    if img.get("image_id") == img_id:
                        image_data = img
                        break
                if image_data:
                    cmd = DeleteImageCommand(self._project, self, image_data)
                    self._undo_stack.push(cmd)
        else:
            for img_item in images_to_delete:
                img_id = img_item.image_id
                self._scene.removeItem(img_item)
                if img_id in self._image_items:
                    del self._image_items[img_id]
                # Eliminar del proyecto
                self._project.canvas_images = [
                    img for img in self._project.canvas_images
                    if img.get("image_id") != img_id
                ]
                self._project.update_modified()
        
        if self._undo_stack and (beats_to_delete or connections_to_delete):
            from beatboard.ui.undo_commands import DeleteBeatCommand, DeleteConnectionCommand
            
            for item, beat in beats_to_delete:
                if beat:
                    cmd = DeleteBeatCommand(self._project, self, beat)
                    self._undo_stack.push(cmd)
            
            for conn_item in connections_to_delete:
                conn = self._project.get_connection_by_id(conn_item.connection_id)
                if conn:
                    cmd = DeleteConnectionCommand(self._project, self, conn)
                    self._undo_stack.push(cmd)
        else:
            for item, beat in beats_to_delete:
                if beat:
                    beat_id = beat.id
                    self._scene.removeItem(item)
                    self._project.remove_beat(beat_id)
                    if beat_id in self._beat_items:
                        del self._beat_items[beat_id]
                    self.beat_deleted.emit(beat_id)
            
            for conn_item in connections_to_delete:
                conn_id = conn_item.connection_id
                self._scene.removeItem(conn_item)
                self._project.remove_connection(conn_id)
                if conn_id in self._connection_items:
                    del self._connection_items[conn_id]
    
    def select_all_beats(self) -> None:
        for item in self._beat_items.values():
            item.setSelected(True)
    
    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            super().wheelEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_mode = True
            self._last_pan_point = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        
        if self._zoom_selection_mode and event.button() == Qt.MouseButton.LeftButton:
            self._zoom_selection_start = self.mapToScene(event.pos())
            event.accept()
            return
        
        if self._image_mode and event.button() == Qt.MouseButton.LeftButton:
            self._add_image_at(event.pos())
            event.accept()
            return
        
        if event.button() == Qt.MouseButton.RightButton:
            item = self.itemAt(event.pos())
            if isinstance(item, BeatItem):
                item.setSelected(True)
                self._show_context_menu(event.globalPos(), item.beat_id)
                event.accept()
                return
            elif hasattr(item, 'image_id'):
                item.setSelected(True)
                self._show_image_context_menu(event.globalPos(), item.image_id)
                event.accept()
                return
        
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item is None:
                self._scene.clearSelection()
            self.setFocus()
        
        super().mousePressEvent(event)
    
    def _add_image_at(self, pos) -> None:
        from PySide6.QtWidgets import QFileDialog
        from PySide6.QtCore import QPointF
        import uuid
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self._tr("select_image"),
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp)"
        )
        
        if not file_path:
            return
        
        scene_pos = self.mapToScene(pos)
        
        # Cargar imagen para obtener dimensiones originales
        image_data = self._create_image_data(file_path, scene_pos)
        if not image_data:
            return
        
        if self._undo_stack:
            from beatboard.ui.undo_commands import CreateImageCommand
            cmd = CreateImageCommand(self._project, self, image_data)
            self._undo_stack.push(cmd)
        else:
            self._add_image_item(image_data)
            item = self._image_items.get(image_data["image_id"])
            if item:
                item.setSelected(True)
            self._project.canvas_images.append(image_data)
            self._project.update_modified()
        
        self.toggle_image_mode()
    
    def _create_image_data(self, file_path: str, scene_pos) -> dict | None:
        from PySide6.QtCore import QPointF
        from PySide6.QtGui import QPixmap
        import uuid
        
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            return None
        
        image_id = str(uuid.uuid4().hex)
        position = QPointF(scene_pos.x() - 100, scene_pos.y() - 75)
        size = QPointF(pixmap.width(), pixmap.height())
        
        max_z = self._get_max_z_order()
        z_order = max_z + 1
        
        image_data = {
            "image_id": image_id,
            "image_path": file_path,
            "position": {"x": position.x(), "y": position.y()},
            "size": {"width": size.x(), "height": size.y()},
            "rotation": 0.0,
            "opacity": 1.0,
            "fit_mode": "contain",
            "z_order": z_order,
        }
        return image_data
    
    def _add_image_item(self, image_data: dict):
        from beatboard.ui.canvas.image_item import ImageItem
        from PySide6.QtCore import QPointF
        
        image_path = self._resolve_image_path(image_data["image_path"])
        
        item = ImageItem(
            image_path=image_path,
            position=QPointF(image_data["position"]["x"], image_data["position"]["y"]),
            size=QPointF(image_data["size"]["width"], image_data["size"]["height"]),
            image_id=image_data["image_id"],
            rotation=image_data.get("rotation", 0.0),
            opacity=image_data.get("opacity", 1.0),
            fit_mode=image_data.get("fit_mode", "contain"),
        )
        
        self._scene.addItem(item)
        self._image_items[item.image_id] = item
        
        item.item_moved.connect(self._on_image_moved)
        item.item_resized.connect(self._on_image_resized)
        
        z_order = image_data.get("z_order")
        if z_order is not None:
            item.setZValue(z_order)
        else:
            min_z = self._get_min_z_order()
            item.setZValue(min_z - 1)
        
        return item
    
    def _resolve_image_path(self, image_path: str) -> str:
        from pathlib import Path
        
        path_obj = Path(image_path)
        if path_obj.exists():
            return str(path_obj)
        
        if self._project.project_path:
            project_path = Path(self._project.project_path)
            full_path = project_path / image_path
            if full_path.exists():
                return str(full_path)
            
            target_name = Path(image_path).name
            
            for search_dir in [project_path / "media", project_path / "beats", project_path]:
                if search_dir.exists():
                    for item in search_dir.rglob("*"):
                        if item.is_file() and item.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                            if item.name == target_name:
                                return str(item)
        return image_path
    
    def _remove_image_item(self, image_id: str) -> None:
        if image_id in self._image_items:
            item = self._image_items[image_id]
            self._scene.removeItem(item)
            del self._image_items[image_id]
    
    def _get_min_z_order(self) -> int:
        if not self._project.beats and not self._image_items:
            return 0
        
        min_z = 0
        for beat in self._project.beats:
            if beat.z_order < min_z:
                min_z = beat.z_order
        for item in self._image_items.values():
            z = item.zValue()
            if z < min_z:
                min_z = z
        return min_z
    
    def _tr(self, key: str) -> str:
        from beatboard.i18n import _tr
        return _tr(key)
    
    def _show_context_menu(self, pos: QPointF, beat_id: str) -> None:
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("Editar beat")
        edit_action.triggered.connect(lambda: self._on_beat_double_clicked(beat_id))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Eliminar")
        delete_action.triggered.connect(lambda: self._delete_beat_by_id(beat_id))
        
        menu.exec(pos)
    
    def _show_image_context_menu(self, pos, image_id: str) -> None:
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        delete_action = menu.addAction("Eliminar imagen")
        delete_action.triggered.connect(lambda: self._delete_image_by_id(image_id))
        
        menu.exec(pos)
    
    def _delete_image_by_id(self, image_id: str) -> None:
        import sys
        debug = False
        if debug:
            print(f"[BeatBoardView] _delete_image_by_id: {image_id}", file=sys.stderr)
            print(f"[BeatBoardView]   _image_items keys: {list(self._image_items.keys())}", file=sys.stderr)
            print(f"[BeatBoardView]   canvas_images before: {len(self._project.canvas_images)}", file=sys.stderr)
            for i, img in enumerate(self._project.canvas_images):
                print(f"[BeatBoardView]     [{i}] id: {img.get('image_id')}, path: {img.get('image_path')}", file=sys.stderr)
        
        # Buscar imagen en proyecto
        image_data = None
        for img in self._project.canvas_images:
            if img.get("image_id") == image_id:
                image_data = img
                break
        
        if not image_data:
            if debug:
                print(f"[BeatBoardView]   image_id not found in canvas_images", file=sys.stderr)
            return
        
        if self._undo_stack:
            from beatboard.ui.undo_commands import DeleteImageCommand
            cmd = DeleteImageCommand(self._project, self, image_data)
            self._undo_stack.push(cmd)
        else:
            if image_id in self._image_items:
                item = self._image_items[image_id]
                self._scene.removeItem(item)
                del self._image_items[image_id]
            # Eliminar del proyecto
            self._project.canvas_images = [
                img for img in self._project.canvas_images
                if img.get("image_id") != image_id
            ]
            self._project.update_modified()
            if debug:
                print(f"[BeatBoardView]   Deleted item, canvas_images after: {len(self._project.canvas_images)}", file=sys.stderr)
    
    def _on_image_moved(self, image_id: str, x: float, y: float) -> None:
        """Actualizar posición de imagen en proyecto."""
        for img_data in self._project.canvas_images:
            if img_data.get("image_id") == image_id:
                img_data["position"] = {"x": x, "y": y}
                self._project.update_modified()
                break
    
    def _on_image_resized(self, image_id: str, width: float, height: float) -> None:
        """Actualizar tamaño de imagen en proyecto."""
        for img_data in self._project.canvas_images:
            if img_data.get("image_id") == image_id:
                img_data["size"] = {"width": width, "height": height}
                self._project.update_modified()
                break
    
    def _delete_beat_by_id(self, beat_id: str) -> None:
        beat = self._project.get_beat_by_id(beat_id)
        if not beat:
            return
            
        if self._undo_stack:
            from beatboard.ui.undo_commands import DeleteBeatCommand
            cmd = DeleteBeatCommand(self._project, self, beat)
            self._undo_stack.push(cmd)
        else:
            item = self._get_item_by_beat_id(beat_id)
            if item:
                self._scene.removeItem(item)
                self._project.remove_beat(beat_id)
                if beat_id in self._beat_items:
                    del self._beat_items[beat_id]
                self.beat_deleted.emit(beat_id)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._pan_mode:
            if self._pan_started_with_space:
                self._last_pan_point = event.pos()
                self._pan_started_with_space = False
            
            current_pos = event.pos()
            delta = current_pos - self._last_pan_point
            self._last_pan_point = current_pos
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return
        
        if self._zoom_selection_mode and self._zoom_selection_start:
            current_pos = self.mapToScene(event.pos())
            self._update_zoom_selection_rect(current_pos)
            event.accept()
            return
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_mode = False
            self._pan_started_with_space = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        
        if self._zoom_selection_mode and self._zoom_selection_start and event.button() == Qt.MouseButton.LeftButton:
            end_pos = self.mapToScene(event.pos())
            self._apply_zoom_to_selection(end_pos)
            event.accept()
            return
        
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item is None:
                scene_pos = self.mapToScene(event.pos())
                self.create_beat_at(scene_pos)
                event.accept()
                return
        
        super().mouseDoubleClickEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._scene.clearSelection()
            if self._connection_mode:
                self.toggle_connection_mode()
            if self._zoom_selection_mode:
                self.toggle_zoom_selection_mode()
            if self._image_mode:
                self.toggle_image_mode()
            event.accept()
            return
        
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            self.delete_selected_beats()
            event.accept()
            return
        
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._pan_mode = True
            self._pan_started_with_space = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        
        # Atajos de teclado para colores (1-0)
        if event.key() >= Qt.Key.Key_1 and event.key() <= Qt.Key.Key_9:
            color_index = event.key() - Qt.Key.Key_1
            self._change_selected_beat_color(color_index)
            self._change_selected_connection_color(color_index)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_0:
            color_index = 9  # 0 es el décimo color (índice 9)
            self._change_selected_beat_color(color_index)
            self._change_selected_connection_color(color_index)
            event.accept()
            return
        
        # Tecla C para activar/desactivar modo conexión (cuando no hay nada seleccionado)
        if event.key() == Qt.Key.Key_C and not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            # Solo activar/desactivar modo conexión si no hay nada seleccionado
            selected_items = self._scene.selectedItems()
            if not selected_items:
                self.toggle_connection_mode()
                event.accept()
                return
        
        # Tecla Z para activar/desactivar modo zoom selection (cuando no hay nada seleccionado)
        if event.key() == Qt.Key.Key_Z and not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            selected_items = self._scene.selectedItems()
            if not selected_items:
                self.toggle_zoom_selection_mode()
                event.accept()
                return
        
        # Tecla I para activar/desactivar modo imagen (cuando no hay nada seleccionado)
        if event.key() == Qt.Key.Key_I and not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            selected_items = self._scene.selectedItems()
            if not selected_items:
                self.toggle_image_mode()
                event.accept()
                return
        
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                self.copy_selected_beats()
                event.accept()
                return
            if event.key() == Qt.Key.Key_X:
                self.cut_selected_beats()
                event.accept()
                return
            if event.key() == Qt.Key.Key_V:
                self.paste_beats()
                event.accept()
                return
            if event.key() == Qt.Key.Key_Home:
                self.bring_selected_beats_to_front()
                event.accept()
                return
            if event.key() == Qt.Key.Key_End:
                self.send_selected_beats_to_back()
                event.accept()
                return
            if event.key() == Qt.Key.Key_PageDown:
                self.move_selected_beats_down()
                event.accept()
                return
            if event.key() == Qt.Key.Key_PageUp:
                self.move_selected_beats_up()
                event.accept()
                return
        
        super().keyPressEvent(event)
    
    def _get_current_selection(self) -> dict:
        selected_items = self._scene.selectedItems()
        beat_ids = []
        connection_ids = []
        image_ids = []
        for item in selected_items:
            if isinstance(item, BeatItem):
                beat_ids.append(item.beat_id)
            elif isinstance(item, ConnectionItem):
                connection_ids.append(item._connection.id)
            elif isinstance(item, ImageItem):
                image_ids.append(item.image_id)
        return {'beats': beat_ids, 'connections': connection_ids, 'images': image_ids}
    
    def bring_selected_beats_to_front(self) -> None:
        selected_items = self._scene.selectedItems()
        
        beats_to_move: list[BeatItem] = [item for item in selected_items if isinstance(item, BeatItem)]
        images_to_move: list[ImageItem] = [item for item in selected_items if isinstance(item, ImageItem)]
        
        if not beats_to_move and not images_to_move:
            return
        
        max_z = self._get_max_z_order()
        
        for item in beats_to_move:
            beat = self._project.get_beat_by_id(item.beat_id)
            if beat:
                beat.z_order = max_z + 1
                item.setZValue(beat.z_order)
        
        for item in images_to_move:
            new_z = max_z + 2
            item.setZValue(new_z)
            # Actualizar en proyecto
            image_id = item.image_id
            for img_data in self._project.canvas_images:
                if img_data.get("image_id") == image_id:
                    img_data["z_order"] = new_z
                    break
        self._project.update_modified()
        
        self._normalize_z_order()
        
        for beat in self._project.beats:
            item = self._beat_items.get(beat.id)
            if item:
                item.setZValue(beat.z_order)
        
        self.selection_changed.emit(self._get_current_selection())
    
    def send_selected_beats_to_back(self) -> None:
        selected_items = self._scene.selectedItems()
        
        beats_to_move: list[BeatItem] = [item for item in selected_items if isinstance(item, BeatItem)]
        images_to_move: list[ImageItem] = [item for item in selected_items if isinstance(item, ImageItem)]
        
        if not beats_to_move and not images_to_move:
            return
        
        min_z = self._get_min_z_order()
        
        for item in beats_to_move:
            beat = self._project.get_beat_by_id(item.beat_id)
            if beat:
                beat.z_order = min_z - 1
                item.setZValue(beat.z_order)
        
        for item in images_to_move:
            new_z = min_z - 2
            item.setZValue(new_z)
            # Actualizar en proyecto
            image_id = item.image_id
            for img_data in self._project.canvas_images:
                if img_data.get("image_id") == image_id:
                    img_data["z_order"] = new_z
                    break
        self._project.update_modified()
        
        self._normalize_z_order()
        
        for beat in self._project.beats:
            item = self._beat_items.get(beat.id)
            if item:
                item.setZValue(beat.z_order)
        
        self.selection_changed.emit(self._get_current_selection())
    
    def move_selected_beats_up(self) -> None:
        selected_items = self._scene.selectedItems()
        
        beats_to_move = [item for item in selected_items if isinstance(item, BeatItem)]
        if not beats_to_move:
            return
        
        current_z_orders = sorted([item.zValue() for item in beats_to_move], reverse=True)
        
        for item in beats_to_move:
            beat = self._project.get_beat_by_id(item.beat_id)
            if not beat:
                continue
            
            current_z = beat.z_order
            next_z = current_z + 1
            
            other_beat = self._get_beat_by_z_order(next_z)
            if other_beat:
                other_beat.z_order = current_z
                other_item = self._beat_items.get(other_beat.id)
                if other_item:
                    other_item.setZValue(current_z)
            
            beat.z_order = next_z
            item.setZValue(next_z)
        
        self.selection_changed.emit(self._get_current_selection())
    
    def move_selected_beats_down(self) -> None:
        selected_items = self._scene.selectedItems()
        
        beats_to_move = [item for item in selected_items if isinstance(item, BeatItem)]
        if not beats_to_move:
            return
        
        for item in beats_to_move:
            beat = self._project.get_beat_by_id(item.beat_id)
            if not beat:
                continue
            
            current_z = beat.z_order
            if current_z <= 1:
                continue
            
            prev_z = current_z - 1
            
            other_beat = self._get_beat_by_z_order(prev_z)
            if other_beat:
                other_beat.z_order = current_z
                other_item = self._beat_items.get(other_beat.id)
                if other_item:
                    other_item.setZValue(current_z)
            
            beat.z_order = prev_z
            item.setZValue(prev_z)
        
        self.selection_changed.emit(self._get_current_selection())
    
    def _change_selected_beat_color(self, color_index: int) -> None:
        from beatboard.core.constants import (
            BEAT_PREDEFINED_COLORS,
            BEAT_CUSTOM_COLORS,
            get_valid_beat_color,
        )
        from PySide6.QtWidgets import QApplication
        
        # Obtener colores personalizados del ThemeManager
        custom_colors = BEAT_CUSTOM_COLORS.copy()  # Por defecto
        app = QApplication.instance()
        if app and hasattr(app, 'theme_manager'):
            custom_colors = app.theme_manager.get_custom_colors()
        
        # Combinar colores predefinidos y personalizados
        all_colors = BEAT_PREDEFINED_COLORS + custom_colors
        
        if color_index < 0 or color_index >= len(all_colors):
            return
        
        selected_items = self._scene.selectedItems()
        
        for item in selected_items:
            if isinstance(item, BeatItem):
                beat = self._project.get_beat_by_id(item.beat_id)
                if beat:
                    beat.color = all_colors[color_index]
                    item.update()
                    self._update_connections_for_beat(beat.id)
                    # Emitir señal para actualizar panel de propiedades
                    self.beat_moved.emit(beat.id)
    
    def _change_selected_connection_color(self, color_index: int) -> None:
        from beatboard.core.constants import (
            CONNECTION_COLORS,
            CONNECTION_COLOR_DEFAULT,
        )
        from PySide6.QtWidgets import QApplication
        
        # Obtener colores personalizados del ThemeManager
        custom_colors = []
        app = QApplication.instance()
        if app and hasattr(app, 'theme_manager'):
            custom_colors = app.theme_manager.get_custom_colors()
        
        # Combinar colores predefinidos y personalizados
        predefined_colors = list(CONNECTION_COLORS.keys())
        all_colors = predefined_colors + custom_colors
        
        if color_index < 0 or color_index >= len(all_colors):
            return
        
        selected_items = self._scene.selectedItems()
        
        connection_items = [item for item in selected_items if hasattr(item, '_connection') and item._connection]
        
        for item in connection_items:
            connection = item._connection
            color_value = all_colors[color_index]
            connection.color = color_value
            item.update()
            # Emitir señal para actualizar panel de propiedades
            self.connection_updated.emit(
                connection.id,
                connection.color,
                connection.line_width,
                connection.node_shape,
                connection.label or ""
            )
    
    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._pan_mode = False
            self._pan_started_with_space = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        
        super().keyReleaseEvent(event)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.endswith('.bbp') or file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                    event.acceptProposedAction()
                    return
        super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.endswith('.bbp') or file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                    event.acceptProposedAction()
                    return
        super().dragMoveEvent(event)
    
    def dropEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if not urls:
                super().dropEvent(event)
                return
            
            # Handle project files
            project_files = [url.toLocalFile() for url in urls if url.toLocalFile().endswith('.bbp')]
            if project_files:
                main_window = self.window()
                if hasattr(main_window, '_load_project'):
                    main_window._load_project(project_files[0])
                event.acceptProposedAction()
                return
            
            # Handle image files
            image_files = []
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                    image_files.append(file_path)
            
            if image_files:
                scene_pos = self.mapToScene(event.pos())
                for file_path in image_files:
                    image_data = self._create_image_data(file_path, scene_pos)
                    if not image_data:
                        continue
                    
                    if self._undo_stack:
                        from beatboard.ui.undo_commands import CreateImageCommand
                        cmd = CreateImageCommand(self._project, self, image_data)
                        self._undo_stack.push(cmd)
                    else:
                        self._add_image_item(image_data)
                        item = self._image_items.get(image_data["image_id"])
                        if item:
                            item.setSelected(True)
                        self._project.canvas_images.append(image_data)
                        self._project.update_modified()
                
                event.acceptProposedAction()
                return
        
        super().dropEvent(event)
