"""Behavior tests for MPRIS — Raise, Quit, properties, and future gap documentation.

Tests against the current main branch: Raise/Quit are pass stubs.
Documents what behavior they should have once implemented.
"""

from ui.controllers.mpris_controller import MPRISController


class TestMPRISProperties:
    def test_identity_is_michi(self):
        from adapters.mpris import MPRISObject
        mpris = MPRISObject(None, None)
        props = mpris.GetAll("org.mpris.MediaPlayer2")
        assert props["Identity"] == "Michi Music Player"

    def test_can_raise_is_true(self):
        from adapters.mpris import MPRISObject
        mpris = MPRISObject(None, None)
        props = mpris.GetAll("org.mpris.MediaPlayer2")
        assert props["CanRaise"] is True

    def test_can_quit_is_true(self):
        from adapters.mpris import MPRISObject
        mpris = MPRISObject(None, None)
        props = mpris.GetAll("org.mpris.MediaPlayer2")
        assert props["CanQuit"] is True

    def test_playback_stopped_without_engine(self):
        from adapters.mpris import MPRISObject
        mpris = MPRISObject(None, None)
        props = mpris.GetAll("org.mpris.MediaPlayer2.Player")
        assert props["PlaybackStatus"] == "Stopped"

    def test_desktop_entry_is_michi(self):
        from adapters.mpris import MPRISObject
        mpris = MPRISObject(None, None)
        props = mpris.GetAll("org.mpris.MediaPlayer2")
        assert props["DesktopEntry"] == "michi-music-player"


class TestMPRISRaise:
    """DOCUMENTED GAP: Raise() is a pass stub on main.

    These tests verify the stub doesn't crash and document expected future behavior.
    """

    def test_raise_stub_does_not_crash(self):
        from adapters.mpris import MPRISObject
        mpris = MPRISObject(None, None)
        mpris.Raise()  # must not crash despite being a pass stub


class TestMPRISQuit:
    """DOCUMENTED GAP: Quit() is a pass stub on main.

    These tests verify the stub doesn't crash and document expected future behavior.
    """

    def test_quit_stub_does_not_crash(self):
        from adapters.mpris import MPRISObject
        mpris = MPRISObject(None, None)
        mpris.Quit()  # must not crash despite being a pass stub


class TestMPRISControllerInit:
    def test_init_no_dbus(self, mock_window):
        ctrl = MPRISController(mock_window)
        ctrl.init()
        assert ctrl.adapter is None
        assert not ctrl.is_active

    def test_update_metadata_no_adapter(self, mock_window):
        ctrl = MPRISController(mock_window)
        ctrl.update_metadata("Title", "Artist", "Album", 240)

    def test_is_active_false_without_dbus(self, mock_window):
        ctrl = MPRISController(mock_window)
        ctrl.init()
        assert not ctrl.is_active

    def test_adapter_none_by_default(self, mock_window):
        ctrl = MPRISController(mock_window)
        assert ctrl.adapter is None
