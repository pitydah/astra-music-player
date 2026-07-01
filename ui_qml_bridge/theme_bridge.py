from PySide6.QtCore import QObject, Signal, Property


class ThemeBridge(QObject):
    themeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark_mode = True

    @Property(bool, notify=themeChanged)
    def darkMode(self):
        return self._dark_mode

    @darkMode.setter
    def darkMode(self, enabled: bool):
        if enabled != self._dark_mode:
            self._dark_mode = enabled
            self.themeChanged.emit()
