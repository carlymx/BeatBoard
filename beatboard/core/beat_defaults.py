"""Beat defaults manager - remembers last beat's size and color."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

from PySide6.QtCore import QSizeF

if TYPE_CHECKING:
    from beatboard.core.beat import Beat

_beat_color_default = "yellow"
_beats_default_size = QSizeF(200.0, 150.0)


def set_beat_defaults_constants(color_default, size_default):
    global _beat_color_default, _beats_default_size
    _beat_color_default = color_default
    _beats_default_size = size_default


class BeatDefaults:
    _memorize_enabled: bool = False
    _last_color: str = _beat_color_default
    _last_size: QSizeF = _beats_default_size

    @classmethod
    def is_memorize_enabled(cls) -> bool:
        return cls._memorize_enabled

    @classmethod
    def set_memorize_enabled(cls, enabled: bool) -> None:
        cls._memorize_enabled = enabled

    @classmethod
    def toggle_memorize(cls) -> bool:
        cls._memorize_enabled = not cls._memorize_enabled
        return cls._memorize_enabled

    @classmethod
    def get_last_color(cls) -> str:
        return cls._last_color

    @classmethod
    def set_last_color(cls, color: str) -> None:
        cls._last_color = color

    @classmethod
    def get_last_size(cls) -> QSizeF:
        return cls._last_size

    @classmethod
    def set_last_size(cls, width: float, height: float) -> None:
        cls._last_size = QSizeF(width, height)

    @classmethod
    def update_from_beat(cls, beat: "Beat") -> None:
        if cls._memorize_enabled:
            cls._last_color = beat.color
            if beat.size:
                cls._last_size = QSizeF(beat.size.width(), beat.size.height())

    @classmethod
    def get_default_color(cls) -> str:
        if cls._memorize_enabled:
            return cls._last_color
        return _beat_color_default

    @classmethod
    def get_default_size(cls) -> QSizeF:
        if cls._memorize_enabled:
            return cls._last_size
        return QSizeF(_beats_default_size)
