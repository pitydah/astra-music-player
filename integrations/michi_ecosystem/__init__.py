"""Michi Ecosystem Manager — facade over existing Michi Link services."""

from integrations.michi_ecosystem import constants
from integrations.michi_ecosystem.ecosystem_doctor import MichiEcosystemDoctor
from integrations.michi_ecosystem.health_graph import build_health_graph, summarize_health, EcosystemHealthNode, EcosystemHealthEdge, EcosystemHealthGraph
from integrations.michi_ecosystem.fix_suggester import suggest_fix, suggest_next_steps
from integrations.michi_ecosystem.config_planner import EcosystemConfigPlanner, ConfigPlan, ConfigChange
from integrations.michi_ecosystem.sanitizer import sanitize_for_diagnostic, sanitize_report
from integrations.michi_ecosystem.ecosystem_actions import SAFE_ACTIONS, CONFIRMABLE_ACTIONS, is_action_safe, is_action_confirmable, is_action_allowed

