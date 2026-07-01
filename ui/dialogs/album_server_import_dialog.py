"""AlbumServerImportDialog — preflight + confirm + progress for Michi Micro Server import."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QMessageBox,
)

from ui.central.central_styles import (
    glass_button_qss, section_title_qss,
)


class AlbumServerImportDialog(QDialog):
    """Simple dialog for confirming album import to Michi Micro Server."""

    def __init__(self, parent, album_title: str, total: int, existing: int,
                 needs_upload: int, errors: int = 0):
        super().__init__(parent)
        self.setWindowTitle("Enviar álbum a Michi Micro Server")
        self.setMinimumWidth(420)
        self._confirmed = False

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(f"Álbum: {album_title}")
        title.setStyleSheet(section_title_qss())
        layout.addWidget(title)

        layout.addWidget(QLabel(f"Pistas totales: {total}"))
        layout.addWidget(QLabel(f"Ya existen en servidor: {existing}"))
        layout.addWidget(QLabel(f"Nuevas a subir: {needs_upload}"))
        if errors:
            layout.addWidget(QLabel(f"Errores: {errors}"))

        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(glass_button_qss("secondary"))
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        self._confirm_btn = QPushButton("Enviar")
        self._confirm_btn.setStyleSheet(glass_button_qss("primary"))
        self._confirm_btn.clicked.connect(self._on_confirm)
        btn_row.addWidget(self._confirm_btn)
        layout.addLayout(btn_row)

    def _on_confirm(self):
        self._confirmed = True
        self.accept()

    def was_confirmed(self) -> bool:
        return self._confirmed

    def set_progress(self, current: int, total: int):
        self._progress.setVisible(True)
        self._progress.setMaximum(total)
        self._progress.setValue(current)

    @staticmethod
    def show_report(parent, title: str, message: str, is_error: bool = False):
        if is_error:
            QMessageBox.critical(parent, title, message)
        else:
            QMessageBox.information(parent, title, message)
