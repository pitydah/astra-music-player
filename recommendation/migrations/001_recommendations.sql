-- Migration 001: Recommendation engine schema
-- Stores recommendation profiles, signals, cache, and feedback

CREATE TABLE IF NOT EXISTS recommendation_profile (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_name        TEXT DEFAULT 'default',
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now')),
    enabled             INTEGER DEFAULT 1,
    use_listening_history INTEGER DEFAULT 0,
    use_favorites       INTEGER DEFAULT 1,
    use_playlists       INTEGER DEFAULT 1,
    use_skips           INTEGER DEFAULT 0,
    use_quality_signals INTEGER DEFAULT 1,
    top_artists_json    TEXT DEFAULT '[]',
    top_genres_json     TEXT DEFAULT '[]',
    top_albums_json     TEXT DEFAULT '[]',
    preferred_years_json TEXT DEFAULT '[]',
    preferred_formats_json TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS track_signal (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    track_key           TEXT NOT NULL,
    signal_type         TEXT NOT NULL DEFAULT '',
    signal_value        REAL DEFAULT 1.0,
    source              TEXT DEFAULT '',
    timestamp           TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS recommendation_cache (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    recommendation_id   TEXT UNIQUE NOT NULL,
    seed_type           TEXT DEFAULT '',
    seed_value          TEXT DEFAULT '',
    strategy            TEXT DEFAULT '',
    created_at          TEXT DEFAULT (datetime('now')),
    expires_at          TEXT DEFAULT (datetime('now', '+7 days')),
    tracks_json         TEXT DEFAULT '[]',
    explanation_json    TEXT DEFAULT '[]',
    raw_score_json      TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS recommendation_feedback (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    recommendation_id   TEXT NOT NULL,
    track_key           TEXT NOT NULL DEFAULT '',
    feedback            TEXT DEFAULT '',
    timestamp           TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_track_signal_type ON track_signal(signal_type);
CREATE INDEX IF NOT EXISTS idx_track_signal_key ON track_signal(track_key);
CREATE INDEX IF NOT EXISTS idx_rec_cache_id ON recommendation_cache(recommendation_id);
CREATE INDEX IF NOT EXISTS idx_rec_feedback_id ON recommendation_feedback(recommendation_id);
