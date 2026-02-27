"""Unit tests for Connection entity."""

import pytest

from beatboard.core.connection import Connection
from beatboard.core.constants import CONNECTION_COLOR_DEFAULT


class TestConnection:
    def test_connection_creation(self):
        conn = Connection(
            source_beat_id="beat-1",
            target_beat_id="beat-2",
            color="red"
        )
        assert conn.source_beat_id == "beat-1"
        assert conn.target_beat_id == "beat-2"
        assert conn.color == "red"

    def test_connection_default_color(self):
        conn = Connection(source_beat_id="beat-1", target_beat_id="beat-2")
        assert conn.color == CONNECTION_COLOR_DEFAULT

    def test_connection_to_dict(self):
        conn = Connection(
            id="conn-id",
            source_beat_id="beat-1",
            target_beat_id="beat-2",
            color="green",
            label="test-label"
        )
        data = conn.to_dict()
        
        assert data["id"] == "conn-id"
        assert data["source_beat_id"] == "beat-1"
        assert data["target_beat_id"] == "beat-2"
        assert data["color"] == "green"
        assert data["label"] == "test-label"

    def test_connection_from_dict(self):
        data = {
            "id": "conn-id",
            "source_beat_id": "beat-a",
            "target_beat_id": "beat-b",
            "color": "blue",
            "label": "from dict",
            "created_at": "2024-01-01T00:00:00",
        }
        
        conn = Connection.from_dict(data)
        assert conn.id == "conn-id"
        assert conn.source_beat_id == "beat-a"
        assert conn.target_beat_id == "beat-b"
        assert conn.color == "blue"
        assert conn.label == "from dict"
