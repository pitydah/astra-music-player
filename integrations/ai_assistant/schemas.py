"""Type schemas for Michi AI Assistant."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class PermissionLevel(Enum):
    READ_ONLY = auto()
    REVERSIBLE = auto()
    SENSITIVE = auto()
    FORBIDDEN = auto()
    RESOURCE_INTENSIVE = auto()


@dataclass(slots=True)
class ConversationTurn:
    role: str
    content: str
    tool_name: str | None = None
    tool_result: dict | None = None


@dataclass(slots=True)
class ToolCall:
    name: str
    args: dict = field(default_factory=dict)
    permission: PermissionLevel = PermissionLevel.READ_ONLY


@dataclass(slots=True)
class ToolResult:
    name: str
    success: bool
    data: dict | list | None = None
    error: str = ""
    permission_denied: bool = False


@dataclass(slots=True)
class PendingAction:
    action_id: str
    tool_name: str
    title: str
    description: str = ""
    arguments: dict = field(default_factory=dict)
    preview: dict = field(default_factory=dict)
    permission_level: str = ""
    created_at: float = 0.0
    expires_at: float = 0.0
    requires_confirmation: bool = True
