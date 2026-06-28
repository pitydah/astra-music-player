"""Album Info Banner — premium glass card between CoverFlow and NowPlayingBar.
3 sections: cover (premium shadow + rounded clip), track list (clickeable), action buttons."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QMouseEvent, QColor, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QGraphicsDropShadowEffect,
)

from metadata.album_summary import AlbumSummary

_TRACK_FONT = QFont("sans-serif", 10)
_ITEM_FONT = QFont("sans-serif", 11, 500)
_MORE_LBL_STYLE = "font-size: 10px; color: rgba(255,255,255,0.42); background: transparent;"
_TRACK_ROW_QSS = (
    "background: transparent; border-radius: 6px; padding: 0px 4px;")
_TRACK_ROW_HOVER_QSS = (
    "background: rgba(255,255,255,0.06); border-radius: 6px; padding: 0px 4px;")


def _rounded_pixmap(pixmap: QPixmap, size: int, radius: int) -> QPixmap:
    """Return a rounded version of pixmap scaled to size x size."""
    scaled = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    result = QPixmap(scaled.size())
    result.fill(Qt.transparent)
    p = QPainter(result)
    p.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, scaled.width(), scaled.height(), radius, radius)
    p.setClipPath(path)
    p.drawPixmap(0, 0, scaled)
    p.end()
    return result


class _TrackRow(QWidget):
    """A single track row: number + name + duration. Clickeable."""
    clicked = Signal(str)

    def __init__(self, index: int, title: str, duration: str, filepath: str = ""):
        super().__init__()
        self._filepath = filepath
        self.setStyleSheet(_TRACK_ROW_QSS)
        self.setCursor(Qt.PointingHandCursor)

        hl = QHBoxLayout(self)
        hl.setContentsMargins(4, 1, 4, 1)
        hl.setSpacing(4)

        num_lbl = QLabel(f"{index:2d}.-")
        num_lbl.setFixedWidth(26)
        num_lbl.setFont(_TRACK_FONT)
        num_lbl.setStyleSheet("color: rgba(255,255,255,0.42); background: transparent;")
        num_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        hl.addWidget(num_lbl)

        name_lbl = QLabel(title[:32])
        name_lbl.setFont(_TRACK_FONT)
        name_lbl.setStyleSheet("color: rgba(255,255,255,0.66); background: transparent;")
        hl.addWidget(name_lbl, 1)

        dur_lbl = QLabel(duration)
        dur_lbl.setFont(_TRACK_FONT)
        dur_lbl.setStyleSheet("color: rgba(255,255,255,0.38); background: transparent;")
        dur_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hl.addWidget(dur_lbl)

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self._filepath)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setStyleSheet(_TRACK_ROW_HOVER_QSS)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(_TRACK_ROW_QSS)
        super().leaveEvent(event)


class AlbumInfoBanner(QWidget):
    play_requested = Signal(str)
    queue_requested = Signal(str)
    playlist_requested = Signal(str)
    metadata_requested = Signal(str)
    details_requested = Signal(str)
    refresh_metadata_requested = Signal(str)
    track_clicked = Signal(str)
    open_external_link = Signal(str)  # url

    def __init__(self, parent=None):
        super().__init__(parent)
        self._summary: AlbumSummary | None = None
        self._compact = False
        self.setMinimumHeight(213)
        self.setMaximumHeight(265)

        self._card = QFrame()
        self._card.setObjectName("albumBanner")
        self._card.setStyleSheet(
            "QFrame#albumBanner {"
            "  background: rgba(255,255,255,0.050);"
            "  border: 1px solid rgba(255,255,255,0.085);"
            "  border-radius: 22px; }"
            "QFrame#albumBanner:hover {"
            "  background: rgba(255,255,255,0.060);"
            "  border: 1px solid rgba(255,255,255,0.110); }"
            "QLabel { background: transparent; }")

        self._layout = QHBoxLayout(self._card)
        self._layout.setContentsMargins(20, 12, 16, 12)
        self._layout.setSpacing(18)

        self._build_section1_cover_info()
        self._build_section2_tracks()
        self._build_section3_actions()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._card)

    def _make_section_frame(self, stretch=1) -> QFrame:
        f = QFrame()
        f.setStyleSheet("background: transparent; border: none;")
        self._layout.addWidget(f, stretch)
        return f

    # ── Section 1: Cover (premium) + album info ──

    def _build_section1_cover_info(self):
        frame = self._make_section_frame(4)
        root = QHBoxLayout(frame)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(18)

        # Cover con sombra y hover sutil
        cover_container = QFrame()
        cover_container.setFixedSize(180, 180)
        cover_container.setCursor(Qt.PointingHandCursor)

        self._cover_lbl = QLabel(cover_container)
        self._cover_lbl.setFixedSize(180, 180)
        self._cover_lbl.setStyleSheet(
            "background: rgba(255,255,255,0.06); border-radius: 20px;"
            "border: 1px solid rgba(255,255,255,0.10);")
        self._cover_lbl.setAlignment(Qt.AlignCenter)

        self._cover_shadow = QGraphicsDropShadowEffect(cover_container)
        self._cover_shadow.setBlurRadius(22)
        self._cover_shadow.setOffset(0, 5)
        self._cover_shadow.setColor(QColor(0, 0, 0, 100))
        cover_container.setGraphicsEffect(self._cover_shadow)

        def _on_cover_enter(event):
            self._cover_shadow.setColor(QColor(143, 183, 255, 70))
            self._cover_shadow.setBlurRadius(28)
        def _on_cover_leave(event):
            self._cover_shadow.setColor(QColor(0, 0, 0, 100))
            self._cover_shadow.setBlurRadius(22)
        cover_container.enterEvent = _on_cover_enter
        cover_container.leaveEvent = _on_cover_leave

        root.addWidget(cover_container)

        info_col = QVBoxLayout()
        info_col.setSpacing(3)

        self._title_lbl = QLabel("")
        self._title_lbl.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: rgba(255,255,255,0.95);")
        info_col.addWidget(self._title_lbl)

        self._artist_lbl = QLabel("")
        self._artist_lbl.setStyleSheet(
            "font-size: 12px; color: rgba(255,255,255,0.70);")
        info_col.addWidget(self._artist_lbl)

        self._meta_lbl = QLabel("")
        self._meta_lbl.setStyleSheet(
            "font-size: 10px; color: rgba(255,255,255,0.46);")
        info_col.addWidget(self._meta_lbl)

        badges = QHBoxLayout()
        badges.setSpacing(6)
        self._source_badge = QLabel("")
        self._source_badge.setStyleSheet(
            "font-size: 9px; font-weight: 600; color: rgba(140,190,255,0.80);"
            "background: rgba(143,183,255,0.12); border-radius: 5px; padding: 2px 7px;")
        self._source_badge.setCursor(Qt.PointingHandCursor)
        self._source_badge.mousePressEvent = lambda e: self._on_source_badge_click(e)
        self._source_badge.hide()
        badges.addWidget(self._source_badge)
        self._genre_badge = QLabel("")
        self._genre_badge.setStyleSheet(
            "font-size: 9px; color: rgba(255,255,255,0.48);"
            "background: rgba(255,255,255,0.04); border-radius: 5px; padding: 2px 7px;")
        self._genre_badge.hide()
        badges.addWidget(self._genre_badge)
        badges.addStretch()
        info_col.addLayout(badges)

        self._desc_lbl = QLabel("")
        self._desc_lbl.setStyleSheet(
            "font-size: 10px; color: rgba(255,255,255,0.40);"
            "line-height: 1.3; background: transparent;")
        self._desc_lbl.setWordWrap(True)
        self._desc_lbl.setMaximumHeight(32)
        info_col.addWidget(self._desc_lbl)

        info_col.addStretch()
        root.addLayout(info_col, 1)

    # ── Section 2: Track list ──

    def _build_section2_tracks(self):
        frame = self._make_section_frame(4)
        self._tracks_layout = QVBoxLayout(frame)
        self._tracks_layout.setContentsMargins(0, 0, 0, 0)
        self._tracks_layout.setSpacing(2)

        self._track_rows: list[QWidget] = []
        self._more_lbl = QLabel("")
        self._more_lbl.setStyleSheet(
            _MORE_LBL_STYLE + " QLabel:hover { color: rgba(143,183,255,0.70); }")
        self._more_lbl.setCursor(Qt.PointingHandCursor)
        self._more_lbl.mousePressEvent = lambda e: self.details_requested.emit(
            self._summary.album_key if self._summary else "")
        self._more_lbl.hide()
        self._tracks_layout.addWidget(self._more_lbl)
        self._tracks_layout.addStretch()

    # ── Section 3: Action buttons ──

    def _build_section3_actions(self):
        frame = self._make_section_frame(2)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        play_btn = self._make_action_btn("▶ Reproducir")
        play_btn.clicked.connect(lambda: self.play_requested.emit(
            self._summary.album_key if self._summary else ""))
        queue_btn = self._make_action_btn("+ Cola")
        queue_btn.clicked.connect(lambda: self.queue_requested.emit(
            self._summary.album_key if self._summary else ""))
        details_btn = self._make_action_btn("ℹ Detalles")
        details_btn.clicked.connect(lambda: self.details_requested.emit(
            self._summary.album_key if self._summary else ""))

        lay.addWidget(play_btn)
        lay.addWidget(queue_btn)
        lay.addWidget(details_btn)
        lay.addStretch()

    def _make_action_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFont(QFont("sans-serif", 10, 600))
        btn.setStyleSheet(
            "QPushButton { color: rgba(255,255,255,0.72);"
            "  background: rgba(255,255,255,0.05);"
            "  border: 1px solid rgba(255,255,255,0.08);"
            "  border-radius: 10px; padding: 5px 14px; }"
            "QPushButton:hover { background: rgba(255,255,255,0.09);"
            "  border: 1px solid rgba(255,255,255,0.14);"
            "  color: rgba(255,255,255,0.92); }")
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    # ── Public API ──

    def set_track_list(self, tracks: list):
        for w in self._track_rows:
            w.deleteLater()
        self._track_rows.clear()
        self._more_lbl.hide()

        max_show = 6
        shown = tracks[:max_show]
        for i, t in enumerate(shown):
            title = getattr(t, 'title', '') or ''
            dur = getattr(t, 'duration', 0) or 0
            fp = getattr(t, 'filepath', '') or ''
            dur_str = self._fmt_dur(dur)
            row = _TrackRow(i + 1, title, dur_str, fp)
            row.clicked.connect(lambda f: self.track_clicked.emit(f))
            self._tracks_layout.insertWidget(
                self._tracks_layout.count() - 1, row)
            self._track_rows.append(row)

        remaining = len(tracks) - max_show
        if remaining > 0:
            self._more_lbl.setText(f"y {remaining} más...")
            self._more_lbl.show()
        elif not tracks:
            empty_lbl = QLabel("Sin canciones en biblioteca")
            empty_lbl.setStyleSheet(_MORE_LBL_STYLE)
            self._tracks_layout.insertWidget(
                self._tracks_layout.count() - 1, empty_lbl)
            self._track_rows.append(empty_lbl)

    def set_cover_pixmap(self, pixmap):
        if pixmap and not pixmap.isNull():
            self._cover_lbl.setPixmap(
                _rounded_pixmap(pixmap, 176, 18))

    def set_album_summary(self, summary: AlbumSummary | None):
        self._summary = summary
        if not summary:
            self.clear()
            return
        self._title_lbl.setText(summary.title[:32])
        self._artist_lbl.setText(summary.artist[:38])

        meta_parts = []
        if summary.year:
            meta_parts.append(summary.year)
        if summary.track_count:
            meta_parts.append(f"{summary.track_count} temas")
        if summary.duration > 0:
            s = int(summary.duration)
            if s >= 3600:
                meta_parts.append(f"{s // 3600} h {(s % 3600)//60} min")
            else:
                meta_parts.append(f"{s // 60} min")
        self._meta_lbl.setText(" · ".join(meta_parts))

        if summary.description:
            self._desc_lbl.setText(summary.description[:120])
        else:
            self._desc_lbl.setText("")

        src_labels = {"theaudiodb": "Info externa", "cache": "Cache",
                       "musicbrainz": "MusicBrainz",
                      "local": "Local", "enriching": "Cargando..."}
        self._source_badge.setText(src_labels.get(summary.source, summary.source))
        self._source_badge.setVisible(bool(summary.source and summary.source != "local"))

        genre = summary.genre or summary.style or ""
        self._genre_badge.setText(genre[:16])
        self._genre_badge.setVisible(bool(genre))

        if summary.cover_path and summary.cover_path not in ("", "none"):
            pix = QPixmap(summary.cover_path)
            if not pix.isNull():
                self._cover_lbl.setPixmap(
                    _rounded_pixmap(pix, 176, 18))

    def _on_source_badge_click(self, event):
        if self._summary and self._summary.external_ids:
            url = None
            eids = self._summary.external_ids
            if eids.get("musicbrainz"):
                url = f"https://musicbrainz.org/release/{eids['musicbrainz']}"
            elif eids.get("wikidata"):
                url = f"https://www.wikidata.org/wiki/{eids['wikidata']}"
            elif eids.get("discogs"):
                url = f"https://www.discogs.com/release/{eids['discogs']}"
            if url:
                self.open_external_link.emit(url)

    def set_loading_state(self, state: str):
        labels = {"loading": "Cargando...", "enriching": "Enriqueciendo...",
                  "error": "Error al cargar"}
        self._title_lbl.setText(labels.get(state, state))

    def clear(self):
        self._title_lbl.setText("Sin álbum seleccionado")
        self._artist_lbl.setText("")
        self._meta_lbl.setText("")
        self._desc_lbl.setText("")
        self._source_badge.hide()
        self._genre_badge.hide()
        self._cover_lbl.clear()
        for w in self._track_rows:
            w.deleteLater()
        self._track_rows.clear()
        self._more_lbl.hide()
        self._summary = None

    def set_compact_mode(self, enabled: bool):
        self._compact = enabled

    @staticmethod
    def _fmt_dur(seconds: float) -> str:
        if seconds <= 0:
            return ""
        m, s = divmod(int(seconds), 60)
        if seconds >= 3600:
            h, m = divmod(m, 60)
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
