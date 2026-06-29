"""Real Micro Server compatibility test — generates JSON report.

Usage:
    MICHI_MICRO_TEST_URL=192.168.1.100 MICHI_MICRO_TOKEN=abc \\
    MICHI_MICRO_DEVICE_ID=player_e2e \\
    MICHI_MICRO_PORT=53318 \\
    python -m pytest tests/e2e/test_real_micro_compatibility.py --real-micro -v

Requires the --real-micro flag. Without it, tests are skipped.
"""
from __future__ import annotations

import json
import os

import pytest

from integrations.michi_link.services.compatibility_report import (
    PlayerMicroCompatibilityReport,
)


def _skip_if_no_micro(micro_server_config):
    if micro_server_config is None:
        pytest.skip("Use --real-micro flag + MICHI_MICRO_TEST_URL env var")


class TestRealMicroCompatibility:
    """Runs PlayerMicroCompatibilityReport against a real Micro Server."""

    def test_report_generated(self, micro_server_config):
        _skip_if_no_micro(micro_server_config)
        report_service = PlayerMicroCompatibilityReport()
        result = report_service.generate(micro_server_config)
        assert isinstance(result, dict), "Report must be a dict"
        assert "server_info" in result
        assert "preflight" in result
        assert "upload_mapping" in result
        assert "commit_mapping" in result
        assert "queue_transfer" in result
        assert "remote_playback_confirmation" in result

    def test_report_saved_to_disk(self, micro_server_config):
        """Save the report to reports/player_micro_compatibility_report.json."""
        _skip_if_no_micro(micro_server_config)
        report_service = PlayerMicroCompatibilityReport()
        result = report_service.generate(micro_server_config)

        reports_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        report_path = os.path.join(reports_dir,
                                   "player_micro_compatibility_report.json")
        with open(report_path, "w") as f:
            json.dump(result, f, indent=2)
        assert os.path.exists(report_path), f"Report not saved to {report_path}"

    def test_supports_preflight(self, micro_server_config):
        _skip_if_no_micro(micro_server_config)
        report_service = PlayerMicroCompatibilityReport()
        result = report_service.check_preflight(micro_server_config)
        assert "status" in result

    def test_supports_upload_mapping(self, micro_server_config):
        _skip_if_no_micro(micro_server_config)
        report_service = PlayerMicroCompatibilityReport()
        result = report_service.check_upload_mapping(micro_server_config)
        assert "status" in result

    def test_supports_commit_mapping(self, micro_server_config):
        _skip_if_no_micro(micro_server_config)
        report_service = PlayerMicroCompatibilityReport()
        result = report_service.check_commit_mapping(micro_server_config)
        assert "status" in result

    def test_supports_queue_transfer(self, micro_server_config):
        _skip_if_no_micro(micro_server_config)
        report_service = PlayerMicroCompatibilityReport()
        result = report_service.check_queue_transfer(micro_server_config)
        assert "status" in result

    def test_remote_playback_confirmation(self, micro_server_config):
        _skip_if_no_micro(micro_server_config)
        report_service = PlayerMicroCompatibilityReport()
        result = report_service.check_remote_playback_confirmation(
            micro_server_config)
        assert "status" in result
