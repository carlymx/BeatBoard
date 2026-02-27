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
        
        file_menu = menubar.addMenu("&Archivo")
        
        new_action = file_menu.addAction("&Nuevo")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_project)
        
        open_action = file_menu.addAction("&Abrir...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_project)
        
        file_menu.addSeparator()
        
        save_action = file_menu.addAction("&Guardar")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save_project)
        
        save_as_action = file_menu.addAction("Guardar &como...")
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._on_save_project_as)
        
        file_menu.addSeparator()
        
        export_pdf_action = file_menu.addAction("Exportar a &PDF...")
        export_pdf_action.triggered.connect(self._on_export_pdf)
        
        export_text_action = file_menu.addAction("Exportar a &texto...")
        export_text_action.triggered.connect(self._on_export_text)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("&Salir")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        edit_menu = menubar.addMenu("&Editar")
        
        undo_action = edit_menu.addAction("&Deshacer")
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self._undo_stack.undo)
        
        redo_action = edit_menu.addAction("&Rehacer")
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self._undo_stack.redo)
        
        edit_menu.addSeparator()
        
        select_all_action = edit_menu.addAction("Seleccionar &todo")
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self._on_select_all)
        
        edit_menu.addSeparator()
        
        copy_action = edit_menu.addAction("&Copiar")
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self._on_copy)
        
        cut_action = edit_menu.addAction("Cor&tar")
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self._on_cut)
        
        paste_action = edit_menu.addAction("&Pegar")
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self._on_paste)
        
        edit_menu.addSeparator()
        
        bring_front_action = edit_menu.addAction("Traer al &frente")
        bring_front_action.setShortcut("Ctrl+Home")
        bring_front_action.triggered.connect(self._on_bring_to_front)
        
        send_back_action = edit_menu.addAction("Enviar al &fondo")
        send_back_action.setShortcut("Ctrl+End")
        send_back_action.triggered.connect(self._on_send_to_back)
        
        move_up_action = edit_menu.addAction("Subir &uno")
        move_up_action.setShortcut("Ctrl+PageUp")
        move_up_action.triggered.connect(self._on_move_up)
        
        move_down_action = edit_menu.addAction("&Bajar uno")
        move_down_action.setShortcut("Ctrl+PageDown")
        move_down_action.triggered.connect(self._on_move_down)
        
        edit_menu.addSeparator()
        
        delete_action = edit_menu.addAction("&Eliminar beat")
        delete_action.triggered.connect(self._on_delete_selected)
        
        view_menu = menubar.addMenu("&Ver")
        
        theme_menu = view_menu.addMenu("&Tema")
        
        theme_group = QActionGroup(self)
        
        system_theme_action = theme_menu.addAction("Sistema")
        system_theme_action.setCheckable(True)
        system_theme_action.setData(ThemeMode.SYSTEM.value)
        system_theme_action.triggered.connect(lambda: self._on_theme_changed(ThemeMode.SYSTEM))
        theme_group.addAction(system_theme_action)
        
        theme_menu.addSeparator()
        
        light_submenu = theme_menu.addMenu("Claro")
        light_group = QActionGroup(self)
        
        light_actions = [
            (ThemeMode.LIGHT, "Claro (predeterminado)"),
            (ThemeMode.SOLARIZED_LIGHT, "Solarized Light"),
            (ThemeMode.GITHUB_LIGHT, "GitHub Light"),
            (ThemeMode.PAPERCOLOR, "PaperColor"),
        ]
        for mode, label in light_actions:
            action = light_submenu.addAction(label)
            action.setCheckable(True)
            action.setData(mode.value)
            action.triggered.connect(lambda checked, m=mode: self._on_theme_changed(m))
            light_group.addAction(action)
        
        dark_submenu = theme_menu.addMenu("Oscuro")
        dark_group = QActionGroup(self)
        
        dark_actions = [
            (ThemeMode.DARK, "Oscuro (predeterminado)"),
            (ThemeMode.DRACULA, "Dracula"),
            (ThemeMode.NORD, "Nord"),
            (ThemeMode.ONE_DARK, "One Dark"),
            (ThemeMode.MATERIAL_DARK, "Material Dark"),
        ]
        for mode, label in dark_actions:
            action = dark_submenu.addAction(label)
            action.setCheckable(True)
            action.setData(mode.value)
            action.triggered.connect(lambda checked, m=mode: self._on_theme_changed(m))
            dark_group.addAction(action)
        
        self._update_theme_check(theme_group, light_group, dark_group)
        
        view_menu.addSeparator()
        
        bg_menu = view_menu.addMenu("Color de &fondo")
        
        bg_group = QActionGroup(self)
        
        from beatboard.core.constants import CANVAS_BACKGROUND_COLORS
        
        bg_labels = {
            "white": "Blanco",
            "light_gray": "Gris claro",
            "gray": "Gris",
            "dark_gray": "Gris oscuro",
            "cream": "Crema",
            "dark": "Oscuro",
            "black": "Negro",
        }
        
        for bg_key, bg_hex in CANVAS_BACKGROUND_COLORS.items():
            bg_action = bg_menu.addAction(bg_labels.get(bg_key, bg_key))
            bg_action.setCheckable(True)
            bg_action.setData(bg_key)
            bg_action.triggered.connect(lambda checked, k=bg_key: self._on_canvas_background_changed(k))
            bg_group.addAction(bg_action)
        
        bg_menu.addSeparator()
        
        custom_bg_action = bg_menu.addAction("Personalizado...")
        custom_bg_action.triggered.connect(self._on_custom_canvas_background)
        
        self._update_canvas_background_check(bg_group)
        
        view_menu.addSeparator()
        
        zoom_in_action = view_menu.addAction("Acercar")
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self._beat_board_view.zoom_in)
        
        zoom_out_action = view_menu.addAction("Alejar")
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self._beat_board_view.zoom_out)
        
        fit_action = view_menu.addAction("Ajustar a contenido")
        fit_action.setShortcut("Ctrl+0")
        fit_action.triggered.connect(self._beat_board_view.fit_to_contents)
        
        view_menu.addSeparator()
        
        memorize_defaults_action = view_menu.addAction("Recordar tamaño y color del último beat")
        memorize_defaults_action.setCheckable(True)
        memorize_defaults_action.triggered.connect(self._on_memorize_defaults_toggled)
        self._memorize_action = memorize_defaults_action
        
        grid_action = view_menu.addAction("Mostrar cuadrícula")
        grid_action.setCheckable(True)
        grid_action.triggered.connect(self._on_grid_toggled)
        self._grid_action = grid_action
        
        view_menu.addSeparator()
        
        grid_menu = view_menu.addMenu("Opciones de cuadrícula")
        
        size_menu = grid_menu.addMenu("Tamaño de celda")
        size_group = QActionGroup(self)
        from beatboard.core.constants import GRID_SIZE_OPTIONS
        for size in GRID_SIZE_OPTIONS:
            size_action = size_menu.addAction(f"{size} px")
            size_action.setData(size)
            size_action.setCheckable(True)
            size_action.triggered.connect(lambda checked, s=size: self._on_grid_size_changed(s))
            size_group.addAction(size_action)
        self._update_grid_size_check(size_group)
        
        color_menu = grid_menu.addMenu("Color de cuadrícula")
        color_group = QActionGroup(self)
        
        auto_color_action = color_menu.addAction("Auto")
        auto_color_action.setData("auto")
        auto_color_action.setCheckable(True)
        auto_color_action.triggered.connect(lambda: self._on_grid_color_changed("auto"))
        color_group.addAction(auto_color_action)
        
        color_menu.addSeparator()
        
        from beatboard.core.constants import BEAT_COLORS
        for color_name, color_value in BEAT_COLORS.items():
            color_action = color_menu.addAction(color_name.capitalize())
            color_action.setData(color_value.name())
            color_action.setCheckable(True)
            color_action.triggered.connect(lambda checked, c=color_value.name(): self._on_grid_color_changed(c))
            color_group.addAction(color_action)
        
        self._update_grid_color_check(color_group)
        
        help_menu = menubar.addMenu("A&yuda")
        
        shortcuts_action = help_menu.addAction("Atajos de &teclado")
        shortcuts_action.triggered.connect(self._on_show_shortcuts)
        
        help_menu.addSeparator()
        
        about_action = help_menu.addAction("&Acerca de")
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
        
        toolbar = QToolBar("Barra de herramientas")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        new_btn = toolbar.addAction(self._get_toolbar_icon("new"), "Nuevo")
        new_btn.setToolTip("Crear nuevo proyecto (Ctrl+N)")
        new_btn.triggered.connect(self._on_new_project)
        
        open_btn = toolbar.addAction(self._get_toolbar_icon("open"), "Abrir")
        open_btn.setToolTip("Abrir proyecto existente (Ctrl+O)")
        open_btn.triggered.connect(self._on_open_project)
        
        save_btn = toolbar.addAction(self._get_toolbar_icon("save"), "Guardar")
        save_btn.setToolTip("Guardar proyecto (Ctrl+S)")
        save_btn.triggered.connect(self._on_save_project)
        
        toolbar.addSeparator()
        
        zoom_in_btn = toolbar.addAction(self._get_toolbar_icon("zoom-in"), "+")
        zoom_in_btn.setToolTip("Acercar (Ctrl++)")
        zoom_in_btn.triggered.connect(self._beat_board_view.zoom_in)
        
        zoom_out_btn = toolbar.addAction(self._get_toolbar_icon("zoom-out"), "-")
        zoom_out_btn.setToolTip("Alejar (Ctrl+-)")
        zoom_out_btn.triggered.connect(self._beat_board_view.zoom_out)
        
        fit_btn = toolbar.addAction(self._get_toolbar_icon("fit"), "Ajustar")
        fit_btn.setToolTip("Ajustar a contenido (Ctrl+0)")
        fit_btn.triggered.connect(self._beat_board_view.fit_to_contents)
        
        center_btn = toolbar.addAction(self._get_toolbar_icon("center"), "Centrar")
        center_btn.setToolTip("Centrar vista en el origen (0,0)")
        center_btn.triggered.connect(self._beat_board_view.center_on_origin)
        
        toolbar.addSeparator()
        
        connection_btn = toolbar.addAction(self._get_toolbar_icon("link"), "Conectar")
        connection_btn.setToolTip("Modo conexión (crear líneas entre beats)")
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
        
        memorize_enabled = tm.get_memorize_defaults()
        from beatboard.core.beat_defaults import BeatDefaults
        BeatDefaults.set_memorize_enabled(memorize_enabled)
        if self._memorize_action:
            self._memorize_action.setChecked(memorize_enabled)
    
    def _update_title(self) -> None:
        title = f"{self._project.name}"
        if self._is_modified:
            title += " *"
        title += f" - {APP_NAME}"
        self.setWindowTitle(title)
    
    def _update_status(self, cursor_x: int = 0, cursor_y: int = 0) -> None:
        beat_count = len(self._project.beats)
        zoom_percent = int(self._beat_board_view.zoom_level * 100)
        modified_text = "Modificado" if self._is_modified else "Guardado"
        self._statusbar.showMessage(
            f"Beats: {beat_count} | Zoom: {zoom_percent}% | {modified_text} | Cursor: ({cursor_x}, {cursor_y})"
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
            "Abrir proyecto",
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
        suggested_name = self._project.name.strip() if self._project.name else "Sin título"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar proyecto como",
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
        
        color = QColorDialog.getColor(QColor(current_color), self, "Color de fondo del lienzo")
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
    
    def _update_grid_color_check(self, color_group: QActionGroup) -> None:
        current_color = self._beat_board_view._scene.get_grid_color()
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
            self._statusbar.showMessage("Ningún beat seleccionado")
        elif count == 1:
            beat = self._project.get_beat_by_id(beat_ids[0])
            if beat:
                self._properties_panel.set_beat(beat)
                self._statusbar.showMessage(f"Seleccionado: {beat.title or 'Sin título'}")
        else:
            self._properties_panel.clear()
            self._statusbar.showMessage(f"{count} beats seleccionados")
    
    def _on_beat_updated(self, beat_id: str, title: str, content: str, color: str) -> None:
        beat = self._project.get_beat_by_id(beat_id)
        if beat:
            item = self._beat_board_view._get_item_by_beat_id(beat_id)
            if item:
                item.update()
            self._beat_board_view.beat_moved.emit(beat_id)
    
    def _on_show_shortcuts(self) -> None:
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
        
        shortcuts_text = """
<h2>Atajos de Teclado</h2>

<h3>Archivo</h3>
<ul>
<li><b>Ctrl+N</b>: Nuevo proyecto</li>
<li><b>Ctrl+O</b>: Abrir proyecto</li>
<li><b>Ctrl+S</b>: Guardar proyecto</li>
<li><b>Ctrl+Shift+S</b>: Guardar como</li>
</ul>

<h3>Editar</h3>
<ul>
<li><b>Ctrl+Z</b>: Deshacer</li>
<li><b>Ctrl+Y</b>: Rehacer</li>
<li><b>Ctrl+A</b>: Seleccionar todo</li>
<li><b>Ctrl+C</b>: Copiar beats seleccionados</li>
<li><b>Ctrl+X</b>: Cortar beats seleccionados</li>
<li><b>Ctrl+V</b>: Pegar beats copiados</li>
<li><b>Ctrl+Home</b>: Traer al frente</li>
<li><b>Ctrl+End</b>: Enviar al fondo</li>
<li><b>Ctrl+PageUp</b>: Subir uno</li>
<li><b>Ctrl+PageDown</b>: Bajar uno</li>
<li><b>Delete/Supr</b>: Eliminar selección</li>
</ul>

<h3>Vista</h3>
<ul>
<li><b>Ctrl+0</b>: Ajustar a contenido</li>
<li><b>Ctrl++</b>: Acercar</li>
<li><b>Ctrl+-</b>: Alejar</li>
<li><b>Espacio</b>: Modo paneo (mantener presionado)</li>
<li><b>Escape</b>: Deseleccionar todo / Cancelar modo conexión</li>
</ul>

<h3>Otros</h3>
<ul>
<li><b>1-8</b>: Cambiar color del beat seleccionado</li>
<li><b>Doble clic (canvas)</b>: Crear nuevo beat</li>
<li><b>Doble clic (beat)</b>: Editar beat</li>
</ul>
"""
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Atajos de Teclado")
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
        version_date = "27 de Febrero de 2026"
        
        QMessageBox.about(
            self,
            f"Acerca de {APP_NAME}",
            f"<h3>{APP_NAME}</h3>"
            f"<p><b>Versión {APP_VERSION}</b> - {version_date}</p>"
            f"<p>Una pizarra virtual para escritores de guiones.</p>"
            f"<p>Inspirado en Final Draft Beat Board.</p>"
            f"<hr>"
            f"<p><b>Autor:</b> CarlyMx</p>"
            f"<p><b>Email:</b> <a href='mailto:carlymx@gmail.com'>carlymx@gmail.com</a></p>"
            f"<p><b>GitHub:</b> <a href='https://github.com/carlymx/BeatBoard'>https://github.com/carlymx/BeatBoard</a></p>"
            f"<hr>"
            f"<p>Licencia: <a href='https://creativecommons.org/licenses/by-nc/4.0/legalcode.es'>Creative Commons BY-NC 4.0</a></p>"
            f"<p>© {current_year} CarlyMx. Todos los derechos reservados.</p>",
        )
    
    def closeEvent(self, event) -> None:
        if self._is_modified:
            from PySide6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self,
                "Guardar cambios",
                "¿Deseas guardar los cambios antes de salir?",
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
