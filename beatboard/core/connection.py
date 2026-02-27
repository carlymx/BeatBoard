"""Connection entity - Represents a visual connection between two beats."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from beatboard.core.constants import CONNECTION_COLOR_DEFAULT


@dataclass
class Connection:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_beat_id: str = ""
    target_beat_id: str = ""
    color: str = CONNECTION_COLOR_DEFAULT
    label: str | None = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_beat_id": self.source_beat_id,
            "target_beat_id": self.target_beat_id,
            "color": self.color,
            "label": self.label,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Connection:
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            source_beat_id=data["source_beat_id"],
            target_beat_id=data["target_beat_id"],
            color=data.get("color", CONNECTION_COLOR_DEFAULT),
            label=data.get("label"),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
        )

    def __repr__(self) -> str:
        return f"Connection(id={self.id[:8]}..., {self.source_beat_id[:8]}... -> {self.target_beat_id[:8]}...)"
