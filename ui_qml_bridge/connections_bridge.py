from PySide6.QtCore import QObject, Signal, Property, Slot


class ConnectionsBridge(QObject):
    stateChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._micro_server_state = "not_configured"
        self._discovered = []

    @Property(str, notify=stateChanged)
    def microServerState(self):
        return self._micro_server_state

    @Property("QVariantList", notify=stateChanged)
    def discoveredServers(self):
        return self._discovered

    @Slot()
    def scanForServers(self):
        self._discovered = [
            {"name": "Demo Michi Micro Server", "host": "192.168.1.100:8080",
             "type": "Michi Micro Server", "status": "detected"}
        ]
        self.stateChanged.emit()

    @Slot()
    def addManualServer(self):
        self.stateChanged.emit()

    @Slot()
    def openHomeAudio(self):
        self.stateChanged.emit()
