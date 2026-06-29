"""IntelligencePage — local music intelligence: BPM, key, energy, similarity, local radio.

Connects to existing audio_analysis (FeatureRepository, AnalysisService)
and recommendation engines.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QProgressBar,
)

from ui.icons import get_pixmap
from ui.central.central_styles import (
    glass_card_qss, glass_button_qss, glass_progress_qss,
)

logger = logging.getLogger("michi.intelligence.ui")


class IntelligencePage(QWidget):
    navigate_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("intelligencePage")
        self._analysis = None
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

        title = QLabel("Inteligencia Local")
        title.setStyleSheet(
            "color: rgba(255,255,255,0.92); font-size: 22px; "
            "font-weight: 700; background: transparent;"
        )
        cl.addWidget(title)

        sub = QLabel(
            "Extrae características musicales de tu biblioteca: "
            "BPM, tonalidad, energía y similitud. "
            "Usa estos datos para crear mixes inteligentes y radio local."
        )
        sub.setStyleSheet(
            "color: rgba(255,255,255,0.56); font-size: 13px; "
            "background: transparent;"
        )
        sub.setWordWrap(True)
        cl.addWidget(sub)

        # Status
        status_card = QFrame()
        status_card.setStyleSheet(glass_card_qss("intelStatusCard", "base"))
        svl = QVBoxLayout(status_card)
        svl.setContentsMargins(20, 16, 20, 16)
        svl.setSpacing(8)

        st = QLabel("Estado del análisis")
        st.setStyleSheet(
            "color: rgba(255,255,255,0.88); font-size: 15px; "
            "font-weight: 600; background: transparent;"
        )
        svl.addWidget(st)

        self._status_lines = {}
        for label in ("Backend:", "Archivos analizados:", "Jobs pendientes:"):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(
                "color: rgba(255,255,255,0.56); font-size: 11px; "
                "background: transparent;"
            )
            val = QLabel("--")
            val.setStyleSheet(
                "color: rgba(255,255,255,0.78); font-size: 11px; "
                "font-weight: 600; background: transparent;"
            )
            row.addWidget(lbl)
            row.addWidget(val, 1)
            svl.addLayout(row)
            self._status_lines[label] = val

        btn_row = QHBoxLayout()
        self._scan_btn = QPushButton("Analizar biblioteca completa")
        self._scan_btn.setCursor(Qt.PointingHandCursor)
        self._scan_btn.setStyleSheet(glass_button_qss("primary"))
        self._scan_btn.clicked.connect(self._analyze_all)
        btn_row.addWidget(self._scan_btn)

        self._rebuild_btn = QPushButton("Reconstruir índice")
        self._rebuild_btn.setCursor(Qt.PointingHandCursor)
        self._rebuild_btn.setStyleSheet(glass_button_qss("secondary"))
        self._rebuild_btn.clicked.connect(self._rebuild_index)
        btn_row.addWidget(self._rebuild_btn)

        btn_row.addStretch()
        svl.addLayout(btn_row)

        self._analysis_progress = QProgressBar()
        self._analysis_progress.setRange(0, 100)
        self._analysis_progress.setValue(0)
        self._analysis_progress.setVisible(False)
        self._analysis_progress.setStyleSheet(glass_progress_qss())
        svl.addWidget(self._analysis_progress)

        cl.addWidget(status_card)

        # Feature grid
        grid = QGridLayout()
        grid.setSpacing(14)

        feature_cards = [
            ("sidebar_identifier", "BPM",
             "Tempo en pulsaciones por minuto.\n"
             "Se usa para agrupar canciones por\n"
             "ritmo y generar mixes coherentes.",
             self._show_bpm),
            ("sidebar_mix", "Tonalidad (Key)",
             "Key musical aproximada.\n"
             "Permite mezclar canciones en\n"
             "tonalidades compatibles.",
             self._show_key),
            ("sidebar_popular", "Energía",
             "Nivel de energía RMS.\n"
             "Clasifica canciones como calmadas,\n"
             "moderadas o enérgicas.",
             self._show_energy),
            ("sidebar_albums", "Similitud",
             "Distancia coseno entre vectores\n"
             "defeatures acústicas.\n"
             "Encuentra canciones parecidas.",
             self._show_similarity),
            ("sidebar_radio", "Radio Local",
             "Genera lista de reproducción\n"
             "infinita desde una canción,\n"
             "álbum o artista.",
             self._play_local_radio),
            ("sidebar_library", "Mix Inteligente",
             "Mix basado en reglas:\n"
             "BPM, key, energía, calidad,\n"
             "origen (CD/Vinilo).",
             self._create_smart_mix),
        ]

        for idx, (icon, title_t, desc, callback) in enumerate(feature_cards):
            card = self._build_feature_card(icon, title_t, desc, callback)
            grid.addWidget(card, idx // 3, idx % 3)

        for col in range(3):
            grid.setColumnStretch(col, 1)
        cl.addLayout(grid)
        cl.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

        self._refresh_status()

    def _build_feature_card(self, icon_key: str, title: str, desc: str,
                            callback) -> QFrame:
        card = QFrame()
        card.setObjectName(f"intelFeatureCard_{title}")
        card.setStyleSheet(glass_card_qss(card.objectName(), "elevated"))
        card.setMinimumHeight(160)

        cv = QVBoxLayout(card)
        cv.setContentsMargins(20, 16, 20, 16)
        cv.setSpacing(8)

        pix = get_pixmap(icon_key, size=36)
        icon_lbl = QLabel()
        if pix and not pix.isNull():
            icon_lbl.setPixmap(pix)
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            "background: rgba(143,183,255,0.06);"
            "border: 1px solid rgba(143,183,255,0.06);"
            "border-radius: 8px;"
        )
        cv.addWidget(icon_lbl)

        t = QLabel(title)
        t.setStyleSheet(
            "color: rgba(255,255,255,0.88); font-size: 14px; "
            "font-weight: 600; background: transparent; border: none;"
        )
        cv.addWidget(t)

        d = QLabel(desc)
        d.setStyleSheet(
            "color: rgba(255,255,255,0.50); font-size: 11px; "
            "background: transparent; border: none;"
        )
        d.setWordWrap(True)
        cv.addWidget(d)

        cv.addStretch()

        btn = QPushButton("Abrir")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(glass_button_qss("primary"))
        btn.setFixedWidth(80)
        btn.clicked.connect(callback)
        cv.addWidget(btn)

        return card

    def _get_service(self):
        if self._analysis is None:
            try:
                from audio_analysis.analysis_service import AnalysisService
                self._analysis = AnalysisService(None)
            except Exception as e:
                logger.warning("AnalysisService not available: %s", e)
        return self._analysis

    def _refresh_status(self):
        try:
            analysis = self._get_service()
            if analysis and analysis.enabled:
                self._status_lines["Backend:"].setText(
                    analysis._backend.capitalize()
                )
                repo = analysis._repo
                count = repo._conn.execute(
                    "SELECT COUNT(*) FROM audio_feature WHERE status='completed'"
                ).fetchone()[0]
                pending = repo._conn.execute(
                    "SELECT COUNT(*) FROM audio_analysis_job "
                    "WHERE status IN ('pending','running')"
                ).fetchone()[0]
                self._status_lines["Archivos analizados:"].setText(str(count))
                self._status_lines["Jobs pendientes:"].setText(str(pending))
            else:
                self._status_lines["Backend:"].setText("Desactivado")
        except Exception as e:
            logger.warning("Status refresh error: %s", e)

    def _analyze_all(self):
        analysis = self._get_service()
        if not analysis or not analysis.enabled:
            logger.warning("Analysis not available or disabled")
            return
        self._scan_btn.setEnabled(False)
        self._analysis_progress.setVisible(True)
        logger.info("Starting full library analysis...")

        def progress_cb(current, total, filepath):
            pct = int(current / total * 100) if total > 0 else 0
            self._analysis_progress.setValue(pct)
            from PySide6.QtCore import QCoreApplication
            QCoreApplication.processEvents()

        analysis.analyze_tracks_async(
            None, progress_cb=progress_cb,
            on_done=lambda: self._on_analysis_done(),
        )

    def _on_analysis_done(self):
        self._scan_btn.setEnabled(True)
        self._analysis_progress.setVisible(False)
        self._refresh_status()
        logger.info("Library analysis complete")

    def _rebuild_index(self):
        analysis = self._get_service()
        if not analysis:
            return
        try:
            repo = analysis._repo
            repo._conn.execute("DELETE FROM audio_similarity_cache")
            repo._conn.commit()
            logger.info("Similarity index rebuilt")
        except Exception as e:
            logger.warning("Rebuild failed: %s", e)
        self._refresh_status()

    def _show_bpm(self):
        self.navigate_requested.emit("library_hub")
        logger.info("BPM view requested")

    def _show_key(self):
        self.navigate_requested.emit("library_hub")
        logger.info("Key view requested")

    def _show_energy(self):
        self.navigate_requested.emit("library_hub")
        logger.info("Energy view requested")

    def _show_similarity(self):
        logger.info("Similarity view requested")

    def _play_local_radio(self):
        logger.info("Local radio requested")

    def _create_smart_mix(self):
        logger.info("Smart mix requested")
