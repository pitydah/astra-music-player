"""CoverFlow — QGraphicsView-based carousel with OpenGL, physics, reflections."""

import math
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QVariantAnimation,
    Property, Signal, QRectF, QPointF,
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QLinearGradient, QRadialGradient, QPixmap,
    QTransform, QFont, QPainterPath,
)
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsObject,
    QGraphicsTextItem, QGraphicsOpacityEffect,
)

from library.album_art import CoverFlowItem

try:
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
    HAVE_OPENGL = True
except ImportError:
    HAVE_OPENGL = False


class CoverItem(QGraphicsObject):
    """Single album cover with reflection in the carousel."""

    def __init__(self, pixmap: QPixmap | None, index: int, width: int = 260,
                 height: int = 260):
        super().__init__()
        self._index = index
        self._w = width
        self._h = height
        self._fade_alpha = 1.0

        # Placeholder for async loading
        if pixmap is None or pixmap.isNull():
            self._placeholder = QPixmap(width, height)
            self._placeholder.fill(QColor(40, 40, 45))
            self._pixmap = self._placeholder
        else:
            self._placeholder = QPixmap()
            self._pixmap = pixmap.scaled(
                 width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self._cached = None  # lazy — generated on first paint

    def _ensure_cached(self):
        if self._cached is None:
            self._cached = self._generate_reflection()

    def _generate_reflection(self) -> QPixmap:
        cached = QPixmap(self._w, self._h * 2)
        cached.fill(Qt.transparent)
        p = QPainter(cached)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        # Rounded corners (Sleeve Effect)
        radius = 14.0
        path = QPainterPath()
        path.addRoundedRect(0, 0, self._w, self._h, radius, radius)

        # Cover with clipping
        p.save()
        p.setClipPath(path)
        p.drawPixmap(0, 0, self._pixmap)
        p.restore()

        # Subtle white border (premium)
        p.setPen(QPen(QColor(255, 255, 255, 28), 1.0))
        p.drawPath(path)

        # Reflection ("Wet Floor") — softer
        p.save()
        p.translate(0, self._h * 2)
        p.scale(1, -1)
        p.setOpacity(0.22)
        p.setClipPath(path)
        p.drawPixmap(0, 0, self._pixmap)
        p.restore()

        # Non-linear fade gradient (background-matched)
        grad = QLinearGradient(0, self._h, 0, self._h * 2)
        grad.setColorAt(0.0, QColor(13, 13, 20, 100))
        grad.setColorAt(0.15, QColor(13, 13, 20, 180))
        grad.setColorAt(0.4, QColor(13, 13, 20, 255))
        grad.setColorAt(1.0, QColor(13, 13, 20, 255))
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        p.fillRect(0, self._h, self._w, self._h, grad)
        p.end()
        return cached

    def set_real_cover(self, pixmap: QPixmap):
        """Animated fade from placeholder to real cover (anti-pop-in)."""
        if pixmap is None or pixmap.isNull():
            return
        self._real_cover = pixmap.scaled(
            self._w, self._h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._fade_alpha = 0.0
        anim = QVariantAnimation()
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.valueChanged.connect(self._on_fade_step)
        anim.finished.connect(self._on_fade_done)
        anim.start()
        self._fade_anim = anim  # keep reference

    def _on_fade_step(self, value: float):
        self._fade_alpha = value
        self.update()

    def _on_fade_done(self):
        self._pixmap = self._real_cover
        self._fade_alpha = 1.0
        self._placeholder = QPixmap()
        self._cached = self._generate_reflection()
        self.update()

    def boundingRect(self) -> QRectF:
        return QRectF(-self._w / 2, -self._h / 2, self._w, self._h * 2)

    def paint(self, painter: QPainter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Draw cached cover + reflection (rounded corners + border baked in)
        self._ensure_cached()
        painter.drawPixmap(0, 0, self._cached)

        # Floor shadow for center item
        if hasattr(self, '_is_center') and self._is_center:
            painter.save()
            shadow = QRadialGradient(self._w / 2, self._h, self._w * 0.55)
            shadow.setColorAt(0.0, QColor(0, 0, 0, 50))
            shadow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(shadow)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(self._w / 2, self._h),
                               self._w * 0.4, 10)
            painter.restore()

        # Fade-in overlay: if real_cover is loading, crossfade over cached
        if hasattr(self, '_real_cover') and self._fade_alpha < 1.0:
            painter.save()
            painter.setOpacity(self._fade_alpha)
            painter.drawPixmap(0, 0, self._real_cover)
            painter.translate(0, self._h * 2)
            painter.scale(1, -1)
            painter.setOpacity(0.3 * self._fade_alpha)
            painter.drawPixmap(0, 0, self._real_cover)
            painter.restore()

        # Depth shading for side covers
        if hasattr(self, '_darken_alpha') and self._darken_alpha > 0:
            painter.save()
            painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
            painter.fillRect(0, 0, int(self._w), int(self._h * 2),
                            QColor(0, 0, 0, self._darken_alpha))
            painter.restore()

    def update_transform(self, current_offset: float, view_width: float,
                         view_height: float, velocity: float = 0.0):
        dist = self._index - current_offset
        transform = QTransform()
        max_rot = 58.0
        spacing_center = 185.0
        spacing_side = 34.0
        zoom_out = min(0.15, abs(velocity) * 2.0)

        if abs(dist) < 0.1:
            self.setZValue(1000)
            cx = view_width / 2
            cy = view_height / 2 - 24
            transform.translate(cx, cy)
            transform.scale(1.0 - zoom_out, 1.0 - zoom_out)
        else:
            is_left = dist < 0
            ad = abs(dist)
            self._darken_alpha = min(115, int(ad * 32))
            self.setZValue(1000 - int(ad * 10))
            flip_factor = min(1.0, math.pow(ad, 0.35))
            rot = max_rot * flip_factor
            if is_left:
                rot = -rot

            transform.translate(self._w / 2, self._h / 2)
            transform.rotate(rot, Qt.YAxis)
            transform.translate(-self._w / 2, -self._h / 2)

            cx = view_width / 2
            cy = view_height / 2 - 24
            if is_left:
                cx -= spacing_center * flip_factor + spacing_side * max(0, ad - 1)
            else:
                cx += spacing_center * flip_factor + spacing_side * max(0, ad - 1)
            transform.translate(cx - self._w / 2, cy - self._h / 2)
            scale = 0.85
            transform.scale(scale - zoom_out, scale - zoom_out)

        self.setTransform(transform)


class CoverFlowWidget(QGraphicsView):
    selection_changed = Signal(int)
    double_clicked = Signal(int)
    clicked = Signal(int)
    cover_snapped = Signal(int)    # emitted when snapping to a cover
    request_cover = Signal(int, object)  # index, CoverFlowItem — async loading

    def __init__(self, parent=None):
        super().__init__(parent)

        if HAVE_OPENGL:
            self.setViewport(QOpenGLWidget())
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setBackgroundBrush(QColor(9, 11, 17))
        self.setFrameShape(QGraphicsView.NoFrame)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.OpenHandCursor)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._create_overlay_items()

        # Async album art loading
        from library.album_art_worker import AlbumArtManager
        self._art_mgr = AlbumArtManager(self)
        self._art_mgr._worker.art_ready.connect(self._on_cover_loaded)

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

        self._create_overlay_items()

        for i, item in enumerate(items):
            ci = CoverItem(item.pixmap, i, self._cover_w, self._cover_h)
            self._scene.addItem(ci)
            self._cover_items.append(ci)

        self._update_layout()

    def _create_overlay_items(self):
        """Re-create text items after scene.clear()."""
        self._title_text = QGraphicsTextItem()
        self._title_text.setDefaultTextColor(QColor("#ffffff"))
        self._title_text.setFont(QFont("sans-serif", 16, 750))
        self._title_text.setZValue(2000)
        self._title_effect = QGraphicsOpacityEffect()
        self._title_effect.setOpacity(1.0)
        self._title_text.setGraphicsEffect(self._title_effect)
        self._scene.addItem(self._title_text)

        self._artist_text = QGraphicsTextItem()
        self._artist_text.setDefaultTextColor(QColor(255, 255, 255, 190))
        self._artist_text.setFont(QFont("sans-serif", 12.5))
        self._artist_text.setZValue(2000)
        self._artist_effect = QGraphicsOpacityEffect()
        self._artist_effect.setOpacity(1.0)
        self._artist_text.setGraphicsEffect(self._artist_effect)
        self._scene.addItem(self._artist_text)

        self._meta_text = QGraphicsTextItem()
        self._meta_text.setDefaultTextColor(QColor(255, 255, 255, 120))
        self._meta_text.setFont(QFont("sans-serif", 10))
        self._meta_text.setZValue(2000)
        self._scene.addItem(self._meta_text)

        self._position_text = QGraphicsTextItem()
        self._position_text.setDefaultTextColor(QColor(255, 255, 255, 100))
        self._position_text.setFont(QFont("sans-serif", 10))
        self._position_text.setZValue(2000)
        self._scene.addItem(self._position_text)

        self._empty_msg = QGraphicsTextItem()
        self._empty_msg.setHtml(
            '<div style="text-align:center">'
            '<p style="font-size:16pt;color:rgba(245,245,247,210)">'
            'No hay álbumes en tu biblioteca</p>'
            '<p style="font-size:12pt;color:rgba(245,245,247,148)">'
            'Ctrl+D · Añadir carpeta musical</p>'
            '</div>')
        self._empty_msg.setZValue(3000)
        self._scene.addItem(self._empty_msg)

    def _on_cover_loaded(self, idx: int, pixmap: QPixmap):
        """Async callback — apply loaded cover with fade-in."""
        if 0 <= idx < len(self._cover_items) and not pixmap.isNull():
            self._cover_items[idx].set_real_cover(pixmap)

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
            vw = self.viewport().width()
            vh = self.viewport().height()
            br = self._empty_msg.boundingRect()
            self._empty_msg.setPos(vw / 2 - br.width() / 2, vh / 2 - 60)
            self._empty_msg.setVisible(True)
            self._title_text.setPlainText("")
            self._artist_text.setPlainText("")
            self._meta_text.setPlainText("")
            self._position_text.setPlainText("")
            return

        vw = self.viewport().width()
        vh = self.viewport().height()
        self._empty_msg.setVisible(False)

        # Sliding window (virtualization) — only render ±12 from center
        for ci in self._cover_items:
            dist = ci._index - self._current
            if abs(dist) > 12:
                ci.setVisible(False)
                continue

            ci.setVisible(True)
            ci.update_transform(self._current, vw, vh, self._velocity)
            ci._is_center = abs(dist) < 0.5

            # Async loading: request cover if still placeholder
            if not hasattr(ci, '_real_cover') and not ci._placeholder.isNull():
                item = self._items[ci._index]
                self.request_cover.emit(ci._index, item)

        idx = max(0, min(len(self._items) - 1, int(round(self._current))))

        # Signal throttling — only emit if index changed
        if getattr(self, '_last_emitted_idx', -1) != idx:
            self.selection_changed.emit(idx)
            self._last_emitted_idx = idx

        # Position indicator
        self._position_text.setPlainText(f"{idx + 1} / {len(self._items)}")
        pr = self._position_text.boundingRect()
        self._position_text.setPos(vw - pr.width() - 24, vh - 28)

        # Update central text with crossfade
        if self._items and 0 <= idx < len(self._items):
            item = self._items[idx]
            artist = (
                item.subtitle.split(" · ")[0]
                if item.subtitle and " · " in item.subtitle
                else item.subtitle or "Desconocido")
            tracks = item.data.get("tracks", [])
            count = len(tracks)
            dur = sum(getattr(t, 'duration', 0) or 0 for t in tracks)
            dur_str = f"{int(dur // 60)}:{int(dur % 60):02d}" if dur > 0 else ""
            meta_parts = []
            if count:
                meta_parts.append(f"{count} canciones")
            if dur_str:
                meta_parts.append(dur_str)
            meta = " · ".join(meta_parts)

            self._meta_text.setPlainText(meta)
            mr = self._meta_text.boundingRect()
            self._meta_text.setPos(vw / 2 - mr.width() / 2, vh - 50)

            self._animate_text_change(item.title, artist)
        else:
            self._meta_text.setPlainText("")
            self._animate_text_change("", "")

    def _animate_text_change(self, new_title: str, new_artist: str):
        """Fade out → change text → fade in."""
        vw = self.viewport().width()
        vh = self.viewport().height()

        anim = QVariantAnimation()
        anim.setDuration(120)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)

        def _on_fade_out():
            self._title_text.setPlainText(new_title)
            self._artist_text.setPlainText(new_artist)
            tr = self._title_text.boundingRect()
            ar = self._artist_text.boundingRect()
            self._title_text.setPos(vw / 2 - tr.width() / 2, vh - 92)
            self._artist_text.setPos(vw / 2 - ar.width() / 2, vh - 70)
            self._title_effect.setOpacity(1.0)
            self._artist_effect.setOpacity(1.0)

        anim.finished.connect(_on_fade_out)
        anim.valueChanged.connect(
            lambda v: (self._title_effect.setOpacity(v),
                       self._artist_effect.setOpacity(v)))
        anim.start()
        self._text_anim = anim

    # ── Physics ──

    def _update_physics(self):
        if self._dragging:
            return
        if abs(self._velocity) < 0.003:
            if abs(self._current - round(self._current)) > 0.01:
                self._trigger_snap()
            self._phys_timer.stop()
            return
        self._velocity *= 0.92
        self._current += self._velocity

        # Elastic overscroll: spring back toward valid range
        max_i = max(0.0, float(len(self._items) - 1))
        if self._current < 0:
            self._velocity += -self._current * 0.05
        if self._current > max_i:
            self._velocity += (max_i - self._current) * 0.05

        self._update_layout()
        if abs(self._velocity) < 0.003:
            self._trigger_snap()
            self._phys_timer.stop()

    def _trigger_snap(self):
        target = max(0, min(len(self._items) - 1, int(round(self._current))))
        self._snap_anim.stop()
        self._snap_anim.setStartValue(self._current)
        self._snap_anim.setEndValue(float(target))
        self._snap_anim.start()
        self.cover_snapped.emit(target)

    def drawBackground(self, painter, rect):
        painter.save()
        grad = QRadialGradient(rect.center(), max(rect.width(), rect.height()) * 0.65)
        grad.setColorAt(0.0, QColor(28, 31, 42, 230))
        grad.setColorAt(0.55, QColor(12, 14, 21, 245))
        grad.setColorAt(1.0, QColor(7, 9, 14, 255))
        painter.fillRect(rect, grad)
        painter.restore()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_cover_size()
        self._update_layout()

    def _update_cover_size(self):
        vw = self.viewport().width()
        size = max(210, min(300, int(vw * 0.23)))
        if size != self._cover_w:
            self._cover_w = size
            self._cover_h = size

    def contextMenuEvent(self, event):
        idx = int(round(self._current))
        if not self._items or idx < 0 or idx >= len(self._items):
            return
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction("▶ Reproducir álbum", lambda: self.double_clicked.emit(idx))
        if hasattr(self, 'queue_album_requested'):
            menu.addAction("+ Añadir a cola", lambda: self.queue_album_requested.emit(idx))
        menu.exec(event.globalPos())

    def keyPressEvent(self, event):
        if not self._items:
            return super().keyPressEvent(event)
        current_idx = int(round(self._current))

        if event.key() == Qt.Key_Left:
            self.scroll_to(current_idx - 1)
            event.accept()
        elif event.key() == Qt.Key_Right:
            self.scroll_to(current_idx + 1)
            event.accept()
        elif event.key() == Qt.Key_PageUp:
            self.scroll_to(current_idx - 5)
            event.accept()
        elif event.key() == Qt.Key_PageDown:
            self.scroll_to(current_idx + 5)
            event.accept()
        elif event.key() == Qt.Key_Home:
            self.scroll_to(0)
            event.accept()
        elif event.key() == Qt.Key_End:
            self.scroll_to(len(self._items) - 1)
            event.accept()
        elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.double_clicked.emit(current_idx)
            event.accept()
        else:
            super().keyPressEvent(event)

    # ── Mouse events ──

    def mousePressEvent(self, event):
        self._dragging = True
        self._snap_anim.stop()
        self._last_x = event.position().x()
        self._velocity = 0.0
        self.setCursor(Qt.ClosedHandCursor)

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
        self.setCursor(Qt.OpenHandCursor)
        if abs(self._velocity) < 0.01:
            self._trigger_snap()

    def mouseDoubleClickEvent(self, event):
        idx = int(round(self._current))
        if 0 <= idx < len(self._items):
            self.double_clicked.emit(idx)

    def wheelEvent(self, event):
        # High-resolution pixel delta (trackpad gestures on Wayland)
        pixel_delta = event.pixelDelta().x() or event.pixelDelta().y()

        if pixel_delta != 0:
            self._current -= pixel_delta * 0.015
        else:
            # Fallback for traditional mouse wheel (click-based)
            angle_delta = event.angleDelta().y() / 120.0
            self._current -= angle_delta * 0.5

        self._update_layout()

        # Reset physics and restart snap timer with debounce
        self._dragging = False
        self._velocity = 0.0
        self._phys_timer.start(16)
        QTimer.singleShot(150, self._trigger_snap)
