"""Properties panel widget for editing selected beats."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
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
from beatboard.core.constants import (
    BEAT_PREDEFINED_COLORS,
    BEAT_PREDEFINED_NAMES,
    get_valid_beat_color,
)
from beatboard.i18n import _tr
from beatboard.services.spellcheck_service import SpellCheckService
from beatboard.ui.widgets.spellcheck_highlighter import SpellCheckTextEdit

if TYPE_CHECKING:
    pass


class PropertiesPanel(QWidget):
    beat_updated = Signal(str, str, str, str, bool)

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
        
        self._show_title_checkbox = QCheckBox(_tr("show_title"))
        self._show_title_checkbox.stateChanged.connect(self._on_show_title_changed)
        props_layout.addWidget(self._show_title_checkbox)
        
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
        
        # Mapeo de traducción de colores
        color_translation_keys = {
            "#FFF59D": "yellow",
            "#90CAF9": "blue",
            "#A5D6A7": "green",
            "#EF9A9A": "red",
            "#FFCC80": "orange",
            "#CE93D8": "purple",
            "#E0E0E0": "gray",
        }
        
        # Agregar colores predefinidos
        for i, hex_color in enumerate(BEAT_PREDEFINED_COLORS):
            color_key = color_translation_keys.get(hex_color, f"color_{i}")
            color_name = _tr(color_key)
            color_labels[hex_color] = color_name
            combo.addItem(color_name, hex_color)
        
        # Agregar colores personalizados (se actualizarán dinámicamente)
        self._update_custom_colors_in_combo(combo, color_labels)
        
        combo.currentIndexChanged.connect(self._on_color_changed)
        layout.addWidget(combo)
        
        return {"layout": layout, "combo": combo, "labels": color_labels}
    
    def _update_custom_colors_in_combo(self, combo: QComboBox, color_labels: dict) -> None:
        """Actualizar los colores personalizados en el combo box."""
        # Eliminar elementos de colores personalizados existentes (índices 7-9)
        while combo.count() > 7:
            combo.removeItem(7)
        
        # Obtener colores personalizados actuales
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        custom_colors = []
        if app and hasattr(app, 'theme_manager'):
            custom_colors = app.theme_manager.get_custom_colors()
        
        # Agregar colores personalizados actualizados
        for i, hex_color in enumerate(custom_colors):
            color_name = _tr("custom_color").format(num=i+1, color=hex_color)
            color_labels[hex_color] = color_name
            combo.addItem(color_name, hex_color)
    
    def set_beat(self, beat: Beat | None) -> None:
        self._current_beat = beat
        self._updating = True
        
        if beat is None:
            self._no_selection_label.setVisible(True)
            self._properties_widget.setVisible(False)
        else:
            self._no_selection_label.setVisible(False)
            self._properties_widget.setVisible(True)
            
            # Actualizar colores personalizados en el combo box
            self._update_custom_colors_in_combo(self._color_combo, self._color_labels)
            
            self._title_input.setPlainText(beat.title or "")
            
            content = beat.content or ""
            if content and "<" in content and ">" in content:
                self._content_input.setHtml(content)
            else:
                self._content_input.setPlainText(content)
            
            index = self._color_combo.findData(beat.color)
            if index >= 0:
                self._color_combo.setCurrentIndex(index)
            
            self._show_title_checkbox.blockSignals(True)
            self._show_title_checkbox.setChecked(beat.show_title)
            self._show_title_checkbox.blockSignals(False)
        
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
            self._current_beat.color,
            self._current_beat.show_title
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
            self._current_beat.color,
            self._current_beat.show_title
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
            self._current_beat.color,
            self._current_beat.show_title
        )
    
    def _on_show_title_changed(self, state: int) -> None:
        if self._updating or not self._current_beat:
            return
        
        show_title = state == Qt.CheckState.Checked.value
        self._current_beat.show_title = show_title
        self.beat_updated.emit(
            self._current_beat.id,
            self._current_beat.title,
            self._current_beat.content,
            self._current_beat.color,
            show_title
        )
    
    def clear(self) -> None:
        self.set_beat(None)
