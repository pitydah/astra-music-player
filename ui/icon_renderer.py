"""Icon Renderer — SVG to QPixmap with proper alpha, scaling, and centering."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QImage, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer


def render_svg_icon(path: str, size: int = 24, padding: int = 2,
                    scale_factor: int = 4) -> QPixmap:
    """Render an SVG to QPixmap with supersampling and alpha sanitization.

    Uses QImage + scale_factor supersampling to avoid alpha premult halos
    and black borders around native_color SVGs.
    """
    internal = size * scale_factor

    # Create a fully transparent QImage for proper alpha channel
    image = QImage(internal, internal, QImage.Format_ARGB32_Premultiplied)
    image.fill(Qt.transparent)

    if not path:
        pix = QPixmap.fromImage(image)
        return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    renderer = QSvgRenderer(path)
    if not renderer.isValid():
        pix = QPixmap.fromImage(image)
        return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    pad = padding * scale_factor
    target = max(1, internal - pad * 2)
    view = renderer.viewBoxF()

    if view.isEmpty() or view.width() <= 0 or view.height() <= 0:
        renderer.render(painter, QRectF(pad, pad, target, target))
    else:
        s = min(target / view.width(), target / view.height())
        w = view.width() * s
        h = view.height() * s
        x = (internal - w) / 2
        y = (internal - h) / 2
        renderer.render(painter, QRectF(x, y, w, h))

    painter.end()

    # Sanitize: clean dark edge pixels before scaling
    _sanitize_alpha(image)

    pix = QPixmap.fromImage(image)
    result = pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    # Second pass: sanitize the final pixmap too (catches spread from scaling)
    final_image = result.toImage().convertToFormat(QImage.Format_ARGB32_Premultiplied)
    _sanitize_alpha(final_image)
    return QPixmap.fromImage(final_image)


def _sanitize_alpha(image: QImage):
    """Clean edge artifacts and nearly-transparent pixels from SVG rendering."""
    if image.isNull() or image.format() != QImage.Format_ARGB32_Premultiplied:
        return
    try:
        w, h = image.width(), image.height()
        border = max(2, min(w, h) // 16)  # proportional edge cleanup
        for y in range(h):
            line = image.scanLine(y)
            if line is None:
                continue
            for x in range(0, w * 4, 4):
                alpha = line[x + 3]
                is_edge = (x // 4 < border or x // 4 >= w - border or
                           y < border or y >= h - border)
                if is_edge or alpha <= 30:
                    line[x] = 0
                    line[x + 1] = 0
                    line[x + 2] = 0
                    line[x + 3] = 0
    except Exception:
        pass
