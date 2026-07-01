"""Tests for EcosystemConfigPlanner — confirmation-gated plans."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from integrations.michi_ecosystem.ecosystem_config_planner import EcosystemConfigPlanner


def _mock_settings():
    s = MagicMock()
    s.get_str.return_value = ""
    return s


class TestConfigPlanner:
    def test_create_mobile_space_saver_plan(self):
        planner = EcosystemConfigPlanner(settings_manager=_mock_settings())
        plan = planner.create_plan("setup_mobile_space_saver_profile")
        assert plan.plan_id is not None
        assert len(plan.changes) > 0
        assert plan.requires_confirmation

    def test_create_micro_remote_plan(self):
        planner = EcosystemConfigPlanner(settings_manager=_mock_settings())
        plan = planner.create_plan("setup_micro_server_remote")
        assert plan.plan_id is not None
        assert plan.rollback_available

    def test_preview_plan(self):
        planner = EcosystemConfigPlanner(settings_manager=_mock_settings())
        plan = planner.create_plan("setup_mobile_sync")
        preview = planner.preview_plan(plan.plan_id)
        assert "error" not in preview
        assert preview.get("title") == "Configurar sincronizacion movil"

    def test_preview_nonexistent_plan(self):
        planner = EcosystemConfigPlanner()
        preview = planner.preview_plan("nonexistent")
        assert "error" in preview

    def test_apply_plan_requires_confirmation(self):
        planner = EcosystemConfigPlanner(settings_manager=_mock_settings())
        plan = planner.create_plan("setup_mobile_sync")
        result = planner.apply_plan(plan.plan_id, confirmed=False)
        assert not result.get("success", True)

    def test_apply_plan_confirmed(self):
        settings = _mock_settings()
        planner = EcosystemConfigPlanner(settings_manager=settings)
        plan = planner.create_plan("setup_mobile_sync")
        result = planner.apply_plan(plan.plan_id, confirmed=True)
        assert result.get("success")

    def test_rollback_plan_requires_confirmation(self):
        planner = EcosystemConfigPlanner(settings_manager=_mock_settings())
        plan = planner.create_plan("setup_mobile_sync")
        result = planner.rollback_plan(plan.plan_id, confirmed=False)
        assert not result.get("success", True)

    def test_rollback_plan_confirmed(self):
        settings = _mock_settings()
        planner = EcosystemConfigPlanner(settings_manager=settings)
        plan = planner.create_plan("setup_mobile_sync")
        result = planner.rollback_plan(plan.plan_id, confirmed=True)
        assert result.get("success")

    def test_plan_has_risks_and_tests(self):
        planner = EcosystemConfigPlanner(settings_manager=_mock_settings())
        plan = planner.create_plan("setup_mobile_sync")
        assert isinstance(plan.risks, list)
        assert isinstance(plan.tests, list)

    def test_list_plan_types(self):
        planner = EcosystemConfigPlanner()
        types = planner.list_plan_types()
        assert len(types) >= 4
        assert any(t["type"] == "setup_mobile_sync" for t in types)

    def test_unknown_plan_type(self):
        planner = EcosystemConfigPlanner()
        with pytest.raises(ValueError, match="Unknown plan type"):
            planner.create_plan("nonexistent_plan_type")
