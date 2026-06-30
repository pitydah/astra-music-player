"""Tests for AlbumRepository — build, groups, summary, quality, health."""
from unittest.mock import MagicMock


def _make_item(album="Test Album", artist="Test Artist",
               albumartist="", title="Song", filepath="/music/song.flac",
               duration=200.0, year=2024, genre="Rock",
               ext="flac", track_number=1, disc_number=1,
               sample_rate=44100, bit_depth=16, bitrate=1411):
    item = MagicMock()
    item.album = album
    item.artist = artist
    item.albumartist = albumartist or artist
    item.title = title
    item.filepath = filepath
    item.duration = duration
    item.year = year
    item.genre = genre
    item.ext = ext
    item.track_number = track_number
    item.disc_number = disc_number
    item.sample_rate = sample_rate
    item.bit_depth = bit_depth
    item.bitrate = bitrate
    return item


class TestBuild:
    def test_empty(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build([])
        assert len(repo.list_groups()) == 0

    def test_single_album(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build([
            _make_item(album="A", artist="X"),
            _make_item(album="A", artist="X"),
        ])
        assert len(repo.list_groups()) == 1

    def test_multiple_albums(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build([
            _make_item(album="A", artist="X"),
            _make_item(album="B", artist="Y"),
        ])
        assert len(repo.list_groups()) == 2

    def test_compilation(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build([
            _make_item(album="Comp", artist="A1"),
            _make_item(album="Comp", artist="A2"),
        ])
        groups = repo.list_groups()
        assert len(groups) == 1


class TestGetGroup:
    def test_get_group_returns_tracks(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        items = [_make_item(album="A", artist="X")]
        repo.build(items)
        groups = repo.list_groups()
        key = groups[0].identity.album_key
        group = repo.get_group(key)
        assert group is not None
        assert len(group.tracks) == 1

    def test_get_group_nonexistent(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        assert repo.get_group("nonexistent") is None


class TestSummary:
    def test_summary_has_track_count(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        items = [
            _make_item(album="A", artist="X"),
            _make_item(album="A", artist="X"),
        ]
        repo.build(items)
        summary = repo.list_groups()[0].summary
        assert summary is not None
        assert summary.track_count == 2


class TestQuality:
    def test_flac_lossless(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        items = [_make_item(ext="flac", sample_rate=44100)]
        repo.build(items)
        q = repo.get_quality_summary(repo.list_groups()[0].identity.album_key)
        assert q.has_lossless is True
        assert q.has_lossy is False
        assert q.dominant_format == "FLAC"

    def test_mixed_quality(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        items = [
            _make_item(ext="flac", album="A", artist="X"),
            _make_item(ext="mp3", album="A", artist="X"),
        ]
        repo.build(items)
        q = repo.get_quality_summary(repo.list_groups()[0].identity.album_key)
        assert q.has_lossless is True
        assert q.has_lossy is True
        assert q.has_mixed_quality is True


class TestHealth:
    def test_healthy(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        items = [_make_item(album="A", artist="X", title="Song", year=2024)]
        repo.build(items)
        h = repo.get_health_summary(repo.list_groups()[0].identity.album_key)
        assert h.track_count == 1
        assert h.status == "ok"

    def test_missing_title(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        items = [_make_item(album="A", artist="X", title="")]
        repo.build(items)
        h = repo.get_health_summary(repo.list_groups()[0].identity.album_key)
        assert h.missing_titles == 1
        assert h.status == "warning"
