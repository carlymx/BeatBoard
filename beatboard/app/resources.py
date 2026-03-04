"""Resource path utilities for BeatBoard application."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path for resources, compatible with PyInstaller.
    
    In development: returns path relative to project root.
    In frozen executable: returns path inside sys._MEIPASS.
    
    Args:
        relative_path: Relative path from project root (e.g., "beatboard/ui/icons/app_icon.png")
    
    Returns:
        Absolute Path to the resource
    """
    if hasattr(sys, "_MEIPASS"):
        # Running as compiled executable
        return Path(sys._MEIPASS) / relative_path
    else:
        # Running in development
        return Path(__file__).parent.parent.parent / relative_path


def get_app_icon_path() -> Path:
    """Get the application icon path based on platform."""
    if sys.platform == "win32":
        return get_resource_path("beatboard/ui/icons/app_icon.ico")
    elif sys.platform == "darwin":
        return get_resource_path("beatboard/ui/icons/app_icon.icns")
    else:
        # Linux and others - prefer PNG with multiple sizes
        return get_resource_path("beatboard/ui/icons/app_icon.png")


def fix_windows_taskbar_icon() -> None:
    """
    Fix Windows taskbar icon issue for PyInstaller executables.
    
    This assigns a unique AppUserModelID to prevent Windows from
    grouping the app with other Python processes.
    """
    if sys.platform != "win32":
        return
    
    try:
        import ctypes
        myappid = "com.beatboard.app.v1.0.15"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        # Silently fail if not available (e.g., not on Windows)
        pass
