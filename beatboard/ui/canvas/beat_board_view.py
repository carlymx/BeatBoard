"""Custom QGraphicsView for the Beat Board canvas."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QEvent, QPointF, Qt, Signal
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

if TYPE_CHECKING:
    pass


class BeatBoardView(QGraphicsView):
    beat_created = Signal(str)
    beat_deleted = Signal(str)
    beat_moved = Signal(str)
    selection_changed = Signal(dict)
    zoom_changed = Signal(float)
    mouse_moved = Signal(int, int)

    def __init__(self, project: Project, parent: QWidget | None = None, undo_stack=None) -> None:
        super().__init__(parent)
        
        self._project = project
        self._undo_stack = undo_stack
        self._zoom_level = ZOOM_DEFAULT
        self._pan_mode = False
        self._last_pan_point = QPointF()
        self._grid_enabled = GRID_ENABLED_DEFAULT
        self._beat_items: dict[str, BeatItem] = {}
        self._connection_items: dict[str, ConnectionItem] = {}
        self._connection_mode = False
        self._connection_start_beat: str | None = None
        self._temp_connection_line = None
        self._clipboard_beats: list[dict] = []
        
        self._setup_scene()
        self._setup_view()
        
        self._load_beats()
        self._load_connections()
        
        self._create_connection_mode_banner()
        
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
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_connection_banner') and self._connection_banner.isVisible():
            self._update_banner_position()
    
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
        item = BeatItem(beat)
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
        if not self._project.beats:
            return 0
        return max(beat.z_order for beat in self._project.beats)
    
    def _get_beat_by_z_order(self, z_order: int) -> Beat | None:
        for beat in self._project.beats:
            if beat.z_order == z_order:
                return beat
        return None
    
    def _normalize_z_order(self) -> None:
        beats_sorted = sorted(self._project.beats, key=lambda b: b.z_order)
        for i, beat in enumerate(beats_sorted, start=1):
            beat.z_order = i
    
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
                title, content, color = dialog.get_beat_data()
                
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
        self._scene.set_project(project)
        self._load_beats()
        self._load_connections()
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
        selected_items = self._scene.selectedItems()
        beats_to_copy = []
        
        for item in selected_items:
            if isinstance(item, BeatItem):
                beat = self._project.get_beat_by_id(item.beat_id)
                if beat:
                    beats_to_copy.append(beat.to_dict())
        
        self._clipboard_beats = beats_to_copy
    
    def cut_selected_beats(self) -> None:
        self.copy_selected_beats()
        
        if self._clipboard_beats:
            selected_items = self._scene.selectedItems()
            beats_to_delete = []
            
            for item in selected_items:
                if isinstance(item, BeatItem):
                    beat = self._project.get_beat_by_id(item.beat_id)
                    if beat:
                        beats_to_delete.append((item, beat))
            
            for item, beat in beats_to_delete:
                beat_id = beat.id
                self._scene.removeItem(item)
                self._project.remove_beat(beat_id)
                if beat_id in self._beat_items:
                    del self._beat_items[beat_id]
                self.beat_deleted.emit(beat_id)
    
    def paste_beats(self) -> None:
        if not self._clipboard_beats:
            return
        
        import uuid
        beat_id_mapping = {}
        
        for beat_data in self._clipboard_beats:
            old_id = beat_data["id"]
            new_id = str(uuid.uuid4())
            beat_id_mapping[old_id] = new_id
            
            new_beat_data = beat_data.copy()
            new_beat_data["id"] = new_id
            
            pos = beat_data.get("position", {"x": 0, "y": 0})
            new_beat_data["position"] = {
                "x": pos.get("x", 0) + 30,
                "y": pos.get("y", 0) + 30
            }
            
            from beatboard.core.beat import Beat
            new_beat = Beat.from_dict(new_beat_data)
            
            self._project.add_beat(new_beat)
            item = self._add_beat_item(new_beat)
            self.beat_created.emit(new_beat.id)
        
        self._scene.clearSelection()
        
        for beat_data in self._clipboard_beats:
            old_id = beat_data["id"]
            new_id = beat_id_mapping.get(old_id)
            
            if new_id and new_id in self._beat_items:
                self._beat_items[new_id].setSelected(True)
    
    def delete_selected_beats(self) -> None:
        selected_items = self._scene.selectedItems()
        beats_to_delete = []
        connections_to_delete = []
        
        for item in selected_items:
            if isinstance(item, BeatItem):
                beats_to_delete.append((item, self._project.get_beat_by_id(item.beat_id)))
            elif hasattr(item, 'connection_id'):
                connections_to_delete.append(item)
        
        total_to_delete = len(beats_to_delete) + len(connections_to_delete)
        
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
        
        if event.button() == Qt.MouseButton.RightButton:
            item = self.itemAt(event.pos())
            if isinstance(item, BeatItem):
                item.setSelected(True)
                self._show_context_menu(event.globalPos(), item.beat_id)
                event.accept()
                return
        
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if item is None:
                self._scene.clearSelection()
            self.setFocus()
        
        super().mousePressEvent(event)
    
    def _show_context_menu(self, pos: QPointF, beat_id: str) -> None:
        from PySide6.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        edit_action = menu.addAction("Editar beat")
        edit_action.triggered.connect(lambda: self._on_beat_double_clicked(beat_id))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("Eliminar")
        delete_action.triggered.connect(lambda: self._delete_beat_by_id(beat_id))
        
        menu.exec(pos)
    
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
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_mode = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
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
            event.accept()
            return
        
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            self.delete_selected_beats()
            event.accept()
            return
        
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._pan_mode = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        
        # Atajos de teclado para colores (1-0)
        if event.key() >= Qt.Key.Key_1 and event.key() <= Qt.Key.Key_9:
            color_index = event.key() - Qt.Key.Key_1
            self._change_selected_beat_color(color_index)
            event.accept()
            return
        elif event.key() == Qt.Key.Key_0:
            color_index = 9  # 0 es el décimo color (índice 9)
            self._change_selected_beat_color(color_index)
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
        for item in selected_items:
            if isinstance(item, BeatItem):
                beat_ids.append(item.beat_id)
            elif isinstance(item, ConnectionItem):
                connection_ids.append(item._connection.id)
        return {'beats': beat_ids, 'connections': connection_ids}
    
    def bring_selected_beats_to_front(self) -> None:
        selected_items = self._scene.selectedItems()
        
        beats_to_move = [item for item in selected_items if isinstance(item, BeatItem)]
        if not beats_to_move:
            return
        
        max_z = self._get_max_z_order()
        
        for item in beats_to_move:
            beat = self._project.get_beat_by_id(item.beat_id)
            if beat:
                beat.z_order = max_z + 1
                item.setZValue(beat.z_order)
        
        self._normalize_z_order()
        
        for beat in self._project.beats:
            item = self._beat_items.get(beat.id)
            if item:
                item.setZValue(beat.z_order)
        
        self.selection_changed.emit(self._get_current_selection())
    
    def send_selected_beats_to_back(self) -> None:
        selected_items = self._scene.selectedItems()
        
        beats_to_move = [item for item in selected_items if isinstance(item, BeatItem)]
        if not beats_to_move:
            return
        
        min_z = 1
        
        for item in beats_to_move:
            beat = self._project.get_beat_by_id(item.beat_id)
            if beat:
                beat.z_order = min_z
                item.setZValue(beat.z_order)
        
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
    
    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._pan_mode = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        
        super().keyReleaseEvent(event)
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().endswith('.bbp'):
                event.acceptProposedAction()
                return
        super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().endswith('.bbp'):
                event.acceptProposedAction()
                return
        super().dragMoveEvent(event)
    
    def dropEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path.endswith('.bbp'):
                    main_window = self.window()
                    if hasattr(main_window, '_load_project'):
                        main_window._load_project(file_path)
                    event.acceptProposedAction()
                    return
        super().dropEvent(event)
