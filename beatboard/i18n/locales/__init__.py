"""Locale management for i18n."""

from __future__ import annotations

from typing import Callable


_locale: dict[str, str] = {}
_current_locale_name: str = "en"


def get_locale() -> dict[str, str]:
    """Get the current locale dictionary."""
    return _locale


def set_locale(locale_name: str) -> None:
    """Set the current locale by name."""
    global _current_locale_name
    _current_locale_name = locale_name
    _load_locale(locale_name)


def _load_locale(locale_name: str) -> None:
    """Load a locale file."""
    global _locale
    
    if locale_name == "en":
        from beatboard.i18n.locales import en
        _locale = en.TRANSLATIONS
    elif locale_name == "es":
        from beatboard.i18n.locales import es
        _locale = es.TRANSLATIONS
    elif locale_name == "fr":
        from beatboard.i18n.locales import fr
        _locale = fr.TRANSLATIONS
    elif locale_name == "de":
        from beatboard.i18n.locales import de
        _locale = de.TRANSLATIONS
    else:
        from beatboard.i18n.locales import en
        _locale = en.TRANSLATIONS


def get_available_locales() -> list[str]:
    """Get list of available locale codes."""
    return ["en", "es", "fr", "de"]


def get_locale_name(locale_code: str) -> str:
    """Get the display name for a locale code."""
    names = {
        "en": "English",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
    }
    return names.get(locale_code, locale_code)
