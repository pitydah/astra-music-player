"""Michi hover — lift filter and shine overlay for interactive glass cards."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import (
    QColor, QLinearGradient, QPainter, QPainterPath,
)
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


class HoverLiftFilter(QObject):
    """Subtle lift + shine effect on hover for interactive cards."""

    def __init__(self, parent: QWidget, lift_delta: int = 2,
                 enable_shine: bool = True):
        super().__init__(parent)
        self._parent = parent
        self._lift_delta = lift_delta
        self._enable_shine = enable_shine
        self._hovered = False
        parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is not self._parent:
            return False
        t = event.type()
        if t == QEvent.Enter:
            self._hovered = True
            self._update_lift(True)
            if self._enable_shine:
                self._start_shine()
            return True
        elif t == QEvent.Leave:
            self._hovered = False
            self._update_lift(False)
            return True
        return False

    def _update_lift(self, hovered: bool):
        if not hasattr(self._parent, 'graphicsEffect'):
            return
        effect = self._parent.graphicsEffect()
        if isinstance(effect, QGraphicsDropShadowEffect):
            d = self._lift_delta if hovered else 0
            effect.setYOffset(4 + d)
            color = QColor(0, 0, 0, 80 if hovered else 60)
            effect.setColor(color)

    def _start_shine(self):
        pass  # shine is handled by ShineOverlay via the parent's paint


class ShineOverlay(QWidget):
    """Diagonal glossy highlight overlay for glass card hover."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("shineOverlay")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setVisible(False)
        self._active = False
        if parent:
            parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.parent():
            t = event.type()
            if t == QEvent.Enter:
                self.setGeometry(obj.rect())
                self._active = True
                self.setVisible(True)
                self.raise_()
                self.update()
            elif t == QEvent.Leave:
                self._active = False
                self.setVisible(False)
            elif t == QEvent.Resize:
                self.setGeometry(obj.rect())
        return False

    def paintEvent(self, event):
        if not self._active or not self.parent():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 18, 18)
        painter.setClipPath(path)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor(255, 255, 255, 0))
        grad.setColorAt(0.4, QColor(255, 255, 255, 12))
        grad.setColorAt(0.6, QColor(255, 255, 255, 12))
        grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(self.rect(), grad)
        painter.end()
