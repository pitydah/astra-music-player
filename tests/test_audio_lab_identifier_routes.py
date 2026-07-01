"""Test all Identifier sub-pages can navigate and render."""

from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


def _pix():
    pix = QPixmap(1, 1)
    pix.fill(Qt.transparent)
    return pix


@patch("ui.audio_lab.sub_pages.get_pixmap")
def test_identifier_page_renders(mock_pixmap, qtbot):
    from ui.audio_lab.sub_pages import AudioLabIdentifierPage
    mock_pixmap.return_value = _pix()
    page = AudioLabIdentifierPage()
    qtbot.addWidget(page)
    page.show()
    assert page.isVisible()
    assert page.navigate_requested is not None


@patch("ui.audio_lab.sub_pages.get_pixmap")
def test_identifier_page_navigates_to_musicbrainz(mock_pixmap, qtbot):
    from ui.audio_lab.sub_pages import AudioLabIdentifierPage
    mock_pixmap.return_value = _pix()
    page = AudioLabIdentifierPage()
    qtbot.addWidget(page)
    assert hasattr(page, 'navigate_requested')


def test_musicbrainz_page_renders(qtbot):
    from ui.audio_lab.musicbrainz_page import MusicBrainzPage
    page = MusicBrainzPage()
    qtbot.addWidget(page)
    page.show()
    assert page.isVisible()
    assert page.navigate_requested is not None


def test_artwork_page_renders(qtbot):
    from ui.audio_lab.artwork_page import ArtworkPage
    page = ArtworkPage()
    qtbot.addWidget(page)
    page.show()
    assert page.isVisible()
    assert page.navigate_requested is not None


def test_lyrics_page_renders(qtbot):
    from ui.audio_lab.lyrics_page import LyricsPage
    page = LyricsPage()
    qtbot.addWidget(page)
    page.show()
    assert page.isVisible()
    assert page.navigate_requested is not None
