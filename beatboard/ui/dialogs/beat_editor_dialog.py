"""Dialog for editing a beat with WYSIWYG editor."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from beatboard.core.beat import Beat
from beatboard.core.constants import (
    BEAT_PREDEFINED_COLORS,
    BEAT_PREDEFINED_NAMES,
    BEAT_CUSTOM_COLORS,
    get_valid_beat_color,
)
from beatboard.i18n import _tr
from beatboard.ui.widgets.rich_text_editor import RichTextEditor

if TYPE_CHECKING:
    pass


class BeatEditorDialog(QDialog):
    def __init__(self, beat: Beat, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._beat = beat
        self._original_color = beat.color
        self._embedded_images = list(getattr(beat, 'embedded_images', []))
        
        self.setWindowTitle(_tr("edit_beat"))
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self._title_edit = QLineEdit()
        self._title_edit.setText(beat.title or "")
        self._title_edit.setPlaceholderText(_tr("beat_title_placeholder"))
        form_layout.addRow(_tr("title") + ":", self._title_edit)
        
        layout.addLayout(form_layout)
        
        content_label = QLabel(_tr("content"))
        content_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(content_label)
        
        self._content_edit = RichTextEditor()
        self._content_edit.setPlaceholderText(_tr("beat_content_placeholder"))
        self._content_edit.setMinimumHeight(250)
        self._content_edit.set_image_insert_callback(self._on_image_insert)
        
        # Build image path mapping for the editor
        image_path_map = {}
        project_path = self._get_project_path()
        for img_info in self._embedded_images:
            if isinstance(img_info, dict):
                rel_path = img_info.get('relative_path')
                orig_path = img_info.get('original_path')
                if orig_path and Path(orig_path).exists():
                    image_path_map[orig_path] = rel_path
                elif rel_path and project_path:
                    # Try to resolve relative path
                    possible_paths = [
                        project_path / rel_path,
                        project_path / "beats" / self._beat.id / Path(rel_path).name,
                    ]
                    for abs_path in possible_paths:
                        if abs_path.exists():
                            image_path_map[str(abs_path)] = rel_path
                            break
            else:
                # Legacy string path
                rel_path = img_info
                if rel_path and project_path:
                    possible_paths = [
                        project_path / rel_path,
                        project_path / "beats" / self._beat.id / Path(rel_path).name,
                    ]
                    for abs_path in possible_paths:
                        if abs_path.exists():
                            image_path_map[str(abs_path)] = rel_path
                            break
        if image_path_map:
            self._content_edit.set_image_path_map(image_path_map)
        
        content_mode = getattr(beat, 'content_mode', 'html')
        content_markdown = getattr(beat, 'content_markdown', '')
        
        if content_mode == "markdown" and content_markdown:
            self._content_edit.set_content_and_mode(beat.content, content_markdown, content_mode)
        else:
            self._content_edit.set_content_mode(content_mode)
            if beat.content and "<" in beat.content:
                self._content_edit.setHtml(beat.content)
            else:
                self._content_edit.setPlainText(beat.content or "")
        
        layout.addWidget(self._content_edit)
        
        self._color_widget = ColorPickerWidget(beat.color)
        layout.addWidget(self._color_widget)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _get_project_path(self):
        """Get the current project's data directory path."""
        from pathlib import Path
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app and hasattr(app, 'main_window'):
            main_window = app.main_window
            if hasattr(main_window, '_project') and main_window._project:
                project = main_window._project
                if hasattr(project, 'project_path') and project.project_path:
                    return Path(project.project_path)
        return None
    
    def _on_image_insert(self, file_path: str) -> str:
        from pathlib import Path
        import uuid
        
        original_path = Path(file_path)
        if not original_path.exists():
            return file_path
        
        ext = original_path.suffix
        new_filename = f"{uuid.uuid4()}{ext}"
        
        beats_folder = Path("beats") / self._beat.id
        relative_path = str(beats_folder / new_filename)
        
        self._embedded_images.append({
            'original_path': file_path,
            'relative_path': relative_path,
            'filename': new_filename,
        })
        
        return relative_path
    
    def get_beat_data(self) -> tuple[str, str, str, str, str, list]:
        title = self._title_edit.text()
        content = self._content_edit.toHtml()
        color = self._color_widget.get_selected_color()
        content_mode = self._content_edit.get_content_mode()
        content_markdown = self._content_edit.get_saved_markdown()
        embedded_images = self._embedded_images
        return title, content, color, content_mode, content_markdown, embedded_images


class ColorPickerWidget(QWidget):
    def __init__(self, current_color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._selected_color = get_valid_beat_color(current_color)
        
        # Obtener colores personalizados del ThemeManager
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app and hasattr(app, 'theme_manager'):
            self._custom_colors = app.theme_manager.get_custom_colors()
        else:
            self._custom_colors = BEAT_CUSTOM_COLORS.copy()
        
        layout = QVBoxLayout(self)
        
        label = QLabel(_tr("color"))
        layout.addWidget(label)
        
        # Layout para colores predefinidos (1-7)
        predefined_layout = QHBoxLayout()
        for i, (hex_color, color_name) in enumerate(zip(BEAT_PREDEFINED_COLORS, BEAT_PREDEFINED_NAMES)):
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #999; border-radius: 3px;")
            btn.setToolTip(f"{color_name} ({hex_color})")
            btn.clicked.connect(self._make_color_handler(hex_color))
            predefined_layout.addWidget(btn)
        
        predefined_layout.addStretch()
        layout.addLayout(predefined_layout)
        
        # Layout para colores personalizables (8, 9, 0)
        custom_layout = QHBoxLayout()
        custom_label = QLabel("Personalizados (Doble-Click para cambiar):")
        custom_layout.addWidget(custom_label)
        
        for i, hex_color in enumerate(self._custom_colors):
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #999; border-radius: 3px;")
            btn.setToolTip(f"Personalizado {i+1} ({hex_color}) - Click para usar, Doble-Click para personalizar")
            btn.clicked.connect(self._make_color_handler(hex_color))
            
            # Personalizar con Doble-Click
            def make_customize_handler(index):
                def handler(event):
                    if event.type() == event.Type.MouseButtonDblClick:
                        self._customize_color(index)
                    else:
                        self._select_color(self._custom_colors[index])
                return handler
            
            btn.mouseDoubleClickEvent = make_customize_handler(i)
            custom_layout.addWidget(btn)
        
        custom_layout.addStretch()
        layout.addLayout(custom_layout)
    
    def _select_color(self, hex_color: str) -> None:
        self._selected_color = hex_color
    
    def _make_color_handler(self, hex_color: str):
        def handler():
            self._selected_color = hex_color
        return handler
    
    def _customize_color(self, index: int) -> None:
        """Personalizar uno de los colores personalizables."""
        current_color = QColor(self._custom_colors[index])
        color = QColorDialog.getColor(current_color, self, f"Personalizar color {index+1}")
        if color.isValid():
            hex_color = color.name()
            self._custom_colors[index] = hex_color
            
            # Guardar en ThemeManager
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app and hasattr(app, 'theme_manager'):
                app.theme_manager.set_custom_color(index, hex_color)
            
            # Actualizar el botón
            for btn in self.findChildren(QPushButton):
                if btn.toolTip() and f"Personalizado {index+1}" in btn.toolTip():
                    btn.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #999; border-radius: 3px;")
                    btn.setToolTip(f"Personalizado {index+1} ({hex_color}) - Click para usar, Doble-Click para personalizar")
                    break
    

    
    def get_selected_color(self) -> str:
        return self._selected_color
    
    def get_custom_colors(self) -> list[str]:
        return self._custom_colors.copy()