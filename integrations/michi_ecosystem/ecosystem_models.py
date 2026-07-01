"""Data models for the Michi Ecosystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EcosystemService:
    id: str
    name: str
    type: str
    host: str = ""
    port: int = 0
    protocol: str = "michi_link"
    paired: bool = False
    last_seen: str = ""
    capabilities: dict[str, Any] = field(default_factory=dict)
    status: str = "unknown"
    issue_code: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EcosystemNode:
    id: str
    type: str
    label: str
    status: str
    issue_code: str = ""
    suggested_fix: str = ""
    last_checked: str = ""


@dataclass
class EcosystemEdge:
    source: str
    target: str
    protocol: str
    status: str
    issue_code: str = ""
    latency_ms: float | None = None


@dataclass
class EcosystemHealthGraph:
    nodes: list[EcosystemNode] = field(default_factory=list)
    edges: list[EcosystemEdge] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigChange:
    key: str
    current_value: Any
    proposed_value: Any
    description: str
    risk: str = "low"
    requires_confirmation: bool = True


@dataclass
class EcosystemConfigPlan:
    plan_id: str
    title: str
    description: str
    changes: list[ConfigChange] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    requires_confirmation: bool = True
    rollback_available: bool = True
