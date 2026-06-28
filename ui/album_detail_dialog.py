"""Album Detail Dialog — premium glass floating window with full album metadata."""
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices, QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QScrollArea, QWidget,
)

from metadata.album_summary import AlbumSummary


_DIALOG_QSS = """
QDialog#albumDetailDialog {
    background: #090B11;
}
"""

_SECTION_QSS = (
    "background: rgba(255,255,255,0.040);"
    "border: 1px solid rgba(255,255,255,0.06);"
    "border-radius: 16px;"
    "padding: 16px;"
)

_PILL_BTN_QSS = (
    "QPushButton { font-size: 11px; font-weight: 600;"
    "  color: rgba(143,183,255,0.85);"
    "  background: rgba(143,183,255,0.10);"
    "  border: 1px solid rgba(143,183,255,0.16);"
    "  border-radius: 8px; padding: 4px 12px; }"
    "QPushButton:hover { background: rgba(143,183,255,0.18);"
    "  color: rgba(143,183,255,1.0); }"
)

_LINK_BTN_QSS = (
    "QPushButton { font-size: 12px; font-weight: 500;"
    "  color: rgba(143,183,255,0.80);"
    "  background: rgba(255,255,255,0.04);"
    "  border: 1px solid rgba(255,255,255,0.07);"
    "  border-radius: 10px; padding: 6px 14px; }"
    "QPushButton:hover { background: rgba(143,183,255,0.12);"
    "  border: 1px solid rgba(143,183,255,0.20);"
    "  color: rgba(143,183,255,1.0); }"
)

_CLOSE_BTN_QSS = (
    "QPushButton { font-size: 16px; font-weight: 400;"
    "  color: rgba(255,255,255,0.50);"
    "  background: transparent; border: none; padding: 4px 10px; }"
    "QPushButton:hover { color: rgba(255,255,255,0.90); }"
)

_TITLE_FONT = QFont("sans-serif", 16, 700)
_ARTIST_FONT = QFont("sans-serif", 13, 500)
_META_FONT = QFont("sans-serif", 11)
_DESC_FONT = QFont("sans-serif", 11)
_TRACK_FONT = QFont("sans-serif", 11)
_SECTION_TITLE_FONT = QFont("sans-serif", 10, 700)


def _fmt_dur(seconds: float) -> str:
    if seconds <= 0:
        return ""
    m, s = divmod(int(seconds), 60)
    if seconds >= 3600:
        h, m = divmod(m, 60)
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


class AlbumDetailDialog(QDialog):
    def __init__(self, summary: AlbumSummary, parent=None):
        super().__init__(parent)
        self._summary = summary
        self._album_key = summary.album_key if summary else ""
        self.setObjectName("albumDetailDialog")
        self.setWindowTitle("Detalles del álbum")
        self.setFixedWidth(540)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet(_DIALOG_QSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 16, 28, 20)
        layout.setSpacing(16)

        self._build_top_bar(layout)
        self._build_info_section(layout)
        self._build_description_section(layout)
        self._build_tracklist_section(layout)
        self._build_links_section(layout)

        scroll.setWidget(content)
        root.addWidget(scroll)

        self.setMaximumHeight(int(parent.height() * 0.85) if parent else 700)

    def _make_section(self, title: str) -> tuple[QVBoxLayout, QFrame]:
        frame = QFrame()
        frame.setStyleSheet(_SECTION_QSS)
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(16, 14, 16, 14)
        fl.setSpacing(10)
        if title:
            lbl = QLabel(title)
            lbl.setFont(_SECTION_TITLE_FONT)
            lbl.setStyleSheet("color: rgba(143,183,255,0.60); background: transparent;")
            fl.addWidget(lbl)
        return fl, frame

    def _build_top_bar(self, layout):
        bar = QHBoxLayout()
        close_btn = QPushButton("✕  Cerrar")
        close_btn.setStyleSheet(_CLOSE_BTN_QSS)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        bar.addWidget(close_btn)
        bar.addStretch()

        if self._summary.external_ids:
            mbid = self._summary.external_ids.get("musicbrainz", "")
            if mbid:
                mb_btn = QPushButton("Abrir en MusicBrainz")
                mb_btn.setStyleSheet(_PILL_BTN_QSS)
                mb_btn.setCursor(Qt.PointingHandCursor)
                mb_btn.clicked.connect(
                    lambda: QDesktopServices.openUrl(
                        QUrl(f"https://musicbrainz.org/release/{mbid}")))
                bar.addWidget(mb_btn)
        layout.addLayout(bar)

    def _build_info_section(self, layout):
        cols = QHBoxLayout()
        cols.setSpacing(20)

        cover_lbl = QLabel()
        cover_lbl.setFixedSize(180, 180)
        cover_lbl.setStyleSheet(
            "background: rgba(255,255,255,0.06); border-radius: 16px;"
            "border: 1px solid rgba(255,255,255,0.08);")
        cover_lbl.setAlignment(Qt.AlignCenter)
        s = self._summary
        if s.cover_path and s.cover_path not in ("", "none"):
            pix = QPixmap(s.cover_path)
            if not pix.isNull():
                cover_lbl.setPixmap(
                    pix.scaled(176, 176, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        cols.addWidget(cover_lbl)

        info_col = QVBoxLayout()
        info_col.setSpacing(6)

        title_lbl = QLabel(s.title or "Sin título")
        title_lbl.setFont(_TITLE_FONT)
        title_lbl.setStyleSheet("color: rgba(255,255,255,0.95); background: transparent;")
        title_lbl.setWordWrap(True)
        info_col.addWidget(title_lbl)

        artist_lbl = QLabel(s.artist or "")
        artist_lbl.setFont(_ARTIST_FONT)
        artist_lbl.setStyleSheet("color: rgba(255,255,255,0.70); background: transparent;")
        info_col.addWidget(artist_lbl)

        meta_parts = []
        if s.year:
            meta_parts.append(s.year)
        genre = s.genre or s.style or ""
        if genre:
            meta_parts.append(genre)
        if s.track_count:
            meta_parts.append(f"{s.track_count} temas")
        if s.duration > 0:
            meta_parts.append(_fmt_dur(s.duration))
        if meta_parts:
            meta_lbl = QLabel(" · ".join(meta_parts))
            meta_lbl.setFont(_META_FONT)
            meta_lbl.setStyleSheet("color: rgba(255,255,255,0.50); background: transparent;")
            info_col.addWidget(meta_lbl)

        badges = QHBoxLayout()
        badges.setSpacing(8)
        if s.source and s.source != "local":
            src_lbl = QLabel({"theaudiodb": "Info externa", "cache": "Cache",
                              "musicbrainz": "MusicBrainz",
                              "enriched": "MusicBrainz"}.get(s.source, s.source))
            src_lbl.setStyleSheet(
                "font-size: 10px; font-weight: 600; color: rgba(143,183,255,0.80);"
                "background: rgba(143,183,255,0.10); border-radius: 6px; padding: 2px 8px;")
            badges.addWidget(src_lbl)
        if s.match_confidence > 0:
            conf_lbl = QLabel(f"Confianza: {int(s.match_confidence * 100)}%")
            conf_lbl.setStyleSheet(
                "font-size: 10px; color: rgba(255,255,255,0.42);"
                "background: transparent;")
            badges.addWidget(conf_lbl)
        badges.addStretch()
        info_col.addLayout(badges)
        info_col.addStretch()

        cols.addLayout(info_col, 1)
        layout.addLayout(cols)

    def _build_description_section(self, layout):
        fl, frame = self._make_section("Acerca del álbum")
        text = self._summary.description or "Buscando información del álbum..."
        self._desc_lbl = QLabel(text)
        self._desc_lbl.setFont(_DESC_FONT)
        self._desc_lbl.setStyleSheet("color: rgba(255,255,255,0.72); background: transparent;"
                                     "line-height: 1.5;")
        self._desc_lbl.setWordWrap(True)
        fl.addWidget(self._desc_lbl)
        layout.addWidget(frame)

    def update_summary(self, summary: AlbumSummary):
        """Live-update description when enrichment arrives."""
        if not summary or summary.album_key != self._album_key:
            return
        self._summary = summary
        if summary.description and hasattr(self, '_desc_lbl'):
            self._desc_lbl.setText(summary.description)

    def _build_tracklist_section(self, layout):
        tracks = self._summary.track_list or []
        if not tracks:
            return
        fl, frame = self._make_section("Temas")
        total_dur = 0
        for t in tracks:
            if isinstance(t, dict):
                name = t.get("title", t.get("name", "") or "")
                dur = t.get("duration", 0) or 0
            else:
                name = getattr(t, 'title', '') or getattr(t, 'name', '') or str(t)
                dur = getattr(t, 'duration', 0) or 0
            total_dur += dur
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            dur_str = _fmt_dur(dur)
            lbl = QLabel(f"♪  {name}")
            lbl.setFont(_TRACK_FONT)
            lbl.setStyleSheet("color: rgba(255,255,255,0.76); background: transparent;")
            dur_lbl = QLabel(dur_str)
            dur_lbl.setFont(_TRACK_FONT)
            dur_lbl.setStyleSheet("color: rgba(255,255,255,0.42); background: transparent;")
            dur_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(lbl, 1)
            row.addWidget(dur_lbl)
            fl.addLayout(row)
        if total_dur > 0 and not tracks:
            pass
        layout.addWidget(frame)

    def _build_links_section(self, layout):
        s = self._summary
        links = []
        eids = s.external_ids or {}
        if eids.get("musicbrainz"):
            links.append(("MusicBrainz", f"https://musicbrainz.org/release/{eids['musicbrainz']}"))
        if eids.get("wikidata"):
            links.append(("Wikipedia", f"https://www.wikidata.org/wiki/{eids['wikidata']}"))
        if eids.get("discogs"):
            links.append(("Discogs", f"https://www.discogs.com/release/{eids['discogs']}"))
        if eids.get("theaudiodb"):
            links.append(("TheAudioDB", f"https://theaudiodb.com/album/{eids['theaudiodb']}"))
        if not links:
            return
        fl, frame = self._make_section("Enlaces")
        row = QHBoxLayout()
        row.setSpacing(10)
        for name, url in links:
            btn = QPushButton(f"🔗  {name}")
            btn.setStyleSheet(_LINK_BTN_QSS)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, u=url: QDesktopServices.openUrl(QUrl(u)))
            row.addWidget(btn)
        row.addStretch()
        fl.addLayout(row)
        layout.addWidget(frame)

    def mousePressEvent(self, event):
        if event.position().y() < 40:
            self.accept()
        super().mousePressEvent(event)
