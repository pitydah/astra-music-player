"""Sidebar Widget — scrollable sections with collapsible headers."""

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QFrame, QScrollArea, QSizePolicy,
)

from icons import get_icon


def _qicon(name: str) -> QIcon:
    path = get_icon(name)
    return QIcon(path) if path else QIcon()


class _SectionHeader(QPushButton):
    def __init__(self, text: str, dark: bool):
        super().__init__()
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self._collapsed = False
        self._text = text
        self._dark = dark
        self._refresh()

    def _refresh(self):
        arrow = "▸" if self._collapsed else "▾"
        sec = "#a0a0a8" if self._dark else "#8e8e93"
        txt = "#f5f5f7" if self._dark else "#1c1c1e"
        self.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 12px 12px 4px 12px;
                border: none; background: transparent;
                font-size: 12px; font-weight: 700;
                color: {sec}; letter-spacing: 0.5px;
            }}
            QPushButton:hover {{ color: {txt}; }}
        """)
        self.setText(f"{arrow}  {self._text}")

    def toggle(self) -> bool:
        self._collapsed = not self._collapsed
        self._refresh()
        return self._collapsed

    @property
    def collapsed(self) -> bool:
        return self._collapsed


class _Item(QPushButton):
    def __init__(self, text: str, key: str, icon: str = "",
                 badge: str = "", dark: bool = False):
        super().__init__()
        self._key = key
        self._dark = dark
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(36)

        if icon:
            qicon = _qicon(icon)
            if not qicon.isNull():
                self.setIcon(qicon)
                self.setIconSize(QSize(22, 22))
        label = f"{text}  ·  {badge}" if badge else text
        self.setText(f"  {label}")
        self.set_style_active(False)

    def _style(self, active: bool) -> str:
        if active:
            return """
                QPushButton {
                    text-align: left; padding: 6px 10px; border: none;
                    border-radius: 8px; margin: 1px 4px; font-size: 14px;
                    color: #ffffff; font-weight: 600;
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FF7A00, stop:1 #DD007A
                    );
                }
            """
        txt = "#f5f5f7" if self._dark else "#1c1c1e"
        hover = ("rgba(255,122,0,0.10)" if self._dark
                 else "rgba(255,122,0,0.06)")
        return f"""
            QPushButton {{
                text-align: left; padding: 6px 10px; border: none;
                border-radius: 6px; margin: 1px 4px; font-size: 14px;
                color: {txt}; background: transparent;
            }}
            QPushButton:hover {{ background: {hover}; }}
        """

    def set_style_active(self, active: bool):
        self.setStyleSheet(self._style(active))

    @property
    def key(self) -> str:
        return self._key


class _Section:
    def __init__(self, parent: QWidget, layout: QVBoxLayout,
                 key: str, title: str, dark: bool):
        self.key = key
        self._items: list[_Item] = []
        self.header = _SectionHeader(title, dark)
        self.header.clicked.connect(self._on_header_click)
        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._inner = QVBoxLayout(self._container)
        self._inner.setContentsMargins(0, 0, 0, 0)
        self._inner.setSpacing(0)
        layout.addWidget(self.header)
        layout.addWidget(self._container)

    def _on_header_click(self):
        self._container.setVisible(not self.header.toggle())

    def add_item(self, item: _Item):
        self._inner.addWidget(item)
        self._items.append(item)

    def destroy(self):
        self.header.setParent(None)
        self.header.deleteLater()
        self._container.setParent(None)
        self._container.deleteLater()
        self._items.clear()


class SidebarWidget(QWidget):
    item_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._sections: dict[str, _Section] = {}
        self._items: dict[str, _Item] = {}
        self._current_key = "library"
        self._dark = True  # force dark for glassmorphism

        self.setObjectName("sidebarGlass")
        self.setAutoFillBackground(True)

        txt = "#f5f5f7" if self._dark else "#1c1c1e"
        sep_c = "rgba(255,255,255,0.06)" if self._dark else "rgba(0,0,0,0.06)"
        sbg = "rgba(255,255,255,0.06)" if self._dark else "rgba(0,0,0,0.04)"
        sbd = "rgba(255,255,255,0.06)" if self._dark else "rgba(0,0,0,0.08)"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 4, 8)
        outer.setSpacing(4)

        h = QLabel("✦ ASTRA")
        h.setStyleSheet(f"font-size:15px;font-weight:700;color:{txt};padding:4px 10px;")
        outer.addWidget(h)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar...")
        self._search.setClearButtonEnabled(True)
        self._search.setStyleSheet(f"""
            QLineEdit {{
                background:{sbg}; border:1px solid {sbd}; border-radius:6px;
                padding:4px 10px; font-size:12px; color:{txt};
            }}
            QLineEdit:focus {{ border-color:rgba(255,122,0,0.4); }}
        """)
        self._search.setAttribute(Qt.WA_MacShowFocusRect, False)
        self._search.textChanged.connect(self._filter)
        outer.addWidget(self._search)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background:{sep_c};")
        outer.addWidget(sep)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollBar:vertical{width:4px;background:transparent;}"
            "QScrollBar::handle:vertical{background:rgba(128,128,128,0.25);border-radius:2px;}"
            "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setSpacing(0)
        self._container_layout.addStretch()

        self._scroll.setWidget(self._container)
        outer.addWidget(self._scroll)

    def _clear(self):
        # Remove all section widgets from container layout
        for sec in list(self._sections.values()):
            self._container_layout.removeWidget(sec.header)
            sec.header.hide()
            self._container_layout.removeWidget(sec._container)
            sec._container.hide()
        self._sections.clear()
        self._items.clear()

    def add_section(self, key: str, title: str, icon: str = ""):
        # Remove terminal stretch, add section, re-add stretch
        n = self._container_layout.count()
        if n > 0:
            stretch_item = self._container_layout.takeAt(n - 1)
            del stretch_item
        sec = _Section(self._container, self._container_layout,
                       key, title, self._dark)
        self._container_layout.addStretch()
        self._sections[key] = sec
        return sec

    def add_item(self, section_key: str, key: str, text: str,
                 icon: str = "", badge: str = ""):
        sec = self._sections.get(section_key)
        if not sec:
            return None
        item = _Item(text, key, icon, badge, self._dark)
        item.clicked.connect(lambda checked=None, k=key: self._on_item_click(k))
        sec.add_item(item)
        self._items[key] = item
        return item

    def _on_item_click(self, key: str):
        self.set_active(key)
        self.item_clicked.emit(key)

    def set_active(self, key: str):
        old = self._items.get(self._current_key)
        if old:
            old.set_style_active(False)
        new = self._items.get(key)
        if new:
            new.set_style_active(True)
            self._current_key = key

    def _filter(self, text: str):
        text = text.lower()
        for item in self._items.values():
            item.setVisible(text == "" or text in item.text().lower())
        for sec in self._sections.values():
            has_vis = any(it.isVisible() for it in sec._items)
            if text != "":
                sec.header.setVisible(has_vis)
                sec._container.setVisible(has_vis and not sec.header.collapsed)
            else:
                sec.header.setVisible(True)
                sec._container.setVisible(not sec.header.collapsed)
