"""Tests for Audio Lab hub, sub-pages, and navigation routing.

These tests validate structure, constants, and navigation contracts
without requiring a QApplication (no widget instantiation).
"""

from __future__ import annotations


# ── Hub page data tests (no widget instantiation) ──

class TestAudioLabHubData:
    def test_hub_defines_five_sections(self):
        from ui.audio_lab.audio_lab_page import _SECTIONS

        assert len(_SECTIONS) == 5

        expected_keys = {
            "audio_lab_diagnostics", "audio_lab_identifier",
            "audio_lab_backup", "audio_lab_output",
            "audio_lab_intelligence",
        }
        found_keys = {s["key"] for s in _SECTIONS}
        assert found_keys == expected_keys

    def test_every_section_has_required_fields(self):
        from ui.audio_lab.audio_lab_page import _SECTIONS

        required = {"key", "icon", "title", "subtitle", "status", "nav"}
        for sec in _SECTIONS:
            assert required.issubset(sec.keys()), f"{sec['key']} missing fields"

    def test_status_styles_cover_all_section_statuses(self):
        from ui.audio_lab.audio_lab_page import _STATUS_STYLES
        from ui.audio_lab.audio_lab_page import _SECTIONS

        for sec in _SECTIONS:
            assert sec["status"] in _STATUS_STYLES, (
                f"Section '{sec['key']}' has unknown status '{sec['status']}'"
            )


# ── Sub-page data tests (no widget instantiation) ──

class TestAudioLabSubPagesData:
    def test_sub_pages_module_imports_safely(self):
        from ui.audio_lab import sub_pages

        assert hasattr(sub_pages, "AudioLabIdentifierPage")
        assert hasattr(sub_pages, "AudioLabBackupPage")
        assert hasattr(sub_pages, "AudioLabDiagnosticsPage")
        assert hasattr(sub_pages, "AudioLabOutputPage")
        assert hasattr(sub_pages, "AudioLabIntelligencePage")

    def test_identifier_sub_cards_and_backup_sub_cards_importable(self):
        from ui.audio_lab.sub_pages import AudioLabIdentifierPage
        from ui.audio_lab.sub_pages import AudioLabBackupPage

        assert AudioLabIdentifierPage is not None
        assert AudioLabBackupPage is not None


# ── NAV_ROUTES integrity tests ──

class TestAudioLabNavRoutes:
    def test_all_audio_lab_routes_exist_in_nav_routes(self):
        from ui.controllers.navigation_controller import NAV_ROUTES

        expected = {
            "audio_lab", "audio_lab_diagnostics", "audio_lab_identifier",
            "audio_lab_backup", "audio_lab_output", "audio_lab_intelligence",
        }
        for key in expected:
            assert key in NAV_ROUTES, f"Missing NAV_ROUTES entry: {key}"

    def test_all_audio_lab_routes_have_section_config(self):
        from ui.controllers.navigation_controller import SECTION_CONFIG

        expected = {
            "audio_lab", "audio_lab_diagnostics", "audio_lab_identifier",
            "audio_lab_backup", "audio_lab_output", "audio_lab_intelligence",
        }
        for key in expected:
            assert key in SECTION_CONFIG, f"Missing SECTION_CONFIG entry: {key}"
            cfg = SECTION_CONFIG[key]
            assert "title" in cfg
            assert "subtitle" in cfg
            assert "icon" in cfg

    def test_audio_lab_michi_disc_lab_section_exists(self):
        from ui.controllers.navigation_controller import (
            SECTION_CONFIG, NAV_ROUTES,
        )

        assert "michi_disc_lab" in SECTION_CONFIG
        assert "michi_disc_lab" in NAV_ROUTES


# ── No context_repository import guard ──

class TestAudioLabNoCoreLeak:
    def test_no_context_repository_import_in_audio_lab(self):
        import os

        audio_lab_dir = os.path.join(
            os.path.dirname(__file__), "..", "ui", "audio_lab"
        )
        audio_lab_dir = os.path.abspath(audio_lab_dir)

        for root, _dirs, files in os.walk(audio_lab_dir):
            for f in files:
                if f.endswith(".py"):
                    filepath = os.path.join(root, f)
                    with open(filepath) as fh:
                        content = fh.read()
                    assert "context_repository" not in content, (
                        f"{filepath} imports context_repository"
                    )
