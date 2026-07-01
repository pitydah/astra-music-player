"""Section context provider for devices section (Michi Sync Suite)."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class DevicesContextProvider(SectionContextProvider):
    section_key = "devices"

    def __init__(self, db=None, device_registry=None, sync_controller=None):
        self._db = db
        self._device_registry = device_registry
        self._sync_controller = sync_controller

    def get_context(self) -> dict[str, Any]:
        return _build_devices_context(self._device_registry)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _devices_suggestions(self._device_registry)

    def get_allowed_actions(self) -> list[str]:
        return [
            "diagnose_mobile_sync",
            "diagnose_pairing",
            "create_ecosystem_config_plan",
            "open_section",
        ]


def _build_devices_context(device_registry) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "devices",
        "device_count": 0,
        "paired_devices": [],
    }
    if device_registry is None:
        return ctx
    try:
        if hasattr(device_registry, "list_all"):
            devices = device_registry.list_all()
            ctx["device_count"] = len(devices)
            safe = []
            for d in devices:
                safe.append({
                    "name": getattr(d, "name", ""),
                    "device_type": getattr(d, "device_type", ""),
                    "status": getattr(d, "status", "unknown"),
                })
            ctx["paired_devices"] = safe
    except Exception:
        pass
    return ctx


def _devices_suggestions(device_registry) -> list[dict[str, Any]]:
    suggestions = []
    ctx = _build_devices_context(device_registry)
    dc = ctx.get("device_count", 0)
    if dc == 0:
        suggestions.append({
            "id": "devices_no_paired",
            "title": "Emparejar dispositivo movil",
            "description": "No hay dispositivos emparejados. Conecta Michi Mobile para sincronizar.",
            "section": "devices",
            "action": "diagnose_mobile_sync",
            "args": {},
            "priority": "medium",
            "requires_confirmation": False,
            "reason": "device_count=0",
        })
    suggestions.append({
        "id": "devices_diagnose_sync",
        "title": "Diagnosticar sincronizacion",
        "description": "Revisa el estado del emparejamiento y los manifiestos.",
        "section": "devices",
        "action": "diagnose_mobile_sync",
        "args": {},
        "priority": "low",
        "requires_confirmation": False,
        "reason": "",
    })
    return suggestions[:5]
