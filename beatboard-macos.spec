# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for BeatBoard v1.0.7 (macOS)
"""

import sys
import os
from pathlib import Path

block_cipher = None

# Get the directory where this spec file is located
spec_file = Path(SPECPATH)
spec_dir = spec_file.parent.resolve()

# Local paths
script_path = Path(SPECPATH) / 'beatboard' / 'app' / 'main.py'
beatboard_root = Path(SPECPATH)

# Icons are in beatboard/ui/icons/
icons_base = beatboard_root / "beatboard"

a = Analysis(
    [str(script_path)],
    pathex=[str(beatboard_root)],
    binaries=[],
    datas=[
        (str(icons_base / "ui" / "icons" / "toolbar_dark"), "beatboard/ui/icons/toolbar_dark"),
        (str(icons_base / "ui" / "icons" / "toolbar_light"), "beatboard/ui/icons/toolbar_light"),
    ],
    hiddenimports=[
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name="BeatBoard",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
