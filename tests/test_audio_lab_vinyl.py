"""Tests for VinylLabPage — requires pytest-qt."""

from unittest.mock import patch


def test_vinyl_page_renders(qtbot):
    from ui.audio_lab.vinyl_lab_page import VinylLabPage
    page = VinylLabPage()
    qtbot.addWidget(page)
    page.show()
    assert page.isVisible()
    assert page.navigate_requested is not None


def test_vinyl_export_no_recording_no_crash(qtbot):
    from ui.audio_lab.vinyl_lab_page import VinylLabPage
    page = VinylLabPage()
    qtbot.addWidget(page)
    page._export_and_import()
    # No debe crashear si no hay grabacion


def test_vinyl_export_no_split_points_no_crash(qtbot):
    from ui.audio_lab.vinyl_lab_page import VinylLabPage
    import tempfile, os
    page = VinylLabPage()
    qtbot.addWidget(page)
    # Simular que hay grabacion pero sin split points
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    try:
        page._side_a_path = path
        page._split_points = []
        page._export_and_import()
    finally:
        os.unlink(path)
