"""Smoke tests for QML bridges (Python side only, no QML rendering)."""

from ui_qml_bridge.app_bridge import AppBridge
from ui_qml_bridge.navigation_bridge import NavigationBridge
from ui_qml_bridge.command_bus import CommandBus
from ui_qml_bridge.theme_bridge import ThemeBridge
from ui_qml_bridge.home_bridge import HomeBridge
from ui_qml_bridge.connections_bridge import ConnectionsBridge
from ui_qml_bridge.home_audio_bridge import HomeAudioBridge


class TestAppBridge:
    def test_instantiate(self):
        bridge = AppBridge()
        assert bridge.appName == "Michi Music Player"
        assert bridge.version == "0.1.0-qml"
        assert bridge.experimentalQml is True


class TestNavigationBridge:
    def test_default_route(self):
        bridge = NavigationBridge()
        assert bridge.currentRoute == "home"

    def test_navigate_changes_route(self):
        bridge = NavigationBridge()
        bridge.navigate("connections")
        assert bridge.currentRoute == "connections"

    def test_same_route_no_change(self):
        bridge = NavigationBridge()
        bridge.navigate("home")
        assert bridge.currentRoute == "home"


class TestCommandBus:
    def test_instantiate(self):
        bus = CommandBus()
        assert bus is not None

    def test_execute_does_not_crash(self):
        bus = CommandBus()
        bus.execute("navigate", {"route": "home"})


class TestThemeBridge:
    def test_default_dark(self):
        bridge = ThemeBridge()
        assert bridge.darkMode is True

    def test_set_light(self):
        bridge = ThemeBridge()
        bridge.darkMode = False
        assert bridge.darkMode is False

    def test_set_dark(self):
        bridge = ThemeBridge()
        bridge.darkMode = True
        assert bridge.darkMode is True


class TestHomeBridge:
    def test_default_stats(self):
        bridge = HomeBridge()
        assert bridge.libraryAlbums == 0
        assert bridge.libraryArtists == 0
        assert bridge.libraryTracks == 0
        assert bridge.microServerState == "not_configured"

    def test_set_library_stats(self):
        bridge = HomeBridge()
        bridge.set_library_stats(10, 5, 100)
        assert bridge.libraryAlbums == 10
        assert bridge.libraryArtists == 5
        assert bridge.libraryTracks == 100

    def test_refresh_does_not_crash(self):
        bridge = HomeBridge()
        bridge.refresh()


class TestConnectionsBridge:
    def test_default_state(self):
        bridge = ConnectionsBridge()
        assert bridge.microServerState == "not_configured"

    def test_scan_for_servers(self):
        bridge = ConnectionsBridge()
        bridge.scanForServers()
        assert bridge.microServerState == "not_configured"

    def test_add_manual_server(self):
        bridge = ConnectionsBridge()
        bridge.addManualServer()


class TestHomeAudioBridge:
    def test_default_state(self):
        bridge = HomeAudioBridge()
        assert bridge.homeAssistantState == "not_configured"
        assert bridge.streamState == "concept"
        assert bridge.receiverCount == 0

    def test_configure_home_assistant(self):
        bridge = HomeAudioBridge()
        bridge.configureHomeAssistant()

    def test_open_diagnostics(self):
        bridge = HomeAudioBridge()
        bridge.openDiagnostics()

    def test_open_stream_concept(self):
        bridge = HomeAudioBridge()
        bridge.openStreamConcept()
