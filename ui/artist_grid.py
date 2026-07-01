"""Artist Grid — premium mosaic/list of artists with search, filters, sorting and enhanced cards."""
import os as _os
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QColor, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGridLayout,
    QLabel, QFrame, QListWidget, QListWidgetItem,
    QLineEdit, QComboBox, QMenu,
)

from library.artist_grouping import ArtistGroup
from library.album_art import load_cover_pixmap
from ui.effects.michi_glass import apply_card_shadow
from ui.central.central_styles import (
    glass_card_qss, menu_qss, badge_qss, card_meta_qss, card_desc_qss,
    glass_combo_qss, search_qss,
)

_BG = "#090B11"
_PANEL = "rgba(255,255,255,0.035)"
_HOVER = "rgba(255,255,255,0.075)"
_SELECTED = "rgba(255,255,255,0.115)"
_BORDER = "rgba(255,255,255,0.075)"
_TEXT = "#FFFFFF"
_TEXT2 = "rgba(255,255,255,0.78)"
_TEXT3 = "rgba(255,255,255,0.62)"
_ACCENT = "#8FB7FF"
_ACCENT_BG = "rgba(143,183,255,0.12)"


def _format_dur(secs: float) -> str:
    if secs <= 0:
        return ""
    s = int(secs)
    h = s // 3600
    m = (s % 3600) // 60
    return f"{h} h {m} min" if h > 0 else f"{m} min"


_SORT_OPTIONS = [
    ("A–Z", "name_asc"),
    ("Z–A", "name_desc"),
    ("Más álbumes", "albums_desc"),
    ("Más canciones", "tracks_desc"),
    ("Más duración", "duration_desc"),
    ("Más recientes", "year_desc"),
    ("Mejor calidad", "quality_desc"),
    ("Con problemas", "warnings_desc"),
    ("Con info externa", "enriched_first"),
]

_FILTER_OPTIONS = [
    ("Todos", "all"),
    ("Con biografía", "has_bio"),
    ("Sin biografía", "no_bio"),
    ("Con imagen externa", "has_image"),
    ("Sin imagen externa", "no_image"),
    ("Con duplicados", "has_aliases"),
    ("Con problemas metadata", "has_warnings"),
    ("Lossless", "lossless"),
    ("Hi-Res", "hires"),
    ("Artistas desconocidos", "unknown"),
]

_LOSSLESS_EXTS = {"flac", "alac", "wav", "aiff", "ape", "wv", "dsd", "dff", "dsf"}
_LOSSY_EXTS = {"mp3", "aac", "m4a", "ogg", "opus", "wma"}


class ArtistGridWidget(QWidget):
    artist_selected = Signal(str)
    artist_play_requested = Signal(str)
    artist_queue_requested = Signal(str)
    artist_playlist_requested = Signal(str)
    artist_metadata_requested = Signal(str)
    artist_enrich_requested = Signal(str)
    artist_mix_requested = Signal(str)
    artist_analyze_requested = Signal(str)
    artist_send_to_server_requested = Signal(str)
    artist_resolve_aliases_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {_BG};")
        self._artists: list[ArtistGroup] = []
        self._filtered: list[ArtistGroup] = []
        self._view_mode = "grid"
        self._cover_size = 180
        self._selected_key = ""
        self._last_cols = -1
        self._sort_key = "name_asc"
        self._filter_key = "all"
        self._search_text = ""

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Local toolbar ──
        toolbar = QFrame()
        toolbar.setObjectName("artistToolbar")
        toolbar.setStyleSheet("""
            QFrame#artistToolbar {
                background: transparent; border: none;
                padding: 8px 20px 4px 20px;
            }
        """)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(20, 8, 20, 4)
        tb_layout.setSpacing(8)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Buscar artista…")
        self._search_input.setStyleSheet(search_qss())
        self._search_input.setFixedWidth(240)
        self._search_input.textChanged.connect(self._on_search)
        tb_layout.addWidget(self._search_input)

        self._sort_combo = QComboBox()
        self._sort_combo.setStyleSheet(glass_combo_qss())
        for label, _ in _SORT_OPTIONS:
            self._sort_combo.addItem(label)
        self._sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        tb_layout.addWidget(self._sort_combo)

        self._filter_combo = QComboBox()
        self._filter_combo.setStyleSheet(glass_combo_qss())
        for label, _ in _FILTER_OPTIONS:
            self._filter_combo.addItem(label)
        self._filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        tb_layout.addWidget(self._filter_combo)

        tb_layout.addStretch()

        self._count_label = QLabel()
        self._count_label.setStyleSheet(
            f"color: {_TEXT3}; font-size: 11px; background: transparent; border: none;")
        tb_layout.addWidget(self._count_label)

        outer.addWidget(toolbar)

        # ── Scroll area ──
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{ background: {_BG}; border: none; }}
            QScrollBar:vertical {{
                background: rgba(255,255,255,0.025); width: 10px;
                margin: 4px; border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255,255,255,0.18); min-height: 44px; border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{ background: rgba(255,255,255,0.30); }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(18)
        self._grid.setContentsMargins(24, 8, 24, 24)
        self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self._scroll.setWidget(self._container)

        self._list = QListWidget()
        self._list.setStyleSheet(f"""
            QListWidget {{
                background: transparent; border: none; color: {_TEXT2}; font-size: 13px;
            }}
            QListWidget::item {{ padding: 10px 14px; border-radius: 10px; margin: 2px 8px; }}
            QListWidget::item:hover {{ background: {_HOVER}; color: {_TEXT}; }}
            QListWidget::item:selected {{ background: {_SELECTED}; color: {_TEXT}; }}
        """)
        self._list.itemClicked.connect(self._on_list_item_clicked)
        self._list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._on_list_context)
        self._list.hide()

        outer.addWidget(self._scroll)
        outer.addWidget(self._list)

        # ── Empty state ──
        self._empty_frame = QFrame()
        self._empty_frame.setObjectName("emptyState")
        self._empty_frame.setStyleSheet("""
            QFrame#emptyState {
                background: transparent; border: none;
            }
        """)
        empty_layout = QVBoxLayout(self._empty_frame)
        empty_layout.setAlignment(Qt.AlignCenter)

        empty_icon = QLabel("🎵")
        empty_icon.setAlignment(Qt.AlignCenter)
        empty_icon.setStyleSheet(
            "font-size: 48px; background: transparent; border: none;")
        empty_layout.addWidget(empty_icon)

        self._empty_title = QLabel("No hay artistas en tu biblioteca")
        self._empty_title.setAlignment(Qt.AlignCenter)
        self._empty_title.setStyleSheet(
            "font-size: 17px; font-weight: 700; color: rgba(255,255,255,0.82);"
            "background: transparent; border: none;")
        empty_layout.addWidget(self._empty_title)

        self._empty_subtitle = QLabel(
            "Escanea una carpeta musical o revisa los metadatos de tus archivos.")
        self._empty_subtitle.setAlignment(Qt.AlignCenter)
        self._empty_subtitle.setWordWrap(True)
        self._empty_subtitle.setStyleSheet(
            "font-size: 13px; color: rgba(255,255,255,0.56);"
            "background: transparent; border: none;")
        empty_layout.addWidget(self._empty_subtitle)

        self._empty_frame.hide()
        outer.addWidget(self._empty_frame, 1)

        self._empty_filter_frame = QFrame()
        self._empty_filter_frame.setObjectName("emptyFilterState")
        self._empty_filter_frame.setStyleSheet("""
            QFrame#emptyFilterState {
                background: transparent; border: none;
            }
        """)
        ef_layout = QVBoxLayout(self._empty_filter_frame)
        ef_layout.setAlignment(Qt.AlignCenter)

        ef_icon = QLabel("🔍")
        ef_icon.setAlignment(Qt.AlignCenter)
        ef_icon.setStyleSheet(
            "font-size: 48px; background: transparent; border: none;")
        ef_layout.addWidget(ef_icon)

        ef_title = QLabel("Ningún artista coincide con los filtros")
        ef_title.setAlignment(Qt.AlignCenter)
        ef_title.setStyleSheet(
            "font-size: 17px; font-weight: 700; color: rgba(255,255,255,0.82);"
            "background: transparent; border: none;")
        ef_layout.addWidget(ef_title)

        ef_sub = QLabel("Prueba con otros términos o limpia los filtros.")
        ef_sub.setAlignment(Qt.AlignCenter)
        ef_sub.setStyleSheet(
            "font-size: 13px; color: rgba(255,255,255,0.56);"
            "background: transparent; border: none;")
        ef_layout.addWidget(ef_sub)

        self._empty_filter_frame.hide()
        outer.addWidget(self._empty_filter_frame, 1)

    def set_artists(self, artists: list[ArtistGroup]):
        self._artists = artists
        self._last_cols = -1
        self._apply_filters()

    def set_view_mode(self, mode: str):
        self._view_mode = mode
        self._refresh()

    # ── Search, sort, filter ──

    def _on_search(self, text: str):
        self._search_text = text.strip().lower()
        self._apply_filters()

    def _on_sort_changed(self, idx: int):
        if 0 <= idx < len(_SORT_OPTIONS):
            self._sort_key = _SORT_OPTIONS[idx][1]
            self._apply_filters()

    def _on_filter_changed(self, idx: int):
        if 0 <= idx < len(_FILTER_OPTIONS):
            self._filter_key = _FILTER_OPTIONS[idx][1]
            self._apply_filters()

    def _apply_filters(self):
        filtered = self._artists
        if self._search_text:
            filtered = [
                a for a in filtered
                if self._search_text in a.display_name.lower()
                or any(self._search_text in (g or "").lower() for g in a.genres)
            ]
        if self._filter_key != "all":
            filtered = [a for a in filtered if self._matches_filter(a)]
        filtered = self._sort_groups(filtered)
        self._filtered = filtered
        self._update_count()
        self._refresh()

    def _matches_filter(self, artist: ArtistGroup) -> bool:
        fk = self._filter_key
        if fk == "has_bio":
            return bool(getattr(artist, "bio", ""))
        if fk == "no_bio":
            return not getattr(artist, "bio", "")
        if fk == "has_image":
            return bool(getattr(artist, "thumb_path", "")) and _os.path.exists(artist.thumb_path)
        if fk == "no_image":
            return not (getattr(artist, "thumb_path", "") and _os.path.exists(artist.thumb_path))
        if fk == "has_aliases":
            from library.artist_aliases import find_artist_alias_candidates
            return bool(find_artist_alias_candidates(self._artists))
        if fk == "has_warnings":
            from library.artist_insights import compute_metadata_health
            h = compute_metadata_health(artist)
            return h.total_issues > 0
        if fk == "lossless":
            return any(
                _os.path.splitext(t.filepath)[1].lower().lstrip(".") in _LOSSLESS_EXTS
                for t in artist.all_tracks
            )
        if fk == "hires":
            return any(
                (getattr(t, "sample_rate", 0) or 0) >= 88200
                or (getattr(t, "bit_depth", 0) or 0) >= 24
                for t in artist.all_tracks
            )
        if fk == "unknown":
            return artist.key in ("artista desconocido", "unknown", "various artists")
        return True

    def _sort_groups(self, groups: list[ArtistGroup]) -> list[ArtistGroup]:
        sk = self._sort_key
        if sk == "name_asc":
            return sorted(groups, key=lambda g: g.sort_name)
        if sk == "name_desc":
            return sorted(groups, key=lambda g: g.sort_name, reverse=True)
        if sk == "albums_desc":
            return sorted(groups, key=lambda g: -g.album_count)
        if sk == "tracks_desc":
            return sorted(groups, key=lambda g: -g.track_count)
        if sk == "duration_desc":
            return sorted(groups, key=lambda g: -g.total_duration)
        if sk == "year_desc":
            return sorted(groups, key=lambda g: -(g.years[-1] if g.years else 0))
        if sk == "quality_desc":
            return sorted(groups, key=lambda g: -(
                sum(1 for t in g.all_tracks
                    if (_os.path.splitext(t.filepath)[1].lower().lstrip(".") in _LOSSLESS_EXTS))
                / max(len(g.all_tracks), 1)
            ))
        if sk == "warnings_desc":
            from library.artist_insights import compute_metadata_health
            return sorted(groups, key=lambda g: -compute_metadata_health(g).total_issues)
        if sk == "enriched_first":
            return sorted(groups, key=lambda g: (
                0 if g.enrichment_status == "loaded" else 1, g.sort_name))
        return groups

    def _update_count(self):
        total = len(self._artists)
        shown = len(self._filtered)
        if total == shown:
            self._count_label.setText(f"{total} artistas")
        else:
            self._count_label.setText(f"{shown} de {total} artistas")

    # ── Render ──

    def _refresh(self):
        if not self._filtered:
            self._list.hide()
            self._scroll.hide()
            if not self._artists:
                self._empty_frame.show()
                self._empty_filter_frame.hide()
            else:
                self._empty_frame.hide()
                self._empty_filter_frame.show()
            return
        self._empty_frame.hide()
        self._empty_filter_frame.hide()
        if self._view_mode == "grid":
            self._list.hide()
            self._scroll.show()
            self._rebuild_grid()
        else:
            self._scroll.hide()
            self._list.show()
            self._rebuild_list()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._view_mode == "grid":
            self._rebuild_grid()

    def _clear_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _rebuild_grid(self):
        if not self._filtered:
            self._clear_grid()
            self._last_cols = -1
            if not self._artists:
                self._empty_frame.show()
                self._empty_filter_frame.hide()
            else:
                self._empty_frame.hide()
                self._empty_filter_frame.show()
            self._scroll.hide()
            return
        self._empty_frame.hide()
        self._empty_filter_frame.hide()
        self._scroll.show()

        cols = max(1, (self._scroll.viewport().width() - 48) // (self._cover_size + 40))
        if cols == self._last_cols and self._grid.count() > 0:
            return
        self._last_cols = cols
        self._clear_grid()

        for i, artist in enumerate(self._filtered):
            card = _ArtistCard(artist, self._cover_size, i)
            card.clicked.connect(lambda k=artist.key: self.artist_selected.emit(k))
            card.context_action.connect(lambda act, k=artist.key: self._handle_context(act, k))
            if artist.key == self._selected_key:
                card.set_active(True)
            row = i // cols
            col = i % cols
            self._grid.addWidget(card, row, col, Qt.AlignTop)

    def _rebuild_list(self):
        if not self._filtered:
            self._list.clear()
            if not self._artists:
                self._empty_frame.show()
                self._empty_filter_frame.hide()
            else:
                self._empty_frame.hide()
                self._empty_filter_frame.show()
            self._list.hide()
            return
        self._empty_frame.hide()
        self._empty_filter_frame.hide()
        self._list.show()
        self._list.clear()
        for artist in self._filtered:
            dur = _format_dur(artist.total_duration)
            meta = f"{artist.album_count} álbumes · {artist.track_count} canciones"
            if dur:
                meta += f" · {dur}"
            if artist.genres:
                meta += f" · {', '.join(artist.genres[:3])}"

            it = QListWidgetItem(f"{artist.display_name}\n{meta}")
            it.setData(Qt.UserRole, artist.key)
            if artist.cover_paths:
                cover = load_cover_pixmap(artist.cover_paths[0], 48)
                if cover and not cover.isNull():
                    it.setIcon(QIcon(cover))
            self._list.addItem(it)

    def _on_list_item_clicked(self, item):
        key = item.data(Qt.UserRole)
        if key:
            self.artist_selected.emit(key)

    def _on_list_context(self, pos):
        item = self._list.itemAt(pos)
        if not item:
            return
        key = item.data(Qt.UserRole)
        if key:
            self._show_context_menu(self._list.viewport().mapToGlobal(pos), key)

    def _handle_context(self, action: str, artist_key: str):
        if action == "open":
            self.artist_selected.emit(artist_key)
        elif action == "play":
            self.artist_play_requested.emit(artist_key)
        elif action == "queue":
            self.artist_queue_requested.emit(artist_key)
        elif action == "playlist":
            self.artist_playlist_requested.emit(artist_key)
        elif action == "metadata":
            self.artist_metadata_requested.emit(artist_key)
        elif action == "refresh_info":
            self.artist_enrich_requested.emit(artist_key)
        elif action == "mix":
            self.artist_mix_requested.emit(artist_key)
        elif action == "analyze":
            self.artist_analyze_requested.emit(artist_key)
        elif action == "send_to_server":
            self.artist_send_to_server_requested.emit(artist_key)
        elif action == "resolve_aliases":
            self.artist_resolve_aliases_requested.emit(artist_key)

    def _show_context_menu(self, pos, artist_key: str):
        menu = QMenu(self)
        menu.setStyleSheet(menu_qss())

        acts = {
            "Abrir artista": "open",
            "Reproducir todo": "play",
            "Reproducir aleatorio": "shuffle",
            "Añadir a la cola": "queue",
            "Crear playlist": "playlist",
            "Crear mix del artista": "mix",
            "_sep1": None,
            "Editar metadatos": "metadata",
            "Analizar discografía": "analyze",
            "Enviar a Micro Server": "send_to_server",
            "_sep2": None,
            "Actualizar info externa": "refresh_info",
            "Resolver duplicados/alias": "resolve_aliases",
        }
        for label, action in acts.items():
            if action is None:
                menu.addSeparator()
            else:
                menu.addAction(
                    label,
                    lambda checked=False, a=action, k=artist_key: self._handle_context(a, k),
                )

        menu.exec(pos)


class _ArtistCard(QFrame):
    clicked = Signal(str)
    context_action = Signal(str)

    def __init__(self, artist: ArtistGroup, size: int, index: int):
        super().__init__()
        self._artist = artist
        self._active = False
        card_w = size + 24
        card_h = size + 165
        self.setFixedSize(card_w, card_h)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_qss()

        v = QVBoxLayout(self)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(6)

        # Cover area
        cover_area = QFrame()
        cover_area.setFixedSize(size, size)
        cover_area.setStyleSheet(
            "QFrame { background: rgba(255,255,255,0.035); border-radius: 24px; }")
        c_layout = QGridLayout(cover_area)
        c_layout.setContentsMargins(4, 4, 4, 4)
        c_layout.setSpacing(4)

        external_img = None
        thumb_path = getattr(artist, 'thumb_path', '') or ''
        if thumb_path and _os.path.exists(thumb_path):
            external_img = QPixmap(thumb_path)

        if external_img and not external_img.isNull():
            thumb_lbl = QLabel()
            thumb_lbl.setPixmap(
                external_img.scaled(size - 8, size - 8,
                                     Qt.KeepAspectRatio, Qt.SmoothTransformation))
            thumb_lbl.setAlignment(Qt.AlignCenter)
            c_layout.addWidget(thumb_lbl, 0, 0, 2, 2, Qt.AlignCenter)
        elif artist.cover_paths:
            for ci in range(min(4, len(artist.cover_paths))):
                pix = load_cover_pixmap(artist.cover_paths[ci], size // 2 - 4)
                lbl = QLabel()
                if pix and not pix.isNull():
                    lbl.setPixmap(pix.scaled(size // 2 - 8, size // 2 - 8,
                                              Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    lbl.setStyleSheet(
                        "background: rgba(255,255,255,0.04); border-radius: 8px;")
                lbl.setAlignment(Qt.AlignCenter)
                c_layout.addWidget(lbl, ci // 2, ci % 2, Qt.AlignCenter)
        else:
            place = QLabel()
            place.setPixmap(_artist_placeholder(size))
            place.setAlignment(Qt.AlignCenter)
            c_layout.addWidget(place, 0, 0, 2, 2, Qt.AlignCenter)

        v.addWidget(cover_area)

        # Name
        name = artist.display_name
        if len(name) > 24:
            name = name[:23] + "\u2026"
        name_lbl = QLabel(name)
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setWordWrap(False)
        name_lbl.setStyleSheet(
            f"color: {_TEXT}; font-size: 13px; font-weight: 700; background: transparent;")
        v.addWidget(name_lbl)

        # Badge row
        badge_row = QHBoxLayout()
        badge_row.setAlignment(Qt.AlignCenter)
        badge_row.setSpacing(6)

        if artist.enrichment_status == "loaded":
            ext_badge = QLabel("Info")
            ext_badge.setStyleSheet(
                "background: rgba(143,183,255,0.14); color: rgba(143,183,255,0.88);"
                "font-size: 9px; font-weight: 700; border-radius: 5px; padding: 1px 6px;")
            ext_badge.setFixedHeight(16)
            badge_row.addWidget(ext_badge)
        elif artist.enrichment_status == "loading":
            ext_badge = QLabel("Cargando")
            ext_badge.setStyleSheet(
                "background: rgba(143,183,255,0.08); color: rgba(143,183,255,0.56);"
                "font-size: 9px; font-weight: 600; border-radius: 5px; padding: 1px 6px;")
            ext_badge.setFixedHeight(16)
            badge_row.addWidget(ext_badge)
        elif artist.enrichment_status == "error":
            ext_badge = QLabel("Error")
            ext_badge.setStyleSheet(
                "background: rgba(143,183,255,0.06); color: rgba(143,183,255,0.52);"
                "font-size: 9px; font-weight: 600; border-radius: 5px; padding: 1px 6px;")
            ext_badge.setFixedHeight(16)
            badge_row.addWidget(ext_badge)
        elif artist.enrichment_status == "not_found":
            ext_badge = QLabel("Sin info")
            ext_badge.setStyleSheet(
                "background: rgba(255,255,255,0.03); color: rgba(255,255,255,0.44);"
                "font-size: 9px; font-weight: 600; border-radius: 5px; padding: 1px 6px;")
            ext_badge.setFixedHeight(16)
            badge_row.addWidget(ext_badge)

        meta = f"{artist.album_count} alb · {artist.track_count} canc"
        if len(meta) > 28:
            meta = meta[:27] + "\u2026"
        meta_lbl = QLabel(meta)
        meta_lbl.setAlignment(Qt.AlignCenter)
        meta_lbl.setStyleSheet(card_meta_qss())
        badge_row.addWidget(meta_lbl)
        v.addLayout(badge_row)

        # Quality badge
        quality_row = QHBoxLayout()
        quality_row.setAlignment(Qt.AlignCenter)
        quality_row.setSpacing(4)
        if artist.all_tracks:
            exts = set(
                _os.path.splitext(t.filepath)[1].lower().lstrip(".")
                for t in artist.all_tracks
            )
            has_lossless = any(e in _LOSSLESS_EXTS for e in exts)
            has_lossy = any(e in _LOSSY_EXTS for e in exts)
            has_hires = any(
                (getattr(t, "sample_rate", 0) or 0) >= 88200
                or (getattr(t, "bit_depth", 0) or 0) >= 24
                for t in artist.all_tracks
            )
            if has_hires:
                hb = QLabel("Hi-Res")
                hb.setStyleSheet(
                    "background: rgba(143,183,255,0.10); color: rgba(143,183,255,0.68);"
                    "font-size: 8px; font-weight: 700; border-radius: 4px; padding: 1px 5px;")
                quality_row.addWidget(hb)
            if has_lossless:
                lb = QLabel("Lossless")
                lb.setStyleSheet(
                    "background: rgba(72,199,142,0.10); color: rgba(72,199,142,0.60);"
                    "font-size: 8px; font-weight: 700; border-radius: 4px; padding: 1px 5px;")
                quality_row.addWidget(lb)
            if has_lossy and not has_lossless:
                lyb = QLabel("Lossy")
                lyb.setStyleSheet(
                    "background: rgba(255,180,50,0.10); color: rgba(255,180,50,0.60);"
                    "font-size: 8px; font-weight: 700; border-radius: 4px; padding: 1px 5px;")
                quality_row.addWidget(lyb)
        v.addLayout(quality_row)

        # Genres as badges
        if artist.genres:
            genre_row = QHBoxLayout()
            genre_row.setAlignment(Qt.AlignCenter)
            genre_row.setSpacing(4)
            for g in artist.genres[:2]:
                g_lbl = QLabel(g[:12])
                g_lbl.setStyleSheet(badge_qss("info"))
                genre_row.addWidget(g_lbl)
            v.addLayout(genre_row)

        # Years
        if artist.years:
            y_str = f"{artist.years[0]}\u2013{artist.years[-1]}" if len(artist.years) > 1 else str(artist.years[0])
            y_lbl = QLabel(y_str)
            y_lbl.setAlignment(Qt.AlignCenter)
            y_lbl.setStyleSheet(card_desc_qss())
            v.addWidget(y_lbl)

        v.addStretch()

    def _apply_qss(self):
        self.setObjectName("artistCard")
        style = glass_card_qss("artistCard")
        style += """
            QFrame#artistCard[active="true"] {
                background: rgba(143,183,255,0.10);
                border: 1px solid rgba(143,183,255,0.14);
            }
        """
        self.setStyleSheet(style)
        apply_card_shadow(self)

    def set_active(self, active: bool):
        if self._active == active:
            return
        self._active = active
        self.setProperty("active", str(active).lower())
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._artist.key)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._artist.key)
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(menu_qss())

        menu.addAction("Abrir artista", lambda: self.context_action.emit("open"))
        menu.addSeparator()
        menu.addAction("Reproducir todo", lambda: self.context_action.emit("play"))
        menu.addAction("Reproducir aleatorio", lambda: self.context_action.emit("shuffle"))
        menu.addAction("Añadir a la cola", lambda: self.context_action.emit("queue"))
        menu.addAction("Crear playlist", lambda: self.context_action.emit("playlist"))
        menu.addAction("Crear mix del artista", lambda: self.context_action.emit("mix"))
        menu.addSeparator()
        menu.addAction("Editar metadatos", lambda: self.context_action.emit("metadata"))
        menu.addAction("Analizar discografía", lambda: self.context_action.emit("analyze"))
        menu.addAction("Enviar a Micro Server", lambda: self.context_action.emit("send_to_server"))
        menu.addSeparator()
        menu.addAction("Actualizar info externa", lambda: self.context_action.emit("refresh_info"))
        menu.addAction("Resolver duplicados/alias", lambda: self.context_action.emit("resolve_aliases"))
        menu.exec(event.globalPos())


def _artist_placeholder(size: int) -> QPixmap:
    from PySide6.QtGui import QPainter, QPen
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(255, 255, 255, 20), 2))
    p.setBrush(QColor(255, 255, 255, 8))
    p.drawRoundedRect(8, 8, size - 16, size - 16, 20, 20)
    p.end()
    return pix
