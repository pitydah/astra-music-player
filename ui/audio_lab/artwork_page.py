"""ArtworkPage — manage album artwork: view, scan local covers, replace, embed."""

from __future__ import annotations

import logging
import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QFileDialog, QScrollArea,
    QListWidget, QProgressBar, QMessageBox,
)

from ui.central.central_styles import (
    glass_card_qss, glass_button_qss, glass_progress_qss,
)

logger = logging.getLogger("michi.artwork.ui")

_AUDIO_FILTER = "Audio (*.flac *.mp3 *.m4a *.mp4 *.ogg *.oga *.opus)"
_IMAGE_FILTER = "Imágenes (*.jpg *.jpeg *.png *.gif *.webp *.bmp)"


class ArtworkPage(QWidget):
    """Small, safe artwork tool for Audio Lab.

    The page intentionally avoids pretending that a library album context exists.
    Users must choose explicit destination audio files before embedding artwork.
    """

    navigate_requested = Signal(str)

    def __init__(self, db=None):
        super().__init__()
        self.setObjectName("artworkPage")
        self._resolver = None
        self._db = db
        self._new_artwork_path = ""
        self._target_audio_files: list[str] = []
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

        title = QLabel("Carátulas")
        title.setStyleSheet(
            "color: rgba(255,255,255,0.92); font-size: 22px; "
            "font-weight: 700; background: transparent;"
        )
        cl.addWidget(title)

        sub = QLabel(
            "Gestiona carátulas de forma segura: carga una imagen, "
            "elige archivos destino y luego incrusta la portada."
        )
        sub.setStyleSheet(
            "color: rgba(255,255,255,0.56); font-size: 13px; "
            "background: transparent;"
        )
        sub.setWordWrap(True)
        cl.addWidget(sub)

        art_card = QFrame()
        art_card.setStyleSheet(glass_card_qss("artDisplayCard"))
        avl = QVBoxLayout(art_card)
        avl.setContentsMargins(20, 16, 20, 16)
        avl.setSpacing(10)

        art_top = QHBoxLayout()
        self._art_preview = QLabel()
        self._art_preview.setFixedSize(200, 200)
        self._art_preview.setAlignment(Qt.AlignCenter)
        self._art_preview.setStyleSheet(
            "background: rgba(255,255,255,0.03); "
            "border: 1px solid rgba(255,255,255,0.06); "
            "border-radius: 12px;"
        )
        art_top.addWidget(self._art_preview)

        art_info = QVBoxLayout()
        self._art_status = QLabel(
            "Carga una imagen y selecciona los archivos de audio donde se incrustará."
        )
        self._art_status.setStyleSheet(
            "color: rgba(255,255,255,0.62); font-size: 12px; "
            "background: transparent;"
        )
        self._art_status.setWordWrap(True)
        art_info.addWidget(self._art_status)

        self._target_label = QLabel("Destino: ningún archivo seleccionado")
        self._target_label.setStyleSheet(
            "color: rgba(255,255,255,0.50); font-size: 11px; "
            "background: transparent;"
        )
        self._target_label.setWordWrap(True)
        art_info.addWidget(self._target_label)
        art_info.addStretch()

        self._replace_btn = QPushButton("Cargar imagen...")
        self._replace_btn.setCursor(Qt.PointingHandCursor)
        self._replace_btn.setStyleSheet(glass_button_qss("secondary"))
        self._replace_btn.clicked.connect(self._replace_artwork)
        art_info.addWidget(self._replace_btn)

        self._select_audio_btn = QPushButton("Seleccionar archivos destino...")
        self._select_audio_btn.setCursor(Qt.PointingHandCursor)
        self._select_audio_btn.setStyleSheet(glass_button_qss("secondary"))
        self._select_audio_btn.clicked.connect(self._select_target_audio_files)
        art_info.addWidget(self._select_audio_btn)

        self._embed_btn = QPushButton("Incrustar en archivos")
        self._embed_btn.setCursor(Qt.PointingHandCursor)
        self._embed_btn.setStyleSheet(glass_button_qss("primary"))
        self._embed_btn.clicked.connect(self._embed_artwork)
        self._embed_btn.setEnabled(False)
        art_info.addWidget(self._embed_btn)

        art_top.addLayout(art_info, 1)
        avl.addLayout(art_top)
        cl.addWidget(art_card)

        missing_card = QFrame()
        missing_card.setStyleSheet(glass_card_qss("artMissingCard"))
        mvl = QVBoxLayout(missing_card)
        mvl.setContentsMargins(20, 16, 20, 16)
        mvl.setSpacing(10)

        ml = QLabel("Álbumes sin carátula")
        ml.setStyleSheet(
            "color: rgba(255,255,255,0.88); font-size: 14px; "
            "font-weight: 600; background: transparent;"
        )
        mvl.addWidget(ml)

        self._scan_missing_btn = QPushButton("Detectar álbumes sin carátula")
        self._scan_missing_btn.setCursor(Qt.PointingHandCursor)
        self._scan_missing_btn.setStyleSheet(glass_button_qss("secondary"))
        self._scan_missing_btn.clicked.connect(self._scan_missing)
        mvl.addWidget(self._scan_missing_btn)

        self._missing_list = QListWidget()
        self._missing_list.setStyleSheet(
            "QListWidget { background: rgba(255,255,255,0.02); "
            "border: 1px solid rgba(255,255,255,0.04); "
            "border-radius: 8px; color: rgba(255,255,255,0.72); "
            "font-size: 11px; min-height: 100px; }"
        )
        mvl.addWidget(self._missing_list)

        self._missing_progress = QProgressBar()
        self._missing_progress.setRange(0, 100)
        self._missing_progress.setValue(0)
        self._missing_progress.setVisible(False)
        self._missing_progress.setStyleSheet(glass_progress_qss())
        mvl.addWidget(self._missing_progress)

        cl.addWidget(missing_card)
        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _get_resolver(self):
        if self._resolver is None:
            from ui.audio_lab.services.artwork_resolver import ArtworkResolver
            self._resolver = ArtworkResolver()
        return self._resolver

    def _update_embed_enabled(self):
        self._embed_btn.setEnabled(
            bool(self._new_artwork_path and self._target_audio_files)
        )

    def _replace_artwork(self):
        fp, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", _IMAGE_FILTER
        )
        if not fp:
            return

        pix = QPixmap(fp)
        if pix.isNull():
            QMessageBox.warning(self, "Carátulas", "No se pudo cargar la imagen.")
            return

        scaled = pix.scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._art_preview.setPixmap(scaled)
        self._art_status.setText(
            f"Imagen cargada: {os.path.basename(fp)}\n"
            f"{pix.width()}x{pix.height()} px"
        )
        self._new_artwork_path = fp
        self._update_embed_enabled()

    def _select_target_audio_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar archivos de audio", "", _AUDIO_FILTER
        )
        self._target_audio_files = [f for f in files if os.path.isfile(f)]
        count = len(self._target_audio_files)
        if count == 0:
            self._target_label.setText("Destino: ningún archivo seleccionado")
        elif count == 1:
            self._target_label.setText(
                f"Destino: {os.path.basename(self._target_audio_files[0])}"
            )
        else:
            self._target_label.setText(f"Destino: {count} archivos seleccionados")
        self._update_embed_enabled()

    def _embed_artwork(self):
        fp = self._new_artwork_path
        if not fp or not os.path.exists(fp):
            QMessageBox.information(
                self, "Carátulas",
                "Selecciona una imagen primero."
            )
            return
        if not self._target_audio_files:
            QMessageBox.information(
                self, "Carátulas",
                "Selecciona los archivos de audio destino antes de incrustar."
            )
            return

        confirm = QMessageBox.question(
            self, "Incrustar carátula",
            f"Incrustar la imagen seleccionada en {len(self._target_audio_files)} archivo(s)?\n\n"
            "La carátula existente será reemplazada.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            from ui.audio_lab.services.tag_writer import TagWriter
            tw = TagWriter()
            ok = 0
            failed: list[str] = []
            for audio_path in self._target_audio_files:
                try:
                    result = tw.embed_cover(audio_path, fp)
                    if result.get("ok"):
                        ok += 1
                    else:
                        failed.append(os.path.basename(audio_path))
                except Exception:
                    logger.exception("Failed to embed artwork in %s", audio_path)
                    failed.append(os.path.basename(audio_path))

            if failed:
                self._art_status.setText(
                    f"Carátula incrustada en {ok}/{len(self._target_audio_files)} archivos. "
                    f"Fallidos: {', '.join(failed[:4])}"
                )
            else:
                self._art_status.setText(
                    f"Carátula incrustada en {ok} archivo(s)."
                )
            logger.info("Artwork embedded in %d files", ok)
        except Exception as e:
            logger.exception("Failed to embed artwork")
            QMessageBox.warning(self, "Error", f"No se pudo incrustar: {e}")

    def _scan_missing(self):
        self._missing_list.clear()
        self._missing_progress.setVisible(True)
        self._missing_progress.setValue(0)

        temp_db = None
        db = self._db
        try:
            if db is None:
                from library.library_db import LibraryDB, DB_PATH
                temp_db = LibraryDB(DB_PATH)
                db = temp_db

            rows = db._conn.execute(
                "SELECT DISTINCT album, albumartist, directory "
                "FROM media_items WHERE deleted_at IS NULL "
                "AND album IS NOT NULL AND album != ''"
            ).fetchall()

            resolver = self._get_resolver()
            missing = []
            total = max(1, len(rows))

            for i, (album, artist, directory) in enumerate(rows):
                if (i + 1) % 10 == 0:
                    pct = int((i + 1) / total * 100)
                    self._missing_progress.setValue(pct)
                    from PySide6.QtCore import QCoreApplication
                    QCoreApplication.processEvents()

                if not directory or not os.path.isdir(directory):
                    continue

                covers = resolver.search_album_art({
                    "album": album, "artist": artist, "directory": directory,
                })
                if not covers:
                    missing.append(f"{artist} — {album}" if artist else album)

            self._missing_list.clear()
            if missing:
                for entry in missing[:100]:
                    self._missing_list.addItem(entry)
                if len(missing) > 100:
                    self._missing_list.addItem(
                        f"... y {len(missing) - 100} más"
                    )
            else:
                self._missing_list.addItem(
                    "Todos los álbumes tienen carátula."
                )

        except Exception as e:
            logger.exception("Missing artwork scan failed")
            self._missing_list.addItem(f"Error: {e}")
        finally:
            if temp_db is not None:
                try:
                    temp_db.close()
                except Exception:
                    logger.debug("Temporary artwork DB close failed", exc_info=True)
            self._missing_progress.setVisible(False)
