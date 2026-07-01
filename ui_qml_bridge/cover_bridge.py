"""CoverBridge — QQuickPaintedItem that renders cover art in QML.

Usage in QML:
    import ui_qml_bridge.cover_bridge 1.0
    CoverBridge { coverKey: "album_xyz"; width: 180; height: 180 }

Registered as "ui_qml_bridge" import in qml_main.py.
"""

from PySide6.QtQuick import QQuickPaintedItem
from PySide6.QtGui import QImage, QPainter, QColor, QFont, QLinearGradient, QPixmap
from PySide6.QtCore import Property, Signal, QByteArray
from pathlib import Path

_FALLBACK_CACHE: dict[str, QPixmap] = {}
_COVER_CACHE: dict[str, QImage] = {}


def _make_fallback_pixmap(seed: str, size: int) -> QPixmap:
    key = f"fallback_{seed}_{size}"
    if key in _FALLBACK_CACHE:
        return _FALLBACK_CACHE[key]

    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(0x0D0F16)

    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0.0, QColor(0x0A, 0x0D, 0x14))
    gradient.setColorAt(1.0, QColor(0x11, 0x13, 0x1C))
    p.fillRect(img.rect(), gradient)
    p.setPen(QColor(0x8F, 0xB7, 0xFF))
    p.setFont(QFont("sans-serif", size // 4, QFont.Bold))
    glyph = seed[:2].upper() if seed else "MM"
    p.drawText(img.rect(), 0x0084, glyph)
    p.end()

    pm = QPixmap.fromImage(img)
    _FALLBACK_CACHE[key] = pm
    return pm


def _load_cover_image(album_key: str, size: int) -> QImage | None:
    if album_key in _COVER_CACHE:
        cached = _COVER_CACHE[album_key]
        if cached.width() != size:
            return cached.scaled(size, size, 0x01, 0x01)
        return cached

    try:
        from library.library_db import LibraryDB
        db_path = Path.home() / ".local" / "share" / "michi-music-player" / "library.db"
        if db_path.exists():
            db = LibraryDB(str(db_path))
            row = db.get_album_art_cache(album_key)
            if row:
                mime, data = row
                img = QImage()
                if img.loadFromData(QByteArray(data)):
                    scaled = img.scaled(size, size, 0x01, 0x01)
                    _COVER_CACHE[album_key] = scaled
                    return scaled
    except Exception:
        pass

    return None


class CoverBridge(QQuickPaintedItem):
    coverChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cover_key = ""
        self._pixmap = None

    @Property(str, notify=coverChanged)
    def coverKey(self):
        return self._cover_key

    @coverKey.setter
    def coverKey(self, key: str):
        if key != self._cover_key:
            self._cover_key = key
            self._pixmap = None
            self.coverChanged.emit()
            self.update()

    def paint(self, painter: QPainter):
        w = int(self.width())
        h = int(self.height())
        if w < 1 or h < 1:
            return

        if self._pixmap is None and self._cover_key:
            img = _load_cover_image(self._cover_key, max(w, h))
            if img:
                self._pixmap = QPixmap.fromImage(img)

        if self._pixmap:
            painter.drawPixmap(0, 0, w, h, self._pixmap)
        else:
            key = self._cover_key or "COVER"
            fallback = _make_fallback_pixmap(key, max(w, h))
            painter.drawPixmap(0, 0, w, h, fallback)
