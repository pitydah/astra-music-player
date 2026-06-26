"""SQLite utilities — common connection, pragmas, migrations for auxiliary DBs."""

import logging
import sqlite3

logger = logging.getLogger("michi.sqlite_utils")


def open_sqlite(path: str, wal: bool = True, busy_timeout_ms: int = 5000) -> sqlite3.Connection:
    """Open a SQLite connection with safe defaults."""
    conn = sqlite3.connect(path)
    if wal:
        conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(f"PRAGMA busy_timeout={busy_timeout_ms}")
    return conn


def apply_pragmas(conn: sqlite3.Connection):
    """Apply standard pragmas to an existing connection."""
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")


def close_quietly(conn: sqlite3.Connection | None):
    """Close a connection without raising errors."""
    if conn:
        with __import__("contextlib").suppress(sqlite3.Error):
            conn.close()


def get_user_version(conn: sqlite3.Connection) -> int:
    """Read PRAGMA user_version."""
    return conn.execute("PRAGMA user_version").fetchone()[0]


def set_user_version(conn: sqlite3.Connection, version: int):
    """Set PRAGMA user_version."""
    conn.execute(f"PRAGMA user_version={version}")
    conn.commit()


def run_migrations(conn: sqlite3.Connection, migrations: list[tuple[int, list[str]]]):
    """Apply SQL migrations sequentially based on user_version."""
    current = get_user_version(conn)
    for ver, statements in sorted(migrations, key=lambda x: x[0]):
        if ver <= current:
            continue
        try:
            for stmt in statements:
                conn.execute(stmt)
            set_user_version(conn, ver)
            logger.info("Migration %d applied to %s", ver, "DB")
        except sqlite3.Error as e:
            logger.warning("Migration %d failed: %s", ver, e)
            break
