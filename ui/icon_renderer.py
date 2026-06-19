"""Icon Renderer — SVG to QPixmap with proper scaling and centering."""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer


def render_svg_icon(path: str, size: int = 20) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    if not path:
        return pixmap

    renderer = QSvgRenderer(path)
    if not renderer.isValid():
        return pixmap

    view = renderer.viewBoxF()

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)

    if view.isEmpty():
        renderer.render(painter, QRectF(0, 0, size, size))
        painter.end()
        return pixmap

    scale = min(size / view.width(), size / view.height())
    w = view.width() * scale
    h = view.height() * scale
    x = (size - w) / 2
    y = (size - h) / 2

    renderer.render(painter, QRectF(x, y, w, h))
    painter.end()

    return pixmap
