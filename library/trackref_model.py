"""TrackRefTableModel — adapts list[TrackRef] to QStandardItemModel for QTableView."""
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel, QBrush, QColor

from sources.base_source import TrackRef
from library.metadata_normalizer import infer_metadata_from_filename


def _title(item: TrackRef) -> str:
    t = (item.title or "").strip()
    if t and t != "Sin título":
        return t
    if item.uri:
        inferred = infer_metadata_from_filename(item.uri)
        t = str(inferred.get("title", "") or "")
        if t:
            return t
        return os.path.splitext(os.path.basename(item.uri))[0]
    return "Sin título"


def _artist(item: TrackRef) -> str:
    a = (item.artist or "").strip()
    if a and a != "Artista desconocido":
        return a
    if item.uri:
        inferred = infer_metadata_from_filename(item.uri)
        a = str(inferred.get("artist", "") or "")
        if a:
            return a
    return "Artista desconocido"


def _album(item: TrackRef) -> str:
    return (item.album or "").strip() or "Sin álbum"


class TrackRefTableModel(QStandardItemModel):
    COL_TRACK = 0
    COL_TITLE = 1
    COL_ARTIST = 2
    COL_ALBUM = 3
    COL_YEAR = 4
    COL_GENRE = 5
    COL_DURATION = 6
    COL_QUALITY = 7
    COL_URI = 8

    def __init__(self, parent=None):
        super().__init__(0, 9, parent)
        self.setHorizontalHeaderLabels(
            ["Nº pista", "Título", "Artista", "Álbum",
             "Año", "Género", "Duración", "Calidad", "Ruta"])
        self._quality_cache = {}

    def populate(self, items: list[TrackRef]):
        self.removeRows(0, self.rowCount())

        paths = [i.uri for i in items if i.uri]
        badges_by_uri = {}
        if paths:
            try:
                from library.audio_lab_badges import get_audio_lab_badges_for_paths
                badges_by_uri = get_audio_lab_badges_for_paths(paths)
            except Exception:
                pass

        for item in items:
            tr = QStandardItem()
            tr.setEditable(False)
            tr.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            tr.setForeground(QBrush(QColor("rgba(255,255,255,0.72)")))
            tn = self._parse_track_number(item.track_number)
            if tn is not None:
                tr.setText(str(tn))
                tr.setData(tn, Qt.UserRole)
            else:
                tr.setText("—")

            t = QStandardItem(_title(item))
            t.setEditable(False)
            t.setToolTip(item.uri)
            t.setData(item, Qt.UserRole)

            a = QStandardItem(_artist(item))
            a.setEditable(False)
            al = QStandardItem(_album(item))
            al.setEditable(False)

            y = QStandardItem()
            y.setEditable(False)
            y.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            y.setForeground(QBrush(QColor("#8e8e93")))
            if item.year:
                y.setText(str(item.year))
                y.setData(item.year, Qt.UserRole)
            else:
                y.setText("—")

            g = QStandardItem(item.genre or "—")
            g.setEditable(False)

            d = QStandardItem()
            d.setEditable(False)
            d.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            d.setForeground(QBrush(QColor("#8e8e93")))
            if item.duration:
                d.setText(self._fmt_duration(item.duration))
                d.setData(item.duration, Qt.UserRole)
            else:
                d.setText("—")

            ql = QStandardItem()
            ql.setEditable(False)
            ql.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            ql.setForeground(QBrush(QColor("#8e8e93")))
            if item.uri:
                badge = badges_by_uri.get(item.uri) or self._get_badge(item.uri)
                if badge and badge.get("label"):
                    ql.setText(badge["label"])
                    kind = badge.get("kind", "")
                    if kind == "hires":
                        ql.setForeground(QBrush(QColor("#64DC64")))
                    elif kind == "lossless":
                        ql.setForeground(QBrush(QColor("#8FB7FF")))
                    elif kind == "lossy":
                        ql.setForeground(QBrush(QColor("#FFB347")))
                    elif kind == "dsd":
                        ql.setForeground(QBrush(QColor("#C084FC")))
                    elif kind == "warning":
                        ql.setForeground(QBrush(QColor("#FF8C42")))
                    tooltip = badge.get("tooltip", "")
                    if tooltip:
                        ql.setToolTip(tooltip)

            uri = QStandardItem(item.uri)
            uri.setEditable(False)
            self.appendRow([tr, t, a, al, y, g, d, ql, uri])

    def invalidate_quality_cache(self, paths: list[str] | None = None):
        if paths:
            for p in paths:
                self._quality_cache.pop(p, None)
        else:
            self._quality_cache.clear()

    def _get_badge(self, uri: str) -> dict | None:
        if uri in self._quality_cache:
            return self._quality_cache[uri]
        try:
            from library.audio_lab_badges import get_audio_lab_badge_for_path as get_badge_for_file
            badge = get_badge_for_file(uri)
            self._quality_cache[uri] = badge
            return badge
        except Exception:
            return None

    def get_trackref(self, row: int) -> TrackRef | None:
        idx = self.index(row, self.COL_TITLE)
        return self.data(idx, Qt.UserRole)

    @staticmethod
    def _parse_track_number(value) -> int | None:
        if value in (None, "", 0, "0"):
            return None
        text = str(value).strip()
        if "/" in text:
            text = text.split("/", 1)[0].strip()
        try:
            return int(text)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _fmt_duration(seconds: float) -> str:
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m}:{s:02d}"
