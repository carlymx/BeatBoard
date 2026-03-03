"""Main application window."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QActionGroup, QUndoStack
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMenuBar,
    QSplitter,
    QStatusBar,
    QToolBar,
    QWidget,
)

from beatboard.core.constants import APP_NAME, APP_VERSION, PROJECT_FILE_FILTER
from beatboard.core.project import Project
from beatboard.services.autosave_service import AutosaveService
from beatboard.services.spellcheck_service import SpellCheckService
from beatboard.ui.canvas.beat_board_view import BeatBoardView
from beatboard.ui.theme_manager import ThemeMode
from beatboard.ui.widgets.properties_panel import PropertiesPanel
from beatboard.ui.undo_commands import (
    CreateBeatCommand,
    DeleteBeatCommand,
    CreateConnectionCommand,
    DeleteConnectionCommand,
    EditBeatCommand,
    MoveBeatCommand,
)
from beatboard.i18n import _tr

if TYPE_CHECKING:
    pass


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._project = Project()
        self._is_modified = False
        self._current_file: str | None = None
        
        self._autosave_service: AutosaveService | None = None
        self._undo_stack = QUndoStack(self)
        
        self._memorize_action = None
        self._grid_action = None
        self._enable_spellcheck_action = None
        
        spell_service = SpellCheckService.instance()
        from beatboard.core.paths import get_config_dir
        spell_service.initialize(get_config_dir())
        
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()
        self._load_saved_preferences()
        
        self._update_title()
    
    def _setup_ui(self) -> None:
        self.setMinimumSize(1024, 768)
        self.resize(1280, 800)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self._beat_board_view = BeatBoardView(self._project, self, self._undo_stack)
        splitter.addWidget(self._beat_board_view)
        
        self._properties_panel = PropertiesPanel(self)
        splitter.addWidget(self._properties_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        
        self.setCentralWidget(splitter)
    
    def _setup_menus(self) -> None:
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu(_tr("menu_file"))
        
        new_action = file_menu.addAction(_tr("new_project"))
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_project)
        
        open_action = file_menu.addAction(_tr("open_project"))
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_project)
        
        file_menu.addSeparator()
        
        save_action = file_menu.addAction(_tr("save_project"))
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_project)
        
        save_as_action = file_menu.addAction(_tr("save_project_as"))
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._on_save_project_as)
        
        file_menu.addSeparator()
        
        export_pdf_action = file_menu.addAction(_tr("export_pdf"))
        export_pdf_action.triggered.connect(self._on_export_pdf)
        
        export_text_action = file_menu.addAction(_tr("export_text"))
        export_text_action.triggered.connect(self._on_export_text)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction(_tr("exit"))
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        edit_menu = menubar.addMenu(_tr("menu_edit"))
        
        undo_action = edit_menu.addAction(_tr("undo"))
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self._undo_stack.undo)
        
        redo_action = edit_menu.addAction(_tr("redo"))
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self._undo_stack.redo)
        
        edit_menu.addSeparator()
        
        select_all_action = edit_menu.addAction(_tr("select_all"))
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self._on_select_all)
        
        edit_menu.addSeparator()
        
        copy_action = edit_menu.addAction(_tr("copy"))
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self._on_copy)
        
        cut_action = edit_menu.addAction(_tr("cut"))
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self._on_cut)
        
        paste_action = edit_menu.addAction(_tr("paste"))
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self._on_paste)
        
        edit_menu.addSeparator()
        
        bring_front_action = edit_menu.addAction(_tr("bring_to_front"))
        bring_front_action.setShortcut("Ctrl+Home")
        bring_front_action.triggered.connect(self._on_bring_to_front)
        
        send_back_action = edit_menu.addAction(_tr("send_to_back"))
        send_back_action.setShortcut("Ctrl+End")
        send_back_action.triggered.connect(self._on_send_to_back)
        
        move_up_action = edit_menu.addAction(_tr("move_up"))
        move_up_action.setShortcut("Ctrl+PageUp")
        move_up_action.triggered.connect(self._on_move_up)
        
        move_down_action = edit_menu.addAction(_tr("move_down"))
        move_down_action.setShortcut("Ctrl+PageDown")
        move_down_action.triggered.connect(self._on_move_down)
        
        edit_menu.addSeparator()
        
        delete_action = edit_menu.addAction(_tr("delete_beat"))
        delete_action.triggered.connect(self._on_delete_selected)
        
        view_menu = menubar.addMenu(_tr("menu_view"))
        
        theme_menu = view_menu.addMenu(_tr("theme"))
        
        theme_group = QActionGroup(self)
        
        system_theme_action = theme_menu.addAction(_tr("system"))
        system_theme_action.setCheckable(True)
        system_theme_action.setData(ThemeMode.SYSTEM.value)
        system_theme_action.triggered.connect(lambda: self._on_theme_changed(ThemeMode.SYSTEM))
        theme_group.addAction(system_theme_action)
        
        theme_menu.addSeparator()
        
        light_submenu = theme_menu.addMenu(_tr("light"))
        light_group = QActionGroup(self)
        
        light_actions = [
            (ThemeMode.LIGHT, _tr("light_default")),
            (ThemeMode.SOLARIZED_LIGHT, _tr("solarized_light")),
            (ThemeMode.GITHUB_LIGHT, _tr("github_light")),
            (ThemeMode.PAPERCOLOR, _tr("papercolor")),
        ]
        for mode, label in light_actions:
            action = light_submenu.addAction(label)
            action.setCheckable(True)
            action.setData(mode.value)
            action.triggered.connect(lambda checked, m=mode: self._on_theme_changed(m))
            light_group.addAction(action)
        
        dark_submenu = theme_menu.addMenu(_tr("dark"))
        dark_group = QActionGroup(self)
        
        dark_actions = [
            (ThemeMode.DARK, _tr("dark_default")),
            (ThemeMode.DRACULA, _tr("dracula")),
            (ThemeMode.NORD, _tr("nord")),
            (ThemeMode.ONE_DARK, _tr("one_dark")),
            (ThemeMode.MATERIAL_DARK, _tr("material_dark")),
        ]
        for mode, label in dark_actions:
            action = dark_submenu.addAction(label)
            action.setCheckable(True)
            action.setData(mode.value)
            action.triggered.connect(lambda checked, m=mode: self._on_theme_changed(m))
            dark_group.addAction(action)
        
        self._update_theme_check(theme_group, light_group, dark_group)
        
        view_menu.addSeparator()
        
        bg_menu = view_menu.addMenu(_tr("canvas_background"))
        
        bg_group = QActionGroup(self)
        
        from beatboard.core.constants import CANVAS_BACKGROUND_COLORS
        
        bg_labels = {
            "white": _tr("white"),
            "light_gray": _tr("light_gray"),
            "gray": _tr("gray"),
            "dark_gray": _tr("dark_gray"),
            "cream": _tr("cream"),
            "dark": _tr("dark"),
            "black": _tr("black"),
        }
        
        for bg_key, bg_hex in CANVAS_BACKGROUND_COLORS.items():
            bg_action = bg_menu.addAction(bg_labels.get(bg_key, bg_key))
            bg_action.setCheckable(True)
            bg_action.setData(bg_key)
            bg_action.triggered.connect(lambda checked, k=bg_key: self._on_canvas_background_changed(k))
            bg_group.addAction(bg_action)
        
        bg_menu.addSeparator()
        
        custom_bg_action = bg_menu.addAction(_tr("custom"))
        custom_bg_action.triggered.connect(self._on_custom_canvas_background)
        
        self._update_canvas_background_check(bg_group)
        
        view_menu.addSeparator()
        
        zoom_in_action = view_menu.addAction(_tr("zoom_in"))
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self._beat_board_view.zoom_in)
        
        zoom_out_action = view_menu.addAction(_tr("zoom_out"))
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self._beat_board_view.zoom_out)
        
        fit_action = view_menu.addAction(_tr("fit_to_content"))
        fit_action.setShortcut("Ctrl+0")
        fit_action.triggered.connect(self._beat_board_view.fit_to_contents)
        
        view_menu.addSeparator()
        
        memorize_defaults_action = view_menu.addAction(_tr("memorize_defaults"))
        memorize_defaults_action.setCheckable(True)
        memorize_defaults_action.triggered.connect(self._on_memorize_defaults_toggled)
        self._memorize_action = memorize_defaults_action
        
        grid_action = view_menu.addAction(_tr("show_grid"))
        grid_action.setCheckable(True)
        grid_action.triggered.connect(self._on_grid_toggled)
        self._grid_action = grid_action
        
        view_menu.addSeparator()
        
        grid_menu = view_menu.addMenu(_tr("grid_options"))
        
        size_menu = grid_menu.addMenu(_tr("cell_size"))
        size_group = QActionGroup(self)
        from beatboard.core.constants import GRID_SIZE_OPTIONS
        for size in GRID_SIZE_OPTIONS:
            size_action = size_menu.addAction(f"{size} px")
            size_action.setData(size)
            size_action.setCheckable(True)
            size_action.triggered.connect(lambda checked, s=size: self._on_grid_size_changed(s))
            size_group.addAction(size_action)
        self._update_grid_size_check(size_group)
        
        color_menu = grid_menu.addMenu(_tr("grid_color"))
        color_group = QActionGroup(self)
        
        auto_color_action = color_menu.addAction(_tr("auto"))
        auto_color_action.setData("auto")
        auto_color_action.setCheckable(True)
        auto_color_action.triggered.connect(lambda: self._on_grid_color_changed("auto"))
        color_group.addAction(auto_color_action)
        
        color_menu.addSeparator()
        
        # Colores predefinidos para la cuadrícula
        grid_colors = [
            ("Amarillo", "#FFF59D"),
            ("Azul", "#90CAF9"),
            ("Verde", "#A5D6A7"),
            ("Rojo", "#EF9A9A"),
            ("Naranja", "#FFCC80"),
            ("Púrpura", "#CE93D8"),
            ("Gris", "#E0E0E0"),
        ]
        
        for color_name, hex_color in grid_colors:
            color_action = color_menu.addAction(color_name)
            color_action.setData(hex_color)
            color_action.setCheckable(True)
            color_action.triggered.connect(lambda checked, c=hex_color: self._on_grid_color_changed(c))
            color_group.addAction(color_action)
        
        color_menu.addSeparator()
        
        custom_grid_color_action = color_menu.addAction(_tr("custom"))
        custom_grid_color_action.triggered.connect(self._on_custom_grid_color)
        
        self._update_grid_color_check(color_group)
        
        view_menu.addSeparator()
        
        lang_menu = view_menu.addMenu(_tr("language"))
        lang_group = QActionGroup(self)
        
        from beatboard.i18n import get_locale_name, get_available_locales
        current_locale = self._get_current_locale()
        
        for locale_code in get_available_locales():
            locale_name = get_locale_name(locale_code)
            lang_action = lang_menu.addAction(locale_name)
            lang_action.setCheckable(True)
            lang_action.setData(locale_code)
            if locale_code == current_locale:
                lang_action.setChecked(True)
            lang_action.triggered.connect(lambda checked, lc=locale_code: self._on_language_changed(lc))
            lang_group.addAction(lang_action)
        
        view_menu.addSeparator()
        
        spellcheck_menu = view_menu.addMenu(_tr("spellcheck"))
        
        enable_spellcheck_action = spellcheck_menu.addAction(_tr("enable_spellcheck"))
        enable_spellcheck_action.setCheckable(True)
        enable_spellcheck_action.triggered.connect(self._on_spellcheck_enabled_changed)
        self._enable_spellcheck_action = enable_spellcheck_action
        
        dict_menu = spellcheck_menu.addMenu(_tr("dictionary_language"))
        dict_group = QActionGroup(self)
        
        spell_service = SpellCheckService.instance()
        available_langs = spell_service.get_available_languages()
        current_dict = spell_service.get_current_language()
        
        for lang_code, lang_name in available_langs:
            dict_action = dict_menu.addAction(lang_name)
            dict_action.setCheckable(True)
            dict_action.setData(lang_code)
            if lang_code == current_dict:
                dict_action.setChecked(True)
            dict_action.triggered.connect(lambda checked, lc=lang_code: self._on_spellcheck_language_changed(lc))
            dict_group.addAction(dict_action)
        
        help_menu = menubar.addMenu(_tr("menu_help"))
        
        shortcuts_action = help_menu.addAction(_tr("keyboard_shortcuts"))
        shortcuts_action.triggered.connect(self._on_show_shortcuts)
        
        help_menu.addSeparator()
        
        about_action = help_menu.addAction(_tr("about"))
        about_action.triggered.connect(self._on_about)
    
    def _get_toolbar_icon(self, icon_name: str) -> "QIcon":
        from PySide6.QtGui import QIcon
        from pathlib import Path
        from PySide6.QtWidgets import QApplication
        
        base_path = Path(__file__).parent / "icons"
        
        app = QApplication.instance()
        is_dark = False
        if app and hasattr(app, "theme_manager"):
            is_dark = app.theme_manager.is_dark_mode()
        
        theme_folder = "toolbar_light" if is_dark else "toolbar_dark"
        icon_path = base_path / theme_folder / f"{icon_name}.png"
        
        if icon_path.exists():
            return QIcon(str(icon_path))
        else:
            return QIcon.fromTheme(icon_name)
    
    def _setup_toolbar(self) -> None:
        from PySide6.QtGui import QIcon
        
        toolbar = QToolBar(_tr("toolbar"))
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        new_btn = toolbar.addAction(self._get_toolbar_icon("new"), _tr("new"))
        new_btn.setToolTip(_tr("new_tooltip"))
        new_btn.triggered.connect(self._on_new_project)
        
        open_btn = toolbar.addAction(self._get_toolbar_icon("open"), _tr("open"))
        open_btn.setToolTip(_tr("open_tooltip"))
        open_btn.triggered.connect(self._on_open_project)
        
        save_btn = toolbar.addAction(self._get_toolbar_icon("save"), _tr("save"))
        save_btn.setToolTip(_tr("save_tooltip"))
        save_btn.triggered.connect(self._on_save_project)
        
        toolbar.addSeparator()
        
        zoom_in_btn = toolbar.addAction(self._get_toolbar_icon("zoom-in"), _tr("zoom_in_toolbar"))
        zoom_in_btn.setToolTip(_tr("zoom_in_tooltip"))
        zoom_in_btn.triggered.connect(self._beat_board_view.zoom_in)
        
        zoom_out_btn = toolbar.addAction(self._get_toolbar_icon("zoom-out"), _tr("zoom_out_toolbar"))
        zoom_out_btn.setToolTip(_tr("zoom_out_tooltip"))
        zoom_out_btn.triggered.connect(self._beat_board_view.zoom_out)
        
        fit_btn = toolbar.addAction(self._get_toolbar_icon("fit"), _tr("fit"))
        fit_btn.setToolTip(_tr("fit_tooltip"))
        fit_btn.triggered.connect(self._beat_board_view.fit_to_contents)
        
        center_btn = toolbar.addAction(self._get_toolbar_icon("center"), _tr("center"))
        center_btn.setToolTip(_tr("center_tooltip"))
        center_btn.triggered.connect(self._beat_board_view.center_on_origin)
        
        toolbar.addSeparator()
        
        connection_btn = toolbar.addAction(self._get_toolbar_icon("link"), _tr("connect"))
        connection_btn.setToolTip(_tr("connect_tooltip"))
        connection_btn.triggered.connect(self._beat_board_view.toggle_connection_mode)
    
    def _setup_statusbar(self) -> None:
        self._statusbar = QStatusBar(self)
        self.setStatusBar(self._statusbar)
        self._update_status()
    
    def _connect_signals(self) -> None:
        self._beat_board_view.beat_created.connect(self._on_beat_created)
        self._beat_board_view.beat_deleted.connect(self._on_beat_deleted)
        self._beat_board_view.beat_moved.connect(self._on_beat_moved)
        self._beat_board_view.selection_changed.connect(self._on_selection_changed)
        self._beat_board_view.mouse_moved.connect(self._on_mouse_moved)
        self._properties_panel.beat_updated.connect(self._on_beat_updated)
        
        app = QApplication.instance()
        if app and hasattr(app, "locale_manager"):
            app.locale_manager.locale_changed.connect(self._on_locale_changed)
    
    def _on_locale_changed(self, locale: str) -> None:
        self._rebuild_ui()
    
    def _rebuild_ui(self) -> None:
        self._update_title()
        self._update_status()
    
    def _load_saved_preferences(self) -> None:
        app = QApplication.instance()
        if not app or not hasattr(app, "theme_manager"):
            return
        
        tm = app.theme_manager
        
        grid_enabled = tm.get_grid_enabled()
        self._beat_board_view._scene.set_grid_enabled(grid_enabled)
        if self._grid_action:
            self._grid_action.setChecked(grid_enabled)
        
        grid_size = tm.get_grid_size()
        self._beat_board_view._scene.set_grid_size(grid_size)
        
        grid_color = tm.get_grid_color()
        self._beat_board_view._scene.set_grid_color(grid_color)
        
        memorize_enabled = tm.get_memorize_defaults()
        from beatboard.core.beat_defaults import BeatDefaults
        BeatDefaults.set_memorize_enabled(memorize_enabled)
        if self._memorize_action:
            self._memorize_action.setChecked(memorize_enabled)
        
        spellcheck_enabled = tm.get_spellcheck_enabled()
        spell_service = SpellCheckService.instance()
        
        config_dir = tm._get_config_path().parent
        spell_service.initialize(config_dir)
        
        spell_service.set_enabled(spellcheck_enabled)
        spellcheck_dict = tm.get_spellcheck_dictionary()
        spell_service.set_language(spellcheck_dict)
        
        if self._enable_spellcheck_action:
            self._enable_spellcheck_action.setChecked(spellcheck_enabled)
    
    def _update_title(self) -> None:
        title = f"{self._project.name}"
        if self._is_modified:
            title += " *"
        title += f" - {APP_NAME}"
        self.setWindowTitle(title)
    
    def _update_status(self, cursor_x: int = 0, cursor_y: int = 0) -> None:
        beat_count = len(self._project.beats)
        zoom_percent = int(self._beat_board_view.zoom_level * 100)
        modified_text = _tr("modified") if self._is_modified else _tr("saved")
        self._statusbar.showMessage(
            f"{_tr('beats_count').format(count=beat_count)} | {_tr('zoom_level').format(percent=zoom_percent)} | {modified_text} | {_tr('cursor_position').format(x=cursor_x, y=cursor_y)}"
        )
    
    def _on_mouse_moved(self, x: int, y: int) -> None:
        self._update_status(x, y)
    
    def _set_modified(self, modified: bool = True) -> None:
        self._is_modified = modified
        self._update_title()
        self._update_status()
    
    def _on_new_project(self) -> None:
        if self._is_modified:
            pass
        
        self._project = Project()
        self._current_file = None
        self._is_modified = False
        self._undo_stack.clear()
        self._beat_board_view.set_project(self._project)
        self._stop_autosave()
        self._update_title()
        self._update_status()
    
    def _on_open_project(self) -> None:
        if self._is_modified:
            pass
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            _tr("open_project"),
            "",
            PROJECT_FILE_FILTER,
        )
        
        if file_path:
            self._load_project(file_path)
    
    def _on_save_project(self) -> None:
        if self._current_file:
            self._save_project(self._current_file)
        else:
            self._on_save_project_as()
    
    def _on_save_project_as(self) -> None:
        suggested_name = self._project.name.strip() if self._project.name else "Untitled"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            _tr("save_project_as"),
            f"{suggested_name}.bbp",
            PROJECT_FILE_FILTER,
        )
        
        if file_path:
            self._save_project(file_path)
            self._current_file = file_path
            self._start_autosave()
    
    def _save_project(self, file_path: str) -> None:
        import json
        from pathlib import Path
        
        Path(file_path).write_text(
            json.dumps(self._project.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        
        self._set_modified(False)
        
        app = QApplication.instance()
        if hasattr(app, "logger"):
            app.logger.info(f"Project saved to {file_path}")
    
    def _load_project(self, file_path: str) -> None:
        import json
        from pathlib import Path
        
        try:
            data = json.loads(Path(file_path).read_text(encoding="utf-8"))
            self._project = Project.from_dict(data)
            self._current_file = file_path
            self._is_modified = False
            self._beat_board_view.set_project(self._project)
            self._start_autosave()
            self._update_title()
            self._update_status()
            
            app = QApplication.instance()
            if hasattr(app, "logger"):
                app.logger.info(f"Project loaded from {file_path}")
        except Exception as e:
            app = QApplication.instance()
            if hasattr(app, "logger"):
                app.logger.error(f"Error loading project: {e}")
    
    def _on_export_pdf(self) -> None:
        from beatboard.services.export_service import ExportService
        ExportService.export_to_pdf(self._project, self)
    
    def _on_export_text(self) -> None:
        from beatboard.services.export_service import ExportService
        ExportService.export_to_text(self._project, self)
    
    def _get_current_file_path(self) -> str | None:
        return self._current_file
    
    def _start_autosave(self) -> None:
        if self._autosave_service is None:
            self._autosave_service = AutosaveService(
                self._project, 
                self._get_current_file_path
            )
        self._autosave_service.start()
    
    def _stop_autosave(self) -> None:
        if self._autosave_service:
            self._autosave_service.stop()
    
    def _on_theme_changed(self, mode: ThemeMode) -> None:
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            app.theme_manager.set_theme(mode)
    
    def _update_theme_check(self, main_group: QActionGroup, light_group: QActionGroup | None = None, dark_group: QActionGroup | None = None) -> None:
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            current_mode = app.theme_manager.get_current_mode()
            for action in main_group.actions():
                if action.data() == current_mode.value:
                    action.setChecked(True)
                    break
            
            all_groups = [main_group]
            if light_group:
                all_groups.append(light_group)
            if dark_group:
                all_groups.append(dark_group)
            
            for group in all_groups:
                for action in group.actions():
                    if action.data() == current_mode.value:
                        action.setChecked(True)
    
    def _on_canvas_background_changed(self, color_key: str) -> None:
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            app.theme_manager.set_canvas_background(color_key)
    
    def _update_canvas_background_check(self, bg_group: QActionGroup) -> None:
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            current_bg = app.theme_manager.get_canvas_background()
            for action in bg_group.actions():
                if action.data() == current_bg:
                    action.setChecked(True)
                    break
    
    def _on_custom_canvas_background(self) -> None:
        from PySide6.QtWidgets import QColorDialog
        from PySide6.QtGui import QColor
        
        app = QApplication.instance()
        current_color = "#f0f0f0"
        if app and hasattr(app, "theme_manager"):
            current_key = app.theme_manager.get_canvas_background()
            from beatboard.core.constants import CANVAS_BACKGROUND_COLORS
            current_color = CANVAS_BACKGROUND_COLORS.get(current_key, "#f0f0f0")
        
        color = QColorDialog.getColor(QColor(current_color), self, _tr("canvas_background_color"))
        if color.isValid():
            hex_color = color.name()
            self._set_custom_canvas_background(hex_color)
    
    def _set_custom_canvas_background(self, hex_color: str) -> None:
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            app.theme_manager.set_custom_canvas_background(hex_color)
    
    def _on_grid_toggled(self, checked: bool) -> None:
        self._beat_board_view._scene.set_grid_enabled(checked)
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            app.theme_manager.set_grid_enabled(checked)
    
    def _on_memorize_defaults_toggled(self, checked: bool) -> None:
        from beatboard.core.beat_defaults import BeatDefaults
        BeatDefaults.set_memorize_enabled(checked)
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            app.theme_manager.set_memorize_defaults(checked)
    
    def _on_spellcheck_enabled_changed(self, checked: bool) -> None:
        spell_service = SpellCheckService.instance()
        spell_service.set_enabled(checked)
        
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            app.theme_manager.set_spellcheck_enabled(checked)
    
    def _on_spellcheck_language_changed(self, lang_code: str) -> None:
        spell_service = SpellCheckService.instance()
        spell_service.set_language(lang_code)
        
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            app.theme_manager.set_spellcheck_dictionary(lang_code)
    
    def _on_grid_size_changed(self, size: int) -> None:
        self._beat_board_view._scene.set_grid_size(size)
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            app.theme_manager.set_grid_size(size)
    
    def _update_grid_size_check(self, size_group: QActionGroup) -> None:
        current_size = self._beat_board_view._scene.get_grid_size()
        for action in size_group.actions():
            if action.data() == current_size:
                action.setChecked(True)
                break
    
    def _on_grid_color_changed(self, color: str) -> None:
        self._beat_board_view._scene.set_grid_color(color)
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            app.theme_manager.set_grid_color(color)
    
    def _on_custom_grid_color(self) -> None:
        from PySide6.QtWidgets import QColorDialog
        from PySide6.QtGui import QColor
        
        app = QApplication.instance()
        current_color = "#CCCCCC"
        if app and hasattr(app, "theme_manager"):
            current_key = app.theme_manager.get_grid_color()
            if current_key not in ("auto", "custom") and current_key.startswith("#"):
                current_color = current_key
        
        color = QColorDialog.getColor(QColor(current_color), self, _tr("select_color"))
        if color.isValid():
            hex_color = color.name()
            self._beat_board_view._scene.set_grid_color(hex_color)
            if app and hasattr(app, "theme_manager"):
                app.theme_manager.set_grid_color(hex_color)
    
    def _update_grid_color_check(self, color_group: QActionGroup) -> None:
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            current_color = app.theme_manager.get_grid_color()
        else:
            current_color = "auto"
        for action in color_group.actions():
            if action.data() == current_color:
                action.setChecked(True)
                break
    
    def _on_beat_created(self, beat_id: str) -> None:
        self._set_modified(True)
    
    def _on_beat_deleted(self, beat_id: str) -> None:
        self._set_modified(True)
    
    def _on_beat_moved(self, beat_id: str) -> None:
        self._set_modified(True)
    
    def _on_delete_selected(self) -> None:
        self._beat_board_view.delete_selected_beats()
    
    def _on_copy(self) -> None:
        self._beat_board_view.copy_selected_beats()
    
    def _on_cut(self) -> None:
        self._beat_board_view.cut_selected_beats()
    
    def _on_paste(self) -> None:
        self._beat_board_view.paste_beats()
    
    def _on_bring_to_front(self) -> None:
        self._beat_board_view.bring_selected_beats_to_front()
    
    def _on_send_to_back(self) -> None:
        self._beat_board_view.send_selected_beats_to_back()
    
    def _on_move_up(self) -> None:
        self._beat_board_view.move_selected_beats_up()
    
    def _on_move_down(self) -> None:
        self._beat_board_view.move_selected_beats_down()
    
    def _on_select_all(self) -> None:
        self._beat_board_view.select_all_beats()
    
    def _on_selection_changed(self, beat_ids: list[str]) -> None:
        count = len(beat_ids)
        if count == 0:
            self._properties_panel.clear()
            self._statusbar.showMessage(_tr("no_beat_selected_status"))
        elif count == 1:
            beat = self._project.get_beat_by_id(beat_ids[0])
            if beat:
                self._properties_panel.set_beat(beat)
                self._statusbar.showMessage(_tr("selected_beat_status").format(title=beat.title or _tr("title_placeholder")))
        else:
            self._properties_panel.clear()
            self._statusbar.showMessage(_tr("multiple_selected_status").format(count=count))
    
    def _on_beat_updated(self, beat_id: str, title: str, content: str, color: str, show_title: bool) -> None:
        beat = self._project.get_beat_by_id(beat_id)
        if beat:
            beat.title = title
            beat.content = content
            beat.color = color
            beat.show_title = show_title
            item = self._beat_board_view._get_item_by_beat_id(beat_id)
            if item:
                item.refresh()
            self._beat_board_view.beat_moved.emit(beat_id)
    
    def _on_show_shortcuts(self) -> None:
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
        
        shortcuts_text = f"""
        <h2>{_tr("keyboard_shortcuts")}</h2>

        <h3>{_tr("shortcuts_file")}</h3>
        <ul>
        <li><b>Ctrl+N</b>: {_tr("shortcut_new_project")}</li>
        <li><b>Ctrl+O</b>: {_tr("shortcut_open_project")}</li>
        <li><b>Ctrl+S</b>: {_tr("shortcut_save_project")}</li>
        <li><b>Ctrl+Shift+S</b>: {_tr("shortcut_save_as")}</li>
        </ul>

        <h3>{_tr("shortcuts_edit")}</h3>
        <ul>
        <li><b>Ctrl+Z</b>: {_tr("shortcut_undo")}</li>
        <li><b>Ctrl+Y</b>: {_tr("shortcut_redo")}</li>
        <li><b>Ctrl+A</b>: {_tr("shortcut_select_all")}</li>
        <li><b>Ctrl+C</b>: {_tr("shortcut_copy")}</li>
        <li><b>Ctrl+X</b>: {_tr("shortcut_cut")}</li>
        <li><b>Ctrl+V</b>: {_tr("shortcut_paste")}</li>
        <li><b>Ctrl+Home</b>: {_tr("shortcut_bring_front")}</li>
        <li><b>Ctrl+End</b>: {_tr("shortcut_send_back")}</li>
        <li><b>Ctrl+PageUp</b>: {_tr("shortcut_move_up")}</li>
        <li><b>Ctrl+PageDown</b>: {_tr("shortcut_move_down")}</li>
        <li><b>Delete/Supr</b>: {_tr("shortcut_delete")}</li>
        </ul>

        <h3>{_tr("shortcuts_view")}</h3>
        <ul>
        <li><b>Ctrl+0</b>: {_tr("shortcut_fit")}</li>
        <li><b>Ctrl++</b>: {_tr("shortcut_zoom_in")}</li>
        <li><b>Ctrl+-</b>: {_tr("shortcut_zoom_out")}</li>
        <li><b>Espacio</b>: {_tr("shortcut_pan")}</li>
        <li><b>Escape</b>: {_tr("shortcut_deselect")}</li>
        </ul>

        <h3>{_tr("shortcuts_other")}</h3>
        <ul>
        <li><b>1-8</b>: {_tr("shortcut_change_color")}</li>
        <li><b>{_tr("shortcut_new_beat")}</b></li>
        <li><b>{_tr("shortcut_edit_beat")}</b></li>
        </ul>
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle(_tr("keyboard_shortcuts"))
        dialog.setMinimumSize(400, 500)
        
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setHtml(shortcuts_text)
        text_edit.setReadOnly(True)
        
        layout.addWidget(text_edit)
        dialog.setLayout(layout)
        
        dialog.exec()
    
    def _on_about(self) -> None:
        from PySide6.QtWidgets import QMessageBox
        from datetime import date
        
        current_year = date.today().year
        version_date = "March 03, 2026"
        
        QMessageBox.about(
            self,
            f"{_tr('about')} {APP_NAME}",
            f"<h3>{APP_NAME}</h3>"
            f"<p><b>{_tr('version').format(version=APP_VERSION)}</b> - {version_date}</p>"
            f"<p>{_tr('app_description')}</p>"
            f"<p>{_tr('inspired_by')}</p>"
            f"<hr>"
            f"<p><b>{_tr('author')}</b> CarlyMx</p>"
            f"<p><b>{_tr('email')}</b> <a href='mailto:carlymx@gmail.com'>carlymx@gmail.com</a></p>"
            f"<p><b>{_tr('github')}</b> <a href='https://github.com/carlymx/BeatBoard'>https://github.com/carlymx/BeatBoard</a></p>"
            f"<hr>"
            f"<p><b>{_tr('license')}:</b> <a href='https://creativecommons.org/licenses/by-nc/4.0/legalcode'>Creative Commons BY-NC 4.0</a></p>"
            f"<p>{_tr('copyright').format(year=current_year)}</p>",
        )
    
    def closeEvent(self, event) -> None:
        if self._is_modified:
            from PySide6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self,
                _tr("save_changes"),
                _tr("save_changes_question"),
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self._on_save_project()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def _get_current_locale(self) -> str:
        app = QApplication.instance()
        if app and hasattr(app, "locale_manager"):
            return app.locale_manager.get_current_locale()
        return "en"
    
    def _on_language_changed(self, locale_code: str) -> None:
        app = QApplication.instance()
        if app and hasattr(app, "locale_manager"):
            app.locale_manager.set_locale(locale_code)
            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                _tr("language_changed"),
                _tr("language_changed_message"),
            )
