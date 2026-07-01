from PySide6.QtQml import QQuickImageProvider
from PySide6.QtGui import QImage
from PySide6.QtCore import QSize


class MichiImageProvider(QQuickImageProvider):
    def __init__(self, cache_dir=None):
        super().__init__(QQuickImageProvider.Image)
        self._cache = {}

    def requestImage(self, id: str, size: QSize, requestedSize: QSize):
        w = requestedSize.width() if requestedSize and requestedSize.width() > 0 else 64
        h = requestedSize.height() if requestedSize and requestedSize.height() > 0 else 64

        if id in self._cache:
            return self._cache[id].scaled(w, h, aspectMode=True)

        img = QImage(w, h, QImage.Format_ARGB32)
        img.fill(0x0D0F16)

        from PySide6.QtGui import QPainter, QColor, QFont
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QColor(0x48, 0x50, 0x68))
        p.setFont(QFont("sans-serif", w // 4))
        glyph = id[:2].upper() if id else "MM"
        p.drawText(img.rect(), 0x0084, glyph)
        p.end()

        self._cache[id] = img
        return img
