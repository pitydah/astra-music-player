"""Segmented view switcher — premium capsule control with QButtonGroup."""
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup

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
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.075);
        border-radius: 14px;
    }
    QWidget#segmentedViewSwitcher QPushButton {
        background: transparent;
        color: rgba(255,255,255,0.72);
        border: 1px solid transparent;
        border-radius: 11px;
        margin: 2px;
        padding: 0px;
        min-width: 42px; max-width: 42px;
        min-height: 34px; max-height: 34px;
    }
    QWidget#segmentedViewSwitcher QPushButton:hover {
        background: rgba(255,255,255,0.08);
        color: #FFFFFF;
        border: 1px solid rgba(255,255,255,0.10);
    }
    QWidget#segmentedViewSwitcher QPushButton:checked {
        background: rgba(255,255,255,0.135);
        color: #FFFFFF;
        border: 1px solid rgba(255,255,255,0.16);
    }
    QWidget#segmentedViewSwitcher QPushButton:disabled {
        background: transparent;
        color: rgba(255,255,255,0.28);
        border: 1px solid transparent;
    }
"""


class SegmentedViewSwitcher(QWidget):
    view_changed = Signal(str)

    def __init__(self, get_icon_func, parent=None):
        super().__init__(parent)
        self.setObjectName("segmentedViewSwitcher")
        self.setFixedHeight(38)
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
        self.setStyleSheet(_QSS)
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

        if visible_count == 0:
            self.setFixedWidth(0)
            self.hide()
            return

        self.show()
        self.setFixedWidth((VIEW_BUTTON_W * visible_count) + 6)

        if self._current not in self._available_modes:
            target = default if default and default in self._available_modes else modes[0]
            self.set_view(target, emit=False)
