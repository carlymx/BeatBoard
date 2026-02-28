# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for BeatBoard v1.0.7
"""

import sys
import os
from pathlib import Path

block_cipher = None

# Print debug info
print(f"SPECPATH: {SPECPATH}")

# Get the directory where this spec file is located
spec_file = Path(SPECPATH)
print(f"spec_file: {spec_file}")
spec_dir = spec_file.parent.resolve()
print(f"spec_dir: {spec_dir}")

# Local paths
script_path = Path(SPECPATH) / 'beatboard' / 'app' / 'main.py'
beatboard_root = Path(SPECPATH)

print(f"Using script_path: {script_path}")
print(f"script exists: {script_path.exists()}")
print(f"Using beatboard_root: {beatboard_root}")

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
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
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
    icon=None,
)
