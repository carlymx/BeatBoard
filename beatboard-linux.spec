# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for BeatBoard v1.0.19
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
        (str(icons_base / "ui" / "icons" / "app_icon.png"), "beatboard/ui/icons"),
        (str(icons_base / "ui" / "icons" / "toolbar_dark"), "beatboard/ui/icons/toolbar_dark"),
        (str(icons_base / "ui" / "icons" / "toolbar_light"), "beatboard/ui/icons/toolbar_light"),
        (str(icons_base / "resources" / "dictionaries"), "resources/dictionaries"),
    ],
    hiddenimports=[
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "spylls",
        "spylls.hunspell",
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

# 1. DEFINICIÓN PARA EL PORTABLE (Onefile)
# Aquí metemos TODO dentro del EXE
exe_portable = EXE(
    pyz,
    a.scripts,
    a.binaries,   # <--- Contenido dentro del exe
    a.zipfiles,   # <--- Contenido dentro del exe
    a.datas,      # <--- Contenido dentro del exe
    [],
    name="BeatBoard_portable",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='beatboard/ui/icons/app_icon.png',
)

# 2. DEFINICIÓN PARA EL APPDIR (Onedir)
# Aquí el EXE solo lleva los scripts, las librerías van fuera
exe_appdir = EXE(
    pyz,
    a.scripts,
    [],           # <--- VACÍO (las librerías irán a la carpeta)
    exclude_binaries=True, # <--- IMPORTANTE
    name="BeatBoard_launch", # Un nombre temporal para el ejecutable interno
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='beatboard/ui/icons/app_icon.png',
)

coll = COLLECT(
    exe_appdir,   # Usamos el exe "ligero"
    a.binaries,   # Las librerías se copian sueltas aquí
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="BeatBoard_appdir",
)
