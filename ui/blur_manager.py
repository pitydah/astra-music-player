"""KWin blur effect manager for Plasma (safe, no crash on Wayland)."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

try:
    from PyKDE5.KWindowEffects import KWindowEffects
    HAVE_KWINDOWEFFECTS = True
except ImportError:
    HAVE_KWINDOWEFFECTS = False


class BlurManager:
    @staticmethod
    def enable_blur(window: QWidget):
        """Activates transparency + KWin blur on the window."""
        window.setAttribute(Qt.WA_TranslucentBackground)
        if HAVE_KWINDOWEFFECTS:
            KWindowEffects.enableBlurBehind(window.winId(), True)
        else:
            print("Astra: KWindowEffects not available.")
            print("  Enable System Settings → Desktop Effects → Blur for glassmorphism.")

    @staticmethod
    def disable(widget: QWidget):
        """Remove transparency."""
        widget.setAttribute(Qt.WA_TranslucentBackground, False)
