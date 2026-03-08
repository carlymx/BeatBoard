"""Properties panel widget for editing selected beats."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from beatboard.core.beat import Beat
from beatboard.core.connection import Connection
from beatboard.core.constants import (
    BEAT_PREDEFINED_COLORS,
    BEAT_PREDEFINED_NAMES,
    CONNECTION_COLORS,
    CONNECTION_LINE_WIDTH_OPTIONS,
    CONNECTION_NODE_SHAPES,
    get_valid_beat_color,
)
from beatboard.i18n import _tr
from beatboard.services.spellcheck_service import SpellCheckService
from beatboard.ui.widgets.spellcheck_highlighter import SpellCheckTextEdit

if TYPE_CHECKING:
    pass


class PropertiesPanel(QWidget):
    beat_updated = Signal(str, str, str, str, bool)
    connection_updated = Signal(str, str, float, str, str)
    multiple_beats_updated = Signal(list, str, bool)  # beat_ids, color, show_title
    multiple_connections_updated = Signal(list, str, float, str, str)  # connection_ids, color, line_width, node_shape, label

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._current_beat: Beat | None = None
        self._current_connection: Connection | None = None
        self._selected_beats: list[Beat] = []
        self._selected_connections: list[Connection] = []
        self._element_type: str = "none"  # "beat", "connection", "shape", "image", "none"
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
        
        self._beat_properties_widget = QWidget()
        self._beat_properties_widget.setVisible(False)
        main_layout.addWidget(self._beat_properties_widget)
        
        self._connection_properties_widget = QWidget()
        self._connection_properties_widget.setVisible(False)
        main_layout.addWidget(self._connection_properties_widget)
        self._setup_connection_properties()
        
        self._multiple_beats_widget = QWidget()
        self._multiple_beats_widget.setVisible(False)
        main_layout.addWidget(self._multiple_beats_widget)
        self._setup_multiple_beats_properties()
        
        self._multiple_connections_widget = QWidget()
        self._multiple_connections_widget.setVisible(False)
        main_layout.addWidget(self._multiple_connections_widget)
        self._setup_multiple_connections_properties()
        
        props_layout = QVBoxLayout(self._beat_properties_widget)
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
        
        self._open_editor_btn = QPushButton(_tr("open_full_editor"))
        self._open_editor_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._open_editor_btn.clicked.connect(self._open_full_editor)
        self._open_editor_btn.setVisible(False)
        props_layout.addWidget(self._open_editor_btn)
        
        main_layout.addStretch()
        
        info_label = QLabel(_tr("tip_double_click"))
        info_label.setStyleSheet("color: gray; font-size: 11px; padding: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)
    
    def _setup_connection_properties(self) -> None:
        """Configurar widgets de propiedades para conexiones."""
        conn_layout = QVBoxLayout(self._connection_properties_widget)
        conn_layout.setContentsMargins(0, 0, 0, 0)
        conn_layout.setSpacing(10)
        
        # Color de conexión
        color_label = QLabel(_tr("connection_color"))
        color_label.setStyleSheet("font-weight: bold;")
        conn_layout.addWidget(color_label)
        
        self._connection_color_combo = QComboBox()
        self._connection_color_combo.setMinimumWidth(150)
        
        # Agregar colores de conexión predefinidos
        for color_name, qcolor in CONNECTION_COLORS.items():
            color_key = color_name
            color_display = _tr(f"connection_color_{color_name}")
            self._connection_color_combo.addItem(color_display, color_name)
        
        self._connection_color_combo.currentIndexChanged.connect(self._on_connection_color_changed)
        
        color_layout = QHBoxLayout()
        color_layout.setSpacing(8)
        color_layout.addWidget(self._connection_color_combo)
        
        self._connection_color_indicator = QFrame()
        self._connection_color_indicator.setFixedSize(30, 24)
        self._connection_color_indicator.setStyleSheet("background-color: #42A5F5; border: 2px solid #333333; border-radius: 4px;")
        color_layout.addWidget(self._connection_color_indicator)
        
        conn_layout.addLayout(color_layout)
        
        # Grosor de línea
        width_label = QLabel(_tr("line_width"))
        width_label.setStyleSheet("font-weight: bold;")
        conn_layout.addWidget(width_label)
        
        self._line_width_spin = QDoubleSpinBox()
        self._line_width_spin.setRange(0.5, 10.0)
        self._line_width_spin.setSingleStep(0.5)
        self._line_width_spin.setSuffix(" px")
        self._line_width_spin.valueChanged.connect(self._on_line_width_changed)
        conn_layout.addWidget(self._line_width_spin)
        
        # Forma de nodos
        node_label = QLabel(_tr("node_shape"))
        node_label.setStyleSheet("font-weight: bold;")
        conn_layout.addWidget(node_label)
        
        self._node_shape_combo = QComboBox()
        for shape in CONNECTION_NODE_SHAPES:
            self._node_shape_combo.addItem(_tr(f"node_shape_{shape}"), shape)
        self._node_shape_combo.currentIndexChanged.connect(self._on_node_shape_changed)
        conn_layout.addWidget(self._node_shape_combo)
        
        # Etiqueta de texto
        label_label = QLabel(_tr("label"))
        label_label.setStyleSheet("font-weight: bold;")
        conn_layout.addWidget(label_label)
        
        self._connection_label_input = QLineEdit()
        self._connection_label_input.setPlaceholderText(_tr("label_placeholder"))
        self._connection_label_input.textChanged.connect(self._on_connection_label_changed)
        conn_layout.addWidget(self._connection_label_input)
        
        conn_layout.addStretch()
    
    def _setup_multiple_beats_properties(self) -> None:
        """Configurar widgets de propiedades comunes para múltiples beats."""
        multi_layout = QVBoxLayout(self._multiple_beats_widget)
        multi_layout.setContentsMargins(0, 0, 0, 0)
        multi_layout.setSpacing(10)
        
        count_label = QLabel("")  # se actualizará dinámicamente
        count_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #666;")
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        multi_layout.addWidget(count_label)
        self._multiple_beats_count_label = count_label
        
        # Color común
        color_label = QLabel(_tr("color"))
        color_label.setStyleSheet("font-weight: bold;")
        multi_layout.addWidget(color_label)
        
        self._multiple_beats_color_combo = QComboBox()
        self._multiple_beats_color_combo.setMinimumWidth(150)
        
        color_translation_keys = {
            "#FFF59D": "yellow",
            "#90CAF9": "blue",
            "#A5D6A7": "green",
            "#EF9A9A": "red",
            "#FFCC80": "orange",
            "#CE93D8": "purple",
            "#E0E0E0": "gray",
        }
        
        for i, hex_color in enumerate(BEAT_PREDEFINED_COLORS):
            color_key = color_translation_keys.get(hex_color, f"color_{i}")
            color_name = _tr(color_key)
            self._multiple_beats_color_combo.addItem(color_name, hex_color)
        
        self._update_custom_colors_in_combo(self._multiple_beats_color_combo, {})
        
        self._multiple_beats_color_combo.currentIndexChanged.connect(self._on_multiple_beats_color_changed)
        
        color_layout = QHBoxLayout()
        color_layout.setSpacing(8)
        color_layout.addWidget(self._multiple_beats_color_combo)
        
        self._multiple_beats_color_indicator = QFrame()
        self._multiple_beats_color_indicator.setFixedSize(30, 24)
        self._multiple_beats_color_indicator.setStyleSheet("background-color: #FFF59D; border: 2px solid #333333; border-radius: 4px;")
        color_layout.addWidget(self._multiple_beats_color_indicator)
        
        multi_layout.addLayout(color_layout)
        
        # Mostrar título común
        self._multiple_beats_show_title_checkbox = QCheckBox(_tr("show_title"))
        self._multiple_beats_show_title_checkbox.stateChanged.connect(self._on_multiple_beats_show_title_changed)
        multi_layout.addWidget(self._multiple_beats_show_title_checkbox)
        
        multi_layout.addStretch()
    
    def _setup_multiple_connections_properties(self) -> None:
        """Configurar widgets de propiedades comunes para múltiples conexiones."""
        multi_layout = QVBoxLayout(self._multiple_connections_widget)
        multi_layout.setContentsMargins(0, 0, 0, 0)
        multi_layout.setSpacing(10)
        
        count_label = QLabel("")
        count_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #666;")
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        multi_layout.addWidget(count_label)
        self._multiple_connections_count_label = count_label
        
        # Color común
        color_label = QLabel(_tr("connection_color"))
        color_label.setStyleSheet("font-weight: bold;")
        multi_layout.addWidget(color_label)
        
        self._multiple_connections_color_combo = QComboBox()
        self._multiple_connections_color_combo.setMinimumWidth(150)
        
        for color_name, qcolor in CONNECTION_COLORS.items():
            color_display = _tr(f"connection_color_{color_name}")
            self._multiple_connections_color_combo.addItem(color_display, color_name)
        
        self._multiple_connections_color_combo.currentIndexChanged.connect(self._on_multiple_connections_color_changed)
        
        color_layout = QHBoxLayout()
        color_layout.setSpacing(8)
        color_layout.addWidget(self._multiple_connections_color_combo)
        
        self._multiple_connections_color_indicator = QFrame()
        self._multiple_connections_color_indicator.setFixedSize(30, 24)
        self._multiple_connections_color_indicator.setStyleSheet("background-color: #42A5F5; border: 2px solid #333333; border-radius: 4px;")
        color_layout.addWidget(self._multiple_connections_color_indicator)
        
        multi_layout.addLayout(color_layout)
        
        # Grosor de línea común
        width_label = QLabel(_tr("line_width"))
        width_label.setStyleSheet("font-weight: bold;")
        multi_layout.addWidget(width_label)
        
        self._multiple_connections_line_width_spin = QDoubleSpinBox()
        self._multiple_connections_line_width_spin.setRange(0.5, 10.0)
        self._multiple_connections_line_width_spin.setSingleStep(0.5)
        self._multiple_connections_line_width_spin.setSuffix(" px")
        self._multiple_connections_line_width_spin.valueChanged.connect(self._on_multiple_connections_line_width_changed)
        multi_layout.addWidget(self._multiple_connections_line_width_spin)
        
        # Forma de nodos común
        node_label = QLabel(_tr("node_shape"))
        node_label.setStyleSheet("font-weight: bold;")
        multi_layout.addWidget(node_label)
        
        self._multiple_connections_node_shape_combo = QComboBox()
        for shape in CONNECTION_NODE_SHAPES:
            self._multiple_connections_node_shape_combo.addItem(_tr(f"node_shape_{shape}"), shape)
        self._multiple_connections_node_shape_combo.currentIndexChanged.connect(self._on_multiple_connections_node_shape_changed)
        multi_layout.addWidget(self._multiple_connections_node_shape_combo)
        
        # Etiqueta de texto común
        label_label = QLabel(_tr("label"))
        label_label.setStyleSheet("font-weight: bold;")
        multi_layout.addWidget(label_label)
        
        self._multiple_connections_label_input = QLineEdit()
        self._multiple_connections_label_input.setPlaceholderText(_tr("label_placeholder"))
        self._multiple_connections_label_input.textChanged.connect(self._on_multiple_connections_label_changed)
        multi_layout.addWidget(self._multiple_connections_label_input)
        
        multi_layout.addStretch()
    
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
        
        # Crear indicador de color seleccionado
        color_indicator_layout = QHBoxLayout()
        color_indicator_layout.setSpacing(8)
        color_indicator_layout.addWidget(combo)
        
        self._color_indicator = QFrame()
        self._color_indicator.setFixedSize(30, 24)
        self._color_indicator.setStyleSheet("background-color: #FFF59D; border: 2px solid #333333; border-radius: 4px;")
        color_indicator_layout.addWidget(self._color_indicator)
        
        layout.addLayout(color_indicator_layout)
        
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
        self._current_connection = None
        self._selected_beats = []
        self._selected_connections = []
        self._updating = True
        
        if beat is None:
            self._no_selection_label.setVisible(True)
            self._beat_properties_widget.setVisible(False)
            self._connection_properties_widget.setVisible(False)
            self._multiple_beats_widget.setVisible(False)
            self._multiple_connections_widget.setVisible(False)
            self._open_editor_btn.setVisible(False)
        else:
            self._no_selection_label.setVisible(False)
            self._beat_properties_widget.setVisible(True)
            self._connection_properties_widget.setVisible(False)
            self._multiple_beats_widget.setVisible(False)
            self._multiple_connections_widget.setVisible(False)
            self._open_editor_btn.setVisible(True)
            
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
            
            self._update_color_indicator(beat.color)
            
            self._show_title_checkbox.blockSignals(True)
            self._show_title_checkbox.setChecked(beat.show_title)
            self._show_title_checkbox.blockSignals(False)
        
        self._updating = False
    
    def set_connection(self, connection: Connection | None) -> None:
        self._current_connection = connection
        self._current_beat = None
        self._selected_beats = []
        self._selected_connections = []
        self._updating = True
        
        if connection is None:
            self._no_selection_label.setVisible(True)
            self._beat_properties_widget.setVisible(False)
            self._connection_properties_widget.setVisible(False)
            self._multiple_beats_widget.setVisible(False)
            self._multiple_connections_widget.setVisible(False)
        else:
            self._no_selection_label.setVisible(False)
            self._beat_properties_widget.setVisible(False)
            self._connection_properties_widget.setVisible(True)
            self._multiple_beats_widget.setVisible(False)
            self._multiple_connections_widget.setVisible(False)
            
            # Configurar color
            index = self._connection_color_combo.findData(connection.color)
            if index >= 0:
                self._connection_color_combo.setCurrentIndex(index)
            self._update_connection_color_indicator(connection.color)
            
            # Configurar grosor
            self._line_width_spin.setValue(connection.line_width)
            
            # Configurar forma de nodos
            index = self._node_shape_combo.findData(connection.node_shape)
            if index >= 0:
                self._node_shape_combo.setCurrentIndex(index)
            
            # Configurar etiqueta
            self._connection_label_input.blockSignals(True)
            self._connection_label_input.setText(connection.label or "")
            self._connection_label_input.blockSignals(False)
        
        self._updating = False
    
    def set_multiple_beats(self, beats: list[Beat]) -> None:
        self._selected_beats = beats
        self._selected_connections = []
        self._current_beat = None
        self._current_connection = None
        self._updating = True
        
        if not beats:
            self._no_selection_label.setVisible(True)
            self._beat_properties_widget.setVisible(False)
            self._connection_properties_widget.setVisible(False)
            self._multiple_beats_widget.setVisible(False)
            self._multiple_connections_widget.setVisible(False)
        else:
            self._no_selection_label.setVisible(False)
            self._beat_properties_widget.setVisible(False)
            self._connection_properties_widget.setVisible(False)
            self._multiple_beats_widget.setVisible(True)
            self._multiple_connections_widget.setVisible(False)
            
            # Actualizar etiqueta de conteo
            count_text = _tr("multiple_selected_beats").format(count=len(beats))
            self._multiple_beats_count_label.setText(count_text)
            
            # Actualizar colores personalizados en el combo box
            self._update_custom_colors_in_combo(self._multiple_beats_color_combo, {})
            
            # Determinar valores comunes
            colors = {beat.color for beat in beats}
            show_titles = {beat.show_title for beat in beats}
            
            # Configurar color común
            if len(colors) == 1:
                color = next(iter(colors))
                index = self._multiple_beats_color_combo.findData(color)
                if index >= 0:
                    self._multiple_beats_color_combo.setCurrentIndex(index)
                else:
                    self._multiple_beats_color_combo.setCurrentIndex(0)
                self._update_multiple_beats_color_indicator(color)
            else:
                # Valores mixtos: establecer índice -1 (sin selección)
                self._multiple_beats_color_combo.setCurrentIndex(-1)
                self._multiple_beats_color_indicator.setStyleSheet("background-color: transparent; border: 2px dashed #666; border-radius: 4px;")
            
            # Configurar checkbox de show_title
            self._multiple_beats_show_title_checkbox.blockSignals(True)
            if len(show_titles) == 1:
                show_title = next(iter(show_titles))
                self._multiple_beats_show_title_checkbox.setChecked(show_title)
                self._multiple_beats_show_title_checkbox.setTristate(False)
            else:
                self._multiple_beats_show_title_checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
                self._multiple_beats_show_title_checkbox.setTristate(True)
            self._multiple_beats_show_title_checkbox.blockSignals(False)
        
        self._updating = False
    
    def set_multiple_connections(self, connections: list[Connection]) -> None:
        self._selected_connections = connections
        self._selected_beats = []
        self._current_beat = None
        self._current_connection = None
        self._updating = True
        
        if not connections:
            self._no_selection_label.setVisible(True)
            self._beat_properties_widget.setVisible(False)
            self._connection_properties_widget.setVisible(False)
            self._multiple_beats_widget.setVisible(False)
            self._multiple_connections_widget.setVisible(False)
        else:
            self._no_selection_label.setVisible(False)
            self._beat_properties_widget.setVisible(False)
            self._connection_properties_widget.setVisible(False)
            self._multiple_beats_widget.setVisible(False)
            self._multiple_connections_widget.setVisible(True)
            
            count_text = _tr("multiple_selected_connections").format(count=len(connections))
            self._multiple_connections_count_label.setText(count_text)
            
            # Determinar valores comunes
            colors = {conn.color for conn in connections}
            line_widths = {conn.line_width for conn in connections}
            node_shapes = {conn.node_shape for conn in connections}
            
            # Configurar color común
            if len(colors) == 1:
                color = next(iter(colors))
                index = self._multiple_connections_color_combo.findData(color)
                if index >= 0:
                    self._multiple_connections_color_combo.setCurrentIndex(index)
                else:
                    self._multiple_connections_color_combo.setCurrentIndex(0)
                self._update_multiple_connections_color_indicator(color)
            else:
                self._multiple_connections_color_combo.setCurrentIndex(-1)
                self._multiple_connections_color_indicator.setStyleSheet("background-color: transparent; border: 2px dashed #666; border-radius: 4px;")
            
            # Configurar grosor común
            if len(line_widths) == 1:
                line_width = next(iter(line_widths))
                self._multiple_connections_line_width_spin.setValue(line_width)
            else:
                self._multiple_connections_line_width_spin.setValue(1.0)  # valor por defecto
            
            # Configurar forma de nodos común
            if len(node_shapes) == 1:
                node_shape = next(iter(node_shapes))
                index = self._multiple_connections_node_shape_combo.findData(node_shape)
                if index >= 0:
                    self._multiple_connections_node_shape_combo.setCurrentIndex(index)
                else:
                    self._multiple_connections_node_shape_combo.setCurrentIndex(0)
            else:
                self._multiple_connections_node_shape_combo.setCurrentIndex(-1)
        
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
        self._update_color_indicator(color_key)
        self.beat_updated.emit(
            self._current_beat.id,
            self._current_beat.title,
            self._current_beat.content,
            self._current_beat.color,
            self._current_beat.show_title
        )
    
    def _update_color_indicator(self, hex_color: str) -> None:
        if hasattr(self, '_color_indicator') and self._color_indicator:
            self._color_indicator.setStyleSheet(
                f"background-color: {hex_color}; border: 2px solid #333333; border-radius: 4px;"
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
    
    def _on_connection_color_changed(self, index: int) -> None:
        if self._updating or not self._current_connection:
            return
        
        color_key = self._connection_color_combo.itemData(index)
        self._current_connection.color = color_key
        self._update_connection_color_indicator(color_key)
        self._emit_connection_updated()
    
    def _on_line_width_changed(self, value: float) -> None:
        if self._updating or not self._current_connection:
            return
        
        self._current_connection.line_width = value
        self._emit_connection_updated()
    
    def _on_node_shape_changed(self, index: int) -> None:
        if self._updating or not self._current_connection:
            return
        
        shape_key = self._node_shape_combo.itemData(index)
        self._current_connection.node_shape = shape_key
        self._emit_connection_updated()
    
    def _on_connection_label_changed(self, text: str) -> None:
        if self._updating or not self._current_connection:
            return
        
        self._current_connection.label = text if text else None
        self._emit_connection_updated()
    
    def _on_multiple_beats_color_changed(self, index: int) -> None:
        if self._updating or not self._selected_beats:
            return
        
        color_key = self._multiple_beats_color_combo.itemData(index)
        self._update_multiple_beats_color_indicator(color_key)
        self._emit_multiple_beats_updated(color=color_key)
    
    def _on_multiple_beats_show_title_changed(self, state: int) -> None:
        if self._updating or not self._selected_beats:
            return
        
        show_title = state == Qt.CheckState.Checked.value
        self._emit_multiple_beats_updated(show_title=show_title)
    
    def _on_multiple_connections_color_changed(self, index: int) -> None:
        if self._updating or not self._selected_connections:
            return
        
        color_key = self._multiple_connections_color_combo.itemData(index)
        self._update_multiple_connections_color_indicator(color_key)
        self._emit_multiple_connections_updated(color=color_key)
    
    def _on_multiple_connections_line_width_changed(self, value: float) -> None:
        if self._updating or not self._selected_connections:
            return
        
        self._emit_multiple_connections_updated(line_width=value)
    
    def _on_multiple_connections_node_shape_changed(self, index: int) -> None:
        if self._updating or not self._selected_connections:
            return
        
        shape_key = self._multiple_connections_node_shape_combo.itemData(index)
        self._emit_multiple_connections_updated(node_shape=shape_key)
    
    def _on_multiple_connections_label_changed(self, text: str) -> None:
        if self._updating or not self._selected_connections:
            return
        
        self._emit_multiple_connections_updated(label=text)
    
    def _update_connection_color_indicator(self, color_name: str) -> None:
        if hasattr(self, '_connection_color_indicator') and self._connection_color_indicator:
            qcolor = CONNECTION_COLORS.get(color_name, CONNECTION_COLORS["blue"])
            hex_color = qcolor.name()
            self._connection_color_indicator.setStyleSheet(
                f"background-color: {hex_color}; border: 2px solid #333333; border-radius: 4px;"
            )
    
    def _emit_connection_updated(self) -> None:
        if not self._current_connection:
            return
        
        self.connection_updated.emit(
            self._current_connection.id,
            self._current_connection.color,
            self._current_connection.line_width,
            self._current_connection.node_shape,
            self._current_connection.label or ""
        )
    
    def _update_multiple_beats_color_indicator(self, hex_color: str) -> None:
        if hasattr(self, '_multiple_beats_color_indicator') and self._multiple_beats_color_indicator:
            self._multiple_beats_color_indicator.setStyleSheet(
                f"background-color: {hex_color}; border: 2px solid #333333; border-radius: 4px;"
            )
    
    def _update_multiple_connections_color_indicator(self, color_name: str) -> None:
        if hasattr(self, '_multiple_connections_color_indicator') and self._multiple_connections_color_indicator:
            qcolor = CONNECTION_COLORS.get(color_name, CONNECTION_COLORS["blue"])
            hex_color = qcolor.name()
            self._multiple_connections_color_indicator.setStyleSheet(
                f"background-color: {hex_color}; border: 2px solid #333333; border-radius: 4px;"
            )
    
    def _emit_multiple_beats_updated(self, color: str | None = None, show_title: bool | None = None) -> None:
        if not self._selected_beats:
            return
        
        beat_ids = [beat.id for beat in self._selected_beats]
        # Determinar valores actuales si alguno es None
        if color is None:
            # Usar color actual del primer beat (no cambiar)
            color = self._selected_beats[0].color
        if show_title is None:
            show_title = self._selected_beats[0].show_title
        
        self.multiple_beats_updated.emit(beat_ids, color, show_title)
    
    def _emit_multiple_connections_updated(self, color: str | None = None, line_width: float | None = None, node_shape: str | None = None) -> None:
        if not self._selected_connections:
            return
        
        connection_ids = [conn.id for conn in self._selected_connections]
        # Determinar valores actuales si alguno es None
        if color is None:
            color = self._selected_connections[0].color
        if line_width is None:
            line_width = self._selected_connections[0].line_width
        if node_shape is None:
            node_shape = self._selected_connections[0].node_shape
        
        self.multiple_connections_updated.emit(connection_ids, color, line_width, node_shape)
    
    def clear(self) -> None:
        self.set_beat(None)
        self.set_connection(None)
        self._selected_beats = []
        self._selected_connections = []
        self._no_selection_label.setVisible(True)
        self._beat_properties_widget.setVisible(False)
        self._connection_properties_widget.setVisible(False)
        self._multiple_beats_widget.setVisible(False)
        self._multiple_connections_widget.setVisible(False)
    
    def update_selected_color(self, hex_color: str) -> None:
        # Actualizar para beat individual seleccionado
        if self._current_beat and self._color_combo:
            # Bloquear señales para evitar ciclo
            self._updating = True
            
            index = self._color_combo.findData(hex_color)
            if index >= 0:
                self._color_combo.setCurrentIndex(index)
            self._update_color_indicator(hex_color)
            
            self._updating = False
        
        # Actualizar para múltiples beats seleccionados
        if self._selected_beats and self._multiple_beats_color_combo:
            self._updating = True
            
            # Verificar si todos los beats seleccionados tienen el mismo color
            colors = {beat.color for beat in self._selected_beats}
            if len(colors) == 1 and next(iter(colors)) == hex_color:
                # Todos tienen el mismo color, actualizar combo box
                index = self._multiple_beats_color_combo.findData(hex_color)
                if index >= 0:
                    self._multiple_beats_color_combo.setCurrentIndex(index)
                self._update_multiple_beats_color_indicator(hex_color)
            else:
                # Valores mixtos: establecer índice -1 (sin selección)
                self._multiple_beats_color_combo.setCurrentIndex(-1)
                self._multiple_beats_color_indicator.setStyleSheet("background-color: transparent; border: 2px dashed #666; border-radius: 4px;")
            
            self._updating = False
    
    def _open_full_editor(self) -> None:
        if not self._current_beat:
            return
        
        from beatboard.ui.dialogs.beat_editor_dialog import BeatEditorDialog
        
        dialog = BeatEditorDialog(self._current_beat, self)
        if dialog.exec():
            title, content, color = dialog.get_beat_data()
            self._current_beat.title = title
            self._current_beat.content = content
            self._current_beat.color = color
            
            self.beat_updated.emit(
                self._current_beat.id,
                self._current_beat.title,
                self._current_beat.content,
                self._current_beat.color,
                self._current_beat.show_title
            )
