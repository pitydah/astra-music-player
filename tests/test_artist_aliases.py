"""Tests for artist_aliases module."""
from library.artist_aliases import (
    normalize_artist_alias,
    split_artist_names,
    detect_featured_artists,
    find_artist_alias_candidates,
)
from library.artist_grouping import ArtistGroup


def _make_group(key, display_name):
    return ArtistGroup(
        key=key,
        display_name=display_name,
        sort_name=display_name.lower(),
    )


class TestNormalizeAlias:
    def test_the_beatles(self):
        assert normalize_artist_alias("The Beatles") == "beatles"

    def test_the_lowercase(self):
        assert normalize_artist_alias("the beatles") == "beatles"

    def test_accented(self):
        assert normalize_artist_alias("Björk") == "bjork"

    def test_acdc_slash(self):
        result = normalize_artist_alias("AC/DC")
        assert "ac" in result
        assert "dc" in result

    def test_punctuation(self):
        assert normalize_artist_alias("Guns N' Roses") == "guns n roses"

    def test_multi_space(self):
        result = normalize_artist_alias("   The    Beatles   ")
        assert result == "beatles"

    def test_spanish_articles(self):
        assert normalize_artist_alias("El Cuarteto") == "cuarteto"
        assert normalize_artist_alias("Los Angeles") == "angeles"

    def test_german_article(self):
        assert normalize_artist_alias("Der Plan") == "plan"


class TestSplitArtists:
    def test_simple(self):
        assert split_artist_names("Artist A") == ["Artist A"]

    def test_feat(self):
        result = split_artist_names("Artist feat. Guest")
        assert "Artist" in result
        assert "Guest" in result

    def test_ft(self):
        result = split_artist_names("Artist ft. Guest")
        assert "Guest" in result

    def test_ampersand(self):
        result = split_artist_names("A & B")
        assert "A" in result
        assert "B" in result

    def test_slash(self):
        result = split_artist_names("A / B")
        assert "A" in result


class TestFeaturedDetection:
    def test_feat(self):
        assert detect_featured_artists("A feat. B") == ["B"]

    def test_ft(self):
        assert detect_featured_artists("A ft. B") == ["B"]

    def test_multiple_featured(self):
        result = detect_featured_artists("A feat. B & C")
        assert "B" in result
        assert "C" in result

    def test_no_feat(self):
        assert detect_featured_artists("Just Artist") == []


class TestAliasCandidates:
    def test_exact_match_via_articles(self):
        groups = [
            _make_group("the_beatles", "The Beatles"),
            _make_group("beatles", "Beatles"),
        ]
        candidates = find_artist_alias_candidates(groups)
        assert len(candidates) >= 1

    def test_exact_match_normalized(self):
        groups = [
            _make_group("bjork", "Björk"),
            _make_group("bjork2", "Bjork"),
        ]
        candidates = find_artist_alias_candidates(groups)
        assert len(candidates) >= 1

    def test_no_duplicates(self):
        groups = [
            _make_group("unique1", "Unique Artist One"),
            _make_group("unique2", "Unique Artist Two"),
        ]
        candidates = find_artist_alias_candidates(groups)
        # These are different names (One vs Two), should not be aliases
        high_conf = [c for c in candidates if c[2] >= 0.95]
        assert len(high_conf) == 0
