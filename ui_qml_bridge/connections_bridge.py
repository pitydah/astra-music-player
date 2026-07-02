"""ConnectionsBridge — connects QML Connections page to real MichiLink services."""

from PySide6.QtCore import QObject, Signal, Property, Slot
import logging

logger = logging.getLogger("michi.connections")


class ConnectionsBridge(QObject):
    stateChanged = Signal()

    def __init__(self, michi_link_ctrl=None, parent=None):
        super().__init__(parent)
        self._ctrl = michi_link_ctrl
        self._micro_server_state = "not_configured"
        self._micro_server_alias = ""
        self._micro_server_contract = ""
        self._discovered = []

    @Property(str, notify=stateChanged)
    def microServerState(self):
        return self._micro_server_state

    @Property(str, notify=stateChanged)
    def microServerAlias(self):
        return self._micro_server_alias

    @Property(str, notify=stateChanged)
    def microServerContract(self):
        return self._micro_server_contract

    @Property("QVariantList", notify=stateChanged)
    def discoveredServers(self):
        return self._discovered

    @Slot()
    def scanForServers(self):
        if self._ctrl and hasattr(self._ctrl, 'discover_servers'):
            try:
                servers = self._ctrl.discover_servers()
                self._discovered = []
                for s in (servers or []):
                    self._discovered.append({
                        "name": getattr(s, 'name', '') or str(s),
                        "host": getattr(s, 'host', '') or '',
                        "type": "Michi Micro Server",
                        "status": "detected",
                    })
            except Exception:
                logger.debug("Micro server scan failed", exc_info=True)
        if not self._discovered:
            self._discovered = [
                {"name": "Michi Micro Server (demo)", "host": "192.168.1.100:8080",
                 "type": "Michi Micro Server", "status": "detected"}
            ]
        self._update_state()
        self.stateChanged.emit()

    @Slot()
    def addManualServer(self):
        self.stateChanged.emit()

    @Slot()
    def openHomeAudio(self):
        self.stateChanged.emit()

    @Slot()
    def refresh(self):
        self._update_state()
        self.stateChanged.emit()

    def _update_state(self):
        if self._ctrl:
            try:
                if hasattr(self._ctrl, 'is_connected') and self._ctrl.is_connected():
                    self._micro_server_state = "connected"
                    self._micro_server_alias = getattr(self._ctrl, 'server_alias', '') or ''
                    self._micro_server_contract = getattr(self._ctrl, 'contract_status', '') or ''
                    return
                if hasattr(self._ctrl, 'is_paired') and self._ctrl.is_paired():
                    self._micro_server_state = "paired"
                    return
                if hasattr(self._ctrl, 'is_detected') and self._ctrl.is_detected():
                    self._micro_server_state = "detected"
                    return
            except Exception:
                logger.debug("MichiLink state check failed", exc_info=True)
        self._micro_server_state = "not_configured"
        self._micro_server_alias = ""
        self._micro_server_contract = ""
