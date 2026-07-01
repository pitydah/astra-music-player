"""Ecosystem health graph — build node/edge graphs from diagnostic reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from integrations.michi_ecosystem.sanitizer import sanitize_for_diagnostic


@dataclass
class EcosystemHealthNode:
    id: str
    label: str
    type: str
    status: str
    issue_code: str = ""


@dataclass
class EcosystemHealthEdge:
    source: str
    target: str
    protocol: str
    status: str
    issue_code: str = ""


@dataclass
class EcosystemHealthGraph:
    nodes: list[EcosystemHealthNode] = field(default_factory=list)
    edges: list[EcosystemHealthEdge] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


_EDGE_DEFS: list[tuple[str, str, str]] = [
    ("player", "mobile_sync", "michi_link"),
    ("player", "micro_server", "michi_link"),
    ("player", "remote_music_servers", "subsonic"),
    ("player", "home_audio", "http"),
    ("player", "assistant", "ollama"),
]


def build_health_graph(report: dict[str, Any]) -> EcosystemHealthGraph:
    nodes: list[EcosystemHealthNode] = []
    edges: list[EcosystemHealthEdge] = []
    statuses: dict[str, int] = {}

    for component_key, diag in report.items():
        if not isinstance(diag, dict):
            continue
        status = diag.get("status", diag.get("state", "unknown"))
        statuses[status] = statuses.get(status, 0) + 1
        nodes.append(EcosystemHealthNode(
            id=f"node:{component_key}",
            label=component_key.replace("_", " ").title(),
            type=diag.get("service", component_key),
            status=status,
            issue_code=diag.get("issue_code", ""),
        ))

    for source, target, protocol in _EDGE_DEFS:
        source_id = f"node:{source}"
        target_id = f"node:{target}"
        if any(n.id == source_id for n in nodes) and any(n.id == target_id for n in nodes):
            source_node = next(n for n in nodes if n.id == source_id)
            target_node = next(n for n in nodes if n.id == target_id)
            edge_status = "ok" if source_node.status == "ok" and target_node.status == "ok" else "warning"
            edges.append(EcosystemHealthEdge(
                source=source_id,
                target=target_id,
                protocol=protocol,
                status=edge_status,
            ))

    total = len(nodes)
    summary = {
        "total": total,
        "ok": statuses.get("ok", 0) + statuses.get("connected", 0) + statuses.get("active", 0),
        "warning": statuses.get("warning", 0) + statuses.get("unreachable", 0) + statuses.get("requires_pairing", 0),
        "error": statuses.get("error", 0),
        "unknown": statuses.get("unknown", 0) + statuses.get("not_configured", 0),
        "disabled": statuses.get("disabled", 0),
    }
    summary["overall"] = _overall(summary)

    return EcosystemHealthGraph(
        nodes=sanitize_for_diagnostic(nodes),
        edges=sanitize_for_diagnostic(edges),
        summary=sanitize_for_diagnostic(summary),
    )


def _overall(s: dict[str, int]) -> str:
    if s.get("error", 0) > 0:
        return "error"
    if s.get("warning", 0) > 0:
        return "warning"
    if s.get("ok", 0) == s.get("total", 0) and s.get("total", 0) > 0:
        return "ok"
    return "unknown"


def summarize_health(graph: EcosystemHealthGraph) -> dict[str, Any]:
    s = graph.summary
    if s.get("error", 0) > 0:
        overall = "error"
    elif s.get("warning", 0) > 0:
        overall = "warning"
    elif s.get("ok", 0) == s.get("total", 0) and s.get("total", 0) > 0:
        overall = "ok"
    else:
        overall = "unknown"
    return {"overall": overall, "total": s.get("total", 0), "ok": s.get("ok", 0), "warning": s.get("warning", 0), "error": s.get("error", 0), "disabled": s.get("disabled", 0)}
