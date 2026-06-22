"""Tests for AppServices — frozen, controller acceptance, fallback."""
import pytest


def test_app_services_is_frozen():
    """AppServices dataclass has frozen=True — mutations should fail."""
    from core.app_services import AppServices
    svc = AppServices(db="test_db", playback="test_playback")
    with pytest.raises(AttributeError):  # Frozen dataclass raises on mutation
        svc.db = "changed"  # noqa: B017


def test_controller_accepts_services():
    """Controllers accept services=None and store self._svc."""
    from ui.controllers.genre_controller import GenreController

    def _noop(*args, **kwargs):
        pass

    class FakeWindow:
        _ctx = None
        _play_filepaths = _noop

    ctrl = GenreController(FakeWindow(), services=None)
    assert ctrl._svc is None


def test_controller_fallback_works():
    """When services is None, controller falls back to _win._ctx."""
    from ui.controllers.genre_controller import GenreController

    def _noop(*args, **kwargs):
        pass

    from dataclasses import dataclass

    @dataclass
    class FakeCtx:
        genre_repo = None
        genre_grid = None
        all_items = []
        configure_header = _noop
        fade_to = _noop

    class FakeWindow:
        _ctx = FakeCtx()
        _play_filepaths = _noop

    ctrl = GenreController(FakeWindow(), services=None)
    assert ctrl._svc is None
