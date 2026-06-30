"""Tests for album identity — normalization, detection, canonical keys."""
from unittest.mock import MagicMock


def _make_item(album="", artist="", albumartist="", year=0,
               track_number=0, disc_number=1, duration=0.0,
               filepath="/music/test.flac", title="Test Song",
               genre="Rock", ext="flac"):
    item = MagicMock()
    item.album = album
    item.artist = artist
    item.albumartist = albumartist
    item.year = year
    item.track_number = track_number
    item.disc_number = disc_number
    item.duration = duration
    item.filepath = filepath
    item.title = title
    item.genre = genre
    item.ext = ext
    return item


class TestNormalize:
    def test_normalize_album_title_simple(self):
        from library.album_identity import normalize_album_title
        assert normalize_album_title("  Hello   World  ") == "hello world"
        assert normalize_album_title("GREATEST HITS") == "greatest hits"
        assert normalize_album_title("") == ""
        assert normalize_album_title(None) == ""

    def test_normalize_album_title_strip_edition(self):
        from library.album_identity import normalize_album_title
        assert normalize_album_title("Album (Remastered)", strip_edition=True) == "album"
        assert normalize_album_title("Album (Deluxe Edition)", strip_edition=True) == "album"
        assert normalize_album_title("Album (Remastered) (Deluxe Edition)", strip_edition=True) == "album"
        assert normalize_album_title("Album", strip_edition=True) == "album"

    def test_normalize_artist_simple(self):
        from library.album_identity import normalize_artist_name
        assert normalize_artist_name("  The Beatles  ") == "the beatles"
        assert normalize_artist_name(None) == "various artists"
        assert normalize_artist_name("") == "various artists"

    def test_normalize_artist_va(self):
        from library.album_identity import normalize_artist_name
        assert normalize_artist_name("VA") == "various artists"
        assert normalize_artist_name("V.A.") == "various artists"
        assert normalize_artist_name("Various Artists") == "various artists"
        assert normalize_artist_name("Varios Artistas") == "various artists"


class TestDetectAlbumArtist:
    def test_uses_albumartist(self):
        from library.album_identity import detect_album_artist
        tracks = [
            _make_item(artist="Singer", albumartist="Band"),
            _make_item(artist="Singer", albumartist="Band"),
        ]
        assert detect_album_artist(tracks) == "Band"

    def test_fallback_to_artist(self):
        from library.album_identity import detect_album_artist
        tracks = [
            _make_item(artist="Band"),
            _make_item(artist="Band"),
        ]
        assert detect_album_artist(tracks) == "Band"

    def test_various_artists(self):
        from library.album_identity import detect_album_artist
        tracks = [
            _make_item(artist="Artist A"),
            _make_item(artist="Artist B"),
        ]
        assert detect_album_artist(tracks) == "Various Artists"

    def test_unknown(self):
        from library.album_identity import detect_album_artist
        tracks = [_make_item(artist="")]
        result = detect_album_artist(tracks)
        assert result in ("Artista desconocido", "Various Artists")


class TestIsCompilation:
    def test_compilation_by_artists(self):
        from library.album_identity import is_compilation
        tracks = [
            _make_item(artist="A1", album="Comp"),
            _make_item(artist="A2", album="Comp"),
        ]
        assert is_compilation(tracks) is True

    def test_not_compilation(self):
        from library.album_identity import is_compilation
        tracks = [
            _make_item(artist="Band", album="Album"),
            _make_item(artist="Band", album="Album"),
        ]
        assert is_compilation(tracks) is False


class TestAlbumIdentity:
    def test_compute(self):
        from library.album_identity import compute_album_identity
        tracks = [
            _make_item(album="Test Album", artist="Artist", albumartist="Artist",
                       year=2024, duration=200.0),
            _make_item(album="Test Album", artist="Artist", albumartist="Artist",
                       year=2024, duration=180.0),
        ]
        ident = compute_album_identity(tracks)
        assert ident.display_title == "Test Album"
        assert ident.display_artist == "Artist"
        assert ident.year == "2024"
        assert ident.disc_count == 1

    def test_multi_disc(self):
        from library.album_identity import compute_album_identity
        tracks = [
            _make_item(album="Album", artist="A", disc_number=1),
            _make_item(album="Album", artist="A", disc_number=2),
        ]
        ident = compute_album_identity(tracks)
        assert ident.disc_count == 2

    def test_key_stable(self):
        from library.album_identity import compute_album_identity
        t1 = [_make_item(album="Test", artist="Artist")]
        t2 = [_make_item(album="  Test  ", artist="  Artist  ")]
        id1 = compute_album_identity(t1)
        id2 = compute_album_identity(t2)
        assert id1.album_key == id2.album_key
