-- Migration 001: Audio analysis schema
-- Stores audio features, analysis jobs, similarity cache, and settings

CREATE TABLE IF NOT EXISTS audio_feature (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    track_key           TEXT UNIQUE NOT NULL,
    duration            REAL DEFAULT 0.0,
    bpm                 REAL DEFAULT 0.0,
    bpm_confidence      REAL DEFAULT 0.0,
    energy              REAL DEFAULT 0.0,
    dynamic_range       REAL DEFAULT 0.0,
    spectral_centroid   REAL DEFAULT 0.0,
    spectral_rolloff    REAL DEFAULT 0.0,
    zero_crossing_rate  REAL DEFAULT 0.0,
    mfcc_json           TEXT DEFAULT '[]',
    chroma_json         TEXT DEFAULT '[]',
    backend             TEXT DEFAULT '',
    status              TEXT DEFAULT 'pending',
    error               TEXT DEFAULT '',
    analyzed_at         TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audio_similarity_cache (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    seed_track_key  TEXT NOT NULL,
    strategy        TEXT NOT NULL DEFAULT '',
    result_json     TEXT DEFAULT '[]',
    created_at      TEXT DEFAULT (datetime('now')),
    expires_at      TEXT DEFAULT (datetime('now', '+7 days'))
);

CREATE TABLE IF NOT EXISTS audio_analysis_job (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id          TEXT UNIQUE NOT NULL,
    track_key       TEXT NOT NULL DEFAULT '',
    status          TEXT DEFAULT 'pending',
    priority        INTEGER DEFAULT 5,
    created_at      TEXT DEFAULT (datetime('now')),
    started_at      TEXT DEFAULT '',
    finished_at     TEXT DEFAULT '',
    error           TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS audio_analysis_settings (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    key     TEXT UNIQUE NOT NULL,
    value   TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_audio_feat_key ON audio_feature(track_key);
CREATE INDEX IF NOT EXISTS idx_audio_feat_bpm ON audio_feature(bpm);
CREATE INDEX IF NOT EXISTS idx_audio_feat_energy ON audio_feature(energy);
CREATE INDEX IF NOT EXISTS idx_audio_cache_seed ON audio_similarity_cache(seed_track_key);
CREATE INDEX IF NOT EXISTS idx_audio_job_status ON audio_analysis_job(status);
