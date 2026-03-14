"""Beat entity - Represents a single beat card on the board."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from PySide6.QtCore import QPointF, QSizeF

from beatboard.core.constants import (
    BEAT_COLOR_DEFAULT,
    BEAT_DEFAULT_SIZE,
)


@dataclass
class Beat:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    color: str = BEAT_COLOR_DEFAULT
    position: QPointF = field(default_factory=lambda: QPointF(0, 0))
    size: QSizeF = field(default_factory=lambda: QSizeF(BEAT_DEFAULT_SIZE))
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    image_path: str | None = None
    tags: list[str] = field(default_factory=list)
    z_order: float = 0.0
    show_title: bool = True
    content_mode: str = "html"
    content_markdown: str = ""
    embedded_images: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.position, dict):
            self.position = QPointF(self.position["x"], self.position["y"])
        if isinstance(self.size, dict):
            self.size = QSizeF(self.size["width"], self.size["height"])
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        if isinstance(self.modified_at, str):
            self.modified_at = datetime.fromisoformat(self.modified_at.replace("Z", "+00:00"))

    def update_modified(self) -> None:
        self.modified_at = datetime.now()

    def set_position(self, x: float, y: float) -> None:
        self.position = QPointF(x, y)
        self.update_modified()

    def set_size(self, width: float, height: float) -> None:
        self.size = QSizeF(width, height)
        self.update_modified()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "color": self.color,
            "position": {"x": self.position.x(), "y": self.position.y()},
            "size": {"width": self.size.width(), "height": self.size.height()},
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "image_path": self.image_path,
            "tags": self.tags,
            "z_order": self.z_order,
            "show_title": self.show_title,
            "content_mode": self.content_mode,
            "content_markdown": self.content_markdown,
            "embedded_images": self.embedded_images,
        }

    @classmethod
    def _normalize_embedded_images(cls, embedded_images):
        """Convert embedded_images to list of dicts with 'relative_path' key."""
        normalized = []
        for item in embedded_images:
            if isinstance(item, dict):
                normalized.append(item)
            else:
                normalized.append({'relative_path': item})
        return normalized
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Beat:
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            content=data.get("content", ""),
            color=data.get("color", BEAT_COLOR_DEFAULT),
            position=QPointF(data["position"]["x"], data["position"]["y"]),
            size=QSizeF(data["size"]["width"], data["size"]["height"]),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            modified_at=datetime.fromisoformat(data["modified_at"].replace("Z", "+00:00")),
            image_path=data.get("image_path"),
            tags=data.get("tags", []),
            z_order=data.get("z_order", 0.0),
            show_title=data.get("show_title", True),
            content_mode=data.get("content_mode", "html"),
            content_markdown=data.get("content_markdown", ""),
            embedded_images=cls._normalize_embedded_images(data.get("embedded_images", [])),
        )

    def __repr__(self) -> str:
        return f"Beat(id={self.id[:8]}..., title={self.title!r})"
