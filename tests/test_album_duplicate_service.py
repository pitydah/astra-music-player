"""Tests for album duplicate detection."""
from unittest.mock import MagicMock

from library.album_identity import AlbumIdentity
from library.album_repository import AlbumGroup


def _make_group(album_key="key1", title="Album", artist="Artist",
                year="2024", track_count=10) -> AlbumGroup:
    identity = AlbumIdentity(
        album_key=album_key,
        display_title=title,
        display_artist=artist,
        year=year,
    )
    tracks = [MagicMock() for _ in range(track_count)]
    return AlbumGroup(identity=identity, tracks=tracks)


class TestFindDuplicates:
    def test_exact_duplicate(self):
        from library.album_duplicate_service import AlbumDuplicateService
        svc = AlbumDuplicateService()
        groups = [
            _make_group(album_key="a", title="Album", artist="Artist"),
            _make_group(album_key="b", title="Album", artist="Artist"),
        ]
        results = svc.find_duplicates(groups)
        assert len(results) >= 1
        assert results[0].confidence >= 0.8

    def test_different_albums(self):
        from library.album_duplicate_service import AlbumDuplicateService
        svc = AlbumDuplicateService()
        groups = [
            _make_group(album_key="a", title="Album A", artist="Artist"),
            _make_group(album_key="b", title="Album B", artist="Artist"),
        ]
        results = svc.find_duplicates(groups)
        assert len(results) == 0

    def test_remaster_edition(self):
        from library.album_duplicate_service import AlbumDuplicateService
        svc = AlbumDuplicateService()
        groups = [
            _make_group(album_key="a", title="Album", artist="Artist"),
            _make_group(album_key="b", title="Album (Remastered)", artist="Artist"),
        ]
        results = svc.find_duplicates(groups)
        assert len(results) >= 1
        assert results[0].confidence >= 0.6

    def test_find_for_group(self):
        from library.album_duplicate_service import AlbumDuplicateService
        svc = AlbumDuplicateService()
        groups = [
            _make_group(album_key="a", title="Same", artist="Artist"),
            _make_group(album_key="b", title="Same", artist="Artist"),
            _make_group(album_key="c", title="Different", artist="Artist"),
        ]
        target = groups[0]
        results = svc.find_for_group(groups, target)
        assert len(results) == 1
        assert results[0].right_key == "b"

    def test_reasons_non_empty(self):
        from library.album_duplicate_service import AlbumDuplicateService
        svc = AlbumDuplicateService()
        groups = [
            _make_group(album_key="a", title="Album", artist="Artist"),
            _make_group(album_key="b", title="Album", artist="Artist"),
        ]
        results = svc.find_duplicates(groups)
        assert len(results[0].reasons) > 0
