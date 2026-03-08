"""Main entry point for BeatBoard application."""

import sys
import re

from beatboard.app.application import Application
from beatboard.app.resources import fix_windows_taskbar_icon
from beatboard.ui.main_window import MainWindow


def main() -> int:
    fix_windows_taskbar_icon()
    
    app = Application(sys.argv)
    
    file_to_open = None
    for arg in sys.argv[1:]:
        if arg.endswith('.bbp') and not arg.startswith('-'):
            file_to_open = arg
            break
    
    window = MainWindow(file_to_open_on_start=file_to_open)
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
