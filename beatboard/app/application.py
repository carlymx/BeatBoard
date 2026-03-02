"""Custom QApplication with logging and configuration."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from beatboard.core.constants import APP_NAME, APP_ORGANIZATION, APP_VERSION
from beatboard.core.paths import get_config_dir, get_data_dir
from beatboard.ui.theme_manager import ThemeManager, ThemeMode
from beatboard.i18n import LocaleManager
from beatboard.services.spellcheck_service import spell_check_service

if TYPE_CHECKING:
    pass


def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("beatboard")
    logger.setLevel(log_level)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    log_dir = get_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / "beatboard.log")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


class Application(QApplication):
    def __init__(self, argv: list[str] | None = None) -> None:
        super().__init__(argv or [])
        
        self._logger = setup_logging()
        self._logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)
        self.setOrganizationName(APP_ORGANIZATION)
        
        self._theme_manager = ThemeManager(self)
        self._locale_manager = LocaleManager(self)
        
        spell_check_service.initialize(get_config_dir())
        
        QTimer.singleShot(0, self._apply_theme_on_start)
    
    def _apply_theme_on_start(self) -> None:
        self._theme_manager.apply_theme()
        mode = self._theme_manager.get_current_mode().value
        is_dark = self._theme_manager.is_dark_mode()
        self._logger.info(f"Theme applied: {mode} (dark: {is_dark})")
    
    @property
    def theme_manager(self) -> ThemeManager:
        return self._theme_manager
    
    @property
    def locale_manager(self) -> LocaleManager:
        return self._locale_manager
    
    @property
    def logger(self) -> logging.Logger:
        return self._logger
