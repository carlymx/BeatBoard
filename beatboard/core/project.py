"""Project entity - Represents a complete BeatBoard project."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from PySide6.QtCore import QPointF

from beatboard.core.beat import Beat
from beatboard.core.connection import Connection
from beatboard.core.constants import ZOOM_DEFAULT


@dataclass
class CanvasState:
    zoom: float = ZOOM_DEFAULT
    pan_x: float = 0.0
    pan_y: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "zoom": self.zoom,
            "pan_x": self.pan_x,
            "pan_y": self.pan_y,
        }

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> CanvasState:
        return cls(
            zoom=data.get("zoom", ZOOM_DEFAULT),
            pan_x=data.get("pan_x", 0.0),
            pan_y=data.get("pan_y", 0.0),
        )


@dataclass
class Project:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Project"
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    beats: list[Beat] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)
    canvas_state: CanvasState = field(default_factory=CanvasState)
    canvas_images: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    project_path: Path | None = field(default_factory=lambda: None, repr=False)

    def __post_init__(self) -> None:
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        if isinstance(self.modified_at, str):
            self.modified_at = datetime.fromisoformat(self.modified_at.replace("Z", "+00:00"))
        if isinstance(self.canvas_state, dict):
            self.canvas_state = CanvasState.from_dict(self.canvas_state)

    def update_modified(self) -> None:
        self.modified_at = datetime.now()

    def add_beat(self, beat: Beat) -> None:
        self.beats.append(beat)
        self.update_modified()

    def remove_beat(self, beat_id: str) -> bool:
        for i, beat in enumerate(self.beats):
            if beat.id == beat_id:
                self.connections = [
                    c
                    for c in self.connections
                    if c.source_beat_id != beat_id and c.target_beat_id != beat_id
                ]
                del self.beats[i]
                self.update_modified()
                return True
        return False

    def get_beat_by_id(self, beat_id: str) -> Beat | None:
        for beat in self.beats:
            if beat.id == beat_id:
                return beat
        return None

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)
        self.update_modified()

    def remove_connection(self, connection_id: str) -> bool:
        for i, conn in enumerate(self.connections):
            if conn.id == connection_id:
                del self.connections[i]
                self.update_modified()
                return True
        return False

    def get_connection_by_id(self, connection_id: str) -> Connection | None:
        for conn in self.connections:
            if conn.id == connection_id:
                return conn
        return None

    def get_connections_for_beat(self, beat_id: str) -> list[Connection]:
        return [
            c
            for c in self.connections
            if c.source_beat_id == beat_id or c.target_beat_id == beat_id
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": "1.0",
            "project": {
                "id": self.id,
                "name": self.name,
                "created_at": self.created_at.isoformat(),
                "modified_at": self.modified_at.isoformat(),
            },
            "canvas": self.canvas_state.to_dict(),
            "beats": [beat.to_dict() for beat in self.beats],
            "connections": [conn.to_dict() for conn in self.connections],
            "canvas_images": self.canvas_images,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        project_data = data.get("project", {})
        canvas_data = data.get("canvas", {})
        beats_data = data.get("beats", [])
        connections_data = data.get("connections", [])
        canvas_images_data = data.get("canvas_images", [])

        return cls(
            id=project_data.get("id", str(uuid.uuid4())),
            name=project_data.get("name", "Untitled Project"),
            created_at=datetime.fromisoformat(
                project_data.get("created_at", datetime.now().isoformat()).replace("Z", "+00:00")
            ),
            modified_at=datetime.fromisoformat(
                project_data.get("modified_at", datetime.now().isoformat()).replace("Z", "+00:00")
            ),
            beats=[Beat.from_dict(b) for b in beats_data],
            connections=[Connection.from_dict(c) for c in connections_data],
            canvas_state=CanvasState.from_dict(canvas_data),
            canvas_images=canvas_images_data,
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return f"Project(id={self.id[:8]}..., name={self.name!r}, beats={len(self.beats)}, connections={len(self.connections)})"
