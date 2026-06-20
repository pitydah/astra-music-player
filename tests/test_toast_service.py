"""Tests for ToastService — unified toast notification API."""
from unittest.mock import patch, MagicMock
from core.toast_service import ToastService


class TestToastService:
    def test_show_info(self):
        with patch("core.toast_service.ToastNotification") as mock_tn:
            svc = ToastService()
            svc.show("test", "info")
            mock_tn.info.assert_called_once_with("test", None, 4000)

    def test_show_success(self):
        with patch("core.toast_service.ToastNotification") as mock_tn:
            svc = ToastService()
            svc.show("ok", "success")
            mock_tn.success.assert_called_once_with("ok", None, 3000)

    def test_show_warning(self):
        with patch("core.toast_service.ToastNotification") as mock_tn:
            svc = ToastService()
            svc.show("warn", "warning")
            mock_tn.warning.assert_called_once_with("warn", None, 5000)

    def test_show_error(self):
        with patch("core.toast_service.ToastNotification") as mock_tn:
            svc = ToastService()
            svc.show("err", "error")
            mock_tn.error.assert_called_once_with("err", None, 6000)

    def test_show_with_parent(self):
        parent = MagicMock()
        with patch("core.toast_service.ToastNotification") as mock_tn:
            svc = ToastService(parent)
            svc.show("test", "info")
            mock_tn.info.assert_called_once_with("test", parent, 4000)

    def test_shortcuts(self):
        with patch("core.toast_service.ToastNotification") as mock_tn:
            svc = ToastService()
            svc.info("i")
            svc.success("s")
            svc.warning("w")
            svc.error("e")
            assert mock_tn.info.called
            assert mock_tn.success.called
            assert mock_tn.warning.called
            assert mock_tn.error.called
