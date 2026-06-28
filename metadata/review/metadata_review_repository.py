"""Metadata review repository — SQLite storage for proposals and review actions."""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import contextlib

from metadata.review.schemas import (
    MetadataFieldChange,
    MetadataProposal,
    MetadataReview,
)

logger = logging.getLogger("michi.metadata.review_repository")


def _synchronized(method):
    """Decorator to acquire the instance lock before calling the method."""
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper


def _default_db_path() -> str:
    from core.paths import metadata_review_db_path
    return metadata_review_db_path()


class MetadataReviewRepository:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            db_path = _default_db_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("""CREATE TABLE IF NOT EXISTS metadata_proposal (
            proposal_id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL DEFAULT '',
            entity_id TEXT DEFAULT '',
            track_id INTEGER DEFAULT 0,
            album_key TEXT DEFAULT '',
            artist_name TEXT DEFAULT '',
            title TEXT DEFAULT '',
            changes_json TEXT DEFAULT '[]',
            source_summary_json TEXT DEFAULT '{}',
            confidence REAL DEFAULT 0.0,
            created_at TEXT DEFAULT (datetime('now')),
            status TEXT DEFAULT 'pending'
        )""")
        self._conn.execute("""CREATE TABLE IF NOT EXISTS metadata_review (
            review_id TEXT PRIMARY KEY,
            created_at TEXT DEFAULT (datetime('now')),
            status TEXT DEFAULT 'pending',
            apply_target TEXT DEFAULT 'local_db',
            reversible INTEGER DEFAULT 1,
            proposals_json TEXT DEFAULT '[]'
        )""")
        self._conn.execute("""CREATE TABLE IF NOT EXISTS metadata_review_action (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id TEXT NOT NULL,
            timestamp TEXT DEFAULT (datetime('now')),
            action TEXT DEFAULT '',
            status TEXT DEFAULT '',
            summary TEXT DEFAULT '',
            raw_json TEXT DEFAULT '{}'
        )""")
        self._conn.execute("""CREATE TABLE IF NOT EXISTS metadata_undo_stack (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id TEXT NOT NULL,
            track_id INTEGER DEFAULT 0,
            field TEXT DEFAULT '',
            old_value TEXT DEFAULT '',
            applied_at TEXT DEFAULT (datetime('now'))
        )""")
        self._conn.commit()

    @staticmethod
    def _proposal_to_row(proposal):
        changes_json = json.dumps([
            {"field": c.field, "current_value": c.current_value,
             "suggested_value": c.suggested_value, "source": c.source,
             "confidence": c.confidence, "reason": c.reason, "accepted": c.accepted}
            for c in proposal.changes
        ], ensure_ascii=False)
        return (proposal.proposal_id, proposal.entity_type, proposal.entity_id,
                proposal.track_id, proposal.album_key, proposal.artist_name,
                proposal.title, changes_json,
                json.dumps(proposal.source_summary, ensure_ascii=False),
                proposal.confidence, proposal.created_at, proposal.status)

    @_synchronized
    def save_proposal(self, proposal: MetadataProposal):
        self._save_proposal_inline(proposal)
        self._conn.commit()

    def _save_proposal_inline(self, proposal: MetadataProposal):
        self._conn.execute(
            """INSERT OR REPLACE INTO metadata_proposal
            (proposal_id, entity_type, entity_id, track_id, album_key,
             artist_name, title, changes_json, source_summary_json,
             confidence, created_at, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            self._proposal_to_row(proposal),
        )

    @_synchronized
    def load_proposal(self, proposal_id: str) -> MetadataProposal | None:
        row = self._conn.execute(
            "SELECT * FROM metadata_proposal WHERE proposal_id=?", (proposal_id,)
        ).fetchone()
        return self._row_to_proposal(row)

    @_synchronized
    def list_proposals(self, limit: int = 50) -> list[MetadataProposal]:
        rows = self._conn.execute(
            "SELECT * FROM metadata_proposal ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._row_to_proposal(r) for r in rows if r]

    @staticmethod
    def _row_to_proposal(row) -> MetadataProposal | None:
        if not row:
            return None
        changes_raw = json.loads(row[7] or "[]")
        changes = [MetadataFieldChange(**c) for c in changes_raw]
        return MetadataProposal(
            proposal_id=row[0], entity_type=row[1], entity_id=row[2],
            track_id=row[3], album_key=row[4], artist_name=row[5],
            title=row[6], changes=changes,
            source_summary=json.loads(row[8] or "{}"),
            confidence=row[9], created_at=row[10], status=row[11],
        )

    @_synchronized
    def update_proposal_status(self, proposal_id: str, status: str):
        self._conn.execute(
            "UPDATE metadata_proposal SET status=? WHERE proposal_id=?",
            (status, proposal_id),
        )
        self._conn.commit()

    @_synchronized
    def save_review(self, review: MetadataReview):
        try:
            self._conn.execute("BEGIN")
            self._conn.execute(
                """INSERT OR REPLACE INTO metadata_review
                (review_id, created_at, status, apply_target, reversible, proposals_json)
                VALUES (?,?,?,?,?,?)""",
                (review.review_id, review.created_at, review.status,
                 review.apply_target, int(review.reversible),
                 json.dumps([p.proposal_id for p in review.proposals], ensure_ascii=False)),
            )
            for proposal in review.proposals:
                self._save_proposal_inline(proposal)
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    @_synchronized
    def load_review(self, review_id: str) -> MetadataReview | None:
        row = self._conn.execute(
            "SELECT * FROM metadata_review WHERE review_id=?", (review_id,)
        ).fetchone()
        if not row:
            return None
        pids = json.loads(row[5] or "[]")
        if pids:
            placeholders = ",".join(["?"] * len(pids))
            prop_rows = self._conn.execute(
                f"SELECT * FROM metadata_proposal WHERE proposal_id IN ({placeholders})",
                pids,
            ).fetchall()
            prop_map = {r[0]: self._row_to_proposal(r) for r in prop_rows if r}
            proposals = [prop_map[pid] for pid in pids if pid in prop_map and prop_map[pid]]
        else:
            proposals = []
        return MetadataReview(
            review_id=row[0], created_at=row[1], status=row[2],
            apply_target=row[3], reversible=bool(row[4]),
            proposals=proposals,
        )

    @_synchronized
    def log_action(self, review_id: str, action: str, status: str = "",
                   summary: str = "", raw: dict | None = None):
        raw_safe = json.dumps(raw or {}, ensure_ascii=False)
        self._conn.execute(
            "INSERT INTO metadata_review_action (review_id, action, status, summary, raw_json) VALUES (?,?,?,?,?)",
            (review_id, action, status, summary, raw_safe),
        )
        self._conn.commit()

    @_synchronized
    def save_undo(self, review_id: str, track_id: int, field: str, old_value: str):
        self._conn.execute(
            "INSERT INTO metadata_undo_stack (review_id, track_id, field, old_value) VALUES (?,?,?,?)",
            (review_id, track_id, field, old_value),
        )
        self._conn.commit()

    @_synchronized
    def get_undo_stack(self, review_id: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT track_id, field, old_value FROM metadata_undo_stack WHERE review_id=? ORDER BY id",
            (review_id,),
        ).fetchall()
        return [{"track_id": r[0], "field": r[1], "old_value": r[2]} for r in rows]

    @_synchronized
    def clear_undo(self, review_id: str):
        self._conn.execute("DELETE FROM metadata_undo_stack WHERE review_id=?", (review_id,))
        self._conn.commit()

    @_synchronized
    def close(self):
        with contextlib.suppress(Exception):
            self._conn.rollback()
        self._conn.close()
