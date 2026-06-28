"""Tests for HomeController."""
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_parent():
    p = MagicMock()
    p.__class__ = __import__("PySide6.QtCore").QtCore.QObject
    return p


@pytest.fixture
def win():
    w = MagicMock()
    w._db = MagicMock()
    w._playback = MagicMock()
    w._views = MagicMock()
    w._views.widget.return_value = None
    w._all_items = []
    w._on_sidebar_navigate = MagicMock()
    w._ctx = MagicMock()
    w._fade_content = MagicMock()
    return w


@pytest.fixture
def ctrl(win):
    from ui.controllers.home_controller import HomeController
    c = HomeController.__new__(HomeController)
    from PySide6.QtCore import QObject
    QObject.__init__(c)
    c._win = win
    c._page = None
    return c


class TestHomeController:
    def test_init_sets_win(self, ctrl, win):
        assert ctrl._win is win
        assert ctrl._page is None

    def test_page_property_returns_none_initially(self, ctrl):
        assert ctrl.page is None

    def test_page_property_returns_page_after_ensure(self, ctrl, win):
        with patch("ui.controllers.home_controller.HomePage") as mock_page_cls:
            mock_page = mock_page_cls.return_value
            page = ctrl._ensure_page()
            assert page is mock_page
            assert ctrl._page is mock_page
            mock_page_cls.assert_called_with(
                db=win._db, playback=win._playback, window=win)

    def test_ensure_page_returns_cached(self, ctrl, win):
        with patch("ui.controllers.home_controller.HomePage") as mock_page_cls:
            first = ctrl._ensure_page()
            second = ctrl._ensure_page()
            assert first is second
            mock_page_cls.assert_called_once()

    def test_show_registers_and_fades(self, ctrl, win):
        with patch("ui.controllers.home_controller.HomePage"):
            ctrl.show()
            win._views.register.assert_called_with("home", ctrl._page)
            win._fade_content.assert_called_with("home")

    def test_show_skips_register_if_exists(self, ctrl, win):
        win._views.widget.return_value = MagicMock()
        with patch("ui.controllers.home_controller.HomePage"):
            ctrl.show()
            win._views.register.assert_not_called()

    def test_refresh_does_nothing_if_no_page(self, ctrl):
        ctrl.refresh()

    def test_refresh_calls_page_refresh(self, ctrl, win):
        win._sync_mgr = None
        with (patch("ui.controllers.home_controller.HomePage") as mock_page_cls,
              patch("streaming.subsonic_client.load_servers") as mock_load):
            mock_page = mock_page_cls.return_value
            mock_load.return_value = ["srv1"]
            ctrl._ensure_page()
            ctrl.refresh()
            mock_page.refresh.assert_called_with(
                items=win._all_items, servers=["srv1"], devices=[])

    def test_refresh_logs_exception(self, ctrl, win):
        with (patch("ui.controllers.home_controller.HomePage") as mock_page_cls,
              patch("ui.controllers.home_controller.logger") as mock_log):
            mock_page = mock_page_cls.return_value
            mock_page.refresh.side_effect = ValueError("fail")
            ctrl._ensure_page()
            ctrl.refresh()
            mock_log.exception.assert_called()

    def test_get_servers_returns_list(self, ctrl):
        with patch("streaming.subsonic_client.load_servers", return_value=["s1"]):
            assert ctrl._get_servers() == ["s1"]

    def test_get_servers_returns_empty_on_exception(self, ctrl):
        with patch("streaming.subsonic_client.load_servers", side_effect=Exception):
            assert ctrl._get_servers() == []

    def test_get_devices_returns_empty_without_sync_mgr(self, ctrl, win):
        win._sync_mgr = None
        assert ctrl._get_devices() == []

    def test_get_devices_returns_peers(self, ctrl, win):
        mgr = MagicMock()
        mgr.is_active = True
        mgr.get_all_peers.return_value = ["peer1"]
        win._sync_mgr = mgr
        assert ctrl._get_devices() == ["peer1"]

    def test_get_devices_returns_empty_on_exception(self, ctrl, win):
        mgr = MagicMock()
        mgr.is_active = True
        mgr.get_all_peers.side_effect = Exception
        win._sync_mgr = mgr
        assert ctrl._get_devices() == []
