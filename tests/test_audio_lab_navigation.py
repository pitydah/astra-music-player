"""Tests for Audio Lab hub, sub-pages, and navigation contracts.

No QApplication required — validates structure, constants, and imports.
"""

from __future__ import annotations


class TestAudioLabHubData:
    def test_hub_defines_five_sections(self):
        from ui.audio_lab.audio_lab_page import _SECTIONS

        assert len(_SECTIONS) == 5
        expected = {
            "audio_lab_diagnostics", "audio_lab_identifier",
            "audio_lab_backup", "audio_lab_output",
            "audio_lab_intelligence",
        }
        assert {s["key"] for s in _SECTIONS} == expected

    def test_every_section_has_required_fields(self):
        from ui.audio_lab.audio_lab_page import _SECTIONS

        required = {"key", "icon", "title", "subtitle", "status", "nav"}
        for sec in _SECTIONS:
            assert required.issubset(sec.keys()), f"{sec['key']} missing fields"

    def test_status_styles_cover_all_statuses(self):
        from ui.audio_lab.audio_lab_page import _STATUS_STYLES, _SECTIONS

        for sec in _SECTIONS:
            assert sec["status"] in _STATUS_STYLES, (
                f"'{sec['key']}' status '{sec['status']}' not in _STATUS_STYLES"
            )


class TestAudioLabSubPagesData:
    def test_sub_pages_module_imports_safely(self):
        from ui.audio_lab import sub_pages

        assert hasattr(sub_pages, "AudioLabIdentifierPage")
        assert hasattr(sub_pages, "AudioLabBackupPage")
        assert hasattr(sub_pages, "AudioLabDiagnosticsPage")
        assert hasattr(sub_pages, "AudioLabOutputPage")
        assert hasattr(sub_pages, "AudioLabIntelligencePage")




class TestAudioLabNavRoutes:
    def test_all_audio_lab_routes_in_nav_routes(self):
        from ui.controllers.navigation_controller import NAV_ROUTES

        for key in ("audio_lab", "audio_lab_diagnostics", "audio_lab_identifier",
                     "audio_lab_backup", "audio_lab_output",
                     "audio_lab_intelligence"):
            assert key in NAV_ROUTES, f"Missing NAV_ROUTES: {key}"

    def test_all_audio_lab_routes_have_section_config(self):
        from ui.controllers.navigation_controller import SECTION_CONFIG

        for key in ("audio_lab", "audio_lab_diagnostics", "audio_lab_identifier",
                     "audio_lab_backup", "audio_lab_output",
                     "audio_lab_intelligence"):
            assert key in SECTION_CONFIG, f"Missing SECTION_CONFIG: {key}"
            cfg = SECTION_CONFIG[key]
            assert "title" in cfg and "subtitle" in cfg and "icon" in cfg

    def test_audio_lab_hijos_mapped_to_sidebar_key(self):
        from ui.controllers.navigation_controller import resolve_sidebar_active_key

        for key in ("audio_lab_diagnostics", "audio_lab_identifier",
                     "audio_lab_backup", "audio_lab_output",
                     "audio_lab_intelligence"):
            assert resolve_sidebar_active_key(key) == "audio_lab"


class TestAudioLabNoCoreLeak:
    def test_no_context_repository_import_in_audio_lab(self):
        import os

        base = os.path.join(os.path.dirname(__file__), "..", "ui", "audio_lab")
        for root, _dirs, files in os.walk(os.path.abspath(base)):
            for f in files:
                if f.endswith(".py"):
                    with open(os.path.join(root, f)) as fh:
                        content = fh.read()
                    assert "context_repository" not in content, (
                        f"{os.path.join(root, f)} imports context_repository"
                    )
