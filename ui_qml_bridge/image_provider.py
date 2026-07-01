"""MichiCoverImageProvider — delivers cover art (real or fallback) to QML.

Registered as provider id "michi-cover" in qml_main.py.
QML usage: image://michi-cover/album/<album_key>
          image://michi-cover/file/<encoded_path>
          image://michi-cover/fallback/<seed>
"""

from pathlib import Path
import base64

from PySide6.QtCore import QSize, qWarning
from PySide6.QtGui import QImage, QPainter, QColor, QFont, QLinearGradient
from PySide6.QtQml import QQmlImageProviderBase, QQmlEngine


_FALLBACK_CACHE: dict[str, QImage] = {}
_COVER_CACHE: dict[str, QImage] = {}
_MAX_COVER_SIZE = 512
_MINI_COVER_SIZE = 96


def _generate_fallback(seed: str, size: int) -> QImage:
    key = f"{seed}_{size}"
    if key in _FALLBACK_CACHE:
        return _FALLBACK_CACHE[key]

    img = QImage(size, size, QImage.Format_ARGB32)
    img.fill(0x0D0F16)

    painter = QPainter(img)
    painter.setRenderHint(QPainter.Antialiasing)

    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0.0, QColor(0x0A, 0x0D, 0x14))
    gradient.setColorAt(1.0, QColor(0x11, 0x13, 0x1C))
    painter.fillRect(img.rect(), gradient)

    painter.setPen(QColor(0x8F, 0xB7, 0xFF))
    painter.setFont(QFont("sans-serif", size // 4, QFont.Bold))
    glyph = seed[:2].upper() if seed else "MM"
    painter.drawText(img.rect(), 0x0084, glyph)

    painter.end()
    _FALLBACK_CACHE[key] = img
    return img


def _load_cover_from_file(filepath: str, size: int) -> QImage | None:
    path = Path(filepath)
    if not path.is_file():
        return None
    try:
        img = QImage(str(path))
        if img.isNull():
            return None
        return img.scaled(size, size, 0x01, 0x01)
    except Exception:
        qWarning(f"[MichiCover] Failed to load: {filepath}")
        return None


class MichiCoverImageProvider(QQmlImageProviderBase):
    def __init__(self):
        super().__init__()
        self._id = "michi-cover"

    def imageType(self):
        return QQmlImageProviderBase.Image

    def requestImage(self, id: str, size: QSize, requestedSize: QSize):
        w = requestedSize.width() if requestedSize and requestedSize.width() > 0 else _MAX_COVER_SIZE
        h = requestedSize.height() if requestedSize and requestedSize.height() > 0 else _MAX_COVER_SIZE
        target = min(max(w, h), _MAX_COVER_SIZE)

        if id.startswith("file/"):
            encoded = id[5:]
            try:
                filepath = base64.urlsafe_b64decode(encoded).decode("utf-8")
            except Exception:
                qWarning(f"[MichiCover] Invalid file path encoding: {encoded[:40]}")
                return _generate_fallback("ERR", target)
            img = _load_cover_from_file(filepath, target)
            if img and not img.isNull():
                return img
            return _generate_fallback(Path(filepath).stem or "COVER", target)

        if id.startswith("album/"):
            key = id[6:]
            return _generate_fallback(key or "ALBUM", target)

        if id.startswith("track/"):
            key = id[6:]
            return _generate_fallback(key or "TRACK", target)

        return _generate_fallback(id or "COVER", target)


def register_image_provider(engine: QQmlEngine):
    provider = MichiCoverImageProvider()
    engine.addImageProvider("michi-cover", provider)
