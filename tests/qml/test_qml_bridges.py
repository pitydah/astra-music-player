"""Smoke tests for QML bridges (Python side only, no QML rendering)."""

from pathlib import Path
from ui_qml_bridge.app_bridge import AppBridge
from ui_qml_bridge.navigation_bridge import NavigationBridge
from ui_qml_bridge.command_bus import CommandBus
from ui_qml_bridge.theme_bridge import ThemeBridge
from ui_qml_bridge.home_bridge import HomeBridge
from ui_qml_bridge.connections_bridge import ConnectionsBridge
from ui_qml_bridge.home_audio_bridge import HomeAudioBridge


QML_DIR = Path(__file__).resolve().parent.parent.parent / "ui_qml"


def test_qml_main_exists():
    assert (QML_DIR / "Main.qml").exists()


def test_michi_app_exists():
    assert (QML_DIR / "MichiApp.qml").exists()


def test_qmldir_exists():
    assert (QML_DIR / "qmldir").exists()


def test_theme_qmldir_exists():
    assert (QML_DIR / "theme" / "qmldir").exists()


def test_theme_files():
    for name in ("MichiColors", "MichiTypography", "MichiSpacing", "MichiMotion", "MichiTheme"):
        assert (QML_DIR / "theme" / f"{name}.qml").exists(), f"Missing theme file: {name}.qml"


def test_materials_files():
    for name in ("GlassMaterial", "HeroMaterial", "PopupMaterial", "SidebarMaterial", "InputMaterial", "AcrylicBackdrop"):
        assert (QML_DIR / "materials" / f"{name}.qml").exists(), f"Missing material: {name}.qml"


def test_components_files():
    for name in ("GlassPanel", "GlassCard", "HeroPanel", "ActionButton", "StatusBadge",
                 "EmptyState", "SearchField", "SidebarItem", "SectionHeader", "IconSlot",
                 "InspectorPanel", "DiscoveryResultCard"):
        assert (QML_DIR / "components" / f"{name}.qml").exists(), f"Missing component: {name}.qml"


def test_shell_files():
    for name in ("AppShell", "Sidebar", "HeaderBar", "PageStack", "RouteTransition"):
        assert (QML_DIR / "shell" / f"{name}.qml").exists(), f"Missing shell: {name}.qml"


def test_page_stack_references_exist():
    import re
    page_stack = (QML_DIR / "shell" / "PageStack.qml").read_text()
    refs = re.findall(r'"([^"]+\.qml)"', page_stack)
    shell_dir = QML_DIR / "shell"
    for ref in refs:
        p = Path(ref)
        if not p.is_absolute():
            p = (shell_dir / ref).resolve()
        else:
            p = p.resolve()
        if p.exists():
            continue
        rel = QML_DIR / ref.replace("../", "")
        assert rel.exists(), (
            f"PageStack references non-existent file: {ref}\n"
            f"  Tried: {p}\n  Tried: {rel}"
        )


def test_qml_main_importable():
    import importlib
    mod = importlib.import_module("ui_qml_bridge.qml_main")
    assert hasattr(mod, "main")


class TestAppBridge:
    def test_instantiate(self):
        bridge = AppBridge()
        assert bridge.appName == "Michi Music Player"
        assert bridge.version == "0.1.0-qml"
        assert bridge.experimentalQml is True

    def test_quit_slot(self):
        bridge = AppBridge()
        assert hasattr(bridge, 'quit')


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

    def test_empty_route_falls_back(self):
        bridge = NavigationBridge()
        bridge.navigate("")
        assert bridge.currentRoute == "home"

    def test_invalid_route_falls_back(self):
        bridge = NavigationBridge()
        bridge.navigate("nonexistent_route")
        assert bridge.currentRoute == "placeholder"

    def test_navigate_slot(self):
        bridge = NavigationBridge()
        assert hasattr(bridge, 'navigate')


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

    def test_set_library_stats_slot(self):
        bridge = HomeBridge()
        assert hasattr(bridge, 'set_library_stats')


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

    def test_scan_slot(self):
        bridge = ConnectionsBridge()
        assert hasattr(bridge, 'scanForServers')


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

    def test_slots_exist(self):
        bridge = HomeAudioBridge()
        assert hasattr(bridge, 'configureHomeAssistant')
        assert hasattr(bridge, 'openDiagnostics')
        assert hasattr(bridge, 'openStreamConcept')
