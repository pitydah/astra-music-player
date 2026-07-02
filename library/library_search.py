"""LibrarySearch — unified search contract for all library sections."""
from __future__ import annotations

from dataclasses import dataclass, field

from library.library_state import LibraryFilters, LibrarySection, LibrarySort


@dataclass
class LibrarySearchRequest:
    section: LibrarySection = LibrarySection.SONGS
    query: str = ""
    filters: LibraryFilters = field(default_factory=LibraryFilters)
    sort: LibrarySort = field(default_factory=LibrarySort)
    limit: int = 5000
    offset: int = 0


@dataclass
class LibrarySearchResult:
    section: LibrarySection
    items: list = field(default_factory=list)
    total_count: int = 0
    visible_count: int = 0
    empty_reason: str = ""
    context: dict = field(default_factory=dict)


class LibrarySearchService:
    def __init__(self, db=None, song_search=None, album_repo=None,
                 artist_repo=None, genre_repo=None):
        self._db = db
        self._song_search = song_search
        self._album_repo = album_repo
        self._artist_repo = artist_repo
        self._genre_repo = genre_repo

    def search(self, request: LibrarySearchRequest) -> LibrarySearchResult:
        q = request.query.strip().lower()
        section = request.section

        if section == LibrarySection.SONGS:
            return self._search_songs(request)
        if section == LibrarySection.ALBUMS:
            return self._search_albums(q, request)
        if section == LibrarySection.ARTISTS:
            return self._search_artists(q, request)
        if section == LibrarySection.GENRES:
            return self._search_genres(q, request)
        if section == LibrarySection.FOLDERS:
            return self._search_folders(q, request)
        return LibrarySearchResult(section=section, empty_reason="Unknown section")

    def _search_songs(self, request: LibrarySearchRequest) -> LibrarySearchResult:
        if self._song_search and hasattr(self._song_search, 'filter'):
            items = self._song_search.filter(text_filter=request.query.strip())
            return LibrarySearchResult(
                section=LibrarySection.SONGS, items=items,
                total_count=len(items), visible_count=len(items))
        if self._db and hasattr(self._db, 'search_advanced'):
            from library.search_engine import SearchEngine
            engine = SearchEngine(self._db)
            items = engine.search(request.query, limit=request.limit)
            return LibrarySearchResult(
                section=LibrarySection.SONGS, items=items,
                total_count=len(items), visible_count=len(items))
        return LibrarySearchResult(section=LibrarySection.SONGS, empty_reason="No search engine")

    def _search_albums(self, q: str, request: LibrarySearchRequest) -> LibrarySearchResult:
        if self._album_repo and hasattr(self._album_repo, 'groups'):
            groups = self._album_repo.groups
            if q:
                groups = [g for g in groups if q in (g.identity.display_title or "").lower()
                          or q in (g.identity.display_artist or "").lower()]
            return LibrarySearchResult(
                section=LibrarySection.ALBUMS, items=groups,
                total_count=len(groups), visible_count=len(groups))
        return LibrarySearchResult(section=LibrarySection.ALBUMS, empty_reason="No album repo")

    def _search_artists(self, q: str, request: LibrarySearchRequest) -> LibrarySearchResult:
        if self._artist_repo and hasattr(self._artist_repo, 'groups'):
            groups = self._artist_repo.groups
            if q:
                groups = [g for g in groups if q in (g.display_name or "").lower()
                          or any(q in (a.title or "").lower() for a in g.albums)
                          or any(q in (t.title or "").lower() for t in g.all_tracks)]
            return LibrarySearchResult(
                section=LibrarySection.ARTISTS, items=groups,
                total_count=len(groups), visible_count=len(groups))
        return LibrarySearchResult(section=LibrarySection.ARTISTS, empty_reason="No artist repo")

    def _search_genres(self, q: str, request: LibrarySearchRequest) -> LibrarySearchResult:
        if self._genre_repo and hasattr(self._genre_repo, 'get_all_genres'):
            genres = self._genre_repo.get_all_genres()
            if q:
                genres = [g for g in genres if q in (g or "").lower()]
            return LibrarySearchResult(
                section=LibrarySection.GENRES, items=genres,
                total_count=len(genres), visible_count=len(genres))
        if self._db:
            try:
                cur = self._db.conn.execute(
                    "SELECT DISTINCT genre FROM media_items "
                    "WHERE genre != '' AND genre IS NOT NULL AND deleted_at IS NULL ORDER BY genre")
                genres = [r[0] for r in cur.fetchall()]
                if q:
                    genres = [g for g in genres if q in g.lower()]
                return LibrarySearchResult(
                    section=LibrarySection.GENRES, items=genres,
                    total_count=len(genres), visible_count=len(genres))
            except Exception:
                pass
        return LibrarySearchResult(section=LibrarySection.GENRES, empty_reason="No genre data")

    def _search_folders(self, q: str, request: LibrarySearchRequest) -> LibrarySearchResult:
        if self._db:
            try:
                cur = self._db.conn.execute(
                    "SELECT DISTINCT directory FROM media_items "
                    "WHERE directory != '' AND deleted_at IS NULL ORDER BY directory")
                folders = [r[0] for r in cur.fetchall()]
                if q:
                    folders = [f for f in folders if q in f.lower()]
                return LibrarySearchResult(
                    section=LibrarySection.FOLDERS, items=folders,
                    total_count=len(folders), visible_count=len(folders))
            except Exception:
                pass
        return LibrarySearchResult(section=LibrarySection.FOLDERS, empty_reason="No folder data")
