-- Migration 001: Initial Knowledge Broker schema
-- Creates all tables, indexes, and FTS5 full-text search

CREATE TABLE IF NOT EXISTS kb_artist (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    sort_name       TEXT DEFAULT '',
    mbid            TEXT UNIQUE,
    wikidata_id     TEXT DEFAULT '',
    country         TEXT DEFAULT '',
    begin_date      TEXT DEFAULT '',
    end_date        TEXT DEFAULT '',
    type            TEXT DEFAULT '',
    disambiguation  TEXT DEFAULT '',
    tags_json       TEXT DEFAULT '[]',
    relations_json  TEXT DEFAULT '[]',
    source          TEXT DEFAULT '',
    confidence      REAL DEFAULT 1.0,
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS kb_album (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               TEXT NOT NULL,
    artist_name         TEXT DEFAULT '',
    artist_mbid         TEXT DEFAULT '',
    release_group_mbid  TEXT UNIQUE,
    release_mbid        TEXT DEFAULT '',
    date                TEXT DEFAULT '',
    year                TEXT DEFAULT '',
    country             TEXT DEFAULT '',
    primary_type        TEXT DEFAULT '',
    secondary_types_json TEXT DEFAULT '[]',
    tags_json           TEXT DEFAULT '[]',
    cover_url           TEXT DEFAULT '',
    cover_path          TEXT DEFAULT '',
    source              TEXT DEFAULT '',
    confidence          REAL DEFAULT 1.0,
    updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS kb_recording (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               TEXT NOT NULL,
    artist_name         TEXT DEFAULT '',
    artist_mbid         TEXT DEFAULT '',
    recording_mbid      TEXT UNIQUE,
    release_group_mbid  TEXT DEFAULT '',
    release_mbid        TEXT DEFAULT '',
    length_ms           INTEGER DEFAULT 0,
    isrc                TEXT DEFAULT '',
    tags_json           TEXT DEFAULT '[]',
    source              TEXT DEFAULT '',
    confidence          REAL DEFAULT 1.0,
    updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS kb_wiki_summary (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL DEFAULT '',
    entity_key  TEXT NOT NULL DEFAULT '',
    language    TEXT NOT NULL DEFAULT 'es',
    title       TEXT DEFAULT '',
    summary     TEXT DEFAULT '',
    source_url  TEXT DEFAULT '',
    license     TEXT DEFAULT '',
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS kb_external_id (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type  TEXT NOT NULL DEFAULT '',
    entity_key   TEXT NOT NULL DEFAULT '',
    provider     TEXT NOT NULL DEFAULT '',
    external_id  TEXT NOT NULL DEFAULT '',
    external_url TEXT DEFAULT '',
    updated_at   TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS kb_cache_meta (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source     TEXT NOT NULL DEFAULT '',
    last_sync  TEXT DEFAULT (datetime('now')),
    expires_at TEXT DEFAULT (datetime('now', '+30 days')),
    license    TEXT DEFAULT '',
    version    TEXT DEFAULT '1.0',
    status     TEXT DEFAULT 'idle'
);

CREATE TABLE IF NOT EXISTS kb_source_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT DEFAULT (datetime('now')),
    source          TEXT NOT NULL DEFAULT '',
    operation       TEXT NOT NULL DEFAULT '',
    query_safe_json TEXT DEFAULT '{}',
    status          TEXT DEFAULT 'success',
    error           TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS kb_negative_cache (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL DEFAULT '',
    query_hash TEXT NOT NULL DEFAULT '',
    reason     TEXT DEFAULT '',
    source     TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT DEFAULT (datetime('now', '+7 days'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_kb_artist_name ON kb_artist(name);
CREATE INDEX IF NOT EXISTS idx_kb_artist_mbid ON kb_artist(mbid);
CREATE INDEX IF NOT EXISTS idx_kb_album_title ON kb_album(title);
CREATE INDEX IF NOT EXISTS idx_kb_album_rg_mbid ON kb_album(release_group_mbid);
CREATE INDEX IF NOT EXISTS idx_kb_recording_title ON kb_recording(title);
CREATE INDEX IF NOT EXISTS idx_kb_recording_mbid ON kb_recording(recording_mbid);
CREATE INDEX IF NOT EXISTS idx_kb_wiki_entity ON kb_wiki_summary(entity_type, entity_key);
CREATE INDEX IF NOT EXISTS idx_kb_neg_hash ON kb_negative_cache(query_hash);

-- FTS5 full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS kb_artist_fts USING fts5(
    name, sort_name, disambiguation, country,
    content='kb_artist', content_rowid='id'
);
CREATE VIRTUAL TABLE IF NOT EXISTS kb_album_fts USING fts5(
    title, artist_name, primary_type,
    content='kb_album', content_rowid='id'
);
CREATE VIRTUAL TABLE IF NOT EXISTS kb_recording_fts USING fts5(
    title, artist_name,
    content='kb_recording', content_rowid='id'
);
CREATE VIRTUAL TABLE IF NOT EXISTS kb_wiki_summary_fts USING fts5(
    title, summary,
    content='kb_wiki_summary', content_rowid='id'
);
