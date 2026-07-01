"""Tests: ArtistGridWidget — Qt widget instantiation, signals, and rendering.

Requires pytest-qt.
"""
import pytest

from library.artist_grouping import ArtistGroup
from library.media_item import MediaItem


def _make_item(**kw):
    defaults = dict(
        id=0, filepath="/tmp/track.flac", filename="track.flac",
        directory="/tmp", ext="flac", kind="audio",
        size=0, mtime=0.0, duration=200.0,
        channels=2, sample_rate=44100, bitrate=1000,
        title="Test", artist="Test Artist", album="Test Album",
        year=2020, genre="Rock",
        track_number=1, composer="", albumartist="",
        disc_number=1, disc_total=1, track_total=10,
        mb_track_id="", mb_album_id="", mb_albumartist_id="",
        bit_depth=16, bpm=120, isrc="", label="",
        conductor="", compilation=0, media_type="",
        encoder="", copyright="", originaldate="",
        remixer="", grouping="", mood="",
        replaygain_track=0.0, replaygain_album=0.0,
        replaygain_track_peak=0.0,
        play_count=5, last_played=0.0, rating=0,
        created_at=0.0, updated_at=0.0, last_scanned=0.0,
        track_uid="",
    )
    defaults.update(kw)
    return MediaItem(**defaults)


def _make_group(key="test_artist", display_name="Test Artist", **kw):
    defaults = dict(
        key=key, display_name=display_name,
        sort_name=display_name.lower(),
        albums=[], loose_tracks=[], all_tracks=[],
        genres=["Rock", "Pop"], years=[2020],
        cover_paths=[],
        total_duration=200.0, track_count=1, album_count=1,
    )
    defaults.update(kw)
    return ArtistGroup(**defaults)


@pytest.fixture
def grid(qtbot):
    from ui.artist_grid import ArtistGridWidget
    g = ArtistGridWidget()
    qtbot.addWidget(g)
    return g


class TestArtistGridWidgetQt:

    def test_instantiation(self, grid):
        assert grid is not None
        assert hasattr(grid, '_search_input')
        assert hasattr(grid, '_sort_combo')
        assert hasattr(grid, '_filter_combo')
        assert hasattr(grid, '_count_label')

    def test_set_artists_populates_grid(self, grid):
        group = _make_group()
        grid.set_artists([group])
        assert grid._filtered == [group]

    def test_empty_state_shown_when_no_artists(self, grid, qtbot):
        grid.set_artists([])
        qtbot.wait(10)
        assert not grid._empty_frame.isHidden()

    def test_empty_state_hidden_with_artists(self, grid, qtbot):
        group = _make_group()
        grid.set_artists([group])
        qtbot.wait(10)
        assert grid._empty_frame.isHidden()

    def test_search_filters_artists(self, grid):
        a1 = _make_group(key="beatles", display_name="The Beatles",
                         sort_name="beatles")
        a2 = _make_group(key="stones", display_name="Rolling Stones",
                         sort_name="rolling stones")
        grid.set_artists([a1, a2])
        grid._on_search("beatles")
        assert len(grid._filtered) == 1
        assert grid._filtered[0].key == "beatles"

    def test_sort_by_name(self, grid):
        a1 = _make_group(key="z", display_name="Z Artist")
        a2 = _make_group(key="a", display_name="A Artist")
        grid.set_artists([a1, a2])
        grid._sort_key = "name_asc"
        grid._apply_filters()
        assert grid._filtered[0].key == "a"

    def test_view_mode_switching(self, grid, qtbot):
        group = _make_group()
        grid.set_artists([group])
        qtbot.wait(10)
        grid.set_view_mode("list")
        qtbot.wait(10)
        assert grid._view_mode == "list"
        assert grid._scroll.isHidden()
        grid.set_view_mode("grid")
        qtbot.wait(10)
        assert grid._view_mode == "grid"
        assert not grid._scroll.isHidden()

    def test_artist_selected_signal(self, grid, qtbot):
        group = _make_group()
        grid.set_artists([group])
        with qtbot.waitSignal(grid.artist_selected, timeout=100):
            grid.artist_selected.emit(group.key)

    def test_artist_play_requested_signal(self, grid, qtbot):
        group = _make_group()
        grid.set_artists([group])
        with qtbot.waitSignal(grid.artist_play_requested, timeout=100):
            grid.artist_play_requested.emit(group.key)
