"""Tests for AppServices — immutable DI container."""

from unittest.mock import MagicMock
from core.app_services import AppServices


class TestAppServices:
    def test_receives_workers(self):
        svc = AppServices(db=MagicMock(), workers="my_workers")
        assert svc.workers == "my_workers"

    def test_context_svc_defaults_to_none(self):
        svc = AppServices(db=MagicMock())
        assert svc.context_svc is None

    def test_context_svc_can_be_set(self):
        svc = AppServices(db=MagicMock(), context_svc="ctx")
        assert svc.context_svc == "ctx"
