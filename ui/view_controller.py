"""ViewController — named view manager for QStackedWidget."""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget, QWidget


class ViewController(QObject):
    view_changed = Signal(str)

    def __init__(self, stack: QStackedWidget, parent=None):
        super().__init__(parent)
        self._stack = stack
        self._views: dict[str, QWidget] = {}
        self._current = ""

    def register(self, name: str, widget: QWidget):
        self._views[name] = widget
        if self._stack.indexOf(widget) < 0:
            self._stack.addWidget(widget)

    def replace(self, name: str, widget: QWidget, delete_old: bool = True):
        old = self._views.get(name)
        if old is widget:
            return
        if old is not None:
            self._stack.removeWidget(old)
            if delete_old:
                old.deleteLater()
        self._views[name] = widget
        self._stack.addWidget(widget)

    def show(self, name: str):
        widget = self._views.get(name)
        if widget is None:
            return
        self._stack.setCurrentWidget(widget)
        self._current = name
        self.view_changed.emit(name)

    def current(self) -> str:
        return self._current

    def widget(self, name: str) -> QWidget | None:
        return self._views.get(name)
