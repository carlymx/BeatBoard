"""Export service for generating PDF documents from BeatBoard projects."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtGui import QPdfWriter, QPagedPaintDevice, QTextDocument
from PySide6.QtWidgets import QApplication, QFileDialog

from beatboard.i18n import _tr

if TYPE_CHECKING:
    from beatboard.core.project import Project


class ExportService:
    @staticmethod
    def export_to_pdf(project: "Project", parent=None) -> bool:
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Exportar a PDF",
            f"{project.name}.pdf",
            "PDF Files (*.pdf)",
        )
        
        if not file_path:
            return False
        
        try:
            ExportService._generate_pdf(project, file_path)
            
            app = QApplication.instance()
            if app and hasattr(app, "logger"):
                app.logger.info(f"PDF exported to {file_path}")
            
            return True
        except Exception as e:
            app = QApplication.instance()
            if app and hasattr(app, "logger"):
                app.logger.error(f"PDF export failed: {e}")
            return False
    
    @staticmethod
    def _generate_pdf(project: "Project", file_path: str) -> None:
        html_content = ExportService._generate_html(project)
        
        document = QTextDocument()
        document.setHtml(html_content)
        
        writer = QPdfWriter(file_path)
        writer.setPageSize(QPagedPaintDevice.A4)
        writer.setPageMargins(30, 30, 30, 30)
        
        document.print(writer)
    
    @staticmethod
    def _generate_html(project: "Project") -> str:
        beats = project.beats
        
        beats_html = ""
        for i, beat in enumerate(beats, 1):
            color = beat.color
            from beatboard.core.constants import BEAT_COLORS
            bg_color = BEAT_COLORS.get(color, BEAT_COLORS["yellow"])
            
            beats_html += f"""
            <div style="
                background-color: {bg_color.name()};
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #333;
            ">
                <h3 style="margin: 0 0 10px 0;">{i}. {beat.title or _tr("no_title")}</h3>
                <p style="margin: 0; white-space: pre-wrap;">{beat.content or 'Sin contenido'}</p>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{project.name}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 12pt;
                    line-height: 1.5;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #333;
                    border-bottom: 2px solid #333;
                    padding-bottom: 10px;
                }}
                .metadata {{
                    color: #666;
                    font-size: 10pt;
                    margin-bottom: 20px;
                }}
                .connections {{
                    margin-top: 20px;
                    padding: 10px;
                    background-color: #f5f5f5;
                    border-radius: 8px;
                }}
            </style>
        </head>
        <body>
            <h1>{project.name}</h1>
            <div class="metadata">
                <p>Fecha de creación: {project.created_at.strftime('%d/%m/%Y')}</p>
                <p>Última modificación: {project.modified_at.strftime('%d/%m/%Y')}</p>
                <p>Total de beats: {len(beats)}</p>
            </div>
            
            <h2>Beats</h2>
            {beats_html}
        """
        
        if project.connections:
            connections_html = ""
            for conn in project.connections:
                source = project.get_beat_by_id(conn.source_beat_id)
                target = project.get_beat_by_id(conn.target_beat_id)
                if source and target:
                    connections_html += f"""
                    <li>{source.title or _tr("no_title")} → {target.title or _tr("no_title")}</li>
                    """
            
            html += f"""
            <div class="connections">
                <h3>Conexiones</h3>
                <ul>
                    {connections_html}
                </ul>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def export_to_text(project: "Project", parent=None) -> bool:
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Exportar a texto",
            f"{project.name}.txt",
            "Text Files (*.txt)",
        )
        
        if not file_path:
            return False
        
        try:
            content = ExportService._generate_text(project)
            Path(file_path).write_text(content, encoding="utf-8")
            
            app = QApplication.instance()
            if app and hasattr(app, "logger"):
                app.logger.info(f"Text exported to {file_path}")
            
            return True
        except Exception as e:
            app = QApplication.instance()
            if app and hasattr(app, "logger"):
                app.logger.error(f"Text export failed: {e}")
            return False
    
    @staticmethod
    def _generate_text(project: "Project") -> str:
        lines = [
            project.name,
            "=" * len(project.name),
            "",
            f"Fecha de creación: {project.created_at.strftime('%d/%m/%Y')}",
            f"Última modificación: {project.modified_at.strftime('%d/%m/%Y')}",
            f"Total de beats: {len(project.beats)}",
            "",
            "BEATS",
            "-" * 50,
            "",
        ]
        
        for i, beat in enumerate(project.beats, 1):
            lines.append(f"{i}. {beat.title or _tr('no_title')}")
            lines.append("-" * 30)
            lines.append(beat.content or "Sin contenido")
            lines.append("")
        
        if project.connections:
            lines.append("")
            lines.append("CONEXIONES")
            lines.append("-" * 50)
            
            for conn in project.connections:
                source = project.get_beat_by_id(conn.source_beat_id)
                target = project.get_beat_by_id(conn.target_beat_id)
                if source and target:
                    lines.append(f"  {source.title or _tr('no_title')} → {target.title or _tr('no_title')}")
        
        return "\n".join(lines)
