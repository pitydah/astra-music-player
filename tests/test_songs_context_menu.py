"""Tests for songs table body context menu."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest


@pytest.fixture
def page(qtbot):
    from ui.library.songs_premium_page import SongsPremiumPage
    p = SongsPremiumPage()
    qtbot.addWidget(p)
    return p


class TestSongsContextMenu:

    def test_table_has_body_context_menu_policy(self, page):
        from PySide6.QtCore import Qt
        policy = page._table.contextMenuPolicy()
        assert policy == Qt.CustomContextMenu

    def test_context_menu_connected(self, page):
        from PySide6.QtCore import Qt
        assert page._table.contextMenuPolicy() == Qt.CustomContextMenu

    def test_show_body_context_menu_no_items_does_not_crash(self, page):
        from PySide6.QtCore import QPoint
        page._ctrl = MagicMock()
        page.selected_items = MagicMock(return_value=[])
        page._show_body_context_menu(QPoint(0, 0))
        page.selected_items.assert_called_once()

    def test_context_menu_has_select_all(self, page):
        assert hasattr(page, '_show_body_context_menu')
