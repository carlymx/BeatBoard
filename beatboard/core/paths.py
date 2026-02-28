"""Cross-platform path utilities for BeatBoard."""

import sys
from pathlib import Path

def get_config_dir() -> Path:
    """Get the config directory based on OS."""
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Roaming" / "BeatBoard"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "BeatBoard"
    else:
        return Path.home() / ".config" / "beatboard"

def get_data_dir() -> Path:
    """Get the data/logs directory based on OS."""
    if sys.platform == "win32":
        return Path.home() / "AppData" / "Roaming" / "BeatBoard"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "BeatBoard"
    else:
        return Path.home() / ".beatboard"
