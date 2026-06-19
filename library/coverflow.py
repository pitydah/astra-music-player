"""CoverFlow — QGraphicsView-based carousel with OpenGL, physics, reflections."""

import math
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, Property, Signal,
    QRectF, QPointF,
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QLinearGradient, QPixmap,
    QTransform, QFont,
)
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsObject

from library.album_art import CoverFlowItem

try:
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
    HAVE_OPENGL = True
except ImportError:
    HAVE_OPENGL = False


class CoverItem(QGraphicsObject):
    """Single album cover with reflection in the carousel."""

    def __init__(self, pixmap: QPixmap, index: int, width: int = 260,
                 height: int = 260):
        super().__init__()
        self._index = index
        self._w = width
        self._h = height
        self._pixmap = pixmap.scaled(
            width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def boundingRect(self) -> QRectF:
        return QRectF(-self._w / 2, -self._h / 2, self._w, self._h * 2)

    def paint(self, painter: QPainter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Cover with rounded corners
        path = painter.clipPath()
        r = 8
        painter.setClipRect(0, 0, self._w, self._h)
        painter.drawPixmap(0, 0, self._pixmap)

        # Reflection (flipped vertically below the cover)
        painter.save()
        painter.translate(0, self._h * 2)
        painter.scale(1, -1)
        painter.setOpacity(0.3)
        painter.drawPixmap(0, 0, self._pixmap)
        painter.restore()

        # Fade gradient over reflection
        gradient = QLinearGradient(0, self._h, 0, self._h * 2)
        gradient.setColorAt(0.0, QColor(0, 0, 0, 90))
        gradient.setColorAt(0.3, QColor(0, 0, 0, 255))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 255))
        painter.fillRect(0, int(self._h), int(self._w), int(self._h), gradient)

    def update_transform(self, current_offset: float, view_width: float,
                         view_height: float):
        dist = self._index - current_offset
        transform = QTransform()
        max_rot = 65.0
        spacing_center = 200.0
        spacing_side = 60.0

        if abs(dist) < 0.1:
            self.setZValue(1000)
            cx = view_width / 2
            cy = view_height / 2 - 20
            transform.translate(cx, cy)
            transform.scale(1.0, 1.0)
        else:
            is_left = dist < 0
            ad = abs(dist)
            self.setZValue(1000 - int(ad * 10))
            rot = max_rot if ad >= 1.0 else max_rot * ad
            if is_left:
                rot = -rot

            transform.translate(self._w / 2, self._h / 2)
            transform.rotate(rot, Qt.YAxis)
            transform.translate(-self._w / 2, -self._h / 2)

            cx = view_width / 2
            cy = view_height / 2 - 20
            if is_left:
                cx -= spacing_center + spacing_side * (ad - 1)
            else:
                cx += spacing_center + spacing_side * (ad - 1)
            transform.translate(cx - self._w / 2, cy - self._h / 2)
            scale = 0.85
            transform.scale(scale, scale)

        self.setTransform(transform)


class CoverFlowWidget(QGraphicsView):
    selection_changed = Signal(int)
    double_clicked = Signal(int)
    clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        if HAVE_OPENGL:
            self.setViewport(QOpenGLWidget())
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setBackgroundBrush(QColor(13, 13, 20))
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._items: list[CoverFlowItem] = []
        self._cover_items: list[CoverItem] = []
        self._current = 0.0
        self._velocity = 0.0
        self._dragging = False
        self._last_x = 0.0
        self._cover_w = 260
        self._cover_h = 260

        self._phys_timer = QTimer(self)
        self._phys_timer.timeout.connect(self._update_physics)
        self._phys_timer.start(16)

        self._snap_anim = QPropertyAnimation(self, b"current_pos")
        self._snap_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._snap_anim.setDuration(350)

    def get_current(self) -> float:
        return self._current

    def set_current(self, value: float):
        self._current = value
        self._update_layout()

    current_pos = Property(float, get_current, set_current)

    # ── Public API (backward compatible) ──

    def set_items(self, items: list[CoverFlowItem]):
        self._items = items
        self._scene.clear()
        self._cover_items.clear()
        self._current = 0.0
        self._velocity = 0.0

        for i, item in enumerate(items):
            ci = CoverItem(item.pixmap, i, self._cover_w, self._cover_h)
            self._scene.addItem(ci)
            self._cover_items.append(ci)

        self._update_layout()

    def scroll_to(self, index: int, animated: bool = True):
        if not self._items:
            return
        index = max(0, min(index, len(self._items) - 1))
        if animated:
            self._snap_anim.setStartValue(self._current)
            self._snap_anim.setEndValue(float(index))
            self._snap_anim.start()
        else:
            self._current = float(index)
            self._update_layout()

    def _update_layout(self):
        if not self._cover_items:
            return
        for ci in self._cover_items:
            ci.update_transform(
                self._current,
                self.viewport().width(),
                self.viewport().height())
        idx = max(0, min(len(self._items) - 1, int(round(self._current))))
        self.selection_changed.emit(idx)

    # ── Physics ──

    def _update_physics(self):
        if self._dragging:
            return
        if abs(self._velocity) < 0.003:
            if abs(self._current - round(self._current)) > 0.01:
                self._trigger_snap()
            return
        self._velocity *= 0.92
        self._current += self._velocity
        self._update_layout()
        if abs(self._velocity) < 0.003:
            self._trigger_snap()

    def _trigger_snap(self):
        target = max(0, min(len(self._items) - 1, int(round(self._current))))
        self._snap_anim.stop()
        self._snap_anim.setStartValue(self._current)
        self._snap_anim.setEndValue(float(target))
        self._snap_anim.start()

    # ── Mouse events ──

    def mousePressEvent(self, event):
        self._dragging = True
        self._snap_anim.stop()
        self._last_x = event.position().x()
        self._velocity = 0.0

    def mouseMoveEvent(self, event):
        if not self._dragging:
            return
        dx = event.position().x() - self._last_x
        sensitivity = 0.004
        self._current -= dx * sensitivity
        self._velocity = -dx * sensitivity * 0.5
        self._last_x = event.position().x()
        self._update_layout()

    def mouseReleaseEvent(self, event):
        self._dragging = False
        if abs(self._velocity) < 0.01:
            self._trigger_snap()

    def mouseDoubleClickEvent(self, event):
        idx = int(round(self._current))
        if 0 <= idx < len(self._items):
            self.double_clicked.emit(idx)

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120.0
        self._current -= delta * 0.5
        max_i = max(0, len(self._items) - 1)
        self._current = max(0.0, min(float(max_i), self._current))
        self._update_layout()
        self._trigger_snap()
