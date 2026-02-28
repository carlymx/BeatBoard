"""Internationalization (i18n) system for BeatBoard."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from beatboard.i18n.locales import (
    get_locale,
    set_locale,
    get_available_locales,
    get_locale_name,
)


class LocaleManager(QObject):
    locale_changed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._app = QApplication.instance()
        self._current_locale = "en"
        self._load_preference()

    def _get_config_path(self) -> Path:
        config_dir = Path.home() / ".config" / "beatboard"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "preferences.json"

    def _load_preference(self) -> None:
        config_path = self._get_config_path()
        available = get_available_locales()
        
        needs_save = False
        
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text(encoding="utf-8"))
                saved_locale = data.get("language", "")
                if saved_locale and saved_locale in available:
                    self._current_locale = saved_locale
                    set_locale(saved_locale)
                    return
            except (json.JSONDecodeError, KeyError, ValueError):
                pass
        
        system_locale = self._detect_system_locale()
        if system_locale in available:
            self._current_locale = system_locale
        else:
            self._current_locale = "en"
        
        set_locale(self._current_locale)
        self._save_preference()

    def _detect_system_locale(self) -> str:
        try:
            from PySide6.QtCore import QLocale
            system_locale = QLocale.system()
            lang = system_locale.language()
            
            locale_map = {
                QLocale.Language.Spanish: "es",
                QLocale.Language.English: "en",
                QLocale.Language.French: "fr",
                QLocale.Language.German: "de",
            }
            
            return locale_map.get(lang, "en")
        except Exception:
            return "en"

    def _save_preference(self) -> None:
        config_path = self._get_config_path()
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            data = {}
        data["language"] = self._current_locale
        config_path.write_text(json.dumps(data, indent=2))

    def get_current_locale(self) -> str:
        return self._current_locale

    def set_locale(self, locale: str) -> None:
        available = get_available_locales()
        if locale in available:
            self._current_locale = locale
            set_locale(locale)
            self._save_preference()
            self.locale_changed.emit(locale)

    def get_locale_name(self, locale: str) -> str:
        return get_locale_name(locale)

    def get_available_locales(self) -> list[str]:
        return get_available_locales()


def _tr(key: str) -> str:
    """Translate a key to the current locale."""
    return get_locale().get(key, key)
