"""Main entry point for BeatBoard application."""

import sys

from beatboard.app.application import Application
from beatboard.app.resources import fix_windows_taskbar_icon
from beatboard.ui.main_window import MainWindow


def main() -> int:
    fix_windows_taskbar_icon()
    
    app = Application(sys.argv)
    
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
