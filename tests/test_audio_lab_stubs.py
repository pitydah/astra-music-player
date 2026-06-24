"""Behavior tests for Audio Lab services — stub validation and error handling.

Tests the STUB implementations on main branch. Documents gaps for future real implementations.
"""



class TestTagWriterStub:
    def test_read_tags_returns_empty_dict(self):
        """TagWriter stub always returns empty dict."""
        from ui.audio_lab.services.tag_writer import TagWriter
        writer = TagWriter()
        assert writer.read_tags("/any/path.mp3") == {}

    def test_write_tags_is_pass(self):
        """TagWriter stub write_tags does nothing."""
        from ui.audio_lab.services.tag_writer import TagWriter
        writer = TagWriter()
        writer.write_tags("/any/path.mp3", {"title": "X"})  # must not crash

    def test_write_batch_is_pass(self):
        """TagWriter stub write_batch does nothing."""
        from ui.audio_lab.services.tag_writer import TagWriter
        writer = TagWriter()
        writer.write_batch(["/a.mp3", "/b.mp3"], {"title": "X"})  # must not crash

    def test_embed_cover_is_pass(self):
        """TagWriter stub embed_cover does nothing."""
        from ui.audio_lab.services.tag_writer import TagWriter
        writer = TagWriter()
        writer.embed_cover("/any.flac", "/cover.jpg")  # must not crash


class TestArtworkResolverStub:
    def test_search_album_art_returns_empty(self):
        """ArtworkResolver stub always returns empty list."""
        from ui.audio_lab.services.artwork_resolver import ArtworkResolver
        resolver = ArtworkResolver()
        assert resolver.search_album_art({"folder": "/tmp"}) == []

    def test_rank_artwork_quality_returns_input(self):
        """ArtworkResolver stub rank returns input unchanged."""
        from ui.audio_lab.services.artwork_resolver import ArtworkResolver
        resolver = ArtworkResolver()
        results = [{"score": 50}, {"score": 100}]
        assert resolver.rank_artwork_quality(results) == results

    def test_download_cover_is_pass(self):
        """ArtworkResolver stub download_cover does nothing."""
        from ui.audio_lab.services.artwork_resolver import ArtworkResolver
        resolver = ArtworkResolver()
        resolver.download_cover("http://x.com/c.jpg", "/tmp/c.jpg")  # must not crash

    def test_embed_cover_is_pass(self):
        """ArtworkResolver stub embed_cover does nothing."""
        from ui.audio_lab.services.artwork_resolver import ArtworkResolver
        resolver = ArtworkResolver()
        resolver.embed_cover("/any.flac", "/cover.jpg")  # must not crash

    def test_save_cover_file_is_pass(self):
        """ArtworkResolver stub save_cover_file does nothing."""
        from ui.audio_lab.services.artwork_resolver import ArtworkResolver
        resolver = ArtworkResolver()
        resolver.save_cover_file("/c.jpg", "/tmp/album")  # must not crash


class TestTranscodeServiceStub:
    def test_available_encoders_returns_dict(self):
        """TranscodeService.available_encoders returns a dict."""
        from ui.services.transcode_service import TranscodeService
        svc = TranscodeService()
        encoders = svc.available_encoders
        assert isinstance(encoders, dict)
        assert "ffmpeg" in encoders
        assert "flac" in encoders
        assert "opus" in encoders

    def test_transcode_is_pass(self):
        """TranscodeService.transcode() is a no-op stub."""
        from ui.services.transcode_service import TranscodeService
        svc = TranscodeService()
        svc.transcode("/tmp/src.flac", "/tmp/dst.opus", "original")  # must not crash

    def test_get_profile_returns_original_for_unknown(self):
        from ui.services.transcode_service import TranscodeService
        svc = TranscodeService()
        p = svc.get_profile("nonexistent")
        assert p["name"] == "Original"

    def test_needs_transcode(self):
        from ui.services.transcode_service import TranscodeService
        svc = TranscodeService()
        assert svc.needs_transcode("/a.flac", "opus_balanced") is True
        assert svc.needs_transcode("/a.flac", "original") is False

    def test_profiles_exist(self):
        from ui.services.transcode_service import TRANSCODE_PROFILES
        assert "original" in TRANSCODE_PROFILES
        assert "flac_mobile" in TRANSCODE_PROFILES
        assert "opus_balanced" in TRANSCODE_PROFILES
        assert "opus_efficient" in TRANSCODE_PROFILES


class TestLibraryImporterStub:
    def test_build_destination_path_returns_empty(self):
        """LibraryImporter stub returns empty string for path."""
        from ui.audio_lab.services.library_importer import LibraryImporter
        imp = LibraryImporter()
        assert imp.build_destination_path({"title": "X"}, "flac") == ""

    def test_import_tracks_is_pass(self):
        from ui.audio_lab.services.library_importer import LibraryImporter
        imp = LibraryImporter()
        imp.import_tracks(["/tmp/a.mp3"], {"title": "X"}, "/tmp/out")  # must not crash

    def test_add_to_library_is_pass(self):
        from ui.audio_lab.services.library_importer import LibraryImporter
        imp = LibraryImporter()
        imp.add_to_library(["/tmp/a.mp3"])  # must not crash

    def test_refresh_library_index_is_pass(self):
        from ui.audio_lab.services.library_importer import LibraryImporter
        imp = LibraryImporter()
        imp.refresh_library_index()  # must not crash


class TestMetadataResolverStub:
    def test_find_album_by_disc_toc_returns_none(self):
        from ui.audio_lab.services.metadata_resolver import MetadataResolver
        r = MetadataResolver()
        assert r.find_album_by_disc_toc({"tracks": 5}) is None

    def test_find_album_by_artist_album_returns_none(self):
        from ui.audio_lab.services.metadata_resolver import MetadataResolver
        r = MetadataResolver()
        assert r.find_album_by_artist_album("Artist", "Album") is None

    def test_calculate_confidence_returns_zero(self):
        from ui.audio_lab.services.metadata_resolver import MetadataResolver
        from ui.audio_lab.models import DiscMetadata
        r = MetadataResolver()
        assert r.calculate_confidence(DiscMetadata(artist="A"), {"track_count": 3}) == 0.0

    def test_merge_candidates_picks_first(self):
        from ui.audio_lab.services.metadata_resolver import MetadataResolver
        from ui.audio_lab.models import DiscMetadata
        r = MetadataResolver()
        c1 = DiscMetadata(artist="A")
        c2 = DiscMetadata(artist="B")
        result = r.merge_metadata_candidates([c1, c2])
        assert result.artist == "A"
