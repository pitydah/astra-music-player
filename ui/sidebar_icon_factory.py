"""Sidebar Icon Factory — QPainter-drawn icons, no SVG dependency.

All icons are drawn in a 24x24 coordinate space with 1.8px stroke,
then scaled to the target size. Safe zone: 4..20.
"""

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QPainterPath, QBrush


def _pen(color: str, width: float = 1.8) -> QPen:
    p = QPen(QColor(color), width)
    p.setCapStyle(Qt.RoundCap)
    p.setJoinStyle(Qt.RoundJoin)
    return p


def sidebar_pixmap(name: str, size: int = 22, color: str = "#FFFFFF") -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)

    scale = size / 24.0
    painter.scale(scale, scale)

    pen = _pen(color, 1.8)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    key = name.replace("sidebar_", "")

    if key in ("library", "songs"):
        # note musical
        painter.drawLine(QPointF(14, 5), QPointF(14, 16))
        painter.drawLine(QPointF(14, 5), QPointF(19, 7))
        painter.drawEllipse(QRectF(8, 14, 6, 4.8))

    elif key == "albums":
        painter.drawRoundedRect(QRectF(5, 5, 14, 14), 2.5, 2.5)
        painter.drawEllipse(QRectF(9, 9, 6, 6))
        painter.drawPoint(QPointF(12, 12))

    elif key == "folders":
        path = QPainterPath()
        path.moveTo(4.5, 8)
        path.lineTo(9, 8)
        path.lineTo(10.8, 10)
        path.lineTo(19.5, 10)
        path.lineTo(19.5, 18)
        path.lineTo(4.5, 18)
        path.closeSubpath()
        painter.drawPath(path)

    elif key in ("playlists", "playlist_item"):
        painter.drawLine(QPointF(8, 7), QPointF(18, 7))
        painter.drawLine(QPointF(8, 12), QPointF(18, 12))
        painter.drawLine(QPointF(8, 17), QPointF(15, 17))
        painter.drawEllipse(QRectF(4.5, 6, 1.8, 1.8))
        painter.drawEllipse(QRectF(4.5, 11, 1.8, 1.8))
        painter.drawEllipse(QRectF(4.5, 16, 1.8, 1.8))

    elif key == "radio":
        painter.drawEllipse(QRectF(10, 10, 4, 4))
        painter.drawArc(QRectF(6, 6, 12, 12), 35 * 16, 110 * 16)
        painter.drawArc(QRectF(3.5, 3.5, 17, 17), 35 * 16, 110 * 16)
        painter.drawArc(QRectF(6, 6, 12, 12), 215 * 16, 110 * 16)
        painter.drawArc(QRectF(3.5, 3.5, 17, 17), 215 * 16, 110 * 16)

    elif key == "servers":
        painter.drawRoundedRect(QRectF(5, 6, 14, 4.5), 1.5, 1.5)
        painter.drawRoundedRect(QRectF(5, 13.5, 14, 4.5), 1.5, 1.5)
        painter.drawEllipse(QRectF(7, 7.3, 1.5, 1.5))
        painter.drawEllipse(QRectF(7, 14.8, 1.5, 1.5))

    elif key == "devices":
        painter.drawRoundedRect(QRectF(5, 6, 14, 10), 2, 2)
        painter.drawLine(QPointF(9, 19), QPointF(15, 19))
        painter.drawLine(QPointF(12, 16), QPointF(12, 19))

    elif key == "mix":
        painter.drawEllipse(QRectF(5, 5, 5, 5))
        painter.drawEllipse(QRectF(14, 5, 5, 5))
        painter.drawEllipse(QRectF(9.5, 14, 5, 5))
        painter.drawLine(QPointF(9, 9), QPointF(11, 14))
        painter.drawLine(QPointF(15, 9), QPointF(13, 14))

    elif key == "unplayed":
        painter.drawEllipse(QRectF(5, 5, 14, 14))
        painter.drawLine(QPointF(12, 8), QPointF(12, 12))
        painter.drawLine(QPointF(12, 12), QPointF(15, 14))

    elif key == "popular":
        path = QPainterPath()
        path.moveTo(12, 5)
        path.lineTo(14, 10)
        path.lineTo(19, 10.5)
        path.lineTo(15.2, 14)
        path.lineTo(16.4, 19)
        path.lineTo(12, 16.2)
        path.lineTo(7.6, 19)
        path.lineTo(8.8, 14)
        path.lineTo(5, 10.5)
        path.lineTo(10, 10)
        path.closeSubpath()
        painter.drawPath(path)

    elif key == "identifier":
        painter.drawEllipse(QRectF(5.5, 5.5, 9, 9))
        painter.drawLine(QPointF(13, 13), QPointF(18.5, 18.5))
        painter.drawLine(QPointF(8, 10), QPointF(12, 10))
        painter.drawLine(QPointF(10, 8), QPointF(10, 12))

    elif key in ("add",):
        painter.drawLine(QPointF(12, 6), QPointF(12, 18))
        painter.drawLine(QPointF(6, 12), QPointF(18, 12))

    elif key == "navidrome":
        painter.drawEllipse(QRectF(5, 5, 14, 14))
        painter.drawEllipse(QRectF(8.5, 8.5, 7, 7))
        painter.drawEllipse(QRectF(11, 11, 2, 2))

    elif key == "jellyfin":
        path = QPainterPath()
        path.moveTo(12, 5)
        path.lineTo(19, 18)
        path.lineTo(5, 18)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawEllipse(QRectF(10.2, 12.5, 3.6, 3.6))

    else:
        painter.drawEllipse(QRectF(6, 6, 12, 12))

    painter.end()
    return pix
