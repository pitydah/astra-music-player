#!/usr/bin/python3
"""Astra Music Player — Plasma-native music player with KWin blur, Apple Music layout.

Self-contained. Python 3 + PySide6 + Qt Multimedia (GStreamer).
"""

import os
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from ui.theme import build_plasma_palette, PLASMA_QSS
from ui.window import MainWindow


def main():
    os.environ.setdefault("QT_MEDIA_BACKEND", "gstreamer")

    app = QApplication(sys.argv)
    app.setApplicationName("AstraMusicPlayer")
    app.setStyle("Fusion")
    app.setPalette(build_plasma_palette())
    app.setStyleSheet(PLASMA_QSS)

    font = QFont("Inter", 11)
    if not font.exactMatch():
        font = QFont("SF Pro Display", 11)
    if not font.exactMatch():
        font = QFont("sans-serif", 11)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
