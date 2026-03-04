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
        self._max_backups = 10
        self._backup_on_open = True
        self._interval = AUTOSAVE_INTERVAL_MS
        self._enabled = True
        
        self._load_preferences()

    def _load_preferences(self) -> None:
        app = QApplication.instance()
        if app and hasattr(app, "theme_manager"):
            tm = app.theme_manager
            self._max_backups = tm.get_max_backups()
            self._backup_on_open = tm.get_backup_on_open()
            self._interval = tm.get_autosave_interval()
            self._enabled = tm.get_autosave_enabled()
            
            if not self._enabled:
                self._timer.stop()

    def start(self) -> None:
        self._load_preferences()
        if self._enabled:
            self._timer.start(self._interval)

    def stop(self) -> None:
        self._timer.stop()

    def is_active(self) -> bool:
        return self._timer.isActive()

    def set_interval(self, interval_ms: int) -> None:
        self._timer.setInterval(interval_ms)

    def _on_autosave(self) -> None:
        if not self._enabled:
            return
        file_path = self._get_file_path()
        if not file_path:
            return

        self.save_backup(file_path, is_auto=True)

    def save_backup(self, file_path: str, is_auto: bool = True) -> None:
        try:
            project_dir = Path(file_path).parent
            project_name = Path(file_path).stem
            backup_dir = project_dir / ".beatboard_backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suffix = "auto" if is_auto else "open"
            backup_file = backup_dir / f"{project_name}_{suffix}_{timestamp}.bbp"

            backup_file.write_text(
                json.dumps(self._project.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            self._cleanup_old_backups(backup_dir, project_name)

            self._last_save_time = datetime.now()

            app = QApplication.instance()
            if app and hasattr(app, "logger"):
                suffix_text = "Auto-save" if is_auto else "Backup on open"
                app.logger.info(f"{suffix_text} completed: {backup_file.name}")

        except Exception as e:
            app = QApplication.instance()
            if app and hasattr(app, "logger"):
                app.logger.error(f"Backup failed: {e}")

    def save_backup_on_open(self) -> None:
        if not self._backup_on_open:
            return
        self._load_preferences()
        file_path = self._get_file_path()
        if file_path:
            self.save_backup(file_path, is_auto=False)

    def _cleanup_old_backups(self, backup_dir: Path, project_name: str) -> None:
        self._load_preferences()
        
        backups = sorted(
            backup_dir.glob(f"{project_name}_*.bbp"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for old_backup in backups[self._max_backups - 1:]:
            try:
                old_backup.unlink()
            except Exception:
                pass

    def cleanup_all_backups(self, file_path: str | None = None) -> int:
        """Elimina todos los backups del proyecto actual. Retorna la cantidad eliminada."""
        if file_path is None:
            file_path = self._get_file_path()
        if not file_path:
            return 0
        
        count = 0
        try:
            project_dir = Path(file_path).parent
            project_name = Path(file_path).stem
            backup_dir = project_dir / ".beatboard_backups"
            
            if backup_dir.exists():
                for backup in backup_dir.glob(f"{project_name}_*.bbp"):
                    try:
                        backup.unlink()
                        count += 1
                    except Exception:
                        pass
                
                if not any(backup_dir.iterdir()):
                    try:
                        backup_dir.rmdir()
                    except Exception:
                        pass
                
                app = QApplication.instance()
                if app and hasattr(app, "logger"):
                    app.logger.info(f"Cleaned up {count} backup files")
        except Exception as e:
            app = QApplication.instance()
            if app and hasattr(app, "logger"):
                app.logger.error(f"Failed to cleanup backups: {e}")
        
        return count

    def get_last_save_time(self) -> datetime | None:
        return self._last_save_time

    def get_max_backups(self) -> int:
        return self._max_backups

    def get_backup_on_open(self) -> bool:
        return self._backup_on_open

    def is_enabled(self) -> bool:
        return self._enabled

    def set_max_backups(self, count: int) -> None:
        self._max_backups = max(1, min(count, 20))

    def set_backup_on_open(self, enabled: bool) -> None:
        self._backup_on_open = enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if enabled:
            self._timer.start(self._interval)
        else:
            self._timer.stop()
