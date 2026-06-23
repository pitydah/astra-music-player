"""Credentials store — secure credential storage using system keyring."""

from __future__ import annotations

import logging

logger = logging.getLogger("michi.connections.credentials")

SERVICE_NAME = "michi-music-player"


class CredentialsStore:
    def __init__(self):
        self._keyring = self._init_keyring()
        self._fallback: dict[str, tuple[str, str]] = {}

    def _init_keyring(self):
        try:
            import keyring
            keyring.get_password("test", "test")
            return keyring
        except Exception:
            return None

    def store(self, profile_id: str, username: str, password: str):
        if self._keyring:
            try:
                self._keyring.set_password(SERVICE_NAME, f"{profile_id}:user", username)
                self._keyring.set_password(SERVICE_NAME, f"{profile_id}:pass", password)
                return
            except Exception as e:
                logger.debug("Keyring store failed: %s", e)
        self._fallback[profile_id] = (username, password)

    def retrieve(self, profile_id: str) -> tuple[str, str]:
        if self._keyring:
            try:
                user = self._keyring.get_password(SERVICE_NAME, f"{profile_id}:user") or ""
                pwd = self._keyring.get_password(SERVICE_NAME, f"{profile_id}:pass") or ""
                if user or pwd:
                    return (user, pwd)
            except Exception as e:
                logger.debug("Keyring retrieve failed: %s", e)
        return self._fallback.get(profile_id, ("", ""))

    def delete(self, profile_id: str):
        if self._keyring:
            try:
                self._keyring.delete_password(SERVICE_NAME, f"{profile_id}:user")
                self._keyring.delete_password(SERVICE_NAME, f"{profile_id}:pass")
            except Exception:
                pass
        self._fallback.pop(profile_id, None)

    def is_available(self) -> bool:
        return self._keyring is not None
