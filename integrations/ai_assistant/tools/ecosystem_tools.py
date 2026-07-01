"""Ecosystem tools for AI Assistant — diagnose, plan, and fix the Michi ecosystem."""

from __future__ import annotations

from typing import Any

from integrations.ai_assistant.schemas import ToolResult
from integrations.michi_ecosystem.ecosystem_diagnostics import EcosystemDiagnostics
from integrations.michi_ecosystem.ecosystem_fix_suggester import EcosystemFixSuggester
from integrations.michi_ecosystem.ecosystem_config_planner import EcosystemConfigPlanner
from integrations.michi_ecosystem.ecosystem_registry import EcosystemRegistry

_diag: EcosystemDiagnostics | None = None
_suggester: EcosystemFixSuggester | None = None
_planner: EcosystemConfigPlanner | None = None


def _setup(diagnostics_service=None, micro_server_service=None, sync_manager=None, device_registry=None, settings_manager=None):
    global _diag, _suggester, _planner
    _diag = EcosystemDiagnostics(registry=EcosystemRegistry(device_registry=device_registry, sync_manager=sync_manager, settings_manager=settings_manager), diagnostics_service=diagnostics_service, micro_server_service=micro_server_service, sync_manager=sync_manager)
    _suggester = EcosystemFixSuggester()
    _planner = EcosystemConfigPlanner(settings_manager=settings_manager)


def diagnose_ecosystem(db=None, **kwargs) -> ToolResult:
    if _diag is None:
        _setup()
    try:
        report = _diag.diagnose_ecosystem(**kwargs)
        return ToolResult(name="diagnose_ecosystem", success=True, data={"message": _format_ecosystem_summary(report), "report": report, "summary": report.get("summary", {})})
    except Exception as e:
        return ToolResult(name="diagnose_ecosystem", success=False, error=str(e))


def diagnose_mobile_sync(db=None, **kwargs) -> ToolResult:
    if _diag is None:
        _setup()
    try:
        result = _diag.diagnose_mobile_sync(**kwargs)
        return ToolResult(name="diagnose_mobile_sync", success=True, data={"message": _format_mobile_sync_result(result), "diagnosis": result})
    except Exception as e:
        return ToolResult(name="diagnose_mobile_sync", success=False, error=str(e))


def diagnose_micro_server(db=None, host: str = "", port: int = 53318, **kwargs) -> ToolResult:
    if _diag is None:
        _setup()
    try:
        result = _diag.diagnose_micro_server(host=host, port=port, **kwargs)
        return ToolResult(name="diagnose_micro_server", success=True, data={"message": _format_micro_server_result(result), "diagnosis": result})
    except Exception as e:
        return ToolResult(name="diagnose_micro_server", success=False, error=str(e))


def diagnose_home_audio(db=None, **kwargs) -> ToolResult:
    if _diag is None:
        _setup()
    try:
        result = _diag.diagnose_home_audio(**kwargs)
        return ToolResult(name="diagnose_home_audio", success=True, data={"message": result.get("message", ""), "diagnosis": result})
    except Exception as e:
        return ToolResult(name="diagnose_home_audio", success=False, error=str(e))


def suggest_ecosystem_fix(db=None, issue_code: str = "", report: dict | None = None, **kwargs) -> ToolResult:
    if _suggester is None:
        _setup()
    try:
        if issue_code:
            fix = _suggester.suggest_next_steps(issue_code)
        elif report:
            fix = _suggester.suggest_fix(report)
        else:
            fix = {"problem": "No se proporciono codigo de error ni reporte."}
        return ToolResult(name="suggest_ecosystem_fix", success=True, data={"message": fix.get("recommended_fix", fix.get("problem", "")), "fix": fix})
    except Exception as e:
        return ToolResult(name="suggest_ecosystem_fix", success=False, error=str(e))


def create_ecosystem_config_plan(db=None, plan_type: str = "", context: dict | None = None, **kwargs) -> ToolResult:
    if _planner is None:
        _setup()
    try:
        plan = _planner.create_plan(plan_type, context)
        return ToolResult(name="create_ecosystem_config_plan", success=True, data={"message": f"Plan '{plan.title}' creado (ID: {plan.plan_id}). Requiere confirmacion.", "plan_id": plan.plan_id, "plan": {"title": plan.title, "description": plan.description, "changes": [{"key": c.key, "description": c.description, "risk": c.risk} for c in plan.changes]}})
    except ValueError as e:
        available = _planner.list_plan_types() if _planner else []
        return ToolResult(name="create_ecosystem_config_plan", success=True, data={"message": f"Tipo de plan no valido. Planos disponibles: {[p['type'] for p in available]}", "available_plans": available})
    except Exception as e:
        return ToolResult(name="create_ecosystem_config_plan", success=False, error=str(e))


def preview_ecosystem_config_plan(db=None, plan_id: str = "", **kwargs) -> ToolResult:
    if _planner is None:
        _setup()
    try:
        preview = _planner.preview_plan(plan_id)
        return ToolResult(name="preview_ecosystem_config_plan", success=True, data={"message": _format_plan_preview(preview), "preview": preview})
    except Exception as e:
        return ToolResult(name="preview_ecosystem_config_plan", success=False, error=str(e))


def apply_ecosystem_config_plan(db=None, plan_id: str = "", confirmed: bool = False, **kwargs) -> ToolResult:
    if not confirmed:
        return ToolResult(name="apply_ecosystem_config_plan", success=False, data={"error": "Permiso denegado. Se requiere confirmacion explicita para aplicar el plan."}, permission_denied=True)
    if _planner is None:
        _setup()
    try:
        result = _planner.apply_plan(plan_id, confirmed=True)
        return ToolResult(name="apply_ecosystem_config_plan", success=result.get("success", False), data=result)
    except Exception as e:
        return ToolResult(name="apply_ecosystem_config_plan", success=False, error=str(e))


def rollback_ecosystem_config_plan(db=None, plan_id: str = "", confirmed: bool = False, **kwargs) -> ToolResult:
    if not confirmed:
        return ToolResult(name="rollback_ecosystem_config_plan", success=False, data={"error": "Permiso denegado. Se requiere confirmacion explicita para revertir el plan."}, permission_denied=True)
    if _planner is None:
        _setup()
    try:
        result = _planner.rollback_plan(plan_id, confirmed=True)
        return ToolResult(name="rollback_ecosystem_config_plan", success=result.get("success", False), data=result)
    except Exception as e:
        return ToolResult(name="rollback_ecosystem_config_plan", success=False, error=str(e))


def _format_ecosystem_summary(report: dict) -> str:
    summary = report.get("summary", {})
    total = summary.get("total_services", 0)
    player = report.get("player", {}).get("status", "?")
    mobile = report.get("mobile_sync", {}).get("status", "?")
    micro = report.get("micro_server", {}).get("status", "?")
    parts = [f"Ecosistema: {total} servicio(s)", f"Player: {player}", f"Mobile Sync: {mobile}", f"Micro Server: {micro}"]
    return " . ".join(parts)


def _format_mobile_sync_result(result: dict) -> str:
    status = result.get("status", "desconocido")
    count = result.get("paired_devices", 0)
    active = result.get("sync_active", False)
    parts = [f"Estado: {status}", f"Dispositivos emparejados: {count}", f"Sync activo: {'Si' if active else 'No'}"]
    return " . ".join(parts)


def _format_micro_server_result(result: dict) -> str:
    status = result.get("status", "desconocido")
    host = result.get("host", "")
    port = result.get("port", 53318)
    parts = [f"Estado: {status}"]
    if host:
        parts.append(f"Host: {host}:{port}")
    return " . ".join(parts)


def _format_plan_preview(preview: dict) -> str:
    if "error" in preview:
        return preview["error"]
    changes = preview.get("changes", [])
    parts = [f"Plan: {preview.get('title', '?')}"]
    for c in changes:
        parts.append(f"  . {c.get('description', '?')}: {c.get('current_value')} -> {c.get('proposed_value')} ({c.get('risk', '?')})")
    risks = preview.get("risks", [])
    if risks:
        parts.append(f"Riesgos: {', '.join(risks)}")
    return "\n".join(parts)
