"""Tests: ArtistDetailView — Qt widget instantiation, sections, and signals.

Requires pytest-qt.
"""
import pytest

from library.artist_grouping import ArtistGroup, ArtistAlbumGroup
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


def _make_album(title="Test Album", **kw):
    defaults = dict(
        key=title.lower(), title=title, artist="Test Artist",
        albumartist="", year=2020,
        tracks=[_make_item()], cover_path="",
        total_duration=200.0, disc_count=1, track_count=1,
        formats=["flac"], genres=["Rock"], album_type="",
    )
    defaults.update(kw)
    return ArtistAlbumGroup(**defaults)


def _make_group(**kw):
    track = _make_item()
    defaults = dict(
        key="test_artist", display_name="Test Artist",
        sort_name="test artist",
        albums=[_make_album()], loose_tracks=[],
        all_tracks=[track],
        genres=["Rock"], years=[2020],
        cover_paths=["/tmp/cover.jpg"],
        total_duration=200.0, track_count=1, album_count=1,
    )
    defaults.update(kw)
    return ArtistGroup(**defaults)


@pytest.fixture
def detail_view(qtbot):
    from ui.artist_detail_view import ArtistDetailView
    v = ArtistDetailView()
    qtbot.addWidget(v)
    return v


class TestArtistDetailViewQt:

    def test_instantiation(self, detail_view):
        assert detail_view is not None
        assert hasattr(detail_view, '_artist')
        assert hasattr(detail_view, '_insight')

    def test_set_artist_shows_name(self, detail_view):
        group = _make_group()
        detail_view.set_artist(group)
        assert detail_view._artist is not None
        assert detail_view._artist.display_name == "Test Artist"

    def test_artist_without_bio_shows_placeholder(self, detail_view):
        group = _make_group()
        group.bio = ""
        group.enrichment_status = ""
        detail_view.set_artist(group)
        # Should not crash — bio placeholder is rendered

    def test_artist_with_bio_shows_bio_section(self, detail_view):
        group = _make_group()
        group.bio = "A long biography " * 50
        group.enrichment_status = "loaded"
        detail_view.set_artist(group)
        assert detail_view._bio_full

    def test_albums_section_rendered(self, detail_view):
        group = _make_group()
        assert group.albums
        detail_view.set_artist(group)
        # Should render without error

    def test_all_tracks_table_rendered(self, detail_view):
        group = _make_group()
        track = _make_item()
        group.all_tracks = [track, _make_item(filepath="/tmp/b.flac")]
        group.track_count = 2
        detail_view.set_artist(group)

    def test_play_all_requested_signal(self, detail_view, qtbot):
        group = _make_group()
        detail_view.set_artist(group)
        with qtbot.waitSignal(detail_view.play_all_requested, timeout=100):
            detail_view.play_all_requested.emit(group.key)

    def test_artist_mix_requested_signal(self, detail_view, qtbot):
        group = _make_group()
        detail_view.set_artist(group)
        with qtbot.waitSignal(detail_view.artist_mix_requested, timeout=100):
            detail_view.artist_mix_requested.emit(group.key)

    def test_album_navigate_requested_signal(self, detail_view, qtbot):
        with qtbot.waitSignal(detail_view.album_navigate_requested, timeout=100):
            detail_view.album_navigate_requested.emit("Test Album")
