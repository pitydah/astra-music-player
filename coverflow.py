"""CoverFlow 3D — QPainter-based carousel with physics scroll and reflections.

Uses QTransform for pseudo-3D perspective. Reliable on all setups.
Physics: momentum, friction, snap. Interactions: click, drag, wheel, keyboard.
"""

import math
import time
import numpy as np
from PySide6.QtCore import (
    Qt, QTimer, QPointF, QRectF, QPropertyAnimation, QEasingCurve,
    Property, Signal,
)
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QLinearGradient, QRadialGradient,
    QPixmap, QTransform, QPainterPath, QBrush,
)
from PySide6.QtWidgets import QWidget

from album_art import CoverFlowItem


class CoverFlowWidget(QWidget):
    """3D CoverFlow carousel with physics-driven scrolling."""

    selection_changed = Signal(int)
    double_clicked = Signal(int)
    clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[CoverFlowItem] = []
        self._current = 0.0          # float position for smooth physics
        self._target = 0
        self._velocity = 0.0
        self._dragging = False
        self._drag_start = QPointF()
        self._drag_last = QPointF()
        self._hover_index = -1
        self._angle = 55.0           # max rotation angle for side covers
        self._spacing = 170.0        # horizontal spacing between covers
        self._cover_size = 240       # max cover size in px
        self._anim = None
        self._last_time = time.time()
        self._snap_enabled = True
        self._show_reflection = True

        # Info overlay
        self._overlay_opacity = 0.0
        self._overlay_target = 0.0

        # Cached pixmaps (scaled)
        self._cache: dict[int, QPixmap] = {}

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumHeight(300)
        self.setStyleSheet("background: rgba(13, 13, 20, 230);")

        # Physics timer
        self._phys_timer = QTimer(self)
        self._phys_timer.timeout.connect(self._update_physics)
        self._phys_timer.start(16)

        # Overlay timer
        self._overlay_timer = QTimer(self)
        self._overlay_timer.timeout.connect(self._update_overlay)
        self._overlay_timer.start(30)

    # ═══════════ Public API ═══════════

    def set_items(self, items: list[CoverFlowItem]):
        self._items = items
        self._cache.clear()
        self._current = 0.0
        self._target = 0
        self._velocity = 0.0
        self._show_overlay()
        self._preload_visible()
        self.update()

    def scroll_to(self, index: int, animated: bool = True):
        index = max(0, min(index, len(self._items) - 1))
        self._target = index

        if animated:
            self._anim = QPropertyAnimation(self, b"current_pos")
            self._anim.setDuration(400)
            self._anim.setStartValue(self._current)
            self._anim.setEndValue(float(index))
            self._anim.setEasingCurve(QEasingCurve.OutCubic)
            self._anim.finished.connect(self._on_anim_done)
            self._anim.start()
        else:
            self._current = float(index)
            self._show_overlay()
            self.update()

        self._preload_visible()

    def scroll_next(self):
        if self._current < len(self._items) - 1:
            self.scroll_to(int(self._current) + 1)

    def scroll_prev(self):
        if self._current > 0:
            self.scroll_to(int(self._current) - 1)

    def _on_anim_done(self):
        self._anim = None
        self._show_overlay()
        idx = int(round(self._current))
        self.selection_changed.emit(idx)

    # ═══════════ Properties ═══════════

    def _get_current_pos(self):
        return self._current

    def _set_current_pos(self, value):
        self._current = value
        self._preload_visible()
        self.update()

    current_pos = Property(float, _get_current_pos, _set_current_pos)

    # ═══════════ Physics ═══════════

    def _update_physics(self):
        if not self._items or self._dragging or self._anim:
            return

        if self._anim and self._anim.state() == QPropertyAnimation.Running:
            return

        dt = time.time() - self._last_time
        self._last_time = time.time()
        if dt > 0.1:
            dt = 0.016

        friction = 0.95
        min_vel = 25.0

        self._velocity *= friction ** (dt * 60)
        self._current += self._velocity * dt
        self._current = max(0.0, min(len(self._items) - 1.0, self._current))

        if abs(self._velocity) < min_vel and self._snap_enabled:
            target = round(self._current)
            diff = target - self._current
            if abs(diff) < 0.01:
                self._current = float(target)
                self._velocity = 0.0
                if target != self._target:
                    self._target = int(target)
                    self._show_overlay()
                    self.selection_changed.emit(int(target))
            else:
                self._current += diff * 0.3

        self._preload_visible()
        self.update()

    # ═══════════ Rendering ═══════════

    def _preload_visible(self):
        center = int(round(self._current))
        for i in range(max(0, center - 8), min(len(self._items), center + 9)):
            if i not in self._cache:
                pix = self._items[i].pixmap
                if pix and not pix.isNull():
                    self._cache[i] = pix.scaled(
                        self._cover_size, self._cover_size,
                        Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def _get_cached(self, idx: int) -> QPixmap:
        if idx in self._cache:
            return self._cache[idx]
        pix = self._items[idx].pixmap
        if pix.isNull():
            return QPixmap()
        scaled = pix.scaled(self._cover_size, self._cover_size,
                           Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._cache[idx] = scaled
        return scaled

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if not self._items:
            painter.end()
            return

        w, h = self.width(), self.height()
        center = int(round(self._current))
        mid_x = w / 2
        mid_y = h * 0.42

        # ── Vignette ──
        self._draw_vignette(painter, w, h)

        # ── Render covers back-to-front ──
        visible = 6
        to_render = []

        for offset in range(-visible, visible + 1):
            idx = center + offset
            if idx < 0 or idx >= len(self._items):
                continue
            x, y, scale, angle, opacity, z_depth = self._compute_position(
                offset, mid_x, mid_y, w)
            to_render.append((z_depth, idx, offset, x, y, scale, angle, opacity))

        to_render.sort(key=lambda t: -t[0])  # farthest first

        for _, idx, offset, x, y, scale, angle, opacity in to_render:
            pix = self._get_cached(idx)
            if pix.isNull():
                continue

            painter.save()
            painter.setOpacity(opacity)

            # Transform: translate → rotate Y → scale → draw centered
            transform = QTransform()
            transform.translate(x, y)
            cos_a = math.cos(math.radians(offset * self._angle))
            if cos_a > 0:
                transform.scale(cos_a * scale, scale)
            else:
                transform.scale(0.01, scale)
            painter.setTransform(transform)

            pw, ph = pix.width(), pix.height()
            painter.drawPixmap(QPointF(-pw / 2, -ph / 2), pix)

            # ── Reflection ──
            if self._show_reflection:
                gradient = QLinearGradient(0, ph / 2, 0, ph + ph * 0.3)
                gradient.setColorAt(0, QColor(255, 255, 255, 50))
                gradient.setColorAt(1, QColor(255, 255, 255, 0))
                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.NoPen)
                # Mirror vertically
                ref_transform = QTransform()
                ref_transform.translate(x, y)
                ref_transform.scale(cos_a * scale if cos_a > 0 else 0.01,
                                    -scale * 0.35)
                painter.setTransform(ref_transform)
                painter.drawPixmap(QPointF(-pw / 2, ph / 2), pix,
                                  QRectF(0, 0, pw, ph * 0.35))

            painter.restore()

        # ── Info overlay ──
        self._draw_overlay(painter, w, h)

        painter.end()

    def _compute_position(self, offset: int, mid_x: float, mid_y: float, w: float):
        """Compute position, scale, angle, opacity for a cover at given offset."""
        scale = 1.0 - abs(offset) * 0.12
        scale = max(0.4, scale)
        angle = offset * self._angle
        opacity = 1.0 - abs(offset) * 0.12
        opacity = max(0.25, opacity)
        x = mid_x + offset * self._spacing - (offset ** 3) * 3.0
        y = mid_y + abs(offset) * 18.0
        z_depth = abs(offset)
        return x, y, scale, angle, opacity, z_depth

    def _draw_vignette(self, painter: QPainter, w: int, h: int):
        left = QLinearGradient(0, 0, w * 0.35, 0)
        left.setColorAt(0, QColor(0, 0, 0, 120))
        left.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(0, 0, int(w * 0.35), h, QBrush(left))

        right = QLinearGradient(w, 0, w * 0.65, 0)
        right.setColorAt(0, QColor(0, 0, 0, 120))
        right.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(int(w * 0.65), 0, int(w * 0.35), h, QBrush(right))

    # ═══════════ Overlay ═══════════

    def _show_overlay(self):
        self._overlay_target = 1.0

    def _update_overlay(self):
        if abs(self._overlay_opacity - self._overlay_target) < 0.003:
            return
        self._overlay_opacity += (self._overlay_target - self._overlay_opacity) * 0.12
        self.update()

    def _draw_overlay(self, painter: QPainter, w: int, h: int):
        if self._overlay_opacity < 0.02 and self._overlay_target < 0.02:
            return

        idx = int(round(self._current))
        if idx < 0 or idx >= len(self._items):
            return

        item = self._items[idx]
        painter.save()
        painter.setOpacity(self._overlay_opacity * 0.95)

        y_base = h * 0.8
        box_w = min(w * 0.5, 500)
        box_x = (w - box_w) / 2

        # Background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(10, 10, 20, 160))
        painter.drawRoundedRect(QRectF(box_x, y_base - 6, box_w, 70), 10, 10)

        # Title
        painter.setPen(QColor("#ffffff"))
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(box_x + 10, y_base + 2, box_w - 20, 26),
                        Qt.AlignHCenter, item.title[:45])

        # Subtitle
        painter.setPen(QColor("#a0a0c0"))
        font.setPointSize(11)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(QRectF(box_x + 10, y_base + 28, box_w - 20, 24),
                        Qt.AlignHCenter, item.subtitle[:70])

        # Page dots
        total = len(self._items)
        if total > 1:
            dot_y = y_base + 58
            dot_start = w / 2 - total * 8
            for i in range(total):
                if i == idx:
                    painter.setBrush(QColor("#FF7A00"))
                    r = 4
                else:
                    painter.setBrush(QColor("#3a3a4e"))
                    r = 3
                painter.drawEllipse(QPointF(dot_start + i * 16, dot_y), r, r)

        painter.restore()

    # ═══════════ Mouse Events ═══════════

    def mousePressEvent(self, event):
        self._dragging = True
        self._drag_start = event.position()
        self._drag_last = event.position()
        self._velocity = 0.0
        self._snap_enabled = True
        self._overlay_target = 0.0

    def mouseMoveEvent(self, event):
        if self._dragging:
            dx = event.position().x() - self._drag_last.x()
            self._velocity = -dx * 4.0
            self._current += -dx * 0.04 / (self._spacing / 170.0)
            self._current = max(0.0, min(len(self._items) - 1.0, self._current))
            self._drag_last = event.position()
            self.update()

    def mouseReleaseEvent(self, event):
        if not self._dragging:
            return
        dx = event.position().x() - self._drag_start.x()
        dy = event.position().y() - self._drag_start.y()

        if abs(dx) < 4 and abs(dy) < 4:
            # Click
            cover_idx = self._find_clicked(event.position())
            if cover_idx >= 0:
                if cover_idx != int(round(self._current)):
                    self.scroll_to(cover_idx)
                else:
                    self.clicked.emit(cover_idx)
        else:
            dt = max(time.time() - self._last_time, 0.001)
            self._velocity = -dx * 2.5 / dt
            self._snap_enabled = True
            self._show_overlay()

        self._dragging = False

    def mouseDoubleClickEvent(self, event):
        cover_idx = self._find_clicked(event.position())
        if cover_idx >= 0:
            if round(self._current) != cover_idx:
                self.scroll_to(cover_idx, animated=True)
            self.double_clicked.emit(cover_idx)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if abs(delta) > 0:
            if delta > 0:
                self.scroll_prev()
            else:
                self.scroll_next()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.scroll_prev()
        elif event.key() == Qt.Key_Right:
            self.scroll_next()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            idx = round(self._current)
            if 0 <= idx < len(self._items):
                self.double_clicked.emit(idx)
        else:
            super().keyPressEvent(event)

    def _find_clicked(self, pos: QPointF) -> int:
        center = int(round(self._current))
        mid_x = self.width() / 2

        for offset in range(-3, 4):
            idx = center + offset
            if idx < 0 or idx >= len(self._items):
                continue
            x = mid_x + offset * self._spacing - (offset ** 3) * 3.0
            scale = 1.0 - abs(offset) * 0.12
            cover_w = self._cover_size * max(0.4, scale)
            if abs(pos.x() - x) < cover_w / 2:
                return idx
        return -1
