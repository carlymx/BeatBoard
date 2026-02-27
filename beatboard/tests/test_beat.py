"""Unit tests for Beat entity."""

import pytest
from PySide6.QtCore import QPointF, QSizeF

from beatboard.core.beat import Beat
from beatboard.core.constants import BEAT_COLOR_DEFAULT, BEAT_DEFAULT_SIZE


class TestBeat:
    def test_beat_creation(self):
        beat = Beat(title="Test Beat", content="Test content")
        assert beat.title == "Test Beat"
        assert beat.content == "Test content"
        assert beat.color == BEAT_COLOR_DEFAULT

    def test_beat_default_values(self):
        beat = Beat()
        assert beat.title == ""
        assert beat.content == ""
        assert beat.color == BEAT_COLOR_DEFAULT
        assert beat.id is not None

    def test_beat_position(self):
        beat = Beat()
        beat.set_position(100, 200)
        assert beat.position.x() == 100
        assert beat.position.y() == 200

    def test_beat_size(self):
        beat = Beat()
        beat.set_size(300, 200)
        assert beat.size.width() == 300
        assert beat.size.height() == 200

    def test_beat_to_dict(self):
        beat = Beat(title="Test", content="Content", color="blue")
        data = beat.to_dict()
        
        assert data["title"] == "Test"
        assert data["content"] == "Content"
        assert data["color"] == "blue"
        assert "id" in data
        assert "position" in data

    def test_beat_from_dict(self):
        data = {
            "id": "test-id",
            "title": "From Dict",
            "content": "Content from dict",
            "color": "red",
            "position": {"x": 50, "y": 75},
            "size": {"width": 200, "height": 150},
            "created_at": "2024-01-01T00:00:00",
            "modified_at": "2024-01-01T00:00:00",
            "image_path": None,
            "tags": [],
        }
        
        beat = Beat.from_dict(data)
        assert beat.id == "test-id"
        assert beat.title == "From Dict"
        assert beat.color == "red"
        assert beat.position.x() == 50
        assert beat.position.y() == 75

    def test_beat_update_modified(self):
        beat = Beat()
        old_modified = beat.modified_at
        beat.update_modified()
        assert beat.modified_at > old_modified
