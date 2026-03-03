"""Dialog for editing a beat with WYSIWYG editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from beatboard.core.beat import Beat
from beatboard.core.constants import (
    BEAT_PREDEFINED_COLORS,
    BEAT_PREDEFINED_NAMES,
    BEAT_CUSTOM_COLORS,
    get_valid_beat_color,
    get_beat_qcolor,
)
from beatboard.i18n import _tr
from beatboard.services.spellcheck_service import SpellCheckService
from beatboard.ui.widgets.spellcheck_highlighter import SpellCheckTextEdit

if TYPE_CHECKING:
    pass


class BeatEditorDialog(QDialog):
    def __init__(self, beat: Beat, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._beat = beat
        self._original_color = beat.color
        
        self.setWindowTitle(_tr("edit_beat"))
        self.setMinimumSize(500, 450)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self._title_edit = SpellCheckTextEdit()
        self._title_edit.setPlainText(beat.title or "")
        self._title_edit.setPlaceholderText(_tr("beat_title_placeholder"))
        self._title_edit.setMaximumHeight(30)
        form_layout.addRow(_tr("title") + ":", self._title_edit)
        
        layout.addLayout(form_layout)
        
        content_label = QLabel(_tr("content"))
        content_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(content_label)
        
        self._toolbar = QToolBar()
        self._toolbar.setMovable(False)
        layout.addWidget(self._toolbar)
        
        self._bold_btn = self._toolbar.addAction("B")
        self._bold_btn.setToolTip(_tr("bold") + " (Ctrl+B)")
        self._bold_btn.triggered.connect(self._toggle_bold)
        
        self._italic_btn = self._toolbar.addAction("I")
        italic_font = QFont()
        italic_font.setItalic(True)
        self._italic_btn.setFont(italic_font)
        self._italic_btn.setToolTip(_tr("italic") + " (Ctrl+I)")
        self._italic_btn.triggered.connect(self._toggle_italic)
        
        self._underline_btn = self._toolbar.addAction("U")
        underline_font = QFont()
        underline_font.setUnderline(True)
        self._underline_btn.setFont(underline_font)
        self._underline_btn.setToolTip(_tr("underline") + " (Ctrl+U)")
        self._underline_btn.triggered.connect(self._toggle_underline)
        
        self._toolbar.addSeparator()
        
        self._font_size_combo = QComboBox()
        self._font_size_combo.setFixedWidth(60)
        self._font_size_combo.addItems(["8", "9", "10", "12", "14", "16", "18", "20", "24", "28", "32"])
        self._font_size_combo.setCurrentText("12")
        self._font_size_combo.setToolTip(_tr("font_size"))
        self._font_size_combo.currentTextChanged.connect(self._change_font_size)
        self._toolbar.addWidget(self._font_size_combo)
        
        self._toolbar.addSeparator()
        
        self._h1_btn = self._toolbar.addAction("H1")
        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(18)
        self._h1_btn.setFont(h1_font)
        self._h1_btn.setToolTip(_tr("heading1"))
        self._h1_btn.triggered.connect(self._insert_h1)
        
        self._h2_btn = self._toolbar.addAction("H2")
        h2_font = QFont()
        h2_font.setBold(True)
        h2_font.setPointSize(16)
        self._h2_btn.setFont(h2_font)
        self._h2_btn.setToolTip(_tr("heading2"))
        self._h2_btn.triggered.connect(self._insert_h2)
        
        self._h3_btn = self._toolbar.addAction("H3")
        h3_font = QFont()
        h3_font.setBold(True)
        h3_font.setPointSize(14)
        self._h3_btn.setFont(h3_font)
        self._h3_btn.setToolTip(_tr("heading3"))
        self._h3_btn.triggered.connect(self._insert_h3)
        
        self._toolbar.addSeparator()
        
        self._bullet_btn = self._toolbar.addAction("•")
        self._bullet_btn.setToolTip(_tr("bullet_list"))
        self._bullet_btn.triggered.connect(self._insert_bullet)
        
        self._toolbar.addSeparator()
        
        self._text_color_btn = self._toolbar.addAction("A")
        self._text_color_btn.setToolTip(_tr("text_color"))
        self._text_color_btn.triggered.connect(self._change_text_color)
        
        self._highlight_btn = self._toolbar.addAction("█")
        self._highlight_btn.setToolTip(_tr("highlight"))
        self._highlight_btn.triggered.connect(self._change_highlight)
        
        self._toolbar.addSeparator()
        
        self._link_btn = self._toolbar.addAction("[Link]")
        self._link_btn.setToolTip(_tr("insert_link") + " (Ctrl+K)")
        self._link_btn.triggered.connect(self._insert_link)
        
        self._code_btn = self._toolbar.addAction("[Code]")
        self._code_btn.setToolTip(_tr("insert_code"))
        self._code_btn.triggered.connect(self._insert_code)
        
        self._quote_btn = self._toolbar.addAction("[Quote]")
        self._quote_btn.setToolTip(_tr("insert_quote"))
        self._quote_btn.triggered.connect(self._insert_quote)
        
        self._content_edit = SpellCheckTextEdit()
        self._content_edit.setPlaceholderText(_tr("beat_content_placeholder"))
        self._content_edit.setMinimumHeight(200)
        
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
    
    def _toggle_bold(self) -> None:
        self._apply_format("bold")
    
    def _toggle_italic(self) -> None:
        self._apply_format("italic")
    
    def _toggle_underline(self) -> None:
        self._apply_format("underline")
    
    def _change_font_size(self, size: str) -> None:
        try:
            font_size = int(size)
        except ValueError:
            return
        
        cursor = self._content_edit.textCursor()
        
        if cursor.hasSelection():
            char_format = cursor.charFormat()
            char_format.setFontPointSize(font_size)
            cursor.setCharFormat(char_format)
            self._content_edit.setTextCursor(cursor)
        else:
            self._content_edit.setFontPointSize(font_size)
    
    def _insert_h1(self) -> None:
        self._insert_heading(1)
    
    def _insert_h2(self) -> None:
        self._insert_heading(2)
    
    def _insert_h3(self) -> None:
        self._insert_heading(3)
    
    def _insert_heading(self, level: int) -> None:
        cursor = self._content_edit.textCursor()
        selected_text = cursor.selectedText()
        
        sizes = {1: 24, 2: 20, 3: 18}
        size = sizes.get(level, 18)
        
        if selected_text:
            html = f'<h{level} style="font-size: {size}px; margin: 10px 0 5px 0;">{selected_text}</h{level}>'
            cursor.insertHtml(html)
        else:
            html = f'<h{level} style="font-size: {size}px; margin: 10px 0 5px 0;">Título {level}</h{level}>'
            cursor.insertHtml(html)
    
    def _apply_format(self, format_type: str) -> None:
        cursor = self._content_edit.textCursor()
        if not cursor.hasSelection():
            return
        
        char_format = cursor.charFormat()
        
        if format_type == "bold":
            current_weight = char_format.fontWeight()
            new_weight = 75 if current_weight < 75 else 50
            char_format.setFontWeight(new_weight)
        elif format_type == "italic":
            char_format.setFontItalic(not char_format.fontItalic())
        elif format_type == "underline":
            char_format.setFontUnderline(not char_format.fontUnderline())
        
        cursor.setCharFormat(char_format)
        self._content_edit.setTextCursor(cursor)
    
    def _insert_bullet(self) -> None:
        cursor = self._content_edit.textCursor()
        cursor.insertText("• ")
    
    def _change_text_color(self) -> None:
        cursor = self._content_edit.textCursor()
        current_color = cursor.charFormat().foreground().color()
        color = QColorDialog.getColor(current_color, self, _tr("text_color_dialog"))
        if color.isValid():
            char_format = cursor.charFormat()
            char_format.setForeground(color)
            cursor.setCharFormat(char_format)
            self._content_edit.setTextCursor(cursor)
    
    def _change_highlight(self) -> None:
        cursor = self._content_edit.textCursor()
        current_color = cursor.charFormat().background().color()
        color = QColorDialog.getColor(current_color, self, _tr("highlight_color_dialog"))
        if color.isValid():
            char_format = cursor.charFormat()
            char_format.setBackground(color)
            cursor.setCharFormat(char_format)
            self._content_edit.setTextCursor(cursor)
    
    def _insert_link(self) -> None:
        cursor = self._content_edit.textCursor()
        selected_text = cursor.selectedText()
        
        link, ok = QInputDialog.getText(self, _tr("insert_link_title"), _tr("link_url"))
        if ok and link:
            if selected_text:
                cursor.insertHtml(f'<a href="{link}">{selected_text}</a>')
            else:
                cursor.insertHtml(f'<a href="{link}">{link}</a>')
    
    def _insert_code(self) -> None:
        cursor = self._content_edit.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            cursor.insertHtml(f'<code style="background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; font-family: monospace;">{selected_text}</code>')
        else:
            cursor.insertHtml('<code style="background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; font-family: monospace;">código</code>')
    
    def _insert_quote(self) -> None:
        cursor = self._content_edit.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            cursor.insertHtml(f'<blockquote style="border-left: 3px solid #ccc; padding-left: 10px; margin-left: 0; color: #666; font-style: italic;">{selected_text}</blockquote>')
        else:
            cursor.insertHtml('<blockquote style="border-left: 3px solid #ccc; padding-left: 10px; margin-left: 0; color: #666; font-style: italic;">Cita</blockquote>')
    
    def get_beat_data(self) -> tuple[str, str, str]:
        title = self._title_edit.toPlainText()
        content = self._content_edit.toHtml()
        color = self._color_widget.get_selected_color()
        return title, content, color


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