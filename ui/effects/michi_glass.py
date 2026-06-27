"""Michi glass — acrylic brush with blur, noise, specular, and card shadow.

Provides the glassmorphism visual foundation for AcrylicGlassFrame cards.
"""

from __future__ import annotations

from PySide6.QtCore import QChildEvent, QEvent, QRectF, Qt
from PySide6.QtGui import (
    QColor, QLinearGradient, QPainter, QPainterPath,
    QPen, QPixmap,
)
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


class AcrylicBrush:
    """Paints a translucent glass surface with tint, specular highlight, and border.

    Mimics acrylic/matte glass material used on macOS/Windows 11 acrylic cards.
    """

    def __init__(self, tint_opacity: float = 0.06,
                 specular_opacity: float = 18,
                 tint_color: QColor | None = None):
        self._tint_opacity = tint_opacity
        self._specular_opacity = specular_opacity
        self._tint_color = tint_color or QColor(255, 255, 255)

    def paint(self, widget: QWidget, painter: QPainter,
              clip_radius: int = 18):
        rect = QRectF(widget.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, clip_radius, clip_radius)
        painter.setClipPath(path)

        # Tinted translucent base
        tint = QColor(self._tint_color)
        tint.setAlphaF(self._tint_opacity)
        painter.fillRect(rect, tint)

        # Specular highlight (thin top edge)
        spec = QLinearGradient(0, 0, 0, rect.height() * 0.3)
        spec.setColorAt(0.0, QColor(255, 255, 255, max(0, min(255, int(self._specular_opacity)))))
        spec.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(rect, spec)

        # Subtle border
        border = QPen(QColor(255, 255, 255, 18), 1.0)
        painter.setPen(border)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5),
                                clip_radius, clip_radius)


class NoiseOverlay(QWidget):
    """Subtle noise/grain texture overlay for glass surfaces."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        if parent:
            self.setParent(parent)
        self.setObjectName("noiseOverlay")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._cached_noise: QPixmap | None = None
        if parent:
            parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.parent():
            if isinstance(event, QChildEvent):
                return super().eventFilter(obj, event)
            if event.type() == QEvent.Resize:
                self.setGeometry(obj.rect())
                self._generate_noise(obj.width(), obj.height())
        return super().eventFilter(obj, event)

    def _generate_noise(self, w: int, h: int):
        from PySide6.QtGui import QImage
        import random as _r
        _r.seed(42)
        img = QImage(w, h, QImage.Format_Grayscale8)
        for y in range(h):
            for x in range(w):
                v = _r.randint(0, 7)
                img.setPixel(x, y, v)
        self._cached_noise = QPixmap.fromImage(img)

    def paintEvent(self, event):
        if self._cached_noise is None:
            return
        painter = QPainter(self)
        painter.setOpacity(0.35)
        painter.drawPixmap(0, 0, self._cached_noise)
        painter.end()


def apply_card_shadow(widget: QWidget):
    """Apply a subtle drop shadow to a card widget."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(24)
    shadow.setXOffset(0)
    shadow.setYOffset(4)
    shadow.setColor(QColor(0, 0, 0, 60))
    widget.setGraphicsEffect(shadow)
