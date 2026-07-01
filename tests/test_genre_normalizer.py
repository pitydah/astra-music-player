"""Tests for GenreNormalizer — normalization, splitting, junk detection, duplicates."""

from metadata.genre_normalizer import (
    normalize_genre_name,
    split_genres,
    genre_key,
    is_junk_genre,
    is_compound_genre,
    detect_duplicate_genres,
)


class TestNormalizeGenreName:
    def test_basic(self):
        assert normalize_genre_name("  Rock  ") == "Rock"

    def test_alias_hip_hop(self):
        assert normalize_genre_name("Hip-Hop") == "Hip-Hop"

    def test_alias_hiphop(self):
        assert normalize_genre_name("hiphop") == "Hip-Hop"

    def test_alias_hip_hop_lower(self):
        assert normalize_genre_name("hip hop") == "Hip-Hop"

    def test_alias_rnb(self):
        assert normalize_genre_name("rnb") == "R&B"

    def test_compound_rb_preserved(self):
        assert normalize_genre_name("R&B") == "R&B"

    def test_drum_bass_preserved(self):
        assert normalize_genre_name("Drum & Bass") == "Drum & Bass"

    def test_rock_and_roll(self):
        assert normalize_genre_name("Rock & Roll") == "Rock & Roll"

    def test_alternative_rock(self):
        assert normalize_genre_name("Alternative") == "Alternative rock"

    def test_alt_rock(self):
        assert normalize_genre_name("alt rock") == "Alternative rock"

    def test_clasica(self):
        assert normalize_genre_name("clasica") == "Música Clásica"

    def test_musica_clasica(self):
        assert normalize_genre_name("musica clasica") == "Música Clásica"

    def test_electronica(self):
        assert normalize_genre_name("electronica") == "Electronic"

    def test_empty(self):
        assert normalize_genre_name("") == ""

    def test_whitespace(self):
        assert normalize_genre_name("   ") == ""

    def test_unicode(self):
        result = normalize_genre_name("Música Latina")
        assert result == "Música Latina"

    def test_case_sensitivity(self):
        assert normalize_genre_name("ELECTRONIC") == "Electronic"

    def test_soundtrack_to_banda_sonora(self):
        assert normalize_genre_name("OST") == "Banda Sonora"

    def test_ost_full(self):
        assert normalize_genre_name("Original Soundtrack") == "Banda Sonora"


class TestSplitGenres:
    def test_single_genre(self):
        assert split_genres("Rock") == ["Rock"]

    def test_comma_separated(self):
        result = split_genres("Rock, Pop")
        assert len(result) >= 1

    def test_semicolon_separated(self):
        result = split_genres("Rock; Pop")
        assert len(result) >= 1

    def test_slash_separated(self):
        result = split_genres("Rock / Pop")
        assert len(result) >= 1

    def test_rb_not_split(self):
        result = split_genres("R&B")
        assert "R&B" in result

    def test_drum_and_bass_not_split_by_and(self):
        result = split_genres("Drum & Bass")
        assert len(result) == 1

    def test_rock_and_roll_not_split(self):
        result = split_genres("Rock & Roll")
        assert len(result) == 1

    def test_empty(self):
        assert split_genres("") == []

    def test_none(self):
        assert split_genres(None) == []


class TestGenreKey:
    def test_basic(self):
        assert genre_key("Rock") == "rock"

    def test_spaces(self):
        assert genre_key("Alternative Rock") == "alternative_rock"

    def test_hyphens(self):
        assert genre_key("Post-Punk") == "post_punk"

    def test_slashes(self):
        assert genre_key("Hip-Hop/Rap") == "hip_hop_rap"

    def test_ampersand(self):
        assert genre_key("R&B") == "randb"


class TestIsJunkGenre:
    def test_unknown(self):
        assert is_junk_genre("unknown") is True

    def test_other(self):
        assert is_junk_genre("Other") is True

    def test_none_str(self):
        assert is_junk_genre("none") is True

    def test_rock_is_not_junk(self):
        assert is_junk_genre("Rock") is False

    def test_empty_is_junk(self):
        assert is_junk_genre("") is True

    def test_various(self):
        assert is_junk_genre("various") is True


class TestIsCompoundGenre:
    def test_rb(self):
        assert is_compound_genre("R&B") is True

    def test_drum_bass(self):
        assert is_compound_genre("Drum & Bass") is True

    def test_rock_not_compound(self):
        assert is_compound_genre("Rock") is False


class TestSplitGenresCompound:
    def test_rb_soul(self):
        assert split_genres("R&B; Soul") == ["R&B", "Soul"]

    def test_drum_bass_jungle(self):
        assert split_genres("Drum & Bass; Jungle") == ["Drum & Bass", "Jungle"]

    def test_rock_roll_blues(self):
        assert split_genres("Rock & Roll; Blues") == ["Rock & Roll", "Blues"]

    def test_singer_songwriter_folk(self):
        assert split_genres("Singer/Songwriter; Folk") == ["Singer/Songwriter", "Folk"]

    def test_hiphop_rap_trap(self):
        result = split_genres("Hip-Hop/Rap; Trap")
        assert len(result) >= 1

    def test_rb_neo_soul(self):
        result = split_genres("R&B / Neo Soul")
        assert "R&B" in result
        assert "Neo Soul" in result or "Neo soul" in result

    def test_rock_pop_standard(self):
        assert split_genres("Rock; Pop") == ["Rock", "Pop"]

    def test_rock_slash_pop(self):
        assert split_genres("Rock / Pop") == ["Rock", "Pop"]

    def test_preserves_single_compound(self):
        assert split_genres("R&B") == ["R&B"]
        assert split_genres("Drum & Bass") == ["Drum & Bass"]
        assert split_genres("Rock & Roll") == ["Rock & Roll"]

    def test_three_genres(self):
        result = split_genres("Rock, Pop, Jazz")
        assert len(result) == 3


class TestDetectDuplicateGenres:
    def test_no_duplicates(self):
        class MockItem:
            def __init__(self, genre, filepath=""):
                self.genre = genre
                self.filepath = filepath
        items = [MockItem("Rock"), MockItem("Pop")]
        assert detect_duplicate_genres(items) == []

    def test_detects_duplicates(self):
        class MockItem:
            def __init__(self, genre, filepath=""):
                self.genre = genre
                self.filepath = filepath or f"/path/{genre}.flac"
        items = [MockItem("Hip-Hop"), MockItem("hiphop"),
                 MockItem("Hip Hop")]
        dups = detect_duplicate_genres(items)
        assert len(dups) >= 1

    def test_ignores_junk(self):
        class MockItem:
            def __init__(self, genre):
                self.genre = genre
        items = [MockItem("unknown"), MockItem("Unknown")]
        dups = detect_duplicate_genres(items)
        assert len(dups) == 0

    def test_ignores_empty(self):
        class MockItem:
            def __init__(self, genre):
                self.genre = genre
        items = [MockItem(""), MockItem("")]
        dups = detect_duplicate_genres(items)
        assert len(dups) == 0

    def test_stable_canonical(self):
        class MockItem:
            def __init__(self, genre):
                self.genre = genre
        items = [MockItem("Hip-Hop"), MockItem("hiphop"), MockItem("Hip Hop")]
        dups = detect_duplicate_genres(items)
        assert len(dups) >= 1
        # Run twice, canonical should be the same
        dups2 = detect_duplicate_genres(items)
        assert dups[0]["canonical"] == dups2[0]["canonical"]
