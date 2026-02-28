"""SpellCheck highlighter for QTextEdit."""

import re
from typing import Optional

from PySide6.QtCore import QObject, QPoint, Qt
from PySide6.QtGui import QTextCharFormat, QSyntaxHighlighter, QTextCursor, QTextDocument, QAction
from PySide6.QtWidgets import QApplication, QTextEdit, QMenu, QWidget

from beatboard.services.spellcheck_service import SpellCheckService


class SpellCheckHighlighter(QSyntaxHighlighter):
    """Highlighter para spellcheck que subraya palabras mal escritas."""
    
    def __init__(self, document: QTextDocument, spell_service: Optional[SpellCheckService] = None):
        super().__init__(document)
        self._spell_service = spell_service or SpellCheckService.instance()
        self._enabled = True
        self._word_pattern = re.compile(r"\b[\w']+\b")
    
    def set_enabled(self, enabled: bool) -> None:
        """Activa/desactiva el highlighter."""
        self._enabled = enabled
        self.rehighlight()
    
    def is_enabled(self) -> bool:
        """Retorna si el highlighter está activo."""
        return self._enabled
    
    def set_spell_service(self, service: SpellCheckService) -> None:
        """Actualiza el servicio de spellcheck."""
        self._spell_service = service
        self.rehighlight()
    
    def highlightBlock(self, text: str) -> None:
        """Procesa cada bloque de texto y subraya errores."""
        if not self._enabled:
            return
        
        if not self._spell_service or not self._spell_service.is_enabled():
            return
        
        if not self._spell_service.is_available:
            return
        
        error_format = QTextCharFormat()
        error_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
        error_format.setUnderlineColor(Qt.GlobalColor.red)
        
        for match in self._word_pattern.finditer(text):
            word = match.group()
            start = match.start()
            end = match.end()
            
            if not self._spell_service.check_word(word):
                self.setFormat(start, end - start, error_format)


class SpellCheckTextEdit(QTextEdit):
    """QTextEdit con spellcheck integrado."""
    
    def __init__(self, parent: Optional[QWidget] = None, spell_service: Optional[SpellCheckService] = None):
        super().__init__(parent)
        self._spell_service = spell_service or SpellCheckService.instance()
        self._highlighter = SpellCheckHighlighter(self.document(), self._spell_service)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def set_spellcheck_enabled(self, enabled: bool) -> None:
        """Activa/desactiva el spellcheck."""
        self._highlighter.set_enabled(enabled)
    
    def set_spell_service(self, service: SpellCheckService) -> None:
        """Actualiza el servicio de spellcheck."""
        self._spell_service = service
        self._highlighter.set_spell_service(service)
    
    def _show_context_menu(self, pos: QPoint) -> None:
        """Maneja el menú contextual para correcciones."""
        cursor = self.cursorForPosition(pos)
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        
        menu = self.createStandardContextMenu()
        
        if not word:
            menu.exec(self.mapToGlobal(pos))
            return
        
        word_start = cursor.selectionStart()
        word_end = cursor.selectionEnd()
        
        is_enabled = self._spell_service.is_enabled()
        is_available = self._spell_service.is_available
        
        if is_enabled and is_available:
            is_misspelled = not self._spell_service.check_word(word)
            
            if is_misspelled:
                menu.addSeparator()
                
                add_action = QAction("Añadir al diccionario", menu)
                add_action.triggered.connect(lambda: self._add_to_user_dict(word))
                menu.addAction(add_action)
                
                suggestions = self._spell_service.get_suggestions(word)
                if suggestions:
                    menu.addSeparator()
                    for suggestion in suggestions[:5]:
                        action = QAction(suggestion, menu)
                        action.triggered.connect(
                            lambda checked, s=suggestion: self._replace_word_at(s, word_start, word_end)
                        )
                        menu.addAction(action)
        
        menu.exec(self.mapToGlobal(pos))
    
    def _add_to_user_dict(self, word: str) -> None:
        """Añade la palabra al diccionario del usuario."""
        self._spell_service.add_to_user_dict(word)
        self._highlighter.rehighlight()
    
    def _replace_word_at(self, replacement: str, start: int, end: int) -> None:
        """Reemplaza la palabra por la sugerencia."""
        cursor = self.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(replacement)
