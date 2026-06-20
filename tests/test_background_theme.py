"""Tests for BackgroundThemeService — requires QStackedWidget via pytest-qt."""
from PySide6.QtWidgets import QStackedWidget
from ui.controllers.background_theme_service import BackgroundThemeService


def test_init(qtbot):
    stack = QStackedWidget()
    svc = BackgroundThemeService(stack)
    assert svc._content is stack


def test_reset(qtbot):
    stack = QStackedWidget()
    svc = BackgroundThemeService(stack)
    svc.reset()
    style = stack.styleSheet()
    assert "background" in style.lower()


def test_apply_null_pixmap_resets(qtbot):
    stack = QStackedWidget()
    svc = BackgroundThemeService(stack)
    # Calling apply with None/null should call reset internally
    svc.apply(None)
    style = stack.styleSheet()
    assert "background" in style.lower()


def test_apply_pixmap(qtbot):
    from PySide6.QtGui import QPixmap
    stack = QStackedWidget()
    svc = BackgroundThemeService(stack)
    pix = QPixmap(100, 100)
    pix.fill(0)  # black
    # apply starts an async animation — just verify no crash
    svc.apply(pix)
    # Animation is async (800ms), don't assert immediate styleSheet
    qtbot.wait(50)
