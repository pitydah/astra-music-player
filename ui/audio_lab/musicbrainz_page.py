"""MusicBrainzPage — search MusicBrainz for artist, album, and recording metadata.

Connects to existing KnowledgeBrokerService for lookups
and SmartTaggingService for applying suggestions.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QComboBox,
    QScrollArea,     QListWidget,
    QProgressBar, QMessageBox, QFileDialog,
)

from ui.central.central_styles import (
    glass_card_qss, glass_button_qss, glass_input_qss,
    glass_progress_qss,
)

logger = logging.getLogger("michi.musicbrainz.ui")


class MusicBrainzPage(QWidget):
    navigate_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("musicbrainzPage")
        self._kb = None
        self._results: list[dict] = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(40, 32, 40, 32)
        cl.setSpacing(16)

        title = QLabel("MusicBrainz")
        title.setStyleSheet(
            "color: rgba(255,255,255,0.92); font-size: 22px; "
            "font-weight: 700; background: transparent;"
        )
        cl.addWidget(title)

        sub = QLabel(
            "Busca álbumes, artistas y canciones en la base de datos "
            "MusicBrainz para identificar y enriquecer tu biblioteca."
        )
        sub.setStyleSheet(
            "color: rgba(255,255,255,0.56); font-size: 13px; "
            "background: transparent;"
        )
        sub.setWordWrap(True)
        cl.addWidget(sub)

        # Search
        search_card = QFrame()
        search_card.setStyleSheet(glass_card_qss("mbSearchCard"))
        svl = QVBoxLayout(search_card)
        svl.setContentsMargins(20, 16, 20, 16)
        svl.setSpacing(10)

        sl = QLabel("Buscar")
        sl.setStyleSheet(
            "color: rgba(255,255,255,0.88); font-size: 14px; "
            "font-weight: 600; background: transparent;"
        )
        svl.addWidget(sl)

        search_row = QHBoxLayout()
        self._search_type = QComboBox()
        self._search_type.setStyleSheet(
            "QComboBox { background: rgba(255,255,255,0.055); "
            "border: 1px solid rgba(255,255,255,0.05); "
            "border-radius: 8px; padding: 6px 10px; "
            "color: rgba(255,255,255,0.86); font-size: 12px; }"
        )
        self._search_type.addItems(["Artista", "Álbum", "Canción"])
        search_row.addWidget(self._search_type)

        self._search_input = QLineEdit()
        self._search_input.setStyleSheet(glass_input_qss())
        self._search_input.setPlaceholderText(
            "Buscar en MusicBrainz..."
        )
        self._search_input.returnPressed.connect(self._do_search)
        search_row.addWidget(self._search_input, 1)

        self._search_btn = QPushButton("Buscar")
        self._search_btn.setCursor(Qt.PointingHandCursor)
        self._search_btn.setStyleSheet(glass_button_qss("primary"))
        self._search_btn.clicked.connect(self._do_search)
        search_row.addWidget(self._search_btn)

        svl.addLayout(search_row)

        cl.addWidget(search_card)

        # Results
        results_card = QFrame()
        results_card.setStyleSheet(glass_card_qss("mbResultsCard"))
        rvl = QVBoxLayout(results_card)
        rvl.setContentsMargins(20, 16, 20, 16)
        rvl.setSpacing(10)

        rl = QLabel("Resultados")
        rl.setStyleSheet(
            "color: rgba(255,255,255,0.88); font-size: 14px; "
            "font-weight: 600; background: transparent;"
        )
        rvl.addWidget(rl)

        self._results_list = QListWidget()
        self._results_list.setStyleSheet(
            "QListWidget { background: rgba(255,255,255,0.02); "
            "border: 1px solid rgba(255,255,255,0.04); "
            "border-radius: 8px; color: rgba(255,255,255,0.72); "
            "font-size: 12px; min-height: 200px; }"
        )
        rvl.addWidget(self._results_list)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        self._progress.setStyleSheet(glass_progress_qss())
        rvl.addWidget(self._progress)

        cl.addWidget(results_card)

        # Apply section
        apply_card = QFrame()
        apply_card.setStyleSheet(glass_card_qss("mbApplyCard"))
        avl = QVBoxLayout(apply_card)
        avl.setContentsMargins(20, 16, 20, 16)
        avl.setSpacing(10)

        ap_label = QLabel("Aplicar metadatos")
        ap_label.setStyleSheet(
            "color: rgba(255,255,255,0.88); font-size: 14px; "
            "font-weight: 600; background: transparent;"
        )
        avl.addWidget(ap_label)

        file_row = QHBoxLayout()
        self._file_label = QLabel("Ningún archivo seleccionado")
        self._file_label.setStyleSheet(
            "color: rgba(255,255,255,0.56); font-size: 11px; "
            "background: transparent;"
        )
        file_row.addWidget(self._file_label, 1)

        self._select_file_btn = QPushButton("Seleccionar archivo...")
        self._select_file_btn.setCursor(Qt.PointingHandCursor)
        self._select_file_btn.setStyleSheet(glass_button_qss("secondary"))
        self._select_file_btn.clicked.connect(self._select_target_file)
        file_row.addWidget(self._select_file_btn)

        self._apply_btn = QPushButton("Aplicar metadatos")
        self._apply_btn.setCursor(Qt.PointingHandCursor)
        self._apply_btn.setStyleSheet(glass_button_qss("primary"))
        self._apply_btn.clicked.connect(self._apply_metadata)
        self._apply_btn.setEnabled(False)
        file_row.addWidget(self._apply_btn)

        avl.addLayout(file_row)
        self._apply_status = QLabel("")
        self._apply_status.setStyleSheet(
            "color: rgba(255,255,255,0.56); font-size: 11px; "
            "background: transparent;"
        )
        avl.addWidget(self._apply_status)

        cl.addWidget(apply_card)

        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _get_kb(self):
        if self._kb is None:
            try:
                from integrations.knowledge_broker.service import (
                    KnowledgeBrokerService
                )
                self._kb = KnowledgeBrokerService()
            except Exception as e:
                logger.warning("KnowledgeBroker not available: %s", e)
        return self._kb

    def _do_search(self):
        query = self._search_input.text().strip()
        if not query:
            return

        kb = self._get_kb()
        if not kb:
            QMessageBox.warning(
                self, "MusicBrainz",
                "KnowledgeBrokerService no está disponible.\n\n"
                "Verifica que MusicBrainz esté habilitado en "
                "Configuración > Privacidad."
            )
            return

        search_type = self._search_type.currentText()
        self._results_list.clear()
        self._results.clear()
        self._progress.setVisible(True)

        try:
            if search_type == "Artista":
                result = kb.lookup_artist(query)
                if result and isinstance(result, dict):
                    item_text = result.get("name", query)
                    if result.get("mbid"):
                        item_text += f"  [{result['mbid'][:8]}...]"
                    if result.get("disambiguation"):
                        item_text += f"  — {result['disambiguation']}"
                    self._results.append(result)
                    self._results_list.addItem(item_text)

            elif search_type == "Álbum":
                result = kb.lookup_album(query)
                if result and isinstance(result, dict):
                    item_text = result.get("title", query)
                    if result.get("artist"):
                        item_text += f"  — {result['artist']}"
                    if result.get("year"):
                        item_text += f"  ({result['year']})"
                    self._results.append(result)
                    self._results_list.addItem(item_text)

            elif search_type == "Canción":
                result = kb.lookup_recording(query)
                if result and isinstance(result, dict):
                    item_text = result.get("title", query)
                    if result.get("artist"):
                        item_text += f"  — {result['artist']}"
                    self._results.append(result)
                    self._results_list.addItem(item_text)

            if self._results_list.count() == 0:
                self._results_list.addItem(
                    "(Sin resultados. Intenta con otro término.)"
                )

        except Exception as e:
            logger.exception("MusicBrainz search failed")
            self._results_list.addItem(f"Error: {e}")

        self._progress.setVisible(False)
        self._apply_btn.setEnabled(bool(self._results))

    def _select_target_file(self):
        fp, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de audio", "",
            "Audio (*.flac *.mp3 *.m4a *.ogg *.opus)"
        )
        if not fp:
            return
        self._target_file = fp
        self._file_label.setText(fp.split("/")[-1])
        self._apply_btn.setEnabled(bool(self._results))

    def _apply_metadata(self):
        if not self._results:
            self._apply_status.setText("No hay resultados de búsqueda para aplicar.")
            return
        target = getattr(self, '_target_file', None)
        if not target:
            self._apply_status.setText("Selecciona un archivo de audio primero.")
            return

        idx = self._results_list.currentRow()
        if idx < 0 or idx >= len(self._results):
            self._apply_status.setText("Selecciona un resultado de la lista.")
            return

        result = self._results[idx]
        search_type = self._search_type.currentText()
        self._apply_status.setText("Aplicando metadatos...")

        try:
            from metadata.tag_writer import write_tags
            from metadata.tag_model import TrackTags

            tags = TrackTags(filepath=target)

            if search_type == "Artista":
                name = result.get("name", "")
                if name:
                    tags.artist = name
                    tags.mark_dirty("artist")

            elif search_type == "Álbum":
                title = result.get("title", "")
                artist = result.get("artist", "")
                year = result.get("year", 0)
                mbid = result.get("mbid", "")
                if title:
                    tags.album = title
                    tags.mark_dirty("album")
                if artist:
                    tags.albumartist = artist
                    tags.mark_dirty("albumartist")
                if year:
                    tags.date = str(year)
                    tags.mark_dirty("date")
                if mbid:
                    tags.musicbrainz_albumid = mbid
                    tags.mark_dirty("musicbrainz_albumid")

            elif search_type == "Canción":
                title = result.get("title", "")
                artist = result.get("artist", "")
                mbid = (result.get("recording_mbid") or
                        result.get("mbid") or "")
                if title:
                    tags.title = title
                    tags.mark_dirty("title")
                if artist:
                    tags.artist = artist
                    tags.mark_dirty("artist")
                if mbid:
                    tags.musicbrainz_trackid = mbid
                    tags.mark_dirty("musicbrainz_trackid")

            write_tags(target, tags)
            self._apply_status.setText(
                f"Metadatos aplicados correctamente a {target.split('/')[-1]}"
            )
            logger.info("MusicBrainz metadata applied to %s", target)

        except Exception as e:
            logger.exception("Failed to apply MusicBrainz metadata")
            self._apply_status.setText(f"Error: {e}")
