"""Properties panel widget for editing selected beats."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from beatboard.core.beat import Beat
from beatboard.core.constants import BEAT_COLORS
from beatboard.i18n import _tr
from beatboard.services.spellcheck_service import SpellCheckService
from beatboard.ui.widgets.spellcheck_highlighter import SpellCheckTextEdit

if TYPE_CHECKING:
    pass


class PropertiesPanel(QWidget):
    beat_updated = Signal(str, str, str, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._current_beat: Beat | None = None
        self._updating = False
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        self.setMinimumWidth(280)
        self.setMaximumWidth(350)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        title_label = QLabel(_tr("beat_properties"))
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        main_layout.addSpacing(10)
        
        self._no_selection_label = QLabel(_tr("no_beat_selected"))
        self._no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_selection_label.setStyleSheet("color: gray; padding: 20px;")
        main_layout.addWidget(self._no_selection_label)
        
        self._properties_widget = QWidget()
        self._properties_widget.setVisible(False)
        main_layout.addWidget(self._properties_widget)
        
        props_layout = QVBoxLayout(self._properties_widget)
        props_layout.setContentsMargins(0, 0, 0, 0)
        props_layout.setSpacing(10)
        
        title_field = self._create_field(_tr("title"))
        self._title_input = title_field["input"]
        props_layout.addLayout(title_field["layout"])
        
        color_field = self._create_color_field(_tr("color"))
        self._color_combo = color_field["combo"]
        self._color_labels = color_field["labels"]
        props_layout.addLayout(color_field["layout"])
        
        content_label = QLabel(_tr("content"))
        content_label.setStyleSheet("font-weight: bold;")
        props_layout.addWidget(content_label)
        
        self._content_input = SpellCheckTextEdit()
        self._content_input.setPlaceholderText(_tr("content_placeholder"))
        self._content_input.setMinimumHeight(150)
        self._content_input.textChanged.connect(self._on_content_changed)
        props_layout.addWidget(self._content_input)
        
        main_layout.addStretch()
        
        info_label = QLabel(_tr("tip_double_click"))
        info_label.setStyleSheet("color: gray; font-size: 11px; padding: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)
    
    def _create_field(self, label_text: str) -> dict:
        layout = QVBoxLayout()
        layout.setSpacing(4)
        
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        input_field = SpellCheckTextEdit()
        input_field.setPlaceholderText(_tr("title_placeholder"))
        input_field.setMaximumHeight(30)
        input_field.textChanged.connect(self._on_title_changed)
        layout.addWidget(input_field)
        
        return {"layout": layout, "input": input_field, "label": label}
    
    def _create_color_field(self, label_text: str) -> dict:
        layout = QVBoxLayout()
        layout.setSpacing(4)
        
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)
        
        combo = QComboBox()
        combo.setMinimumWidth(150)
        
        color_labels = {}
        for color_key, color_value in BEAT_COLORS.items():
            color_labels[color_key] = color_key.capitalize()
            combo.addItem(color_key.capitalize(), color_key)
        
        combo.currentIndexChanged.connect(self._on_color_changed)
        layout.addWidget(combo)
        
        return {"layout": layout, "combo": combo, "labels": color_labels}
    
    def set_beat(self, beat: Beat | None) -> None:
        self._current_beat = beat
        self._updating = True
        
        if beat is None:
            self._no_selection_label.setVisible(True)
            self._properties_widget.setVisible(False)
        else:
            self._no_selection_label.setVisible(False)
            self._properties_widget.setVisible(True)
            
            self._title_input.setPlainText(beat.title or "")
            
            content = beat.content or ""
            if content and "<" in content and ">" in content:
                self._content_input.setHtml(content)
            else:
                self._content_input.setPlainText(content)
            
            index = self._color_combo.findData(beat.color)
            if index >= 0:
                self._color_combo.setCurrentIndex(index)
        
        self._updating = False
    
    def _on_title_changed(self) -> None:
        if self._updating or not self._current_beat:
            return
        
        title = self._title_input.toPlainText()
        self._current_beat.title = title
        self.beat_updated.emit(
            self._current_beat.id,
            self._current_beat.title,
            self._current_beat.content,
            self._current_beat.color
        )
    
    def _on_content_changed(self) -> None:
        if self._updating or not self._current_beat:
            return
        
        content = self._content_input.toPlainText()
        self._current_beat.content = content
        self.beat_updated.emit(
            self._current_beat.id,
            self._current_beat.title,
            self._current_beat.content,
            self._current_beat.color
        )
    
    def _on_color_changed(self, index: int) -> None:
        if self._updating or not self._current_beat:
            return
        
        color_key = self._color_combo.itemData(index)
        self._current_beat.color = color_key
        self.beat_updated.emit(
            self._current_beat.id,
            self._current_beat.title,
            self._current_beat.content,
            self._current_beat.color
        )
    
    def clear(self) -> None:
        self.set_beat(None)
