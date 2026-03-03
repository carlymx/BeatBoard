"""Undo/Redo commands for Beat Board."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF
from PySide6.QtGui import QUndoCommand

if TYPE_CHECKING:
    from beatboard.core.beat import Beat
    from beatboard.core.connection import Connection
    from beatboard.core.project import Project
    from beatboard.ui.canvas.beat_board_view import BeatBoardView


class CreateBeatCommand(QUndoCommand):
    def __init__(
        self,
        project: Project,
        view: BeatBoardView,
        beat: Beat,
        description: str = "Crear beat",
    ) -> None:
        super().__init__(description)
        self._project = project
        self._view = view
        self._beat = beat
        self._item = None

    def redo(self) -> None:
        self._project.add_beat(self._beat)
        self._item = self._view._add_beat_item(self._beat)
        self._view.beat_created.emit(self._beat.id)

    def undo(self) -> None:
        if self._item:
            self._view._scene.removeItem(self._item)
            del self._view._beat_items[self._beat.id]
        self._project.remove_beat(self._beat.id)
        self._view.beat_deleted.emit(self._beat.id)


class DeleteBeatCommand(QUndoCommand):
    def __init__(
        self,
        project: Project,
        view: BeatBoardView,
        beat: Beat,
        description: str = "Eliminar beat",
    ) -> None:
        super().__init__(description)
        self._project = project
        self._view = view
        self._beat = beat
        self._beat_data = beat.to_dict()
        self._item = None
        self._connections = []

    def redo(self) -> None:
        beat_id = self._beat.id
        self._item = self._view._beat_items.get(beat_id)
        
        for conn_id, conn_item in list(self._view._connection_items.items()):
            conn = self._project.get_connection_by_id(conn_id)
            if conn and (conn.source_beat_id == beat_id or conn.target_beat_id == beat_id):
                self._connections.append((conn_id, conn, conn_item))
                self._view._scene.removeItem(conn_item)
                del self._view._connection_items[conn_id]
                self._project.remove_connection(conn_id)

        if self._item:
            self._view._scene.removeItem(self._item)
            del self._view._beat_items[beat_id]
        self._project.remove_beat(beat_id)
        self._view.beat_deleted.emit(beat_id)

    def undo(self) -> None:
        from beatboard.core.beat import Beat
        
        beat = Beat.from_dict(self._beat_data)
        self._project.add_beat(beat)
        self._item = self._view._add_beat_item(beat)
        self._view.beat_created.emit(beat.id)

        for conn_id, conn, _ in self._connections:
            self._project.add_connection(conn)
            self._view._add_connection_item(conn)


class MoveBeatCommand(QUndoCommand):
    def __init__(
        self,
        project: Project,
        view: BeatBoardView,
        beat_id: str,
        old_pos: QPointF,
        new_pos: QPointF,
        description: str = "Mover beat",
    ) -> None:
        super().__init__(description)
        self._project = project
        self._view = view
        self._beat_id = beat_id
        self._old_pos = old_pos
        self._new_pos = new_pos

    def redo(self) -> None:
        beat = self._project.get_beat_by_id(self._beat_id)
        if beat:
            beat.set_position(self._new_pos.x(), self._new_pos.y())
            item = self._view._beat_items.get(self._beat_id)
            if item:
                item.setPos(self._new_pos)
                self._view._update_connections_for_beat(self._beat_id)

    def undo(self) -> None:
        beat = self._project.get_beat_by_id(self._beat_id)
        if beat:
            beat.set_position(self._old_pos.x(), self._old_pos.y())
            item = self._view._beat_items.get(self._beat_id)
            if item:
                item.setPos(self._old_pos)
                self._view._update_connections_for_beat(self._beat_id)


class EditBeatCommand(QUndoCommand):
    def __init__(
        self,
        project: Project,
        view: BeatBoardView,
        beat_id: str,
        old_data: dict,
        new_data: dict,
        description: str = "Editar beat",
    ) -> None:
        super().__init__(description)
        self._project = project
        self._view = view
        self._beat_id = beat_id
        self._old_data = old_data
        self._new_data = new_data

    def redo(self) -> None:
        self._apply_data(self._new_data)

    def undo(self) -> None:
        self._apply_data(self._old_data)

    def _apply_data(self, data: dict) -> None:
        beat = self._project.get_beat_by_id(self._beat_id)
        if beat:
            beat.title = data.get("title", beat.title)
            beat.content = data.get("content", beat.content)
            beat.color = data.get("color", beat.color)
            beat.show_title = data.get("show_title", beat.show_title)
            
            item = self._view._beat_items.get(self._beat_id)
            if item:
                item.refresh()
            
            self._view._update_connections_for_beat(self._beat_id)
            self._view.beat_moved.emit(self._beat_id)


class CreateConnectionCommand(QUndoCommand):
    def __init__(
        self,
        project: Project,
        view: BeatBoardView,
        connection: Connection,
        description: str = "Crear conexión",
    ) -> None:
        super().__init__(description)
        self._project = project
        self._view = view
        self._connection = connection
        self._item = None

    def redo(self) -> None:
        self._project.add_connection(self._connection)
        self._view._add_connection_item(self._connection)

    def undo(self) -> None:
        self._item = self._view._connection_items.get(self._connection.id)
        if self._item:
            self._view._scene.removeItem(self._item)
            del self._view._connection_items[self._connection.id]
        self._project.remove_connection(self._connection.id)


class DeleteConnectionCommand(QUndoCommand):
    def __init__(
        self,
        project: Project,
        view: BeatBoardView,
        connection: Connection,
        description: str = "Eliminar conexión",
    ) -> None:
        super().__init__(description)
        self._project = project
        self._view = view
        self._connection = connection
        self._item = None

    def redo(self) -> None:
        self._item = self._view._connection_items.get(self._connection.id)
        if self._item:
            self._view._scene.removeItem(self._item)
            del self._view._connection_items[self._connection.id]
        self._project.remove_connection(self._connection.id)

    def undo(self) -> None:
        self._project.add_connection(self._connection)
        self._view._add_connection_item(self._connection)
