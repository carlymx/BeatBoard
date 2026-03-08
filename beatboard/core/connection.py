"""Connection entity - Represents a visual connection between two beats."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from beatboard.core.constants import (
    CONNECTION_COLOR_DEFAULT, 
    CONNECTION_LINE_WIDTH_DEFAULT,
    CONNECTION_NODE_SHAPE_DEFAULT
)


@dataclass
class Connection:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_beat_id: str = ""
    target_beat_id: str = ""
    color: str = CONNECTION_COLOR_DEFAULT
    line_width: float = CONNECTION_LINE_WIDTH_DEFAULT
    node_shape: str = CONNECTION_NODE_SHAPE_DEFAULT
    label: str | None = None
    control_factor1: tuple[float, float] | None = None  # (factor_x, factor_y) relative to source
    control_factor2: tuple[float, float] | None = None  # (factor_x, factor_y) relative to target
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
            "line_width": self.line_width,
            "node_shape": self.node_shape,
            "label": self.label,
            "control_factor1": self.control_factor1,
            "control_factor2": self.control_factor2,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Connection:
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            source_beat_id=data["source_beat_id"],
            target_beat_id=data["target_beat_id"],
            color=data.get("color", CONNECTION_COLOR_DEFAULT),
            line_width=data.get("line_width", CONNECTION_LINE_WIDTH_DEFAULT),
            node_shape=data.get("node_shape", CONNECTION_NODE_SHAPE_DEFAULT),
            label=data.get("label"),
            control_factor1=data.get("control_factor1"),
            control_factor2=data.get("control_factor2"),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
        )

    def __repr__(self) -> str:
        return f"Connection(id={self.id[:8]}..., {self.source_beat_id[:8]}... -> {self.target_beat_id[:8]}...)"
