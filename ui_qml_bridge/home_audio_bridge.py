"""HomeAudioBridge — connects QML Home Audio page to real HomeAudio/Snapcast controllers."""

from PySide6.QtCore import QObject, Signal, Property, Slot
import logging

logger = logging.getLogger("michi.home_audio")


class HomeAudioBridge(QObject):
    stateChanged = Signal()

    def __init__(self, ha_controller=None, snapcast_ctrl=None, parent=None):
        super().__init__(parent)
        self._ha_ctrl = ha_controller
        self._snapcast_ctrl = snapcast_ctrl
        self._ha_state = "not_configured"
        self._stream_state = "concept"
        self._devices = []

    @Property(str, notify=stateChanged)
    def homeAssistantState(self):
        return self._ha_state

    @Property(str, notify=stateChanged)
    def streamState(self):
        return self._stream_state

    @Property("QVariantList", notify=stateChanged)
    def devices(self):
        return self._devices

    @Slot()
    def refresh(self):
        if self._ha_ctrl:
            try:
                if hasattr(self._ha_ctrl, 'is_connected') and self._ha_ctrl.is_connected():
                    self._ha_state = "connected"
                    if hasattr(self._ha_ctrl, 'get_devices'):
                        devs = self._ha_ctrl.get_devices()
                        self._devices = [{"name": d.get("name", ""), "entity": d.get("entity_id", "")} for d in (devs or [])]
                else:
                    self._ha_state = "not_configured"
            except Exception:
                logger.debug("HA state check failed", exc_info=True)
        if self._snapcast_ctrl:
            try:
                self._stream_state = "available"
            except Exception:
                logger.debug("Snapcast state check failed", exc_info=True)
        else:
            self._stream_state = "concept"
        self.stateChanged.emit()

    @Slot()
    def configureHomeAssistant(self):
        self.stateChanged.emit()

    @Slot()
    def openDiagnostics(self):
        self.stateChanged.emit()

    @Slot()
    def openStreamConcept(self):
        self.stateChanged.emit()
