from PySide6.QtCore import QObject, Signal, Property, Slot


class HomeAudioBridge(QObject):
    stateChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ha_state = "not_configured"
        self._stream_state = "concept"
        self._receiver_count = 0

    @Property(str, notify=stateChanged)
    def homeAssistantState(self):
        return self._ha_state

    @Property(str, notify=stateChanged)
    def streamState(self):
        return self._stream_state

    @Property(int, notify=stateChanged)
    def receiverCount(self):
        return self._receiver_count

    @Slot()
    def configureHomeAssistant(self):
        self.stateChanged.emit()

    @Slot()
    def openDiagnostics(self):
        self.stateChanged.emit()

    @Slot()
    def openStreamConcept(self):
        self.stateChanged.emit()
