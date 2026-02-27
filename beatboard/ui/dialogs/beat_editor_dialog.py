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
from beatboard.core.constants import BEAT_COLORS

if TYPE_CHECKING:
    pass


class BeatEditorDialog(QDialog):
    def __init__(self, beat: Beat, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._beat = beat
        self._original_color = beat.color
        
        self.setWindowTitle("Editar Beat")
        self.setMinimumSize(500, 450)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self._title_edit = QLineEdit()
        self._title_edit.setText(beat.title or "")
        self._title_edit.setPlaceholderText("Título del beat")
        form_layout.addRow("Título:", self._title_edit)
        
        layout.addLayout(form_layout)
        
        content_label = QLabel("Contenido:")
        content_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(content_label)
        
        self._toolbar = QToolBar()
        self._toolbar.setMovable(False)
        layout.addWidget(self._toolbar)
        
        self._bold_btn = self._toolbar.addAction("B")
        self._bold_btn.setToolTip("Negrita (Ctrl+B)")
        self._bold_btn.triggered.connect(self._toggle_bold)
        
        self._italic_btn = self._toolbar.addAction("I")
        italic_font = QFont()
        italic_font.setItalic(True)
        self._italic_btn.setFont(italic_font)
        self._italic_btn.setToolTip("Cursiva (Ctrl+I)")
        self._italic_btn.triggered.connect(self._toggle_italic)
        
        self._underline_btn = self._toolbar.addAction("U")
        underline_font = QFont()
        underline_font.setUnderline(True)
        self._underline_btn.setFont(underline_font)
        self._underline_btn.setToolTip("Subrayado (Ctrl+U)")
        self._underline_btn.triggered.connect(self._toggle_underline)
        
        self._toolbar.addSeparator()
        
        self._font_size_combo = QComboBox()
        self._font_size_combo.setFixedWidth(60)
        self._font_size_combo.addItems(["8", "9", "10", "12", "14", "16", "18", "20", "24", "28", "32"])
        self._font_size_combo.setCurrentText("12")
        self._font_size_combo.setToolTip("Tamaño de letra")
        self._font_size_combo.currentTextChanged.connect(self._change_font_size)
        self._toolbar.addWidget(self._font_size_combo)
        
        self._toolbar.addSeparator()
        
        self._h1_btn = self._toolbar.addAction("H1")
        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(18)
        self._h1_btn.setFont(h1_font)
        self._h1_btn.setToolTip("Título 1")
        self._h1_btn.triggered.connect(self._insert_h1)
        
        self._h2_btn = self._toolbar.addAction("H2")
        h2_font = QFont()
        h2_font.setBold(True)
        h2_font.setPointSize(16)
        self._h2_btn.setFont(h2_font)
        self._h2_btn.setToolTip("Título 2")
        self._h2_btn.triggered.connect(self._insert_h2)
        
        self._h3_btn = self._toolbar.addAction("H3")
        h3_font = QFont()
        h3_font.setBold(True)
        h3_font.setPointSize(14)
        self._h3_btn.setFont(h3_font)
        self._h3_btn.setToolTip("Título 3")
        self._h3_btn.triggered.connect(self._insert_h3)
        
        self._toolbar.addSeparator()
        
        self._bullet_btn = self._toolbar.addAction("•")
        self._bullet_btn.setToolTip("Viñetas")
        self._bullet_btn.triggered.connect(self._insert_bullet)
        
        self._toolbar.addSeparator()
        
        self._text_color_btn = self._toolbar.addAction("A")
        self._text_color_btn.setToolTip("Color de texto")
        self._text_color_btn.triggered.connect(self._change_text_color)
        
        self._highlight_btn = self._toolbar.addAction("█")
        self._highlight_btn.setToolTip("Resaltado")
        self._highlight_btn.triggered.connect(self._change_highlight)
        
        self._toolbar.addSeparator()
        
        self._link_btn = self._toolbar.addAction("[Link]")
        self._link_btn.setToolTip("Insertar enlace (Ctrl+K)")
        self._link_btn.triggered.connect(self._insert_link)
        
        self._code_btn = self._toolbar.addAction("[Code]")
        self._code_btn.setToolTip("Código")
        self._code_btn.triggered.connect(self._insert_code)
        
        self._quote_btn = self._toolbar.addAction("[Quote]")
        self._quote_btn.setToolTip("Cita")
        self._quote_btn.triggered.connect(self._insert_quote)
        
        self._content_edit = QTextEdit()
        self._content_edit.setPlaceholderText("Contenido del beat...")
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
        color = QColorDialog.getColor(current_color, self, "Color de texto")
        if color.isValid():
            char_format = cursor.charFormat()
            char_format.setForeground(color)
            cursor.setCharFormat(char_format)
            self._content_edit.setTextCursor(cursor)
    
    def _change_highlight(self) -> None:
        cursor = self._content_edit.textCursor()
        current_color = cursor.charFormat().background().color()
        color = QColorDialog.getColor(current_color, self, "Color de resaltado")
        if color.isValid():
            char_format = cursor.charFormat()
            char_format.setBackground(color)
            cursor.setCharFormat(char_format)
            self._content_edit.setTextCursor(cursor)
    
    def _insert_link(self) -> None:
        cursor = self._content_edit.textCursor()
        selected_text = cursor.selectedText()
        
        link, ok = QInputDialog.getText(self, "Insertar enlace", "URL:")
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
        title = self._title_edit.text()
        content = self._content_edit.toHtml()
        color = self._color_widget.get_selected_color()
        return title, content, color


class ColorPickerWidget(QWidget):
    def __init__(self, current_color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._selected_color = current_color
        
        layout = QVBoxLayout(self)
        
        label = QLabel("Color:")
        layout.addWidget(label)
        
        colors_layout = QHBoxLayout()
        
        for color_name, color_value in BEAT_COLORS.items():
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"background-color: {color_value.name()}; border: 1px solid #999; border-radius: 3px;")
            btn.setToolTip(color_name.capitalize())
            btn.clicked.connect(self._make_color_handler(color_name))
            colors_layout.addWidget(btn)
        
        colors_layout.addStretch()
        layout.addLayout(colors_layout)
        
        self._custom_btn = QPushButton("Más colores...")
        self._custom_btn.clicked.connect(self._select_custom_color)
        layout.addWidget(self._custom_btn)
    
    def _select_color(self, color_name: str) -> None:
        self._selected_color = color_name
    
    def _make_color_handler(self, color_name: str):
        def handler():
            self._selected_color = color_name
        return handler
    
    def _select_custom_color(self) -> None:
        current = BEAT_COLORS.get(self._selected_color, BEAT_COLORS["yellow"])
        color = QColorDialog.getColor(current, self, "Seleccionar color")
        if color.isValid():
            self._selected_color = color.name()
    
    def get_selected_color(self) -> str:
        return self._selected_color