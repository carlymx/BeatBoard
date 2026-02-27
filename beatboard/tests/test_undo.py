"""Unit tests for undo/redo commands."""

import pytest

from PySide6.QtCore import QPointF

from beatboard.core.beat import Beat
from beatboard.core.connection import Connection
from beatboard.core.project import Project
from beatboard.ui.undo_commands import (
    CreateBeatCommand,
    DeleteBeatCommand,
    MoveBeatCommand,
    EditBeatCommand,
    CreateConnectionCommand,
    DeleteConnectionCommand,
)


class MockSignal:
    def emit(self, *args):
        pass


class MockScene:
    def __init__(self):
        self.items = []
    
    def removeItem(self, item):
        if item in self.items:
            self.items.remove(item)


class MockView:
    def __init__(self):
        self._beat_items = {}
        self._connection_items = {}
        self._scene = MockScene()
        self.beat_created = MockSignal()
        self.beat_deleted = MockSignal()
        self.beat_moved = MockSignal()
    
    def _add_beat_item(self, beat):
        self._beat_items[beat.id] = beat
        return beat
    
    def _add_connection_item(self, connection):
        self._connection_items[connection.id] = connection
        return connection
    
    def _update_connections_for_beat(self, beat_id):
        pass


class MockScene:
    def __init__(self):
        self.items = []
    
    def addItem(self, item):
        self.items.append(item)
    
    def removeItem(self, item):
        if item in self.items:
            self.items.remove(item)


class TestCreateBeatCommand:
    def test_create_beat_redo(self):
        project = Project()
        view = MockView()
        beat = Beat(id="test-beat", title="Test Beat")
        
        cmd = CreateBeatCommand(project, view, beat, "Create beat")
        
        assert len(project.beats) == 0
        
        cmd.redo()
        
        assert len(project.beats) == 1
        assert project.beats[0].id == "test-beat"
        assert "test-beat" in view._beat_items
    
    def test_create_beat_undo(self):
        project = Project()
        view = MockView()
        beat = Beat(id="test-beat", title="Test Beat")
        
        cmd = CreateBeatCommand(project, view, beat, "Create beat")
        cmd.redo()
        
        cmd.undo()
        
        assert len(project.beats) == 0
        assert "test-beat" not in view._beat_items


class TestDeleteBeatCommand:
    def test_delete_beat_redo(self):
        project = Project()
        view = MockView()
        beat = Beat(id="test-beat", title="Test Beat")
        project.add_beat(beat)
        
        cmd = DeleteBeatCommand(project, view, beat, "Delete beat")
        
        assert len(project.beats) == 1
        
        cmd.redo()
        
        assert len(project.beats) == 0
    
    def test_delete_beat_undo(self):
        project = Project()
        view = MockView()
        beat = Beat(id="test-beat", title="Test Beat")
        project.add_beat(beat)
        
        cmd = DeleteBeatCommand(project, view, beat, "Delete beat")
        cmd.redo()
        
        cmd.undo()
        
        assert len(project.beats) == 1
        assert project.beats[0].title == "Test Beat"


class TestMoveBeatCommand:
    def test_move_beat_redo(self):
        project = Project()
        view = MockView()
        beat = Beat(id="test-beat", title="Test Beat")
        beat.set_position(0, 0)
        project.add_beat(beat)
        
        cmd = MoveBeatCommand(
            project, view, "test-beat",
            QPointF(0, 0), QPointF(100, 50)
        )
        
        cmd.redo()
        
        assert beat.position.x() == 100
        assert beat.position.y() == 50
    
    def test_move_beat_undo(self):
        project = Project()
        view = MockView()
        beat = Beat(id="test-beat", title="Test Beat")
        beat.set_position(0, 0)
        project.add_beat(beat)
        
        cmd = MoveBeatCommand(
            project, view, "test-beat",
            QPointF(0, 0), QPointF(100, 50)
        )
        cmd.redo()
        
        cmd.undo()
        
        assert beat.position.x() == 0
        assert beat.position.y() == 0


class TestEditBeatCommand:
    def test_edit_beat_redo(self):
        project = Project()
        view = MockView()
        beat = Beat(id="test-beat", title="Original")
        beat.color = "yellow"
        project.add_beat(beat)
        
        old_data = {"title": "Original", "content": "", "color": "yellow"}
        new_data = {"title": "Nuevo", "content": "Contenido", "color": "blue"}
        
        cmd = EditBeatCommand(project, view, "test-beat", old_data, new_data)
        cmd.redo()
        
        assert beat.title == "Nuevo"
        assert beat.content == "Contenido"
        assert beat.color == "blue"
    
    def test_edit_beat_undo(self):
        project = Project()
        view = MockView()
        beat = Beat(id="test-beat", title="Original")
        beat.color = "yellow"
        project.add_beat(beat)
        
        old_data = {"title": "Original", "content": "", "color": "yellow"}
        new_data = {"title": "Nuevo", "content": "Contenido", "color": "blue"}
        
        cmd = EditBeatCommand(project, view, "test-beat", old_data, new_data)
        cmd.redo()
        cmd.undo()
        
        assert beat.title == "Original"
        assert beat.color == "yellow"


class TestCreateConnectionCommand:
    def test_create_connection_redo(self):
        project = Project()
        view = MockView()
        
        beat1 = Beat(id="beat-1")
        beat2 = Beat(id="beat-2")
        project.add_beat(beat1)
        project.add_beat(beat2)
        
        connection = Connection(id="conn-1", source_beat_id="beat-1", target_beat_id="beat-2")
        
        cmd = CreateConnectionCommand(project, view, connection, "Create connection")
        
        assert len(project.connections) == 0
        
        cmd.redo()
        
        assert len(project.connections) == 1
    
    def test_create_connection_undo(self):
        project = Project()
        view = MockView()
        
        beat1 = Beat(id="beat-1")
        beat2 = Beat(id="beat-2")
        project.add_beat(beat1)
        project.add_beat(beat2)
        
        connection = Connection(id="conn-1", source_beat_id="beat-1", target_beat_id="beat-2")
        
        cmd = CreateConnectionCommand(project, view, connection, "Create connection")
        cmd.redo()
        
        cmd.undo()
        
        assert len(project.connections) == 0


class TestDeleteConnectionCommand:
    def test_delete_connection_redo(self):
        project = Project()
        view = MockView()
        
        beat1 = Beat(id="beat-1")
        beat2 = Beat(id="beat-2")
        project.add_beat(beat1)
        project.add_beat(beat2)
        
        connection = Connection(id="conn-1", source_beat_id="beat-1", target_beat_id="beat-2")
        project.add_connection(connection)
        
        cmd = DeleteConnectionCommand(project, view, connection, "Delete connection")
        
        assert len(project.connections) == 1
        
        cmd.redo()
        
        assert len(project.connections) == 0
    
    def test_delete_connection_undo(self):
        project = Project()
        view = MockView()
        
        beat1 = Beat(id="beat-1")
        beat2 = Beat(id="beat-2")
        project.add_beat(beat1)
        project.add_beat(beat2)
        
        connection = Connection(id="conn-1", source_beat_id="beat-1", target_beat_id="beat-2")
        project.add_connection(connection)
        
        cmd = DeleteConnectionCommand(project, view, connection, "Delete connection")
        cmd.redo()
        
        cmd.undo()
        
        assert len(project.connections) == 1
