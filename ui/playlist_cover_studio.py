"""Playlist Cover Studio — choose and generate playlist cover art styles."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QGridLayout,
)
from PySide6.QtGui import QPixmap

from ui.central.central_styles import glass_button_qss
from ui.services.playlist_cover_service import get_playlist_cover


_STYLES = [
    ("mosaic", "Mosaico 2×2"),
    ("mosaic_3x3", "Mosaico 3×3"),
    ("dominant_album", "Álbum principal"),
    ("dominant_artist", "Artista principal"),
    ("gradient", "Gradiente"),
    ("genre", "Género"),
    ("quality", "Calidad"),
    ("none", "Ninguna"),
]


class PlaylistCoverStudio(QWidget):
    cover_changed = Signal(int, str, str)  # pid, cover_path, cover_type

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pid = 0
        self._current_type = "mosaic"
        self.setWindowTitle("Playlist Cover Studio")
        self.setStyleSheet("background: #090B11;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("Personalizar portada")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: 700; background: transparent;")
        layout.addWidget(title)

        self._preview = QLabel()
        self._preview.setFixedSize(200, 200)
        self._preview.setAlignment(Qt.AlignCenter)
        self._preview.setStyleSheet(
            "QLabel { background: rgba(255,255,255,0.04); border-radius: 16px; }")
        layout.addWidget(self._preview, alignment=Qt.AlignCenter)

        grid = QGridLayout()
        grid.setSpacing(8)
        self._style_btns = {}
        for i, (key, label) in enumerate(_STYLES):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(36)
            btn.setStyleSheet(glass_button_qss("secondary"))
            btn.clicked.connect(lambda checked=False, k=key: self._select_style(k))
            grid.addWidget(btn, i // 4, i % 4)
            self._style_btns[key] = btn
        layout.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        custom_btn = QPushButton("Imagen personalizada")
        custom_btn.setStyleSheet(glass_button_qss("primary"))
        custom_btn.clicked.connect(self._choose_custom)
        btn_row.addWidget(custom_btn)

        apply_btn = QPushButton("Aplicar")
        apply_btn.setStyleSheet(glass_button_qss("primary"))
        apply_btn.clicked.connect(self._apply)
        btn_row.addWidget(apply_btn)

        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet(glass_button_qss("secondary"))
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)

    def set_playlist(self, pid: int, playlist: dict, tracks: list):
        self._pid = pid
        self._playlist = playlist
        self._tracks = tracks
        self._current_type = playlist.get("cover_type", "mosaic") or "mosaic"
        self._update_preview()
        for key, btn in self._style_btns.items():
            btn.setChecked(key == self._current_type)

    def _select_style(self, key: str):
        self._current_type = key
        for k, btn in self._style_btns.items():
            btn.setChecked(k == key)
        self._update_preview()

    def _update_preview(self):
        pl = self._playlist or {}
        pl = {**pl, "cover_type": self._current_type}
        pix = get_playlist_cover(pl, self._tracks or [])
        if pix and not pix.isNull():
            self._preview.setPixmap(pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _choose_custom(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "",
            "Imágenes (*.png *.jpg *.jpeg *.webp)")
        if path:
            pix = QPixmap(path)
            if not pix.isNull():
                self._preview.setPixmap(pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self._current_type = "custom"
                self.cover_changed.emit(self._pid, path, "custom")

    def _apply(self):
        if self._pid:
            self.cover_changed.emit(self._pid, "", self._current_type)
