"""PeriodicAnalyzer — background timer that runs Audio Lab diagnostics on all media files at a configurable interval."""

from PySide6.QtCore import QObject, QTimer

from core.settings_manager import get, set_
from core.audio_lab.diagnostics_service import analyse_file
from core.audio_lab.audio_lab_sync import sync_audio_lab_result_to_media_item


class PeriodicAnalyzer(QObject):
    def __init__(self, library_db, parent=None):
        super().__init__(parent)
        self._db = library_db
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._run)
        self._running = False

    def start(self):
        if not get("audio_lab/auto_analyze"):
            return
        from core.settings_manager import get_int
        interval_hours = get_int("audio_lab/interval_hours") or 0
        interval_ms = interval_hours * 3600000
        if interval_ms < 60000:
            interval_ms = 60000
        self._timer.start(interval_ms)
        self._running = True

    def stop(self):
        self._timer.stop()
        self._running = False

    def set_interval(self, hours: int):
        set_("audio_lab/interval_hours", max(1, hours))
        if self._running:
            self._timer.setInterval(hours * 3600000)

    def set_enabled(self, enabled: bool):
        set_("audio_lab/auto_analyze", enabled)
        if enabled:
            self.start()
        else:
            self.stop()

    @property
    def is_running(self) -> bool:
        return self._running

    def _run(self):
        rows = self._db.execute("SELECT filepath FROM media_items WHERE filepath IS NOT NULL").fetchall()
        paths = [r[0] for r in rows if r[0]]
        batch_size = 50
        for i in range(0, len(paths), batch_size):
            batch = paths[i:i + batch_size]
            for fp in batch:
                try:
                    result = analyse_file(fp)
                    sync_audio_lab_result_to_media_item(self._db, fp, result)
                except Exception:
                    pass
