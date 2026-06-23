"""Connection profile data model."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConnectionProfile:
    id: str = ""
    name: str = ""
    server_type: str = ""
    url: str = ""
    username: str = ""
    secret_ref: str = ""
    is_default: bool = False
    enabled: bool = True
    last_status: str = "unknown"
    capabilities: list[str] = field(default_factory=list)
    last_checked_at: str = ""
