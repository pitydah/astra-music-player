"""EcosystemHealthGraph — build and summarize a health graph from diagnostic reports."""

from __future__ import annotations

from typing import Any

from integrations.michi_ecosystem.ecosystem_models import EcosystemEdge, EcosystemHealthGraph, EcosystemNode


class EcosystemHealthGraphBuilder:
    def __init__(self):
        pass

    def build(self, report: dict[str, Any]) -> EcosystemHealthGraph:
        nodes: list[EcosystemNode] = []
        edges: list[EcosystemEdge] = []
        statuses = {"ok": 0, "warning": 0, "error": 0, "unknown": 0}
        for service_key, diag in report.items():
            if service_key == "summary":
                continue
            if not isinstance(diag, dict):
                continue
            status = diag.get("status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1
            node = EcosystemNode(id=f"node:{service_key}", type=diag.get("service", service_key), label=service_key.replace("_", " ").title(), status=status, issue_code=diag.get("issue_code", ""), last_checked="")
            nodes.append(node)
            if service_key in ("mobile_sync", "micro_server"):
                edges.append(EcosystemEdge(source="node:player", target=f"node:{service_key}", protocol="michi_link", status=status))
        summary = {"total": len(nodes), "ok": statuses.get("ok", 0), "warning": statuses.get("warning", 0), "error": statuses.get("error", 0), "unknown": statuses.get("unknown", 0)}
        return EcosystemHealthGraph(nodes=nodes, edges=edges, summary=summary)

    def summarize_health(self, graph: EcosystemHealthGraph) -> dict[str, Any]:
        s = graph.summary
        if s.get("error", 0) > 0:
            overall = "error"
        elif s.get("warning", 0) > 0:
            overall = "warning"
        elif s.get("ok", 0) == s.get("total", 0) and s.get("total", 0) > 0:
            overall = "ok"
        else:
            overall = "unknown"
        return {"overall": overall, "total": s.get("total", 0), "ok": s.get("ok", 0), "warning": s.get("warning", 0), "error": s.get("error", 0), "unknown": s.get("unknown", 0)}
