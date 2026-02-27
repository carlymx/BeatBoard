"""Auto-save service for BeatBoard projects."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from beatboard.core.constants import AUTOSAVE_INTERVAL_MS

if TYPE_CHECKING:
    from beatboard.core.project import Project


class AutosaveService:
    def __init__(self, project: "Project", get_file_path: callable) -> None:
        self._project = project
        self._get_file_path = get_file_path
        self._timer = QTimer()
        self._timer.timeout.connect(self._on_autosave)
        self._last_save_time: datetime | None = None
        self._backup_count = 0
        self._max_backups = 10

    def start(self) -> None:
        self._timer.start(AUTOSAVE_INTERVAL_MS)

    def stop(self) -> None:
        self._timer.stop()

    def is_active(self) -> bool:
        return self._timer.isActive()

    def set_interval(self, interval_ms: int) -> None:
        self._timer.setInterval(interval_ms)

    def _on_autosave(self) -> None:
        file_path = self._get_file_path()
        if not file_path:
            return

        self.save_backup(file_path)

    def save_backup(self, file_path: str) -> None:
        try:
            project_dir = Path(file_path).parent
            project_name = Path(file_path).stem
            backup_dir = project_dir / ".beatboard_backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{project_name}_{timestamp}.bbp"

            backup_file.write_text(
                json.dumps(self._project.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            self._cleanup_old_backups(backup_dir, project_name)

            self._last_save_time = datetime.now()

            app = QApplication.instance()
            if app and hasattr(app, "logger"):
                app.logger.info(f"Auto-save completed: {backup_file.name}")

        except Exception as e:
            app = QApplication.instance()
            if app and hasattr(app, "logger"):
                app.logger.error(f"Auto-save failed: {e}")

    def _cleanup_old_backups(self, backup_dir: Path, project_name: str) -> None:
        backups = sorted(
            backup_dir.glob(f"{project_name}_*.bbp"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for old_backup in backups[self._max_backups - 1 :]:
            try:
                old_backup.unlink()
            except Exception:
                pass

    def get_last_save_time(self) -> datetime | None:
        return self._last_save_time
