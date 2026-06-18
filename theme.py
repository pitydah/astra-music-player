"""Plasma-native palette and modern QSS for Astra Music Player."""

from PySide6.QtGui import QPalette, QColor, QFont


def is_dark_mode(palette: QPalette | None = None) -> bool:
    """Detect if the current system theme is dark."""
    if palette is None:
        from PySide6.QtWidgets import QApplication
        palette = QApplication.instance().palette()
    return palette.color(QPalette.Window).lightness() <= 128


def build_plasma_palette() -> QPalette:
    """Clean, modern QPalette — light mode."""
    p = QPalette()
    p.setColor(QPalette.Window,          QColor("#f5f5f7"))
    p.setColor(QPalette.WindowText,      QColor("#1c1c1e"))
    p.setColor(QPalette.Base,            QColor("#ffffff"))
    p.setColor(QPalette.AlternateBase,   QColor("#fafafa"))
    p.setColor(QPalette.Text,            QColor("#1c1c1e"))
    p.setColor(QPalette.Highlight,       QColor("#FF7A00"))
    p.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    p.setColor(QPalette.Button,          QColor("#f5f5f7"))
    p.setColor(QPalette.ButtonText,      QColor("#1c1c1e"))
    p.setColor(QPalette.Light,           QColor("#ffffff"))
    p.setColor(QPalette.Midlight,        QColor("#e5e5ea"))
    p.setColor(QPalette.Mid,             QColor("#c7c7cc"))
    p.setColor(QPalette.Dark,            QColor("#8e8e93"))
    p.setColor(QPalette.Shadow,          QColor("#636366"))
    p.setColor(QPalette.ToolTipBase,     QColor("#f5f5f7"))
    p.setColor(QPalette.ToolTipText,     QColor("#1c1c1e"))
    p.setColor(QPalette.Link,            QColor("#FF7A00"))
    p.setColor(QPalette.LinkVisited,     QColor("#DD007A"))
    p.setColor(QPalette.PlaceholderText, QColor("#8e8e93"))
    return p


PLASMA_QSS = """
QMainWindow { background: palette(window); }

QTreeWidget {
    background: transparent; border: none; outline: none;
    padding: 4px 4px;
}
QTreeWidget::item {
    padding: 6px 10px; border-radius: 6px; margin: 1px 4px;
    font-size: 13px;
}
QTreeWidget::item:selected {
    background: #FF7A00; color: #ffffff; font-weight: 600;
}
QTreeWidget::item:hover:!selected {
    background: rgba(255,122,0,0.06);
}
QTreeWidget::branch { background: transparent; }

QTableView {
    background: #ffffff; border: none; outline: none;
    border-radius: 12px; gridline-color: transparent;
}
QTableView::item { padding: 6px 12px; border-bottom: none; }
QTableView::item:hover { background: rgba(255,122,0,0.04); }
QTableView::item:selected { background: #FF7A00; color: #fff; }
QHeaderView::section {
    background: transparent; color: #8e8e93; padding: 8px 12px;
    border: none; border-bottom: 1px solid rgba(0,0,0,0.06);
    font-size: 11px; font-weight: 600;
}
QHeaderView::section:hover { color: #FF7A00; }

QSlider::groove:horizontal { height: 3px; background: #c7c7cc; border-radius: 2px; }
QSlider::handle:horizontal {
    width: 10px; height: 10px; margin: -4px 0; border-radius: 5px;
    background: #ffffff; border: 2px solid #FF7A00;
}
QSlider::handle:horizontal:hover { background: #FF7A00; }
QSlider::sub-page:horizontal { background: #FF7A00; border-radius: 2px; }

QProgressBar {
    background: #e5e5ea; border: none; border-radius: 4px; height: 6px;
}
QProgressBar::chunk { background: #FF7A00; border-radius: 3px; }

QLineEdit {
    background: #ffffff; border: 1px solid rgba(0,0,0,0.08);
    border-radius: 8px; padding: 6px 12px; color: #1c1c1e;
}
QLineEdit:focus { border-color: #FF7A00; }

QComboBox {
    background: #f5f5f7; border: 1px solid rgba(0,0,0,0.08);
    border-radius: 8px; padding: 5px 10px; color: #1c1c1e; min-width: 80px;
}
QComboBox:hover { border-color: rgba(0,0,0,0.15); }
QComboBox QAbstractItemView {
    background: #fff; border: 1px solid rgba(0,0,0,0.06);
    border-radius: 8px; selection-background-color: #FF7A00;
    selection-color: #fff; outline: none;
}

QScrollBar:vertical { width: 6px; background: transparent; margin: 2px; }
QScrollBar::handle:vertical {
    background: #c7c7cc; border-radius: 3px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #8e8e93; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 6px; background: transparent; margin: 2px; }
QScrollBar::handle:horizontal {
    background: #c7c7cc; border-radius: 3px; min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #8e8e93; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QMenu {
    background: rgba(255, 255, 255, 245); border: 1px solid rgba(0,0,0,0.06);
    border-radius: 10px; padding: 4px;
}
QMenu::item { padding: 6px 32px 6px 12px; border-radius: 6px; }
QMenu::item:selected { background: rgba(255,122,0,0.25); color: #fff; }
QMenu::separator {
    height: 1px; background: rgba(0,0,0,0.06); margin: 3px 8px;
}

QMenuBar {
    background: #f5f5f7; border-bottom: 1px solid rgba(0,0,0,0.04);
    padding: 2px 0;
}
QMenuBar::item {
    padding: 5px 10px; border-radius: 6px; margin: 1px 2px; color: #1c1c1e;
}
QMenuBar::item:selected {
    background: rgba(255,122,0,0.08); color: #FF7A00;
}

QPushButton[flat=\"true\"] {
    border: none; background: transparent; border-radius: 6px;
}
QPushButton[flat=\"true\"]:hover { background: rgba(0,0,0,0.04); }
QPushButton[flat=\"true\"]:pressed { background: rgba(0,0,0,0.08); }

QToolTip {
    background: #f5f5f7; color: #1c1c1e;
    border: 1px solid rgba(0,0,0,0.08); border-radius: 6px; padding: 4px 8px;
}

QDialog { background: #f5f5f7; }
"""


def apply_dialog_shadow(widget, radius=20, offset=3, opacity=50):
    """Apply subtle drop shadow to a dialog or widget."""
    from PySide6.QtWidgets import QGraphicsDropShadowEffect
    from PySide6.QtGui import QColor
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(radius)
    shadow.setXOffset(0)
    shadow.setYOffset(offset)
    shadow.setColor(QColor(0, 0, 0, opacity))
    widget.setGraphicsEffect(shadow)
    return shadow
