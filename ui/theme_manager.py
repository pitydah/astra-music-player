"""Theme Manager — detect, switch, and apply system theme.

Detects KDE Plasma color scheme via QPalette lightness.
Falls back to polling QPalette every 5s (no DBus dependency).
"""

import logging

from PySide6.QtCore import QTimer, QObject, Signal
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from ui.design_tokens import get_tokens, set_theme, current_theme

logger = logging.getLogger("astra.theme")


class ThemeManager(QObject):
    theme_changed = Signal(str)  # "dark" | "light" | "amoled"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = "dark"
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll)
        self._poll_timer.setInterval(5000)

    def detect(self) -> str:
        """Detect system theme from QPalette window color."""
        try:
            app = QApplication.instance()
            if app is None:
                return "dark"
            palette = app.palette()
            lightness = palette.color(QPalette.Window).lightness()
            if lightness <= 20:
                return "amoled"
            elif lightness <= 128:
                return "dark"
            return "light"
        except Exception:
            return "dark"

    def apply(self):
        """Detect and apply theme. Call on startup and on change."""
        detected = self.detect()
        if detected != self._current:
            self._current = detected
            set_theme(detected)
            self.theme_changed.emit(detected)
            logger.info("Theme changed to %s", detected)

    def start_polling(self):
        self._poll_timer.start()

    def stop_polling(self):
        self._poll_timer.stop()

    def _poll(self):
        self.apply()

    @property
    def theme(self) -> str:
        return self._current


def create_theme_manager(parent=None) -> ThemeManager:
    mgr = ThemeManager(parent)
    mgr.apply()
    mgr.start_polling()
    return mgr
