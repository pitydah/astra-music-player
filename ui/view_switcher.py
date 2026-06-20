"""Segmented view switcher — premium capsule control with QButtonGroup."""
from PySide6.QtCore import Signal, Qt, QSize, QPropertyAnimation
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup, QGraphicsOpacityEffect

from ui.design_tokens import VIEW_BUTTON_W, VIEW_BUTTON_H, VIEW_ICON_W, VIEW_ICON_H

VIEW_MODE_DEFS = {
    "list":      {"icon": "warm_view_list",      "tooltip": "Ver como lista"},
    "grid":      {"icon": "warm_view_grid",      "tooltip": "Ver como mosaico"},
    "coverflow": {"icon": "warm_view_coverflow", "tooltip": "CoverFlow de álbumes"},
    "tree":      {"icon": "sidebar_folders",     "tooltip": "Ver árbol de carpetas"},
    "details":   {"icon": "warm_view_list",      "tooltip": "Ver detalles"},
}

_QSS = """
    QWidget#segmentedViewSwitcher {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.085);
        border-radius: 15px;
    }
    QWidget#segmentedViewSwitcher QPushButton {
        background: transparent;
        color: rgba(255,255,255,0.66);
        border: 1px solid transparent;
        border-radius: 12px;
        margin: 2px;
        padding: 0px;
        min-width: 44px; max-width: 44px;
        min-height: 36px; max-height: 36px;
    }
    QWidget#segmentedViewSwitcher QPushButton:hover {
        background: rgba(255,255,255,0.082);
        color: #FFFFFF;
        border: 1px solid rgba(255,255,255,0.105);
    }
    QWidget#segmentedViewSwitcher QPushButton:checked {
        background: rgba(255,255,255,0.142);
        color: #FFFFFF;
        border: 1px solid rgba(255,255,255,0.175);
    }
    QWidget#segmentedViewSwitcher QPushButton:disabled {
        background: transparent;
        color: rgba(255,255,255,0.25);
        border: 1px solid transparent;
    }
"""


class SegmentedViewSwitcher(QWidget):
    view_changed = Signal(str)

    def __init__(self, get_icon_func, parent=None):
        super().__init__(parent)
        self.setObjectName("segmentedViewSwitcher")
        self.setFixedHeight(40)
        self._available_modes: set[str] = set()

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        self._buttons: dict[str, QPushButton] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        for mode, defs in VIEW_MODE_DEFS.items():
            btn = QPushButton(QIcon(get_icon_func(defs["icon"])), "")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setFlat(True)
            btn.setFixedSize(VIEW_BUTTON_W, VIEW_BUTTON_H)
            btn.setMinimumSize(VIEW_BUTTON_W, VIEW_BUTTON_H)
            btn.setMaximumSize(VIEW_BUTTON_W, VIEW_BUTTON_H)
            btn.setIconSize(QSize(VIEW_ICON_W, VIEW_ICON_H))
            btn.setToolTip(defs.get("tooltip", mode))
            btn.clicked.connect(lambda checked=False, m=mode: self.set_view(m))
            btn.setVisible(False)
            self._group.addButton(btn)
            self._buttons[mode] = btn
            layout.addWidget(btn)

        self._current = "list"
        self._active_anim = None
        self.setStyleSheet(_QSS)
        self.setFixedWidth(0)
        self.hide()

    def set_view(self, mode: str, emit: bool = True):
        if mode not in self._buttons:
            return
        if mode not in self._available_modes:
            return
        if self._current == mode:
            return
        self._current = mode
        self._buttons[mode].setChecked(True)
        if emit:
            self.view_changed.emit(mode)
            self._pulse_active_button(self._buttons[mode])

    def _pulse_active_button(self, btn: QPushButton):
        """Subtle opacity pulse on the active button."""
        if self._active_anim is not None:
            self._active_anim.stop()
        effect = QGraphicsOpacityEffect(btn)
        effect.setOpacity(0.72)
        btn.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(120)
        anim.setStartValue(0.72)
        anim.setEndValue(1.0)
        anim.finished.connect(lambda: btn.setGraphicsEffect(None))
        self._active_anim = anim
        anim.start()

    @property
    def current_view(self) -> str:
        return self._current

    def set_available_modes(self, modes: list[str], default: str | None = None):
        self._available_modes = set(modes)
        visible_count = 0
        for mode_name, btn in self._buttons.items():
            vis = mode_name in self._available_modes
            btn.setVisible(vis)
            btn.setEnabled(vis)
            if vis:
                visible_count += 1

        # Hide if 0 or 1 mode (no point in a switcher with one option)
        if visible_count <= 1:
            self.setFixedWidth(0)
            self.hide()
            if visible_count == 1:
                self.set_view(modes[0], emit=False)
            return

        self.show()
        self.setFixedWidth((VIEW_BUTTON_W * visible_count) + 6)

        if self._current not in self._available_modes:
            target = default if default and default in self._available_modes else modes[0]
            self.set_view(target, emit=False)
