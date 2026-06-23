"""MetadataStudioPage — wrapper for the existing metadata editor."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
)


class MetadataStudioPage(QWidget):
    def __init__(self, metadata_editor: QWidget,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("metadataStudioPage")

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
            "Edita metadatos, caratulas y organiza tu biblioteca. "
            "Smart Tagging y Library Doctor estaran disponibles en futuras fases."
        )
        subtitle.setObjectName("metadataStudioSubtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        layout.addWidget(metadata_editor, 1)

        self.setStyleSheet("""
            QWidget#metadataStudioPage {
                background: #090B11;
            }
            QFrame#metadataStudioHeader {
                background: transparent;
                border-bottom: 1px solid rgba(255,255,255,0.03);
            }
            QLabel#metadataStudioTitle {
                color: rgba(255,255,255,0.92);
                font-size: 16px;
                font-weight: 600;
            }
            QLabel#metadataStudioSubtitle {
                color: rgba(255,255,255,0.52);
                font-size: 12px;
                margin-top: 2px;
            }
        """)
