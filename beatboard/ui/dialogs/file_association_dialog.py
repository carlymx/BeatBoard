"""Dialog for registering file associations."""

from __future__ import annotations

import os
import platform
import subprocess
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from beatboard.i18n import _tr

if TYPE_CHECKING:
    pass


class FileAssociationDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        
        self._system = platform.system()
        
        self.setWindowTitle(_tr("file_association_title"))
        self.setMinimumSize(400, 250)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        info_label = QLabel(_tr("file_association_desc"))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        if self._system == "Linux":
            self._setup_linux_section(layout)
        elif self._system == "Windows":
            self._setup_windows_section(layout)
        elif self._system == "Darwin":
            self._setup_macos_section(layout)
        else:
            unsupported_label = QLabel(_tr("file_association_unsupported"))
            unsupported_label.setWordWrap(True)
            layout.addWidget(unsupported_label)
        
        layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
    
    def _setup_linux_section(self, layout) -> None:
        from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QMessageBox
        
        group = QGroupBox(_tr("file_association_linux_title"))
        group_layout = QVBoxLayout(group)
        
        self._register_mime_check = QCheckBox(_tr("file_association_register_mime"))
        self._register_mime_check.setChecked(True)
        group_layout.addWidget(self._register_mime_check)
        
        self._create_desktop_check = QCheckBox(_tr("file_association_create_desktop"))
        self._create_desktop_check.setChecked(True)
        group_layout.addWidget(self._create_desktop_check)
        
        layout.addWidget(group)
    
    def _setup_windows_section(self, layout) -> None:
        from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
        
        group = QGroupBox(_tr("file_association_windows_title"))
        group_layout = QVBoxLayout(group)
        
        info = QLabel(_tr("file_association_windows_info"))
        info.setWordWrap(True)
        group_layout.addWidget(info)
        
        layout.addWidget(group)
    
    def _setup_macos_section(self, layout) -> None:
        from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
        
        group = QGroupBox(_tr("file_association_macos_title"))
        group_layout = QVBoxLayout(group)
        
        info = QLabel(_tr("file_association_macos_info"))
        info.setWordWrap(True)
        group_layout.addWidget(info)
        
        layout.addWidget(group)
    
    def get_linux_options(self) -> dict:
        return {
            "register_mime": self._register_mime_check.isChecked(),
            "create_desktop": self._create_desktop_check.isChecked(),
        }
