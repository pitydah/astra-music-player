"""Sidebar Widget — scrollable sections with collapsible headers."""

from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QFrame, QScrollArea, QGraphicsOpacityEffect,
)

from ui.icons import get_icon
from ui.design_tokens import (COLOR_ACCENT_ORANGE, COLOR_ACCENT_PINK,
    ACCENT_GRADIENT, SIDEBAR_ITEM_H, SIDEBAR_ICON, SIDEBAR_ACCENT_W)


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
                padding: 14px 12px 4px 12px;
                border: none; background: transparent;
                font-size: 11px; font-weight: 700;
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


class _Item(QFrame):
    clicked = Signal(str)

    def __init__(self, text: str, key: str, icon: str = "",
                 badge: str = "", dark: bool = False):
        super().__init__()
        self._key = key
        self._dark = dark
        self._active = False
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(SIDEBAR_ITEM_H)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(0)

        # Accent bar (fixed width, color changes on active)
        self._accent_bar = QFrame()
        self._accent_bar.setFixedWidth(SIDEBAR_ACCENT_W)
        self._accent_bar.setStyleSheet(
            "background: transparent; border: none;"
            "border-radius: 2px;")
        layout.addWidget(self._accent_bar)
        layout.addSpacing(8)

        label_text = text
        self._label = QLabel(label_text)
        self._label.setStyleSheet(
            "font-size:13px; color:rgba(255,255,255,0.6);"
            "background:transparent; border:none;")

        layout.addWidget(self._label)
        layout.addStretch()

        self._badge_label: QLabel | None = None
        if badge:
            self._badge_label = QLabel(badge)
            self._badge_label.setStyleSheet(
                "font-size:11px; color:rgba(255,255,255,0.4);"
                "background: rgba(255,255,255,0.06);"
                "border-radius: 4px; padding: 1px 6px;"
                "border: none;")
            layout.addWidget(self._badge_label)
            layout.addSpacing(8)

        self._icon_label: QLabel | None = None
        self._icon_effect: QGraphicsOpacityEffect | None = None
        if icon:
            qicon = QIcon(get_icon(icon)) if get_icon(icon) else QIcon()
            if not qicon.isNull():
                pix = qicon.pixmap(QSize(SIDEBAR_ICON, SIDEBAR_ICON))
                self._icon_label = QLabel()
                self._icon_label.setFixedSize(SIDEBAR_ICON, SIDEBAR_ICON)
                self._icon_label.setStyleSheet("background:transparent; border:none;")
                self._icon_label.setPixmap(pix)
                self._icon_effect = QGraphicsOpacityEffect()
                self._icon_effect.setOpacity(0.55)
                self._icon_label.setGraphicsEffect(self._icon_effect)
                layout.addWidget(self._icon_label)

        self._refresh_styles()

    def _refresh_styles(self):
        if self._active:
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(255,122,0,0.18), stop:1 rgba(221,0,122,0.08)
                    );
                    border-left: none;
                    border-radius: 10px;
                    margin: 1px 6px;
                }}
            """)
            self._accent_bar.setStyleSheet(
                f"background: qlineargradient(y1:0,y2:1,"
                f"stop:0 {COLOR_ACCENT_ORANGE},stop:1 {COLOR_ACCENT_PINK});"
                "border: none; border-radius: 2px;")
            self._label.setStyleSheet(
                "font-size:13px; color:#ffffff; font-weight:600;"
                "background:transparent; border:none;")
        else:
            self.setStyleSheet("""
                QFrame {
                    background: transparent;
                    border-left: none;
                    border-radius: 10px;
                    margin: 1px 6px;
                }
            """)
            self._accent_bar.setStyleSheet(
                "background: transparent; border: none; border-radius: 2px;")
            self._label.setStyleSheet(
                "font-size:13px; color:rgba(255,255,255,0.6);"
                "background:transparent; border:none;")
        if self._icon_label:
            self._icon_effect.setOpacity(1.0 if self._active else 0.55)

    def enterEvent(self, event):
        if not self._active:
            self.setStyleSheet("""
                QFrame {
                    background: rgba(255,255,255,0.06);
                    border-left: none;
                    border-radius: 10px;
                    margin: 1px 6px;
                }
            """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._active:
            self._refresh_styles()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._key)
        super().mousePressEvent(event)

    def set_style_active(self, active: bool):
        self._active = active
        self._refresh_styles()

    @property
    def key(self) -> str:
        return self._key

    def text(self) -> str:
        return self._label.text()


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
        from ui.theme import is_dark_mode
        self._dark = is_dark_mode()

        self.setObjectName("sidebarGlass")
        self.setAutoFillBackground(True)

        self.setStyleSheet("""
            QWidget#sidebarGlass {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(36,36,42,0.92),
                    stop:1 rgba(28,28,34,0.88)
                );
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 18px;
            }
        """)

        HERE = Path(__file__).parent
        txt = "#f5f5f7" if self._dark else "#1c1c1e"
        sep_c = "rgba(255,255,255,0.06)" if self._dark else "rgba(0,0,0,0.06)"
        sbg = "rgba(255,255,255,0.06)" if self._dark else "rgba(0,0,0,0.04)"
        sbd = "rgba(255,255,255,0.06)" if self._dark else "rgba(0,0,0,0.08)"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 8, 12)
        outer.setSpacing(8)

        # ── Branding: icon + ASTRA / Music Player ──
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(4, 4, 4, 4)
        brand_row.setSpacing(10)

        app_icon_label = QLabel()
        app_icon_path = str(HERE.parent / "icons" / "app_icon.png")
        app_pix = QPixmap(app_icon_path)
        if not app_pix.isNull():
            app_icon_label.setPixmap(
                app_pix.scaled(28, 28, Qt.KeepAspectRatio,
                              Qt.SmoothTransformation))
            app_icon_label.setFixedSize(28, 28)
        app_icon_label.setStyleSheet("background:transparent; border:none;")
        brand_row.addWidget(app_icon_label)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        title_lbl = QLabel("ASTRA")
        title_lbl.setStyleSheet(
            f"font-size:17px; font-weight:750; color:{txt};"
            "background:transparent; border:none;")
        sub_lbl = QLabel("Music Player")
        sub_lbl.setStyleSheet(
            f"font-size:10px; color:rgba(255,255,255,0.4);"
            "background:transparent; border:none;")
        brand_text.addWidget(title_lbl)
        brand_text.addWidget(sub_lbl)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        outer.addLayout(brand_row)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Filtrar menú...")
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
        for sec in list(self._sections.values()):
            sec.destroy()
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
