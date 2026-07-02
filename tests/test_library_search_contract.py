"""Tests for LibrarySearchService."""
from unittest.mock import MagicMock

from library.library_state import LibrarySection
from library.library_search import LibrarySearchRequest, LibrarySearchService


class TestSearch:
    def test_songs_no_engine(self):
        r = LibrarySearchService().search(LibrarySearchRequest(section=LibrarySection.SONGS))
        assert r.empty_reason

    def test_albums_no_repo(self):
        r = LibrarySearchService().search(LibrarySearchRequest(section=LibrarySection.ALBUMS))
        assert r.empty_reason

    def test_unknown_section(self):
        r = LibrarySearchService().search(LibrarySearchRequest(section="bogus"))
        assert r.empty_reason

    def test_songs_with_mock(self):
        mock_s = MagicMock()
        mock_s.filter.return_value = [{"id": 1}]
        r = LibrarySearchService(song_search=mock_s).search(
            LibrarySearchRequest(section=LibrarySection.SONGS, query="t"))
        assert r.total_count == 1

    def test_albums_with_mock(self):
        mock_r = MagicMock()
        mock_r.groups = [MagicMock(identity=MagicMock(display_title="A", display_artist="B"))]
        r = LibrarySearchService(album_repo=mock_r).search(
            LibrarySearchRequest(section=LibrarySection.ALBUMS))
        assert r.total_count == 1

    def test_genres_with_mock(self):
        mock_r = MagicMock()
        mock_r.get_all_genres.return_value = ["Rock", "Jazz"]
        r = LibrarySearchService(genre_repo=mock_r).search(
            LibrarySearchRequest(section=LibrarySection.GENRES))
        assert r.total_count == 2

    def test_folders_with_db(self):
        mock_db = MagicMock()
        mock_c = MagicMock()
        mock_c.fetchall.return_value = [("/m/r",)]
        mock_db.conn.execute.return_value = mock_c
        r = LibrarySearchService(db=mock_db).search(
            LibrarySearchRequest(section=LibrarySection.FOLDERS))
        assert r.total_count == 1
