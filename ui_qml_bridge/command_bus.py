from PySide6.QtCore import QObject, Signal, Slot


class CommandBus(QObject):
    commandRequested = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str, dict)
    def execute(self, command: str, payload: dict):
        self.commandRequested.emit(command, payload)
