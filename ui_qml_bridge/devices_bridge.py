from PySide6.QtCore import QObject, Signal, Property, Slot


class DevicesBridge(QObject):
    stateChanged = Signal()

    def __init__(self, sync_manager=None, parent=None):
        super().__init__(parent)
        self._sync_mgr = sync_manager
        self._server_active = False
        self._server_port = 53318
        self._peers = []
        self._paired_devices = []

    @Property(bool, notify=stateChanged)
    def serverActive(self):
        return self._server_active

    @Property(int, notify=stateChanged)
    def serverPort(self):
        return self._server_port

    @Property("QVariantList", notify=stateChanged)
    def peers(self):
        return self._peers

    @Property("QVariantList", notify=stateChanged)
    def pairedDevices(self):
        return self._paired_devices

    @Slot()
    def startServer(self):
        if self._sync_mgr and hasattr(self._sync_mgr, 'start'):
            self._sync_mgr.start()
        self._server_active = True
        self.stateChanged.emit()

    @Slot()
    def stopServer(self):
        if self._sync_mgr and hasattr(self._sync_mgr, 'stop'):
            self._sync_mgr.stop()
        self._server_active = False
        self.stateChanged.emit()

    @Slot()
    def refresh(self):
        if self._sync_mgr:
            peers = []
            if hasattr(self._sync_mgr, 'get_all_peers'):
                all_peers = self._sync_mgr.get_all_peers()
                for p in all_peers:
                    peers.append({
                        "alias": getattr(p, 'alias', '') or str(p),
                        "device": getattr(p, 'device', 'desktop'),
                        "ip": getattr(p, 'ip', ''),
                        "port": getattr(p, 'port', 0),
                    })
            self._peers = peers
            self._server_active = hasattr(self._sync_mgr, 'is_running') and self._sync_mgr.is_running()
        self.stateChanged.emit()
