"""SongsDetailPanel — right-side detail panel for the selected song."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QPushButton

from ui.central.central_styles import glass_card_qss, glass_button_qss


class SongsDetailPanel(QFrame):
    """Right-side detail panel for the selected song."""

    play_requested = Signal(object)
    queue_requested = Signal(object)
    edit_requested = Signal(object)
    locate_requested = Signal(object)
    fav_requested = Signal(object)
    analyze_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_item = None
        self._status = None
        self.setObjectName("songsDetailPanel")
        self.setFixedWidth(280)
        self.setStyleSheet(glass_card_qss("songsDetailPanel", "elevated"))
        self._setup_ui()
        self.clear()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        self._title_lbl = QLabel()
        self._title_lbl.setWordWrap(True)
        self._title_lbl.setStyleSheet("color: rgba(255,255,255,0.92); font-size: 14px; font-weight: 600; background: transparent; border: none;")
        layout.addWidget(self._title_lbl)

        self._artist_lbl = QLabel()
        self._artist_lbl.setStyleSheet("color: rgba(255,255,255,0.72); font-size: 12px; background: transparent; border: none;")
        layout.addWidget(self._artist_lbl)

        self._album_lbl = QLabel()
        self._album_lbl.setStyleSheet("color: rgba(255,255,255,0.62); font-size: 12px; background: transparent; border: none;")
        layout.addWidget(self._album_lbl)

        self._status_lbl = QLabel()
        self._status_lbl.setWordWrap(True)
        self._status_lbl.setStyleSheet("color: rgba(255,255,255,0.50); font-size: 11px; background: transparent; border: none;")
        layout.addWidget(self._status_lbl)

        self._tech_lbl = QLabel()
        self._tech_lbl.setWordWrap(True)
        self._tech_lbl.setStyleSheet("color: rgba(255,255,255,0.45); font-size: 11px; background: transparent; border: none;")
        layout.addWidget(self._tech_lbl)

        self._path_lbl = QLabel()
        self._path_lbl.setWordWrap(True)
        self._path_lbl.setStyleSheet("color: rgba(255,255,255,0.30); font-size: 10px; background: transparent; border: none;")
        layout.addWidget(self._path_lbl)

        layout.addStretch()

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(3)

        self._play_btn = QPushButton("▶ Reproducir")
        self._play_btn.setStyleSheet(glass_button_qss("primary"))
        self._play_btn.clicked.connect(lambda: self.play_requested.emit(self._current_item))
        btn_layout.addWidget(self._play_btn)

        self._queue_btn = QPushButton("⊕ Añadir a cola")
        self._queue_btn.setStyleSheet(glass_button_qss("primary"))
        self._queue_btn.clicked.connect(lambda: self.queue_requested.emit(self._current_item))
        btn_layout.addWidget(self._queue_btn)

        self._edit_btn = QPushButton("✎ Editar metadatos")
        self._edit_btn.setStyleSheet(glass_button_qss("primary"))
        self._edit_btn.clicked.connect(lambda: self.edit_requested.emit(self._current_item))
        btn_layout.addWidget(self._edit_btn)

        self._fav_btn = QPushButton("♥ Favorito")
        self._fav_btn.setStyleSheet(glass_button_qss("primary"))
        self._fav_btn.clicked.connect(lambda: self.fav_requested.emit(self._current_item))
        btn_layout.addWidget(self._fav_btn)

        self._locate_btn = QPushButton("📁 Localizar")
        self._locate_btn.setStyleSheet(glass_button_qss("primary"))
        self._locate_btn.clicked.connect(lambda: self.locate_requested.emit(self._current_item))
        btn_layout.addWidget(self._locate_btn)

        self._analyze_btn = QPushButton("🔬 Analizar calidad")
        self._analyze_btn.setStyleSheet(glass_button_qss("primary"))
        self._analyze_btn.clicked.connect(lambda: self.analyze_requested.emit(self._current_item))
        btn_layout.addWidget(self._analyze_btn)

        layout.addLayout(btn_layout)

    def show_item(self, item, status=None):
        self._current_item = item
        self._status = status
        self._title_lbl.setText(item.title or item.filename or "?")
        self._artist_lbl.setText(f"Artista: {item.artist or '?'}")
        self._album_lbl.setText(f"Álbum: {item.album or '?'}")

        # Status badges
        status_parts = []
        if status:
            if status.get("is_favorite"):
                status_parts.append("★ Favorito")
            if status.get("missing_metadata"):
                status_parts.append("Sin metadata")
            labels = status.get("badges", [])
            for lb in labels[:4]:
                if lb not in ("★",) and "Sin " not in lb:
                    status_parts.append(lb)
        self._status_lbl.setText(" · ".join(status_parts) if status_parts else "")

        # Technical data
        tech_parts = []
        ext = (item.ext or "").lstrip(".").upper()
        if ext:
            tech_parts.append(ext)
        if item.sample_rate:
            tech_parts.append(f"{item.sample_rate // 1000}kHz")
        if item.bit_depth:
            tech_parts.append(f"{item.bit_depth}bit")
        if item.channels:
            tech_parts.append(f"{item.channels}ch")
        if item.bitrate:
            tech_parts.append(f"{item.bitrate // 1000}kbps")
        if item.bpm:
            tech_parts.append(f"{item.bpm} BPM")
        if item.replaygain_track:
            tech_parts.append(f"RG:{item.replaygain_track:.1f}dB")
        self._tech_lbl.setText(" · ".join(tech_parts))
        self._path_lbl.setText(item.filepath or "")
        self.setVisible(True)

    def clear(self):
        self._current_item = None
        self._status = None
        self._title_lbl.setText("Selecciona una canción")
        self._artist_lbl.setText("")
        self._album_lbl.setText("")
        self._status_lbl.setText("")
        self._tech_lbl.setText("")
        self._path_lbl.setText("")
