"""Icon Renderer — SVG to QPixmap with proper scaling, centering, and alpha cleanup."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter, QImage, QColor
from PySide6.QtSvg import QSvgRenderer


def _clear_near_transparent_pixels(image: QImage, threshold: int = 2,
                                   edge: int = 0) -> None:
    """Clear RGB garbage from transparent pixels and optional edge border.

    threshold: clear pixels with alpha <= this value
    edge: if >0, always clear pixels within edge px of the image border
    """
    if image.isNull():
        return
    w, h = image.width(), image.height()
    for y in range(h):
        for x in range(w):
            c = image.pixelColor(x, y)
            is_edge = edge > 0 and (x < edge or x >= w - edge
                                    or y < edge or y >= h - edge)
            if is_edge or c.alpha() <= threshold:
                image.setPixelColor(x, y, QColor(0, 0, 0, 0))


def render_svg_icon(path: str, size: int = 24, padding: int = 2,
                    edge: int = 1) -> QPixmap:
    """Render an SVG with transparent alpha-safe supersampling.

    padding: margin around content in pre-scale pixels (0 for action icons)
    edge: px border to clear on the final image (1 for sidebar, 0 for action)
    """
    scale_factor = 4
    canvas = max(1, size * scale_factor)
    pad = max(0, padding * scale_factor)

    image = QImage(canvas, canvas, QImage.Format_ARGB32_Premultiplied)
    image.fill(Qt.transparent)

    if not path:
        return QPixmap.fromImage(image).scaled(
            size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    renderer = QSvgRenderer(path)
    if not renderer.isValid():
        return QPixmap.fromImage(image).scaled(
            size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    view = renderer.viewBoxF()
    target_size = max(1, canvas - pad * 2)

    if view.isEmpty() or view.width() <= 0 or view.height() <= 0:
        target_rect = QRectF(pad, pad, target_size, target_size)
    else:
        scale = min(target_size / view.width(), target_size / view.height())
        w = view.width() * scale
        h = view.height() * scale
        x = (canvas - w) / 2
        y = (canvas - h) / 2
        target_rect = QRectF(x, y, w, h)

    renderer.render(painter, target_rect)
    painter.end()

    _clear_near_transparent_pixels(image, threshold=2)

    final = image.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    final = final.convertToFormat(QImage.Format_ARGB32_Premultiplied)
    _clear_near_transparent_pixels(final, threshold=2, edge=edge)

    return QPixmap.fromImage(final)
