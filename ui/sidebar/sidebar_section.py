"""SidebarSection — collapsible section with header and items."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from ui.sidebar.sidebar_tokens import (
    SIDEBAR_SECTION_TOP, SIDEBAR_SECTION_BOTTOM,
)
from ui.sidebar.sidebar_styles import (
    section_header_qss, section_chevron_qss,
)


class SidebarSectionHeader(QWidget):
    clicked = Signal()

    def __init__(self, text: str, dark: bool = True):
        super().__init__()
        self._collapsed = False
        self._text = text
        self._dark = dark
        self._hovered = False
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, SIDEBAR_SECTION_TOP, 12, SIDEBAR_SECTION_BOTTOM)
        layout.setSpacing(0)

        self._title = QLabel(text.upper())
        self._title.setStyleSheet(section_header_qss(dark))
        layout.addWidget(self._title)
        layout.addStretch()

        self._chevron = QLabel("\u25be")  # ▾
        self._chevron.setStyleSheet(section_chevron_qss(dark))
        self._chevron.setFixedWidth(14)
        self._chevron.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._chevron)

    def toggle(self) -> bool:
        self._collapsed = not self._collapsed
        self._chevron.setText("\u25b8" if self._collapsed else "\u25be")
        return self._collapsed

    @property
    def collapsed(self) -> bool:
        return self._collapsed

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self._hovered = True
        self._title.setStyleSheet(section_header_qss(self._dark, hover=True))
        self._chevron.setStyleSheet(section_chevron_qss(self._dark, hover=True))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._title.setStyleSheet(section_header_qss(self._dark))
        self._chevron.setStyleSheet(section_chevron_qss(self._dark))
        super().leaveEvent(event)


class SidebarSection:
    def __init__(self, parent_widget: QWidget, layout: QVBoxLayout,
                 key: str, title: str, dark: bool = True):
        self.key = key
        self._items: list = []
        self.header = SidebarSectionHeader(title, dark)
        self.header.clicked.connect(self._on_header_click)

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._inner = QVBoxLayout(self._container)
        self._inner.setContentsMargins(0, 0, 0, 0)
        self._inner.setSpacing(0)

        layout.addWidget(self.header)
        layout.addWidget(self._container)
        self._container.setVisible(True)

    def _on_header_click(self):
        self.header.toggle()
        self._container.setVisible(not self.header.collapsed)

    def add_item(self, item):
        self._inner.addWidget(item)
        self._items.append(item)

    def destroy(self):
        self.header.setParent(None)
        self.header.deleteLater()
        self._container.setParent(None)
        self._container.deleteLater()
        self._items.clear()
