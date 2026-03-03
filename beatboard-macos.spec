# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None
spec_dir = Path(SPECPATH)
beatboard_root = spec_dir
script_path = beatboard_root / 'beatboard' / 'app' / 'main.py'
icons_base = beatboard_root / "beatboard"

a = Analysis(
    [str(script_path)],
    pathex=[str(beatboard_root)],
    binaries=[],
    datas=[
        (str(icons_base / "ui" / "icons" / "toolbar_dark"), "beatboard/ui/icons/toolbar_dark"),
        (str(icons_base / "ui" / "icons" / "toolbar_light"), "beatboard/ui/icons/toolbar_light"),
        (str(icons_base / "resources" / "dictionaries"), "resources/dictionaries"), # Ruta unificada
    ],
    hiddenimports=[
        "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets",
        "spylls", "spylls.hunspell" # Importante para el corrector
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    name='BeatBoard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Cambia a True si necesitas ver errores de terminal en Mac
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='beatboard/ui/icons/app_icon.icns', # macOS prefiere .icns
)

app = BUNDLE(
    exe,
    name='BeatBoard.app',
    icon='beatboard/ui/icons/app_icon.icns',
    bundle_identifier='com.beatboard.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
        'CFBundleShortVersionString': '1.0.14',
    },
)
