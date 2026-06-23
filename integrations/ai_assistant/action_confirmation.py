"""Pending action store — confirmation-gated reversible actions for Michi Assistant."""

from __future__ import annotations

import time
import uuid

from integrations.ai_assistant.schemas import PendingAction


class PendingActionStore:
    def __init__(self, ttl_seconds: int = 120):
        self._actions: dict[str, PendingAction] = {}
        self._ttl = ttl_seconds

    def create(self, tool_name: str, title: str, description: str = "",
               arguments: dict | None = None, preview: dict | None = None,
               permission_level: str = "REVERSIBLE",
               requires_confirmation: bool = True) -> PendingAction:
        self._expire_old()
        action_id = str(uuid.uuid4())[:12]
        now = time.time()
        action = PendingAction(
            action_id=action_id,
            tool_name=tool_name,
            title=title,
            description=description,
            arguments=arguments or {},
            preview=preview or {},
            permission_level=permission_level,
            created_at=now,
            expires_at=now + self._ttl,
            requires_confirmation=requires_confirmation,
        )
        self._actions[action_id] = action
        return action

    def get(self, action_id: str) -> PendingAction | None:
        self._expire_old()
        return self._actions.get(action_id)

    def remove(self, action_id: str):
        self._actions.pop(action_id, None)

    def list_all(self) -> list[PendingAction]:
        self._expire_old()
        return list(self._actions.values())

    def clear(self):
        self._actions.clear()

    def _expire_old(self):
        now = time.time()
        expired = [aid for aid, a in self._actions.items()
                   if a.expires_at < now]
        for aid in expired:
            del self._actions[aid]

    @property
    def count(self) -> int:
        self._expire_old()
        return len(self._actions)
