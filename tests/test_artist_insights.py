"""Tests for artist_insights module."""
from library.artist_insights import (
    compute_quality_summary,
    compute_metadata_health,
    detect_artist_appearances,
    rank_top_tracks,
    build_artist_insight,
)
from library.library_db import MediaItem
from library.artist_grouping import ArtistGroup


def _make_item(**kw):
    defaults = dict(
        id=0, filepath="/tmp/track.flac", filename="track.flac",
        directory="/tmp", ext="flac", kind="audio",
        size=0, mtime=0.0, duration=200.0,
        channels=2, sample_rate=44100, bitrate=1000,
        title="Test", artist="Test Artist", album="Test Album",
        year=2020, genre="Rock",
        track_number=1, composer="",
        albumartist="", disc_number=1, disc_total=1, track_total=10,
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


def _make_group(tracks=None, **kw):
    defaults = dict(
        key="test_artist", display_name="Test Artist",
        sort_name="test artist",
        albums=[], loose_tracks=[], all_tracks=tracks or [],
        genres=["Rock", "Pop"], years=[2020],
        cover_paths=["/tmp/cover.jpg"],
        total_duration=200.0, track_count=1, album_count=1,
    )
    defaults.update(kw)
    return ArtistGroup(**defaults)


class TestQualitySummary:
    def test_empty_tracks(self):
        s = compute_quality_summary([])
        assert s.total_tracks == 0
        assert s.lossless_count == 0

    def test_flac_track(self):
        item = _make_item(ext="flac", bit_depth=24, sample_rate=96000)
        s = compute_quality_summary([item])
        assert s.total_tracks == 1
        assert s.lossless_count == 1
        assert s.hi_res_count == 1
        assert s.dominant_format == "flac"

    def test_mp3_track(self):
        item = _make_item(ext="mp3", bitrate=320)
        s = compute_quality_summary([item])
        assert s.lossy_count == 1
        assert s.lossless_count == 0
        assert s.average_bitrate == 320

    def test_dsd_hires(self):
        item = _make_item(ext="dsf", sample_rate=2822400, bit_depth=1)
        s = compute_quality_summary([item])
        assert s.hi_res_count == 1

    def test_mixed_formats(self):
        items = [
            _make_item(ext="flac", filepath="/tmp/a.flac"),
            _make_item(ext="flac", filepath="/tmp/b.flac"),
            _make_item(ext="mp3", filepath="/tmp/c.mp3"),
        ]
        s = compute_quality_summary(items)
        assert s.lossless_count == 2
        assert s.lossy_count == 1
        assert s.lossless_ratio == 2.0 / 3.0

    def test_replaygain_count(self):
        items = [
            _make_item(replaygain_track=-8.0),
            _make_item(replaygain_track=0.0, filepath="/tmp/b.flac"),
            _make_item(replaygain_track=-6.0, filepath="/tmp/c.flac"),
        ]
        s = compute_quality_summary(items)
        assert s.replaygain_count == 2


class TestMetadataHealth:
    def test_clean_group(self):
        group = _make_group(tracks=[_make_item()])
        h = compute_metadata_health(group)
        # The track filepath /tmp/track.flac doesn't exist, so missing_files_count is 1
        assert h.missing_files_count == 1
        assert h.missing_album_count == 0
        assert h.missing_genre_count == 0

    def test_missing_genre(self):
        item = _make_item(genre="")
        group = _make_group(tracks=[item])
        h = compute_metadata_health(group)
        assert h.missing_genre_count == 1

    def test_missing_album(self):
        item = _make_item(album="")
        group = _make_group(tracks=[item])
        h = compute_metadata_health(group)
        assert h.missing_album_count == 1

    def test_missing_year(self):
        item = _make_item(year=0)
        group = _make_group(tracks=[item])
        h = compute_metadata_health(group)
        assert h.missing_year_count == 1

    def test_missing_track_number(self):
        item = _make_item(track_number=0)
        group = _make_group(tracks=[item])
        h = compute_metadata_health(group)
        assert h.missing_track_number_count == 1


class TestArtistAppearances:
    def test_feat_detection(self):
        main_group = _make_group(tracks=[_make_item()])
        items = [
            _make_item(artist="Test Artist feat. Guest", title="Collab",
                       filepath="/tmp/collab.flac"),
        ]
        apps = detect_artist_appearances(main_group, items)
        assert len(apps) == 1
        assert apps[0].reason == "feat"

    def test_no_appearance(self):
        main_group = _make_group(tracks=[_make_item()])
        items = [
            _make_item(artist="Other Artist", title="Other",
                       filepath="/tmp/other.flac"),
        ]
        apps = detect_artist_appearances(main_group, items)
        assert len(apps) == 0

    def test_skips_own_tracks(self):
        main_group = _make_group(tracks=[_make_item(filepath="/tmp/track.flac")])
        items = [_make_item(filepath="/tmp/track.flac")]
        apps = detect_artist_appearances(main_group, items)
        assert len(apps) == 0


class TestTopTracks:
    def test_rank_by_play_count(self):
        tracks = [
            _make_item(title="Low", play_count=1, filepath="/tmp/a.flac"),
            _make_item(title="High", play_count=10, filepath="/tmp/b.flac"),
            _make_item(title="Mid", play_count=5, filepath="/tmp/c.flac"),
        ]
        group = _make_group(tracks=tracks)
        top = rank_top_tracks(group, 2)
        assert len(top) == 2
        assert top[0].title == "High"

    def test_fallback_without_play_count(self):
        tracks = [
            _make_item(title="B", year=2020, track_number=2, filepath="/tmp/b.flac",
                       play_count=0),
            _make_item(title="A", year=2020, track_number=1, filepath="/tmp/a.flac",
                       play_count=0),
        ]
        group = _make_group(tracks=tracks)
        top = rank_top_tracks(group, 2)
        assert len(top) == 2


class TestBuildInsight:
    def test_full_insight(self):
        tracks = [_make_item()]
        group = _make_group(tracks=tracks)
        insight = build_artist_insight(group)
        assert insight.artist_key == "test_artist"
        assert insight.primary_genres == ["Rock", "Pop"]
        assert insight.active_year_range == (2020, 2020)
        assert insight.quality.total_tracks == 1

    def test_insight_with_appearances(self):
        tracks = [_make_item()]
        group = _make_group(tracks=tracks)
        all_items = [
            _make_item(artist="Test Artist feat. X",
                       filepath="/tmp/x.flac"),
        ]
        insight = build_artist_insight(group, all_items)
        assert len(insight.collaborations) == 1
