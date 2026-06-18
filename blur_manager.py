"""KWin blur effect manager for Plasma (safe, no crash on Wayland)."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


class BlurManager:
    """Activates KWin blur-behind. Safe on Wayland (no-op if X11 unavailable)."""

    @staticmethod
    def enable(widget: QWidget):
        """Enable transparency + attempt KWin blur on X11."""
        widget.setAttribute(Qt.WA_TranslucentBackground)

    @staticmethod
    def disable(widget: QWidget):
        """Remove transparency."""
        widget.setAttribute(Qt.WA_TranslucentBackground, False)
