# Library Architecture — Michi Music Player

## Concept

**Biblioteca** is the central subsystem for managing the user's local music collection. It provides 5 sections (Canciones, Álbumes, Artistas, Géneros, Carpetas) with unified search, filtering, sorting, and navigation history.

## Canonical State

All UI state for the library is defined in `library/library_state.py`:

```python
LibrarySection  — SONGS, ALBUMS, ARTISTS, GENRES, FOLDERS
LibraryViewMode — LIST, GRID, COVERFLOW, TREE
LibraryState    — section + view_mode + filters + sort + selection + scroll_position
LibraryFilters  — query, formats, qualities, genres, year range, bitrate, favorites, etc.
LibrarySelection — scope, track_id, filepath, album_key, artist_key, genre, folder_path
```

Validation rules:
- COVERFLOW only in ALBUMS
- TREE only in FOLDERS
- Invalid view modes fallback to section default

## State Controller

`ui/controllers/library_state_controller.py` — Qt Signals-based controller:

```
state_changed      → LibraryState
section_changed    → LibrarySection
view_mode_changed  → LibraryViewMode
search_changed     → str
filters_changed    → LibraryFilters
selection_changed  → LibrarySelection
sort_changed       → LibrarySort
```

API: `state()`, `set_section()`, `set_view_mode()`, `set_search()`, `set_filters()`, `set_selection()`, `set_sort()`, `snapshot()`, `restore()`, `breadcrumb_parts()`, `context_payload()`.

## File Organization

```
library/
├── library_state.py           # Canonical state (enums + dataclasses)
├── track_identity.py          # TrackIdentityService — 6-level UID priority
├── media_item.py              # MediaItem dataclass (69 fields, from_row/from_dict/to_dict)
├── media_record_builder.py    # MediaRecordBuilder — file → DB record (shared by Indexer + add_file)
├── library_mutation_service.py  # LibraryMutationService — add/remove/update with result tracking
├── library_organize_service.py  # LibraryOrganizeService — preview, validate, execute with rollback
├── library_search.py          # LibrarySearchService — unified search across all 5 sections
├── library_health_service.py  # LibraryHealthService — health summary + score
├── indexer.py                 # Indexer 2.0 — full scan pipeline (7 phases)
├── library_db.py              # LibraryDB — SQLite operations (Upsert, search, backfill)
├── schema.py                  # Schema — ALL CREATE TABLE + migrations
├── search_engine.py           # SearchEngine — FTS5 + LIKE fallback + field filters
├── search_index.py            # SearchIndex — FTS5 management
├── album_repository.py        # AlbumRepository — grouping, sorting
├── artist_grouping.py         # ArtistRepository — artist groups with albums
├── genre_repository.py        # GenreRepository — genre normalization, backfill
├── file_watcher.py            # FileWatcher — QFileSystemWatcher for real-time changes
├── batch_writer.py            # BatchWriter — transaction-safe batch upserts
├── change_detector.py         # ChangeDetector — mtime+size based skip
├── metadata_extractor.py      # MetadataExtractor — mutagen + GStreamer extraction
├── metadata_normalizer.py     # Normalizer functions (artist, genre, year, etc.)
├── album_key.py               # AlbumKey — stable album identity
└── cover_art_service.py       # CoverArtService — find, cache, embed covers
```

## Navigation Routes

| Route | Section | Tab | Sidebar Active |
|-------|---------|-----|---------------|
| `library_hub` | — | — | library_hub |
| `library` | SONGS | Canciones | library_hub |
| `albums` | ALBUMS | Álbumes | library_hub |
| `artists` | ARTISTS | Artistas | library_hub |
| `genres` | GENRES | Géneros | genres (top-level) |
| `folders` | FOLDERS | Carpetas | library_hub |
| `album:<key>` | ALBUMS | Detail | library_hub |
| `artist:<key>` | ARTISTS | Detail | library_hub |
| `genre:<key>` | GENRES | Detail | genres |

## Track Identity (`track_identity.py`)

Priority chain for `track_uid`:

1. **MusicBrainz Track ID** — `mb:<uuid>` (stable across moves/renames)
2. **AcoustID** — `ac:<id>` (content-based)
3. **Content hash** — `ch:<sha256>` (first + last 64KB)
4. **File hash** — `fh:<sha256>` (full file SHA-256)
5. **Normalized metadata** — `nm:<sha256>` (artist|album|title|duration)
6. **File path hash** — `fp:<sha256>` (UNSTABLE — changes on move)

`is_path_based_uid()` and `needs_identity_upgrade()` allow detecting and fixing path-based UIDs when stronger identity becomes available.

## Indexing Flow (Indexer 2.0)

```
FileActions.scan_path(path)
  → QThread → Indexer.run()
    → Phase 1: WALK — recursive os.walk(), ignore hidden dirs
    → Phase 2: CHANGE DETECT — skip unchanged files (mtime + size)
    → Phase 3: EXTRACT — MediaRecordBuilder.build() extracts + normalizes
    → Phase 4: BATCH WRITE — BatchWriter (batch_size=100, ON CONFLICT upsert)
    → Phase 5: FLUSH — remaining records
    → Phase 6: CLEANUP — mark missing files (delegated to FileActions)
    → Phase 7: REBUILD — SQL indexes + FTS5
    → Phase 8: ENRICH — schedule MusicBrainz/TheAudioDB enrichment
    → Phase 9: SYNC GENRES — GenreRepository.backfill_from_media_items()
```

## Mutation Service (`library_mutation_service.py`)

Single entry point for all library changes:

| Method | Use Case | Result |
|--------|----------|--------|
| `add_file(fp)` | Single file import | LibraryMutationResult |
| `add_files(list)` | Batch import (shared BatchWriter) | LibraryMutationResult |
| `remove_paths(list)` | Soft-delete files | LibraryMutationResult |
| `mark_missing_under_root(root)` | Detect deleted files | LibraryMutationResult |
| `update_filepath(old, new)` | Rename/move tracking | LibraryMutationResult |
| `sync_genres()` | Sync track_genres table | int (rows inserted) |
| `rebuild_fts()` | Rebuild FTS5 index | bool |

Each mutation syncs genres and triggers `on_change` callback.

## Organize Service (`library_organize_service.py`)

Safe file organization with rollback:

1. **Preview** — detect collisions, cross-root moves, existing targets, sidecars
2. **Validate** — reject plans with collisions
3. **Execute** — rename files → update DB → rollback on failure

Rollback renames all completed files back to original paths and reverts DB.

## Unified Search (`library_search.py`)

```python
LibrarySearchRequest → section, query, filters, sort, limit, offset
LibrarySearchResult  → section, items, total_count, visible_count, empty_reason
```

Section adapters:
- **SONGS**: `SongsQueryService` (premium) or `SearchEngine` (legacy)
- **ALBUMS**: `AlbumRepository.groups` filtered by display title/artist
- **ARTISTS**: `ArtistRepository.groups` filtered by name/album/track
- **GENRES**: `GenreRepository.get_all_genres()` or direct SQL
- **FOLDERS**: SQL `SELECT DISTINCT directory FROM media_items`

## Health Service (`library_health_service.py`)

Health summary with score (0-100):

| Issue | Penalty per track |
|-------|------------------|
| Missing file | 100 pts |
| Missing metadata | 50 pts |
| Duplicate UID group | 30 pts |
| Scan error | 50 pts |
| Suspicious audio | 40 pts |

Status: `good` (≥90), `attention` (≥60), `critical` (<60)

## Navigation History

`NavigationEntry` stores:
- `key` — route key
- `search_text` — previous search
- `library_state` — optional LibraryState dict (for library sections)

Back/forward restores: route → search text → library state (section, filters, selection, view mode).

## Validation

```bash
ruff check library/ ui/controllers/navigation_controller.py
python3 -m compileall -q library/ ui/controllers/
QT_QPA_PLATFORM=offscreen python3 -m pytest \
  tests/test_library_state.py \
  tests/test_library_state_controller.py \
  tests/test_library_navigation_state.py \
  tests/test_track_identity.py \
  tests/test_media_item_fields.py \
  tests/test_media_record_builder.py \
  tests/test_library_mutation_service.py \
  tests/test_library_watcher_controller.py \
  tests/test_library_search_contract.py \
  tests/test_library_organize_safe.py \
  tests/test_library_health_service.py \
  tests/test_navigation_history.py \
  tests/test_navigation_back_forward.py \
  tests/test_navigation_controller.py \
  -q
```
