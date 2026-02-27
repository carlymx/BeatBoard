"""Unit tests for Project entity."""

import pytest

from beatboard.core.beat import Beat
from beatboard.core.connection import Connection
from beatboard.core.project import Project


class TestProject:
    def test_project_creation(self):
        project = Project(name="Test Project")
        assert project.name == "Test Project"
        assert len(project.beats) == 0
        assert len(project.connections) == 0

    def test_project_add_beat(self):
        project = Project()
        beat = Beat(title="Test Beat")
        project.add_beat(beat)
        
        assert len(project.beats) == 1
        assert project.beats[0].title == "Test Beat"

    def test_project_remove_beat(self):
        project = Project()
        beat = Beat(title="Test Beat")
        project.add_beat(beat)
        
        result = project.remove_beat(beat.id)
        assert result is True
        assert len(project.beats) == 0

    def test_project_remove_beat_not_found(self):
        project = Project()
        result = project.remove_beat("non-existent-id")
        assert result is False

    def test_project_get_beat_by_id(self):
        project = Project()
        beat = Beat(id="test-id", title="Test Beat")
        project.add_beat(beat)
        
        found = project.get_beat_by_id("test-id")
        assert found is not None
        assert found.title == "Test Beat"
        
        not_found = project.get_beat_by_id("non-existent")
        assert not_found is None

    def test_project_add_connection(self):
        project = Project()
        beat1 = Beat(id="beat-1")
        beat2 = Beat(id="beat-2")
        project.add_beat(beat1)
        project.add_beat(beat2)
        
        conn = Connection(source_beat_id="beat-1", target_beat_id="beat-2")
        project.add_connection(conn)
        
        assert len(project.connections) == 1

    def test_project_remove_connection(self):
        project = Project()
        beat1 = Beat(id="beat-1")
        beat2 = Beat(id="beat-2")
        project.add_beat(beat1)
        project.add_beat(beat2)
        
        conn = Connection(id="conn-id", source_beat_id="beat-1", target_beat_id="beat-2")
        project.add_connection(conn)
        
        result = project.remove_connection("conn-id")
        assert result is True
        assert len(project.connections) == 0

    def test_project_get_connection_by_id(self):
        project = Project()
        beat1 = Beat(id="beat-1")
        beat2 = Beat(id="beat-2")
        project.add_beat(beat1)
        project.add_beat(beat2)
        
        conn = Connection(id="conn-id", source_beat_id="beat-1", target_beat_id="beat-2")
        project.add_connection(conn)
        
        found = project.get_connection_by_id("conn-id")
        assert found is not None
        assert found.source_beat_id == "beat-1"
        
        not_found = project.get_connection_by_id("non-existent")
        assert not_found is None

    def test_project_remove_beat_removes_connections(self):
        project = Project()
        beat1 = Beat(id="beat-1")
        beat2 = Beat(id="beat-2")
        project.add_beat(beat1)
        project.add_beat(beat2)
        
        conn = Connection(source_beat_id="beat-1", target_beat_id="beat-2")
        project.add_connection(conn)
        
        project.remove_beat("beat-1")
        
        assert len(project.connections) == 0
        assert len(project.beats) == 1

    def test_project_to_dict(self):
        project = Project(name="My Project")
        beat = Beat(id="beat-1", title="Test Beat")
        project.add_beat(beat)
        
        data = project.to_dict()
        
        assert data["project"]["name"] == "My Project"
        assert len(data["beats"]) == 1
        assert data["beats"][0]["id"] == "beat-1"

    def test_project_from_dict(self):
        data = {
            "version": "1.0",
            "project": {
                "id": "project-id",
                "name": "Loaded Project",
                "created_at": "2024-01-01T00:00:00",
                "modified_at": "2024-01-01T00:00:00",
            },
            "canvas": {"zoom": 1.0, "pan_x": 0, "pan_y": 0},
            "beats": [
                {
                    "id": "beat-1",
                    "title": "Loaded Beat",
                    "content": "Content",
                    "color": "yellow",
                    "position": {"x": 0, "y": 0},
                    "size": {"width": 200, "height": 150},
                    "created_at": "2024-01-01T00:00:00",
                    "modified_at": "2024-01-01T00:00:00",
                    "image_path": None,
                    "tags": [],
                }
            ],
            "connections": [],
            "metadata": {},
        }
        
        project = Project.from_dict(data)
        
        assert project.id == "project-id"
        assert project.name == "Loaded Project"
        assert len(project.beats) == 1
        assert project.beats[0].title == "Loaded Beat"
