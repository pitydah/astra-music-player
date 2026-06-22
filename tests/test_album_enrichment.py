"""Tests for album enrichment — matching, confidence, no duplicates, artist field."""


def test_album_match_exact():
    from integrations.artist_metadata.album_enrichment_service import _match_album
    assert _match_album("Dark Side of the Moon", "Dark Side of the Moon") == 1.0
    assert _match_album("Abbey Road", "Abbey Road") == 1.0


def test_album_match_case_insensitive():
    from integrations.artist_metadata.album_enrichment_service import _match_album
    assert _match_album("dark side of the moon", "Dark Side Of The Moon") == 1.0


def test_album_match_punctuation():
    from integrations.artist_metadata.album_enrichment_service import _match_album
    assert _match_album("Dark Side of the Moon", "Dark Side Of The Moon") == 1.0
    assert _match_album("Help!", "Help") == 1.0


def test_album_match_rejects_low_confidence():
    from integrations.artist_metadata.album_enrichment_service import _match_album
    score = _match_album("Dark Side of the Moon", "Greatest Hits 1970-1980")
    assert score < 0.60


def test_album_match_contains():
    from integrations.artist_metadata.album_enrichment_service import _match_album
    score = _match_album("Dark Side of the Moon",
                          "The Dark Side of the Moon (Remastered)")
    assert score >= 0.65


def test_dict_to_summary_reads_cover_url():
    from metadata.album_info_repository import _dict_to_summary
    data = {"album_key": "k1", "title": "Test", "artist": "Artist",
            "cover_url": "https://example.com/c.jpg",
            "thumb_url": "https://example.com/t.jpg"}
    s = _dict_to_summary(data)
    assert s is not None
    assert s.cover_url == "https://example.com/c.jpg"
    assert s.thumb_url == "https://example.com/t.jpg"


def test_dict_to_summary_external_ids_from_raw_json():
    from metadata.album_info_repository import _dict_to_summary
    import json
    data = {"album_key": "k2", "title": "Test", "artist": "Artist",
            "raw_json": json.dumps({"external_ids": {"mbid": "abc-123"}})}
    s = _dict_to_summary(data)
    assert s is not None
    assert s.external_ids == {"mbid": "abc-123"}


def test_album_summary_defaults_external_ids():
    from metadata.album_summary import AlbumSummary
    s = AlbumSummary()
    assert s.external_ids == {}
    assert s.track_list == []
    assert s.cover_url == ""
