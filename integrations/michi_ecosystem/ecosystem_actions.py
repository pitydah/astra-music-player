"""EcosystemActions — safe actions that can be executed with or without confirmation."""

from __future__ import annotations


SAFE_ACTIONS = frozenset({"open_section", "diagnose_ecosystem", "diagnose_mobile_sync", "diagnose_micro_server", "diagnose_home_audio", "get_ecosystem_health_summary", "suggest_fix"})

CONFIRMABLE_ACTIONS = frozenset({"apply_config_plan", "rollback_config_plan", "retry_pairing", "retry_micro_discovery", "activate_sync"})


def is_action_safe(action: str) -> bool:
    return action in SAFE_ACTIONS


def is_action_confirmable(action: str) -> bool:
    return action in CONFIRMABLE_ACTIONS


def is_action_allowed(action: str) -> bool:
    return action in SAFE_ACTIONS or action in CONFIRMABLE_ACTIONS
