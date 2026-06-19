"""Segmented view switcher — unified capsule control with QButtonGroup."""

from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup


class SegmentedViewSwitcher(QWidget):
    view_changed = Signal(str)

    def __init__(self, get_icon_func, parent=None):
        super().__init__(parent)
        self.setObjectName("segmentedViewSwitcher")
        self.setFixedHeight(38)
        self.setFixedWidth(132)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        self._buttons = {
            "grid": QPushButton(QIcon(get_icon_func("warm_view_grid")), ""),
            "list": QPushButton(QIcon(get_icon_func("warm_view_list")), ""),
            "coverflow": QPushButton(QIcon(get_icon_func("warm_view_coverflow")), ""),
        }

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        for mode, btn in self._buttons.items():
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setFlat(True)
            btn.setFixedSize(42, 34)
            btn.setMinimumSize(42, 34)
            btn.setMaximumSize(42, 34)
            btn.setIconSize(QSize(32, 23))
            self._group.addButton(btn)
            layout.addWidget(btn)

        self.set_view("list", emit=False)

        self.setStyleSheet("""
            QWidget#segmentedViewSwitcher {
                background: rgba(255,255,255,0.065);
                border: 1px solid rgba(255,255,255,0.09);
                border-radius: 12px;
            }
            QWidget#segmentedViewSwitcher QPushButton {
                background: transparent;
                border: none;
                margin: 0;
                padding: 0;
                min-width: 42px;
                max-width: 42px;
                min-height: 34px;
                max-height: 34px;
                border-radius: 10px;
            }
            QWidget#segmentedViewSwitcher QPushButton:hover {
                background: rgba(255,255,255,0.08);
            }
            QWidget#segmentedViewSwitcher QPushButton:checked {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF7A00,
                    stop:1 #DD007A
                );
                border: none;
                margin: 0;
                padding: 0;
            }
        """)

        for mode, btn in self._buttons.items():
            btn.clicked.connect(lambda checked=False, m=mode: self.set_view(m))

    def set_view(self, mode: str, emit: bool = True):
        if mode not in self._buttons:
            return
        self._current = mode
        self._buttons[mode].setChecked(True)
        if emit:
            self.view_changed.emit(mode)

    @property
    def current_view(self) -> str:
        return self._current
