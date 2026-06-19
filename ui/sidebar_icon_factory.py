"""Sidebar Icon Factory — QPainter-drawn at 96x96, downscaled with SmoothTransformation.

All drawing done at high resolution in a 24×24 logical space with safe
margins (5..19), then scaled down to target size for crisp, clip-free icons.
"""

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QPainterPath, QBrush

_RENDER_SIZE = 96  # internal high-res canvas


def _pen(color: str, width: float = 1.55) -> QPen:
    p = QPen(QColor(color), width)
    p.setCapStyle(Qt.RoundCap)
    p.setJoinStyle(Qt.RoundJoin)
    return p


def sidebar_pixmap(name: str, size: int = 22, color: str = "#FFFFFF") -> QPixmap:
    pix = QPixmap(_RENDER_SIZE, _RENDER_SIZE)
    pix.fill(Qt.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    scale = _RENDER_SIZE / 24.0
    painter.scale(scale, scale)

    pen = _pen(color, 1.55)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    key = name.replace("sidebar_", "")

    if key in ("library", "songs"):
        painter.drawLine(QPointF(14, 6), QPointF(14, 15.5))
        painter.drawLine(QPointF(14, 6), QPointF(18, 7.5))
        painter.drawEllipse(QRectF(8, 14, 5.5, 4.5))

    elif key == "albums":
        painter.drawRoundedRect(QRectF(5.5, 5.5, 13, 13), 2.5, 2.5)
        painter.drawEllipse(QRectF(9.2, 9.2, 5.6, 5.6))
        painter.drawEllipse(QRectF(11.5, 11.5, 1, 1))

    elif key == "folders":
        path = QPainterPath()
        path.moveTo(5.2, 8.2)
        path.lineTo(9.2, 8.2)
        path.lineTo(10.8, 10)
        path.lineTo(18.8, 10)
        path.lineTo(18.8, 17.8)
        path.lineTo(5.2, 17.8)
        path.closeSubpath()
        painter.drawPath(path)

    elif key in ("playlists", "playlist_item"):
        painter.drawLine(QPointF(8.2, 7.3), QPointF(17.8, 7.3))
        painter.drawLine(QPointF(8.2, 12), QPointF(17.8, 12))
        painter.drawLine(QPointF(8.2, 16.7), QPointF(15.8, 16.7))
        painter.drawEllipse(QRectF(5.2, 6.5, 1.6, 1.6))
        painter.drawEllipse(QRectF(5.2, 11.2, 1.6, 1.6))
        painter.drawEllipse(QRectF(5.2, 15.9, 1.6, 1.6))

    elif key == "radio":
        painter.drawEllipse(QRectF(10.2, 10.2, 3.6, 3.6))
        painter.drawArc(QRectF(7, 7, 10, 10), 35 * 16, 110 * 16)
        painter.drawArc(QRectF(5, 5, 14, 14), 35 * 16, 110 * 16)
        painter.drawArc(QRectF(7, 7, 10, 10), 215 * 16, 110 * 16)
        painter.drawArc(QRectF(5, 5, 14, 14), 215 * 16, 110 * 16)

    elif key == "servers":
        painter.drawRoundedRect(QRectF(5.5, 6.5, 13, 4.2), 1.5, 1.5)
        painter.drawRoundedRect(QRectF(5.5, 13.3, 13, 4.2), 1.5, 1.5)
        painter.drawEllipse(QRectF(7.2, 7.7, 1.3, 1.3))
        painter.drawEllipse(QRectF(7.2, 14.5, 1.3, 1.3))

    elif key == "devices":
        painter.drawRoundedRect(QRectF(5.5, 6.2, 13, 9.5), 2, 2)
        painter.drawLine(QPointF(9, 18.2), QPointF(15, 18.2))
        painter.drawLine(QPointF(12, 15.8), QPointF(12, 18.2))

    elif key == "mix":
        painter.drawEllipse(QRectF(5.5, 5.5, 4.6, 4.6))
        painter.drawEllipse(QRectF(13.9, 5.5, 4.6, 4.6))
        painter.drawEllipse(QRectF(9.7, 13.9, 4.6, 4.6))
        painter.drawLine(QPointF(9, 9), QPointF(11, 14))
        painter.drawLine(QPointF(15, 9), QPointF(13, 14))

    elif key == "unplayed":
        painter.drawEllipse(QRectF(5.5, 5.5, 13, 13))
        painter.drawLine(QPointF(12, 8.4), QPointF(12, 12))
        painter.drawLine(QPointF(12, 12), QPointF(15, 14))

    elif key == "popular":
        path = QPainterPath()
        path.moveTo(12, 5.8)
        path.lineTo(13.7, 10)
        path.lineTo(18.1, 10.5)
        path.lineTo(14.8, 13.5)
        path.lineTo(15.8, 17.8)
        path.lineTo(12, 15.4)
        path.lineTo(8.2, 17.8)
        path.lineTo(9.2, 13.5)
        path.lineTo(5.9, 10.5)
        path.lineTo(10.3, 10)
        path.closeSubpath()
        painter.drawPath(path)

    elif key == "identifier":
        painter.drawEllipse(QRectF(6, 6, 8.2, 8.2))
        painter.drawLine(QPointF(13, 13), QPointF(18, 18))
        painter.drawLine(QPointF(8.2, 10.1), QPointF(12, 10.1))
        painter.drawLine(QPointF(10.1, 8.2), QPointF(10.1, 12))

    elif key == "add":
        painter.drawLine(QPointF(12, 6.5), QPointF(12, 17.5))
        painter.drawLine(QPointF(6.5, 12), QPointF(17.5, 12))

    elif key == "navidrome":
        painter.drawEllipse(QRectF(5.8, 5.8, 12.4, 12.4))
        painter.drawEllipse(QRectF(8.8, 8.8, 6.4, 6.4))
        painter.drawEllipse(QRectF(11.3, 11.3, 1.4, 1.4))

    elif key == "jellyfin":
        path = QPainterPath()
        path.moveTo(12, 6)
        path.lineTo(18, 17.5)
        path.lineTo(6, 17.5)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawEllipse(QRectF(10.4, 12.4, 3.2, 3.2))

    else:
        painter.drawEllipse(QRectF(6, 6, 12, 12))

    painter.end()

    return pix.scaled(
        size,
        size,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )
