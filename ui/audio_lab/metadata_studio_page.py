"""MetadataStudioPage — wrapper for metadata editor + Smart Tagging + Library Doctor."""

from __future__ import annotations

import contextlib

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSplitter, QTabWidget,
)

from ui.audio_lab.services.smart_tagging_service import SmartTaggingService
from ui.audio_lab.models import TagSuggestion


class MetadataStudioPage(QWidget):
    def __init__(self, metadata_editor: QWidget,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("metadataStudioPage")
        self._editor = metadata_editor
        self._st_service = SmartTaggingService()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("metadataStudioHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 12, 20, 12)

        title = QLabel("Metadata Studio")
        title.setObjectName("metadataStudioTitle")
        header_layout.addWidget(title)

        subtitle = QLabel(
            "Edita metadatos, caratulas y organiza tu biblioteca."
        )
        subtitle.setObjectName("metadataStudioSubtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._smart_btn = QPushButton("Buscar metadata")
        self._smart_btn.setObjectName("smartTagBtn")
        self._smart_btn.setCursor(Qt.PointingHandCursor)
        self._smart_btn.clicked.connect(self._on_start_smart_tagging)
        self._smart_btn.setVisible(False)
        btn_row.addWidget(self._smart_btn)

        self._doctor_btn = QPushButton("Library Doctor")
        self._doctor_btn.setObjectName("doctorBtn")
        self._doctor_btn.setCursor(Qt.PointingHandCursor)
        self._doctor_btn.clicked.connect(self._on_start_library_doctor)
        self._doctor_btn.setVisible(True)
        btn_row.addWidget(self._doctor_btn)

        btn_row.addStretch()
        header_layout.addLayout(btn_row)
        layout.addWidget(header)

        splitter = QSplitter(Qt.Vertical)
        splitter.setObjectName("metadataStudioSplitter")

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.addWidget(self._editor)
        splitter.addWidget(editor_container)

        self._tools_tabs = QTabWidget()
        self._tools_tabs.setObjectName("metadataStudioTabs")

        from ui.audio_lab.smart_tagging_panel import SmartTaggingPanel
        self._st_panel = SmartTaggingPanel()
        self._st_panel.suggestions_accepted.connect(self._on_suggestions_accepted)
        self._tools_tabs.addTab(self._st_panel, "Smart Tagging")

        from ui.audio_lab.library_doctor_panel import LibraryDoctorPanel
        self._doctor_panel = LibraryDoctorPanel()
        self._doctor_panel.scan_requested.connect(self._on_scan_library)
        self._tools_tabs.addTab(self._doctor_panel, "Library Doctor")

        self._tools_tabs.setVisible(False)
        splitter.addWidget(self._tools_tabs)

        splitter.setSizes([500, 250])
        layout.addWidget(splitter, 1)

        self.setStyleSheet("""
            QWidget#metadataStudioPage { background: #090B11; }
            QFrame#metadataStudioHeader { background: transparent; border-bottom: 1px solid rgba(255,255,255,0.03); }
            QLabel#metadataStudioTitle { color: rgba(255,255,255,0.92); font-size: 16px; font-weight: 600; }
            QLabel#metadataStudioSubtitle { color: rgba(255,255,255,0.52); font-size: 12px; margin-top: 2px; }
            QSplitter#metadataStudioSplitter::handle { background: rgba(255,255,255,0.03); height: 1px; }
            QTabWidget#metadataStudioTabs::pane { border: none; background: transparent; }
            QTabBar::tab {
                background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
                border-radius: 8px; padding: 6px 16px; color: rgba(255,255,255,0.52);
                font-size: 12px; margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: rgba(143,183,255,0.08); border: 1px solid rgba(143,183,255,0.12);
                color: rgba(143,183,255,0.85);
            }
        """)
        from ui.central.central_styles import glass_button_qss
        self._smart_btn.setStyleSheet(glass_button_qss("primary"))
        self._doctor_btn.setStyleSheet(glass_button_qss("ghost"))

        self._editor.files_saved.connect(self._on_files_loaded)

    def _on_files_loaded(self):
        self._smart_btn.setVisible(True)

    def _on_start_smart_tagging(self):
        self._smart_btn.setEnabled(False)
        self._st_panel.set_loading(True)
        self._tools_tabs.setCurrentIndex(0)
        self._tools_tabs.setVisible(True)

        suggestions: list[TagSuggestion] = []

        try:
            editor = self._editor
            if hasattr(editor, '_tags') and editor._tags:
                tags = editor._tags[0]
                artist = getattr(tags, 'artist', '') or ''
                title = getattr(tags, 'title', '') or ''
                album = getattr(tags, 'album', '') or ''
                genre = getattr(tags, 'genre', '') or ''

                if title:
                    track = type('Track', (), {
                        'title': title, 'artist': artist,
                        'album': album, 'genre': genre,
                        'track_number': getattr(tags, 'tracknumber', '') or '',
                        'duration': getattr(tags, 'duration', 0) or 0,
                    })()
                    suggestions.extend(self._st_service.suggest_for_track(track))
                if album:
                    suggestions.extend(self._st_service.suggest_for_album(artist, album))
                if artist:
                    norm = self._st_service.normalize_artist_name(artist)
                    if norm.confidence > 0:
                        suggestions.append(norm)
                if genre:
                    genre_sug = self._st_service.suggest_genre(tags)
                    if genre_sug.confidence > 0:
                        suggestions.append(genre_sug)

        except Exception:
            import logging
            logging.getLogger("michi.audio_lab").warning("Smart tagging failed", exc_info=True)

        self._smart_btn.setEnabled(True)
        self._st_panel.set_loading(False)
        self._st_panel.set_suggestions(suggestions)

    def _on_suggestions_accepted(self, suggestions: list[TagSuggestion]):
        editor = self._editor
        if not hasattr(editor, '_tags') or not editor._tags:
            return

        for sug in suggestions:
            if not sug.apply or not sug.suggested:
                continue
            field = sug.field
            value = sug.suggested
            field_map = {"album": "album", "year": "date", "mb_album_id": "musicbrainz_albumid", "cover_url": ""}
            tag_field = field_map.get(field, field)
            if not tag_field:
                continue

            for tags in editor._tags:
                with contextlib.suppress(Exception):
                    tags.set_field(tag_field, value)

        if hasattr(editor, '_rebuild_after_load'):
            editor._rebuild_after_load()

        self._tools_tabs.setVisible(False)

    def _on_start_library_doctor(self):
        self._doctor_btn.setEnabled(False)
        self._doctor_panel.set_loading(True)
        self._tools_tabs.setCurrentIndex(1)
        self._tools_tabs.setVisible(True)

        editor = self._editor
        db = None
        if hasattr(editor, '_db'):
            db = editor._db
        elif hasattr(self, '_db'):
            db = self._db

        if db is None:
            from library.library_db import LibraryDB
            db = LibraryDB()

        from ui.audio_lab.services.library_doctor import LibraryDoctor
        doctor = LibraryDoctor(db)
        scan = doctor.scan_all()
        repair = doctor.generate_repair_plan()

        self._doctor_btn.setEnabled(True)
        self._doctor_panel.set_loading(False)
        self._doctor_panel.show_results(scan, repair)
