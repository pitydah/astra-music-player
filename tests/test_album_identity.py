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
        assert normalize_artist_name(None) == ""
        assert normalize_artist_name("") == ""

    def test_normalize_artist_va(self):
        from library.album_identity import is_various_artist_alias
        assert is_various_artist_alias("VA") is True
        assert is_various_artist_alias("V.A.") is True
        assert is_various_artist_alias("Various Artists") is True
        assert is_various_artist_alias("Varios Artistas") is True
        assert is_various_artist_alias("The Beatles") is False
        assert is_various_artist_alias(None) is False
        assert is_various_artist_alias("") is False


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
        assert result == "Various Artists"  # fallback for empty artist


class TestIsCompilation:
    def test_compilation_with_albumartist_va(self):
        from library.album_identity import is_compilation
        tracks = [
            _make_item(artist="A1", album="Comp", albumartist="Various Artists"),
            _make_item(artist="A2", album="Comp", albumartist="Various Artists"),
        ]
        assert is_compilation(tracks) is True

    def test_compilation_with_flag(self):
        from library.album_identity import is_compilation
        tracks = [
            _make_item(artist="A1", album="Comp", albumartist="Various Artists"),
        ]
        assert is_compilation(tracks) is True

    def test_not_compilation_different_artists_no_va(self):
        from library.album_identity import is_compilation
        tracks = [
            _make_item(artist="A1", album="Comp"),
            _make_item(artist="A2", album="Comp"),
        ]
        assert is_compilation(tracks) is False

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

    def test_same_title_different_artist_different_key(self):
        from library.album_identity import compute_album_identity
        q1 = [_make_item(album="Greatest Hits", artist="Queen")]
        q2 = [_make_item(album="Greatest Hits", artist="ABBA")]
        id1 = compute_album_identity(q1)
        id2 = compute_album_identity(q2)
        assert id1.album_key != id2.album_key

    def test_compilation_with_various_albumartist(self):
        from library.album_identity import compute_album_identity, is_compilation
        tracks = [
            _make_item(album="Comp", artist="A1", albumartist="Various Artists"),
            _make_item(album="Comp", artist="A2", albumartist="Various Artists"),
        ]
        assert is_compilation(tracks) is True
        ident = compute_album_identity(tracks)
        assert ident.is_compilation is True

    def test_multi_disc_same_identity(self):
        from library.album_identity import make_canonical_album_identity
        d1 = [_make_item(album="Album", artist="A", disc_number=1)]
        d2 = [_make_item(album="Album", artist="A", disc_number=2)]
        group = d1 + d2
        key = make_canonical_album_identity(group)
        k1 = make_canonical_album_identity(d1)
        k2 = make_canonical_album_identity(d2)
        assert k1 == k2  # same canonical key for both discs
        assert key == k1

    def test_remaster_stays_separate(self):
        from library.album_identity import make_canonical_album_identity
        orig = [_make_item(album="Album", artist="A")]
        remaster = [_make_item(album="Album (Remastered)", artist="A")]
        ko = make_canonical_album_identity(orig)
        kr = make_canonical_album_identity(remaster)
        assert ko != kr  # different keys

    def test_key_stable(self):
        from library.album_identity import compute_album_identity
        t1 = [_make_item(album="Test", artist="Artist")]
        t2 = [_make_item(album="  Test  ", artist="  Artist  ")]
        id1 = compute_album_identity(t1)
        id2 = compute_album_identity(t2)
        assert id1.album_key == id2.album_key
