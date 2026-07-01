"""Tests: SongsPremiumPage — Qt widget instantiation and basic interactions.

Requires pytest-qt.
"""

import pytest


@pytest.fixture
def page(qtbot):
    from ui.library.songs_premium_page import SongsPremiumPage
    p = SongsPremiumPage()
    qtbot.addWidget(p)
    return p


def _make_item(fid=1, filepath="/m/a.flac", title="A", artist="Art", ext=".flac"):
    from library.media_item import MediaItem
    return MediaItem(
        id=fid, filepath=filepath, title=title, artist=artist,
        album="Alb", genre="Rock", ext=ext, duration=180.0,
        filename="a.flac", directory="/m", kind="audio", size=0, mtime=0.0,
        track_number=1, composer="", albumartist="", disc_number=0, disc_total=0,
        track_total=0, mb_track_id="", mb_album_id="", mb_albumartist_id="",
        bpm=0, isrc="", label="", conductor="", compilation=False,
        media_type="", encoder="", copyright="", originaldate="", remixer="",
        grouping="", mood="", replaygain_track=0.0, replaygain_album=0.0,
        replaygain_track_peak=0.0, play_count=0, last_played=0.0, rating=0,
        created_at=0.0, updated_at=0.0, last_scanned=0.0, track_uid="",
    )


class TestSongsPremiumPageQt:

    def test_page_instantiation(self, page):
        assert page is not None
        assert hasattr(page, '_table')
        assert hasattr(page, '_filter_bar')
        assert hasattr(page, '_detail_panel')
        assert hasattr(page, '_bulk_bar')

    def test_load_data_populates_model(self, page):
        items = [_make_item(fid=1, filepath="/m/a.flac"),
                 _make_item(fid=2, filepath="/m/b.flac")]
        page.load_data(items, fav_set={items[0].filepath})
        assert page._model.rowCount() == 2
        val = page._model.data(page._model.index(0, 0))
        assert val == "★"
        val = page._model.data(page._model.index(1, 0))
        assert val == ""

    def test_selected_items_empty_initially(self, page):
        assert page.selected_items() == []

    def test_table_has_correct_columns(self, page):
        assert page._model.columnCount() >= 11

    def test_filter_bar_connects(self, page):
        assert page._filter_bar.filters_changed is not None
