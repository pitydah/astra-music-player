#!/usr/bin/env python3
"""CoverFlow diagnostic tool — standalone measurement and geometry dump.

Usage:
    python diagnose_coverflow.py          # Standard test
    MICHI_COVERFLOW_DEBUG=1 python diagnose_coverflow.py  # Verbose

Creates a window with a mock CoverFlow (50 colored squares), runs a 3-second
scrolling test, and dumps /tmp/coverflow_diagnostic.txt.
"""
import os
import sys
import json

os.environ["MICHI_COVERFLOW_DEBUG"] = "1"

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QApplication

# ── Create mock items ──

def _make_mock_pixmap(color: QColor, size: int = 200, index: int = 0) -> QPixmap:
    """Create a colored square with index label for mock covers."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(color)
    painter.setPen(QPen(color.darker(120), 2))
    painter.drawRoundedRect(2, 2, size - 4, size - 4, 14, 14)
    painter.setPen(QColor(255, 255, 255, 200))
    painter.setFont(QFont("sans-serif", 24, QFont.Bold))
    painter.drawText(pix.rect(), Qt.AlignCenter, str(index + 1))
    painter.end()
    return pix


def run_diagnostic():
    app = QApplication.instance() or QApplication(sys.argv)

    from library.coverflow import CoverFlowWidget
    from library.album_art import CoverFlowItem

    # Create mock items
    colors = [QColor(h, 180, 120) for h in range(0, 360, 12)]
    items = []
    for i, color in enumerate(colors[:30]):
        pix = _make_mock_pixmap(color, 200, i)
        item = CoverFlowItem(
            pixmap=pix,
            title=f"Album {i + 1}",
            subtitle=f"Artist {i + 1} · 2024 · 12 ♪",
            data={"album": f"Album {i + 1}", "artist": f"Artist {i + 1}", "tracks": []},
        )
        items.append(item)

    cf = CoverFlowWidget()
    cf.resize(1024, 600)
    cf.show()
    cf.set_items(items)

    print(f"OpenGL: {'sí' if cf._use_opengl else 'no'}")
    print(f"Viewport: {type(cf.viewport()).__name__}")
    print(f"Mode: {cf._render_mode}")
    print(f"Items: {len(cf._cover_items)}")
    print(f"Cover size: {cf._cover_w}x{cf._cover_h}")

    # Animate scrolling for 3 seconds to measure
    step = 0.15
    scroll_steps = 20
    delay_ms = 80

    got_fps = False

    def do_step(n: int = 0):
        nonlocal got_fps
        if n >= scroll_steps:
            # Wait for final frames
            QTimer.singleShot(500, finish)
            return
        cf._current = step * n
        cf._update_layout()
        cf.viewport().update()
        QTimer.singleShot(delay_ms, lambda: do_step(n + 1))

    def finish():
        nonlocal got_fps
        # Dump diagnostic
        cf._dump_diagnostic()

        # Read and display report
        path = "/tmp/coverflow_diagnostic.txt"
        if os.path.exists(path):
            with open(path) as f:
                report = json.load(f)
            print("\n=== CoverFlow Diagnostic Report ===")
            print(f"FPS current: {report['fps_current']}")
            print(f"FPS min: {report['fps_min']}")
            print(f"Paint avg: {report['paint_avg_ms']} ms")
            print(f"Items visible/total: {report['items_visible']}/{report['items_total']}")
            print(f"OpenGL: {report['opengl']}")
            print(f"Viewport: {report['viewport']}")
            print(f"Mode: {report['mode']}")
            print(f"Cover size: {report['cover_size']}")
            print("\nLayout params:")
            for k, v in report['params'].items():
                print(f"  {k}: {v}")
            print("\nItem coordinates (visible items):")
            for key, val in report['coordinates'].items():
                print(f"  {key}: dist={val['dist']} x={val['x']} y={val['y']} "
                      f"rot={val['rot']}° scale={val['scale']} z={val['z']}")
            print(f"\nFull report: {path}")
        app.quit()

    # Start scroll
    QTimer.singleShot(200, lambda: do_step(0))
    app.exec()


if __name__ == "__main__":
    run_diagnostic()
