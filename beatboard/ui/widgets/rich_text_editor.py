"""Rich text editor widget with enhanced formatting toolbar."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QFont, QTextCharFormat, QTextCursor, QDropEvent, QDragEnterEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFontComboBox,
    QHBoxLayout,
    QMessageBox,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from beatboard.i18n import _tr
from beatboard.ui.widgets.spellcheck_highlighter import SpellCheckTextEdit


class RichTextEditor(QWidget):
    """Enhanced rich text editor with full formatting toolbar."""

    content_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._image_insert_callback = None
        self._image_path_map = {}  # file_path -> relative_path
        self._reverse_image_map = {}  # relative_path -> file_path
        self._setup_ui()
        self._setup_connections()

    def _get_editor_icon(self, icon_name: str) -> "QIcon":
        from PySide6.QtGui import QIcon
        from pathlib import Path
        from PySide6.QtWidgets import QApplication
        
        base_path = Path(__file__).parent.parent.parent / "ui" / "icons"
        
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

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._toolbar = QToolBar()
        self._toolbar.setMovable(False)
        layout.addWidget(self._toolbar)

        self._font_combo = QFontComboBox()
        self._font_combo.setFixedWidth(150)
        self._font_combo.setToolTip(_tr("font_family"))
        self._toolbar.addWidget(self._font_combo)

        self._font_size_combo = QComboBox()
        self._font_size_combo.setFixedWidth(60)
        self._font_size_combo.addItems(["8", "9", "10", "12", "14", "16", "18", "20", "24", "28", "32", "36", "48"])
        self._font_size_combo.setCurrentText("12")
        self._font_size_combo.setToolTip(_tr("font_size"))
        self._toolbar.addWidget(self._font_size_combo)

        self._toolbar.addSeparator()

        self._bold_btn = self._toolbar.addAction("B")
        bold_font = QFont()
        bold_font.setBold(True)
        self._bold_btn.setFont(bold_font)
        self._bold_btn.setToolTip(_tr("bold") + " (Ctrl+B)")
        self._bold_btn.setCheckable(True)

        self._italic_btn = self._toolbar.addAction("I")
        italic_font = QFont()
        italic_font.setItalic(True)
        self._italic_btn.setFont(italic_font)
        self._italic_btn.setToolTip(_tr("italic") + " (Ctrl+I)")
        self._italic_btn.setCheckable(True)

        self._underline_btn = self._toolbar.addAction("U")
        underline_font = QFont()
        underline_font.setUnderline(True)
        self._underline_btn.setFont(underline_font)
        self._underline_btn.setToolTip(_tr("underline") + " (Ctrl+U)")
        self._underline_btn.setCheckable(True)

        self._toolbar.addSeparator()

        self._align_left_btn = self._toolbar.addAction("⬅")
        self._align_left_btn.setToolTip(_tr("align_left"))
        self._align_left_btn.setCheckable(True)

        self._align_center_btn = self._toolbar.addAction("⬌")
        self._align_center_btn.setToolTip(_tr("align_center"))
        self._align_center_btn.setCheckable(True)

        self._align_right_btn = self._toolbar.addAction("➡")
        self._align_right_btn.setToolTip(_tr("align_right"))
        self._align_right_btn.setCheckable(True)

        self._align_justify_btn = self._toolbar.addAction("☰")
        self._align_justify_btn.setToolTip(_tr("align_justify"))
        self._align_justify_btn.setCheckable(True)

        self._toolbar.addSeparator()

        self._h1_btn = self._toolbar.addAction("H1")
        h1_font = QFont()
        h1_font.setBold(True)
        h1_font.setPointSize(18)
        self._h1_btn.setFont(h1_font)
        self._h1_btn.setToolTip(_tr("heading1"))

        self._h2_btn = self._toolbar.addAction("H2")
        h2_font = QFont()
        h2_font.setBold(True)
        h2_font.setPointSize(16)
        self._h2_btn.setFont(h2_font)
        self._h2_btn.setToolTip(_tr("heading2"))

        self._h3_btn = self._toolbar.addAction("H3")
        h3_font = QFont()
        h3_font.setBold(True)
        h3_font.setPointSize(14)
        self._h3_btn.setFont(h3_font)
        self._h3_btn.setToolTip(_tr("heading3"))

        self._toolbar.addSeparator()

        self._bullet_btn = self._toolbar.addAction("•")
        self._bullet_btn.setToolTip(_tr("bullet_list"))

        self._number_btn = self._toolbar.addAction("1.")
        self._number_btn.setToolTip(_tr("numbered_list"))

        self._toolbar.addSeparator()

        self._link_btn = self._toolbar.addAction("[Link]")
        self._link_btn.setToolTip(_tr("insert_link") + " (Ctrl+K)")

        self._code_btn = self._toolbar.addAction("[Code]")
        self._code_btn.setToolTip(_tr("insert_code"))

        self._quote_btn = self._toolbar.addAction("[Quote]")
        self._quote_btn.setToolTip(_tr("insert_quote"))

        self._clear_format_btn = self._toolbar.addAction(self._get_editor_icon("noformat"), "")
        self._clear_format_btn.setToolTip(_tr("clear_format"))

        self._toolbar.addSeparator()

        self._image_btn = self._toolbar.addAction(self._get_editor_icon("image"), "")
        self._image_btn.setToolTip(_tr("insert_image"))

        self._toolbar.addSeparator()

        self._markdown_btn = self._toolbar.addAction(self._get_editor_icon("markdown"), "")
        self._markdown_btn.setToolTip(_tr("toggle_markdown"))
        self._markdown_btn.setCheckable(True)

        self._text_edit = RichTextEdit(self)
        self._is_markdown_mode = False
        layout.addWidget(self._text_edit)

    def _setup_connections(self) -> None:
        self._font_combo.currentFontChanged.connect(self._change_font)
        self._font_size_combo.currentTextChanged.connect(self._change_font_size)

        self._bold_btn.triggered.connect(self._toggle_bold)
        self._italic_btn.triggered.connect(self._toggle_italic)
        self._underline_btn.triggered.connect(self._toggle_underline)

        self._align_left_btn.triggered.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignLeft))
        self._align_center_btn.triggered.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignCenter))
        self._align_right_btn.triggered.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignRight))
        self._align_justify_btn.triggered.connect(lambda: self._set_alignment(Qt.AlignmentFlag.AlignJustify))

        self._h1_btn.triggered.connect(lambda: self._insert_heading(1))
        self._h2_btn.triggered.connect(lambda: self._insert_heading(2))
        self._h3_btn.triggered.connect(lambda: self._insert_heading(3))

        self._bullet_btn.triggered.connect(self._insert_bullet)
        self._number_btn.triggered.connect(self._insert_numbered)

        self._link_btn.triggered.connect(self._insert_link)
        self._code_btn.triggered.connect(self._insert_code)
        self._quote_btn.triggered.connect(self._insert_quote)

        self._clear_format_btn.triggered.connect(self._clear_format)

        self._image_btn.triggered.connect(self._insert_image)

        self._markdown_btn.triggered.connect(self._toggle_markdown_mode)

        self._saved_html = ""
        self._saved_markdown = ""

        self._text_edit.textChanged.connect(self._on_text_changed)
        self._text_edit.cursorPositionChanged.connect(self._update_toolbar_state)

    def _change_font(self, font: QFont) -> None:
        cursor = self._text_edit.textCursor()
        if cursor.hasSelection():
            char_format = cursor.charFormat()
            char_format.setFont(font)
            cursor.setCharFormat(char_format)
            self._text_edit.setTextCursor(cursor)
        else:
            self._text_edit.setCurrentFont(font)

    def _change_font_size(self, size: str) -> None:
        try:
            font_size = int(size)
        except ValueError:
            return

        cursor = self._text_edit.textCursor()
        if cursor.hasSelection():
            char_format = cursor.charFormat()
            char_format.setFontPointSize(font_size)
            cursor.setCharFormat(char_format)
            self._text_edit.setTextCursor(cursor)
        else:
            self._text_edit.setFontPointSize(font_size)

    def _toggle_bold(self) -> None:
        cursor = self._text_edit.textCursor()
        char_format = cursor.charFormat()
        current_weight = char_format.fontWeight()
        new_weight = QFont.Weight.Bold if current_weight < QFont.Weight.Bold else QFont.Weight.Normal
        char_format.setFontWeight(new_weight)
        cursor.setCharFormat(char_format)
        self._text_edit.setTextCursor(cursor)

    def _toggle_italic(self) -> None:
        cursor = self._text_edit.textCursor()
        char_format = cursor.charFormat()
        char_format.setFontItalic(not char_format.fontItalic())
        cursor.setCharFormat(char_format)
        self._text_edit.setTextCursor(cursor)

    def _toggle_underline(self) -> None:
        cursor = self._text_edit.textCursor()
        char_format = cursor.charFormat()
        char_format.setFontUnderline(not char_format.fontUnderline())
        cursor.setCharFormat(char_format)
        self._text_edit.setTextCursor(cursor)

    def _set_alignment(self, alignment: Qt.AlignmentFlag) -> None:
        self._text_edit.setAlignment(alignment)
        self._update_alignment_buttons(alignment)

    def _update_alignment_buttons(self, alignment: Qt.AlignmentFlag) -> None:
        self._align_left_btn.setChecked(alignment == Qt.AlignmentFlag.AlignLeft)
        self._align_center_btn.setChecked(alignment == Qt.AlignmentFlag.AlignCenter)
        self._align_right_btn.setChecked(alignment == Qt.AlignmentFlag.AlignRight)
        self._align_justify_btn.setChecked(alignment == Qt.AlignmentFlag.AlignJustify)

    def _insert_heading(self, level: int) -> None:
        cursor = self._text_edit.textCursor()
        selected_text = cursor.selectedText()

        sizes = {1: 24, 2: 20, 3: 18}
        size = sizes.get(level, 18)

        if selected_text:
            html = f'<h{level} style="font-size: {size}px; margin: 10px 0 5px 0;">{selected_text}</h{level}>'
            cursor.insertHtml(html)
        else:
            html = f'<h{level} style="font-size: {size}px; margin: 10px 0 5px 0;">Título {level}</h{level}>'
            cursor.insertHtml(html)

    def _insert_bullet(self) -> None:
        cursor = self._text_edit.textCursor()
        cursor.insertText("• ")

    def _insert_numbered(self) -> None:
        cursor = self._text_edit.textCursor()
        cursor.insertText("1. ")

    def _insert_link(self) -> None:
        from PySide6.QtWidgets import QInputDialog
        cursor = self._text_edit.textCursor()
        selected_text = cursor.selectedText()

        link, ok = QInputDialog.getText(self, _tr("insert_link_title"), _tr("link_url"))
        if ok and link:
            if selected_text:
                cursor.insertHtml(f'<a href="{link}">{selected_text}</a>')
            else:
                cursor.insertHtml(f'<a href="{link}">{link}</a>')

    def _insert_code(self) -> None:
        cursor = self._text_edit.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            cursor.insertHtml(f'<code style="background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; font-family: monospace;">{selected_text}</code>')
        else:
            cursor.insertHtml('<code style="background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px; font-family: monospace;">código</code>')

    def _insert_quote(self) -> None:
        cursor = self._text_edit.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            cursor.insertHtml(f'<blockquote style="border-left: 3px solid #ccc; padding-left: 10px; margin-left: 0; color: #666; font-style: italic;">{selected_text}</blockquote>')
        else:
            cursor.insertHtml('<blockquote style="border-left: 3px solid #ccc; padding-left: 10px; margin-left: 0; color: #666; font-style: italic;">Cita</blockquote>')

    def _clear_format(self) -> None:
        cursor = self._text_edit.textCursor()
        if cursor.hasSelection():
            char_format = QTextCharFormat()
            cursor.setCharFormat(char_format)
            self._text_edit.setTextCursor(cursor)

    def _insert_image(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            _tr("insert_image"),
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp)"
        )
        if file_path:
            self._text_edit.insert_image(file_path)

    def _on_text_changed(self) -> None:
        self.content_changed.emit()

    def _toggle_markdown_mode(self) -> None:
        import markdown

        self._is_markdown_mode = not self._is_markdown_mode
        self._markdown_btn.setChecked(self._is_markdown_mode)

        if self._is_markdown_mode:
            self._saved_html = self._text_edit.toHtml()
            md = self._html_to_markdown(self._saved_html)
            self._saved_markdown = md
            self._text_edit.setPlainText(md)
        else:
            self._saved_markdown = self._text_edit.toPlainText()
            md_content = self._text_edit.toPlainText()
            html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite', 'tables'])
            self._saved_html = html_content
            self._text_edit.setHtml(html_content)

    def _html_to_markdown(self, html: str) -> str:
        import re
        md = html
        
        md = re.sub(r'<style[^>]*>.*?</style>', '', md, flags=re.DOTALL | re.IGNORECASE)
        
        md = re.sub(r'<html[^>]*>', '', md, flags=re.IGNORECASE)
        md = re.sub(r'</html>', '', md, flags=re.IGNORECASE)
        md = re.sub(r'<head[^>]*>.*?</head>', '', md, flags=re.DOTALL | re.IGNORECASE)
        md = re.sub(r'<body[^>]*>', '', md, flags=re.IGNORECASE)
        md = re.sub(r'</body>', '', md, flags=re.IGNORECASE)
        md = re.sub(r'<meta[^>]*>', '', md, flags=re.IGNORECASE)
        md = re.sub(r'<!DOCTYPE[^>]*>', '', md, flags=re.IGNORECASE)
        md = re.sub(r'<!--.*?-->', '', md, flags=re.DOTALL)
        md = re.sub(r'<p[^>]*>', '', md, flags=re.IGNORECASE)
        md = re.sub(r'</p>', '\n', md, flags=re.IGNORECASE)
        
        md = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', md, flags=re.DOTALL)
        md = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', md, flags=re.DOTALL)
        md = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', md, flags=re.DOTALL)
        md = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1\n', md, flags=re.DOTALL)
        
        md = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', md, flags=re.DOTALL)
        md = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', md, flags=re.DOTALL)
        md = re.sub(r'<span[^>]*font-weight:\s*700[^>]*>(.*?)</span>', r'**\1**', md, flags=re.DOTALL | re.IGNORECASE)
        md = re.sub(r'<span[^>]*font-weight:\s*bold[^>]*>(.*?)</span>', r'**\1**', md, flags=re.DOTALL | re.IGNORECASE)
        
        md = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', md, flags=re.DOTALL)
        md = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', md, flags=re.DOTALL)
        md = re.sub(r'<span[^>]*font-style:\s*italic[^>]*>(.*?)</span>', r'*\1*', md, flags=re.DOTALL | re.IGNORECASE)
        
        md = re.sub(r'<u[^>]*>(.*?)</u>', r'_\1_', md, flags=re.DOTALL)
        md = re.sub(r'<span[^>]*text-decoration:\s*underline[^>]*>(.*?)</span>', r'_\1_', md, flags=re.DOTALL | re.IGNORECASE)
        
        md = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', md, flags=re.DOTALL)
        md = re.sub(r'<span[^>]*font-family:\s*monospace[^>]*>(.*?)</span>', r'`\1`', md, flags=re.DOTALL | re.IGNORECASE)
        md = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```', md, flags=re.DOTALL)
        
        md = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', md, flags=re.DOTALL)
        
        md = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1\n', md, flags=re.DOTALL)
        
        md = re.sub(r'<ul[^>]*>', '', md, flags=re.IGNORECASE)
        md = re.sub(r'</ul>', '\n', md, flags=re.IGNORECASE)
        md = re.sub(r'<ol[^>]*>', '', md, flags=re.IGNORECASE)
        md = re.sub(r'</ol>', '\n', md, flags=re.IGNORECASE)
        md = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1\n', md, flags=re.DOTALL)
        
        md = re.sub(r'<div[^>]*>(.*?)</div>', r'\1\n', md, flags=re.DOTALL)
        md = re.sub(r'<br\s*/?>', '\n', md)
        md = re.sub(r'<hr\s*/?>', '\n---\n', md)
        
        md = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', md, flags=re.DOTALL)
        
        md = re.sub(r'<[^>]+>', '', md)
        
        md = re.sub(r'&nbsp;', ' ', md)
        md = re.sub(r'&amp;', '&', md)
        md = re.sub(r'&lt;', '<', md)
        md = re.sub(r'&gt;', '>', md)
        md = re.sub(r'&quot;', '"', md)
        
        md = re.sub(r'\n{3,}', '\n\n', md)
        
        return md.strip()

    def _update_toolbar_state(self) -> None:
        cursor = self._text_edit.textCursor()
        char_format = cursor.charFormat()

        self._bold_btn.setChecked(char_format.fontWeight() == QFont.Weight.Bold)
        self._italic_btn.setChecked(char_format.fontItalic())
        self._underline_btn.setChecked(char_format.fontUnderline())

        self._update_alignment_buttons(self._text_edit.alignment())



    def setPlainText(self, text: str) -> None:
        self._text_edit.setPlainText(text)

    def toPlainText(self) -> str:
        return self._text_edit.toPlainText()

    def setMarkdown(self, md: str) -> None:
        self._text_edit.setMarkdown(md)

    def toMarkdown(self) -> str:
        return self._text_edit.toMarkdown()

    def setPlaceholderText(self, text: str) -> None:
        self._text_edit.setPlaceholderText(text)

    def setMinimumHeight(self, height: int) -> None:
        self._text_edit.setMinimumHeight(height)

    def set_spellcheck_enabled(self, enabled: bool) -> None:
        self._text_edit.set_spellcheck_enabled(enabled)

    def get_content_mode(self) -> str:
        return "markdown" if self._is_markdown_mode else "html"

    def get_content(self) -> str:
        if self._is_markdown_mode:
            return self._text_edit.toPlainText()
        return self._text_edit.toHtml()

    def get_saved_markdown(self) -> str:
        return self._saved_markdown

    def set_saved_markdown(self, md: str) -> None:
        self._saved_markdown = md

    def set_content_mode(self, mode: str) -> None:
        if mode == "markdown" and not self._is_markdown_mode:
            self._toggle_markdown_mode()
        elif mode == "html" and self._is_markdown_mode:
            self._toggle_markdown_mode()

    def set_image_insert_callback(self, callback) -> None:
        self._image_insert_callback = callback
    
    def set_image_path_map(self, path_map: dict) -> None:
        """Set mapping between absolute paths and relative paths."""
        self._image_path_map = path_map.copy()
        self._reverse_image_map = {v: k for k, v in path_map.items() if v}
    
    def register_image_mapping(self, file_path: str, relative_path: str) -> None:
        """Register a mapping between absolute and relative path."""
        self._image_path_map[file_path] = relative_path
        self._reverse_image_map[relative_path] = file_path
    
    def _convert_html_paths(self, html: str, to_relative: bool = False) -> str:
        """Convert image paths in HTML between absolute and relative."""
        import re
        
        def replace_path(match):
            src = match.group(1)
            if to_relative:
                # Convert absolute to relative
                for abs_path, rel_path in self._image_path_map.items():
                    if src == abs_path or src.startswith('file://') and src[7:] == abs_path:
                        return f'src="{rel_path}"'
            else:
                # Convert relative to absolute
                if src in self._reverse_image_map:
                    abs_path = self._reverse_image_map[src]
                    return f'src="{abs_path}"'
            return match.group(0)
        
        # Replace src="..." attributes
        html = re.sub(r'src="([^"]+)"', replace_path, html)
        return html
    
    def setHtml(self, html: str) -> None:
        """Set HTML content, converting relative paths to absolute for display."""
        if self._reverse_image_map:
            html = self._convert_html_paths(html, to_relative=False)
        self._text_edit.setHtml(html)
    
    def toHtml(self) -> str:
        """Get HTML content, converting absolute paths to relative for storage."""
        html = self._text_edit.toHtml()
        if self._image_path_map:
            html = self._convert_html_paths(html, to_relative=True)
        return html

    def set_content_and_mode(self, content: str, content_markdown: str, mode: str) -> None:
        self._saved_html = content
        self._saved_markdown = content_markdown
        
        if mode == "markdown" and content_markdown:
            self._is_markdown_mode = True
            self._markdown_btn.setChecked(True)
            self._text_edit.setPlainText(content_markdown)
        else:
            self._is_markdown_mode = False
            self._markdown_btn.setChecked(False)
            if "<" in content:
                self._text_edit.setHtml(content)
            else:
                self._text_edit.setPlainText(content)


class RichTextEdit(SpellCheckTextEdit):
    """TextEdit with image drag & drop support."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if eventMimeData := event.mimeData():
            if eventMimeData.hasUrls():
                urls = eventMimeData.urls()
                if urls and self._is_image_url(urls[0]):
                    event.acceptProposedAction()
                    return
        super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if eventMimeData := event.mimeData():
            if eventMimeData.hasUrls():
                urls = eventMimeData.urls()
                if urls and self._is_image_url(urls[0]):
                    file_path = urls[0].toLocalFile()
                    self.insert_image(file_path)
                    event.acceptProposedAction()
                    return
        super().dropEvent(event)

    def _is_image_url(self, url) -> bool:
        from PySide6.QtCore import QUrl
        if not url.isLocalFile():
            return False
        local_path = url.toLocalFile().lower()
        return local_path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))

    def insert_image(self, file_path: str) -> None:
        from pathlib import Path
        from PySide6.QtGui import QPixmap, QImage, QTextImageFormat

        path = Path(file_path)
        if not path.exists():
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            return

        max_width = 400
        if pixmap.width() > max_width:
            pixmap = pixmap.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)

        from pathlib import Path
        abs_path = str(Path(file_path).absolute())
        
        relative_path = None
        parent = self.parent()
        if parent and hasattr(parent, '_image_insert_callback') and parent._image_insert_callback:
            relative_path = parent._image_insert_callback(file_path)
            if hasattr(parent, 'register_image_mapping'):
                parent.register_image_mapping(abs_path, relative_path)

        image_format = QTextImageFormat()
        image_format.setName(abs_path)
        image_format.setWidth(pixmap.width())
        image_format.setHeight(pixmap.height())

        cursor = self.textCursor()
        cursor.insertImage(image_format)
        self.setTextCursor(cursor)

    def mouseDoubleClickEvent(self, event):
        cursor = self.cursorForPosition(event.pos())
        char_format = cursor.charFormat()
        if char_format.isImageFormat():
            self._show_image_properties_dialog(cursor, char_format.toImageFormat())
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def _show_image_properties_dialog(self, cursor, image_format):
        from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
                                      QCheckBox, QDialogButtonBox)
        from PySide6.QtCore import Qt
        from beatboard.i18n import _tr
        dialog = QDialog(self)
        dialog.setWindowTitle(_tr('image_properties'))
        layout = QVBoxLayout(dialog)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel(_tr('width') + ':'))
        width_spin = QSpinBox()
        width_spin.setRange(1, 2000)
        width_spin.setValue(int(image_format.width()))
        size_layout.addWidget(width_spin)
        size_layout.addWidget(QLabel(_tr('height') + ':'))
        height_spin = QSpinBox()
        height_spin.setRange(1, 2000)
        height_spin.setValue(int(image_format.height()))
        size_layout.addWidget(height_spin)
        layout.addLayout(size_layout)
        
        keep_aspect = QCheckBox(_tr('keep_aspect_ratio'))
        keep_aspect.setChecked(True)
        layout.addWidget(keep_aspect)
        
        original_width = image_format.width()
        original_height = image_format.height()
        aspect_ratio = original_width / original_height if original_height != 0 else 1
        
        def update_height():
            if keep_aspect.isChecked():
                new_width = width_spin.value()
                new_height = int(new_width / aspect_ratio)
                height_spin.blockSignals(True)
                height_spin.setValue(new_height)
                height_spin.blockSignals(False)
        
        def update_width():
            if keep_aspect.isChecked():
                new_height = height_spin.value()
                new_width = int(new_height * aspect_ratio)
                width_spin.blockSignals(True)
                width_spin.setValue(new_width)
                width_spin.blockSignals(False)
        
        width_spin.valueChanged.connect(update_height)
        height_spin.valueChanged.connect(update_width)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_width = width_spin.value()
            new_height = height_spin.value()
            image_format.setWidth(new_width)
            image_format.setHeight(new_height)
            cursor.setCharFormat(image_format)
            self.setTextCursor(cursor)
            # Notificar cambio
            self.document().setModified(True)
            if hasattr(self.parent(), 'content_changed'):
                self.parent().content_changed.emit()
