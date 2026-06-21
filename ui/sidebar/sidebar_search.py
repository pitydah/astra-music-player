"""SidebarSearch — glass search field with clear button."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLineEdit

from ui.sidebar.sidebar_styles import search_qss


class SidebarSearch(QLineEdit):
    search_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarSearch")
        self.setPlaceholderText("Buscar en Astra")
        self.setClearButtonEnabled(True)
        self.setStyleSheet(search_qss())
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.textChanged.connect(
            lambda t: self.search_changed.emit(t))
