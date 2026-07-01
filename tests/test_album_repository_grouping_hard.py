"""Hard tests: grouping correctness for edge cases."""
from unittest.mock import MagicMock


def _make(album="", artist="", albumartist="", filepath="/m/s.flac",
          disc_number=1, compilation=False):
    t = MagicMock()
    t.album = album
    t.artist = artist
    t.albumartist = albumartist
    t.filepath = filepath
    t.disc_number = disc_number
    t.compilation = compilation
    t.ext = "flac"
    t.sample_rate = 44100
    t.bit_depth = 16
    t.bitrate = 1411
    t.duration = 200.0
    t.year = 2024
    t.title = "Song"
    t.track_number = 1
    t.genre = "Rock"
    return t


class TestGreatestHitsSeparation:
    def test_queen_and_abba_separate(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build([
            _make(album="Greatest Hits", artist="Queen"),
            _make(album="Greatest Hits", artist="ABBA"),
        ])
        assert len(repo.list_groups()) == 2

    def test_same_artist_same_title(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build([
            _make(album="Album", artist="X"),
            _make(album="Album", artist="X"),
        ])
        assert len(repo.list_groups()) == 1


class TestCompilationGrouping:
    def test_va_albumartist_joined(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build([
            _make(album="Comp", artist="A1", albumartist="Various Artists"),
            _make(album="Comp", artist="A2", albumartist="Various Artists"),
        ])
        assert len(repo.list_groups()) == 1

    def test_no_va_albumartist_separate(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build([
            _make(album="Unplugged", artist="A1"),
            _make(album="Unplugged", artist="A2"),
        ])
        assert len(repo.list_groups()) == 2

    def test_compilation_flag_joined(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build([
            _make(album="Comp", artist="A1", compilation=True),
            _make(album="Comp", artist="A2", compilation=True),
        ])
        assert len(repo.list_groups()) == 1


class TestMultiDiscGrouping:
    def test_disc1_disc2_joined(self):
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build([
            _make(album="Album", artist="X", disc_number=1),
            _make(album="Album", artist="X", disc_number=2),
        ])
        groups = repo.list_groups()
        assert len(groups) == 1
        assert groups[0].identity.disc_count == 2

    def test_different_albums_same_title_separate_by_path(self):
        from library.album_repository import AlbumRepository
        import tempfile
        import os
        d1 = tempfile.mkdtemp()
        d2 = tempfile.mkdtemp()
        try:
            repo = AlbumRepository()
            repo.build([
                _make(album="Album", artist="X", filepath=os.path.join(d1, "s.flac")),
                _make(album="Album", artist="Y", filepath=os.path.join(d2, "s.flac")),
            ])
            assert len(repo.list_groups()) == 2
        finally:
            os.rmdir(d1)
            os.rmdir(d2)
