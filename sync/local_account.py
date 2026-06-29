"""LocalAccountManager — local owner account for Michi Sync authorization.

Stores hashed credentials in app data directory using atomic JSON writes.
Password is NEVER stored in plain text. Uses pbkdf2_hmac with random salt.
"""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
import time

from core.json_store import atomic_write_json, read_json_safe
from core.paths import app_data_dir

logger = logging.getLogger("michi.sync.local_account")

_ACCOUNT_FILE = os.path.join(app_data_dir(), "local_account.json")

_HASH_ALGORITHM = "pbkdf2_sha256"
_PBKDF2_ITERATIONS = 600_000
_SALT_BYTES = 32
_HASH_BYTES = 32


def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_bytes(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return dk.hex(), salt.hex()


class LocalAccountManager:
    def __init__(self, path: str = _ACCOUNT_FILE):
        self._path = path
        self._data: dict | None = None

    def _load(self) -> dict:
        if self._data is not None:
            return self._data
        raw = read_json_safe(self._path, default={}, backup_corrupt=True)
        self._data = raw if isinstance(raw, dict) else {}
        return self._data

    def _save(self):
        if self._data is None:
            return
        atomic_write_json(self._path, self._data)

    def exists(self) -> bool:
        return bool(self._load().get("password_hash"))

    def create(self, username: str, password: str) -> bool:
        if self.exists():
            return False
        pwh, salt_hex = _hash_password(password)
        self._data = {
            "username": username,
            "password_hash": pwh,
            "salt": salt_hex,
            "algorithm": _HASH_ALGORITHM,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self._save()
        logger.info("Local account created for user '%s'", username)
        return True

    def verify(self, password: str) -> bool:
        data = self._load()
        pwh = data.get("password_hash", "")
        salt_hex = data.get("salt", "")
        if not pwh or not salt_hex:
            return False
        salt = bytes.fromhex(salt_hex)
        expected, _ = _hash_password(password, salt)
        return secrets.compare_digest(pwh, expected)

    def change_password(self, old_password: str, new_password: str) -> bool:
        if not self.verify(old_password):
            return False
        pwh, salt_hex = _hash_password(new_password)
        self._data["password_hash"] = pwh
        self._data["salt"] = salt_hex
        self._data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._save()
        logger.info("Local account password changed")
        return True

    def get_username(self) -> str:
        return self._load().get("username", "")
