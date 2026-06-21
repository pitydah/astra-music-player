"""SidebarPanel — dark glass background panel with QPainter."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QRadialGradient, QPen
from PySide6.QtWidgets import QWidget

from ui.sidebar.sidebar_tokens import SIDEBAR_PANEL_RADIUS


class SidebarPanel(QWidget):
    """Dark glass panel with subtle gradient, border, highlight, and blue glow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarGlass")
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_StyledBackground, False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        r = SIDEBAR_PANEL_RADIUS

        # Base dark gradient
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, QColor(31, 35, 48, 224))
        grad.setColorAt(0.4, QColor(20, 24, 34, 214))
        grad.setColorAt(1.0, QColor(10, 13, 22, 224))

        painter.setBrush(grad)
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawRoundedRect(rect, r, r)

        # Subtle blue glow from top-left
        glow = QRadialGradient(rect.topLeft(), rect.width())
        glow.setColorAt(0.0, QColor(80, 120, 255, 18))
        glow.setColorAt(0.6, QColor(0, 0, 0, 0))
        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, r, r)

        painter.end()
