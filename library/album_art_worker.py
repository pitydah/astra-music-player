"""Album Art Worker — threaded cover art loading without blocking the UI."""

import logging

from PySide6.QtCore import QObject, Signal, QThread, Slot
from PySide6.QtGui import QImage, QPixmap

logger = logging.getLogger("michi.album_art_worker")


class AlbumArtWorker(QObject):
    art_ready = Signal(int, QPixmap)

    @Slot(int, str)
    def load_art(self, track_id: int, file_path: str):
        image = QImage()
        loaded = image.load(file_path)
        if loaded:
            pixmap = QPixmap.fromImage(image)
            self.art_ready.emit(track_id, pixmap)
        else:
            self.art_ready.emit(track_id, QPixmap())


class AlbumArtManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = QThread()
        self._worker = AlbumArtWorker()
        self._worker.moveToThread(self._thread)
        self._worker.art_ready.connect(self._on_art_ready)
        self._thread.start()

    def request_cover(self, track_id: int, file_path: str):
        from PySide6.QtCore import QMetaObject, Qt
        QMetaObject.invokeMethod(
            self._worker, "load_art", Qt.QueuedConnection,
            track_id, file_path)

    def _on_art_ready(self, track_id: int, pixmap: QPixmap):
        pass  # override by connecting to art_ready signal

    def shutdown(self):
        """Stop the worker thread."""
        self._thread.quit()
        if not self._thread.wait(2000):
            logger.warning("AlbumArtManager thread did not stop in time")
