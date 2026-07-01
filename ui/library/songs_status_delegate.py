"""SongsStatusDelegate — paints quality text with category-based colors."""

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem

_QUALITY_COLORS = {
    "hires": QColor("#66BB6A"),
    "lossless": QColor("#42A5F5"),
    "lossy": QColor("#FFA726"),
    "dsd": QColor("#AB47BC"),
    "unknown": QColor(255, 255, 255, 128),
}


class SongsStatusDelegate(QStyledItemDelegate):
    """Delegate that colors quality text based on the status cache."""

    def __init__(self, status_cache_provider=None, parent=None):
        super().__init__(parent)
        self._cache_provider = status_cache_provider

    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
              index: QModelIndex):
        if not index.isValid():
            super().paint(painter, option, index)
            return

        item_id = _item_id_from_index(index)
        if item_id is not None and self._cache_provider:
            cache = self._cache_provider()
            st = cache.get(item_id)
            if st:
                category = st.get("quality_category", "unknown")
                color = _QUALITY_COLORS.get(category, _QUALITY_COLORS["unknown"])
                option.palette.setColor(QPalette.ColorRole.Text, color)

        super().paint(painter, option, index)


def _item_id_from_index(index: QModelIndex):
    item = index.data(Qt.UserRole)
    if item is not None:
        return getattr(item, 'id', None)
    return None
