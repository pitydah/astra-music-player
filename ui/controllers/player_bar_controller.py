"""Player bar controller — wraps NowPlayingBar interactions for external controllers."""


class PlayerBarController:
    def __init__(self, player_bar):
        self._bar = player_bar

    def set_track(self, name: str, artist: str = "", cover: str = ""):
        self._bar.set_track(name, artist, cover)

    def set_quality(self, text: str):
        self._bar.set_quality(text)

    def set_state(self, state: str):
        self._bar.set_state(state)

    def set_position(self, pos: int):
        self._bar.set_position(pos)

    def set_duration(self, dur: int):
        self._bar.set_duration(dur)

    def reset(self):
        """Full stop — reset all player bar state."""
        self._bar.set_state("stopped")
        self._bar.set_position(0)
        self._bar.set_duration(0)
        self._bar.set_track("Sin reproducción", "Añade música a la biblioteca")

    def set_transmit_active(self, active: bool, device_name: str = ""):
        self._bar.set_transmit_active(active, device_name)

    def transmit_button(self):
        """Returns the transmit QPushButton for menu positioning."""
        return self._bar._transmit_btn

    def volume_value(self) -> int:
        return self._bar._vol.value()

    def change_volume(self, delta: int):
        v = min(100, max(0, self.volume_value() + delta))
        self._bar.volume_changed.emit(v)

    def mute(self):
        self._bar.volume_changed.emit(0)
