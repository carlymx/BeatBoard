# BeatBoard

[📖 Leer en Español](./README_ES.md)

<!-- Badges Section -->
![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.7-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-yellow.svg)
![Qt](https://img.shields.io/badge/Qt-PySide6-purple.svg)

![main](./imgs/beatboard_001.png)

## Description

BeatBoard is a virtual beat board desktop application for writers, inspired by Final Draft's Beat Board. It provides an infinite canvas where screenwriters, novelists, and short story writers can create, organize, and connect "beats" - the fundamental building blocks of a story.

Whether you're outlining a screenplay, novel, short story, or TV series, BeatBoard helps you visualize your story's structure with colorful cards and flow lines.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

### Core Features
- **Infinite Canvas** - Pan and zoom across an unlimited workspace
- **Beat Cards** - Create colorful cards with title and content
- **Connections** - Link beats with curved bezier flow lines
- **Drag & Drop** - Freely arrange beats anywhere on the canvas

### Productivity
- **Undo/Redo** - Full history support for all operations
- **Copy/Paste** - Duplicate beats with Ctrl+C / Ctrl+V
- **Z-Order** - Bring to front, send to back, move up/down
- **Multi-select** - Select and move multiple beats at once

### Customization
- **9 Themes** - Light and dark themes (Nord, Dracula, One Dark, etc.)
- **8 Beat Colors** - Yellow, Blue, Green, Red, Orange, Purple, Gray
- **Custom Background** - Choose from preset or custom canvas colors
- **Optional Grid** - Show/hide alignment grid with customizable size and color

### Internationalization
- **Multi-language Support** - Available in English, Spanish, French, and German
- **System Language Detection** - Automatically detects your system language
- **Persistent Language Preference** - Remembers your language choice

### Export & Save
- **Project Files** - Save and load .bbp project files
- **Auto-save** - Automatic saving every 5 minutes
- **Export PDF** - Generate PDF documents of your beat board
- **Export Text** - Export beats as plain text

### Additional
- **Properties Panel** - Edit selected beat properties
- **Status Bar** - Real-time cursor coordinates display
- **Center Point** - Visual guide at origin (0,0)

## Installation

### Prerequisites
- Python 3.10 or higher
- PySide6

### From Source

```bash
# Clone the repository
git clone https://github.com/carlymx/BeatBoard.git
cd BeatBoard

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install pyside6

# Run the application
python -m beatboard.app.main
```

### Pre-built Executables

Download from the [Releases](https://github.com/carlymx/BeatBoard/releases) page or build from source (see below):

| Platform | Type | File |
|----------|------|------|
| Linux | AppImage | `BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.7.AppImage` |
| Linux | Portable | `BeatBoard-Linux-x86_64-QT6_PySide6-v1.0.7_portable` |
| Windows | Executable | `BeatBoard.exe` (via GitHub Actions) |

### System Requirements

- **Linux**: Ubuntu 20.04+, Linux Mint 20+, Debian 11+, Fedora 34+ (GLIBC 2.31+)

### Build from Source

To compile the executable and AppImage yourself:

```bash
# 1. Navigate to project directory
cd BeatBoard

# 2. Build with Docker/Podman (recommended for maximum compatibility)
podman build -t beatboard-builder:latest -f build/Dockerfile .

# 3. Extract generated files
podman run --rm -v $(pwd)/build:/output:Z beatboard-builder:latest \
    cp -r /build/AppDir /output/ && cp /build/output/BeatBoard-portable /output/

# 4. Create AppImage (requires FUSE)
cd build
wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
chmod +x appimagetool
./appimagetool -s AppDir BeatBoard-x86_64.AppImage
```

Generated files will be in `build/`:
- `BeatBoard-portable` - Portable executable
- `BeatBoard-x86_64.AppImage` - Self-contained AppImage

See `DESARROLLOActual.md` for detailed build instructions.

### Run AppImage (Linux)

```bash
chmod +x BeatBoard-x86_64.AppImage
./BeatBoard-x86_64.AppImage
```

## Usage

### Getting Started

1. **Create a Beat** - Double-click anywhere on the canvas
2. **Edit a Beat** - Double-click on a beat to open the editor
3. **Move a Beat** - Click and drag to reposition
4. **Connect Beats** - Click "Connect" in toolbar, then click source and target beats

### Managing Beats

- **Delete**: Select beat(s) and press Delete/Supr
- **Copy**: Ctrl+C to copy selected beats
- **Paste**: Ctrl+V to paste copied beats
- **Select All**: Ctrl+A to select all beats

### Working with Connections

1. Click the "Connect" button in the toolbar
2. Click on the source beat
3. Click on the target beat
4. Press Escape to exit connection mode

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+A | Select All |
| Ctrl+C | Copy |
| Ctrl+X | Cut |
| Ctrl+V | Paste |
| Delete | Delete selected |
| Ctrl+Home | Bring to Front |
| Ctrl+End | Send to Back |
| Ctrl+PageUp | Move Up |
| Ctrl+PageDown | Move Down |
| Ctrl+0 | Fit to Content |
| Ctrl++ | Zoom In |
| Ctrl+- | Zoom Out |
| Space | Pan mode (hold) |
| Escape | Cancel / Deselect |
| 1-8 | Change beat color |

## Project Structure

```
BeatBoard/
├── beatboard/
│   ├── app/              # Application entry point
│   │   ├── main.py
│   │   └── application.py
│   ├── core/             # Core data models
│   │   ├── beat.py
│   │   ├── connection.py
│   │   ├── project.py
│   │   └── constants.py
│   ├── ui/               # User interface
│   │   ├── main_window.py
│   │   ├── theme_manager.py
│   │   ├── canvas/       # Graphics view components
│   │   ├── dialogs/      # Dialog windows
│   │   └── widgets/      # Custom widgets
│   ├── services/         # Business logic
│   │   ├── autosave_service.py
│   │   └── export_service.py
│   └── tests/            # Unit tests
├── dist/                 # Built executables
├── beatboard.spec        # PyInstaller spec
└── README.md
```

## Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
python -m pytest beatboard/tests/ -v

# Run specific test file
python -m pytest beatboard/tests/test_beat.py -v
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the [Creative Commons BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/legalcode) License.

**You are free to:**
- Share — copy and redistribute the material
- Adapt — remix, transform, and build upon the material

**Under the following terms:**
- Attribution — You must give appropriate credit
- NonCommercial — You may not use the material for commercial purposes

## Changelog

### v1.0.7 (2026-02-28)
- Added custom application icon for Windows executable
- Added cross-platform config paths (Windows: %APPDATA%, macOS: Application Support, Linux: .config)
- Added GitHub Actions workflow for Windows build

### v1.0.5 (2026-02-27)
- Added multi-language support (English, Spanish, French, German)
- Added system language detection on first launch
- Added customizable grid color with color picker
- Added custom grid color option in grid settings
- Changed grid size options to: 50, 100, 150, 200, 250
- Fixed toolbar icons embedded in the executable
- Fixed preferences.json creation on first launch
- Added restart notification when changing language

### v1.0.1 (2026-02-27)
- Fixed toolbar icons (now embedded in the app instead of system-dependent)
- Added theme-aware icons (light icons for dark theme, dark icons for light theme)
- Compiled with Ubuntu 22.04 for maximum compatibility with Linux distributions

### v1.0.0 (2026-02-27)
- Initial release
- Infinite canvas with pan and zoom
- Beat cards with title and content
- Connections between beats with bezier curves
- 9 themes (light and dark)
- 8 beat colors
- Undo/Redo system
- Copy/Paste beats
- Z-order management
- Keyboard shortcuts
- Auto-save
- Export PDF/Text
- Preferences persistence
- Properties panel
- Grid and background customization
- Bug fixes: connections loading, z-order saving

## Acknowledgments

- Inspired by [Final Draft Beat Board](https://www.finaldraft.com/)
- Built with [PySide6](https://www.qt.io/qt-for-python)
- Icon design by CarlyMx

---

**Author:** CarlyMx  
**Email:** carlymx@gmail.com  
**GitHub:** https://github.com/carlymx/BeatBoard
