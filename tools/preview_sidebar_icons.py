"""Preview all sidebar icons at 24x24 and 32x32 for visual verification."""

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QVBoxLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.sidebar_icon_factory import sidebar_pixmap

ICONS = [
    "sidebar_library",
    "sidebar_songs",
    "sidebar_albums",
    "sidebar_folders",
    "sidebar_playlists",
    "sidebar_playlist_item",
    "sidebar_mix",
    "sidebar_unplayed",
    "sidebar_popular",
    "sidebar_identifier",
    "sidebar_radio",
    "sidebar_servers",
    "sidebar_navidrome",
    "sidebar_jellyfin",
    "sidebar_devices",
    "sidebar_add",
]


def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Astra — Sidebar Icon Preview")
    window.setStyleSheet("QWidget { background: #121215; }")

    layout = QVBoxLayout(window)
    layout.setContentsMargins(20, 20, 20, 20)

    title = QLabel("Sidebar Icons — QPainter Factory")
    title.setStyleSheet(
        "color: #FF7A00; font-size: 16px; font-weight: 700; padding: 0 0 12px 0;")
    layout.addWidget(title)

    sizes = [24, 32]
    for sz in sizes:
        sz_label = QLabel(f"{sz}×{sz} px")
        sz_label.setStyleSheet(
            "color: rgba(245,245,247,0.5); font-size: 12px; padding: 8px 0 4px 0;")
        layout.addWidget(sz_label)

        grid = QGridLayout()
        grid.setSpacing(10)

        for i, name in enumerate(ICONS):
            pix = sidebar_pixmap(name, sz)
            icon_label = QLabel()
            icon_label.setPixmap(pix)
            icon_label.setFixedSize(sz + 8, sz + 8)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet(
                "background: rgba(255,255,255,0.03); border-radius: 6px;")

            name_label = QLabel(name.replace("sidebar_", ""))
            name_label.setStyleSheet(
                "color: rgba(245,245,247,0.5); font-size: 9px;")
            name_label.setAlignment(Qt.AlignCenter)

            col = i % 8
            row = (i // 8) * 2

            grid.addWidget(icon_label, row, col, Qt.AlignCenter)
            grid.addWidget(name_label, row + 1, col, Qt.AlignCenter)

        layout.addLayout(grid)

    layout.addStretch()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
