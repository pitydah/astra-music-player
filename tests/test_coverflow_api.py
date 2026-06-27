"""Tests for CoverFlowWidget public API."""
import pytest
from unittest.mock import MagicMock, patch


# Mock PySide6 so we can test without display
@pytest.fixture(autouse=True)
def _mock_qt():
    with patch("PySide6.QtCore.QPropertyAnimation", autospec=True), \
         patch("PySide6.QtCore.QTimer", autospec=True), \
         patch("PySide6.QtWidgets.QGraphicsView.__init__", lambda self, p: None), \
         patch("PySide6.QtWidgets.QGraphicsView.setScene"), \
         patch("PySide6.QtWidgets.QGraphicsView.setViewport"), \
         patch("PySide6.QtWidgets.QGraphicsView.viewport", return_value=MagicMock(width=lambda: 800, height=lambda: 600)):
        yield


class TestCoverFlowPublicAPI:
    def test_count_empty(self):
        from library.coverflow import CoverFlowWidget
        cf = CoverFlowWidget.__new__(CoverFlowWidget)
        cf._items = []
        assert cf.count() == 0

    def test_count_with_items(self):
        from library.coverflow import CoverFlowWidget
        cf = CoverFlowWidget.__new__(CoverFlowWidget)
        cf._items = [MagicMock(), MagicMock(), MagicMock()]
        assert cf.count() == 3

    def test_item_at_in_bounds(self):
        from library.coverflow import CoverFlowWidget
        cf = CoverFlowWidget.__new__(CoverFlowWidget)
        item = MagicMock()
        cf._items = [item]
        assert cf.item_at(0) is item

    def test_item_at_out_of_bounds(self):
        from library.coverflow import CoverFlowWidget
        cf = CoverFlowWidget.__new__(CoverFlowWidget)
        cf._items = []
        assert cf.item_at(0) is None
        assert cf.item_at(-1) is None

    def test_current_index_rounds(self):
        from library.coverflow import CoverFlowWidget
        cf = CoverFlowWidget.__new__(CoverFlowWidget)
        cf._items = [MagicMock()] * 5
        cf._current = 2.3
        assert cf.current_index() == 2
        cf._current = 2.8
        assert cf.current_index() == 3

    def test_cover_size(self):
        from library.coverflow import CoverFlowWidget
        cf = CoverFlowWidget.__new__(CoverFlowWidget)
        cf._items = []
        cf._cover_w = 260
        assert cf.cover_size() == 260

    def test_set_cover_pixmap_delegates(self):
        from library.coverflow import CoverFlowWidget
        cf = CoverFlowWidget.__new__(CoverFlowWidget)
        cf._items = []
        called = {}
        cf._on_cover_loaded = lambda idx, pix: called.update(idx=idx, pix=pix)
        pixmap = MagicMock()
        cf.set_cover_pixmap(0, pixmap)
        assert called.get("idx") == 0
        assert called.get("pix") is pixmap
