"""Tests for library navigation contract."""
from ui.controllers.navigation_controller import (
    resolve_sidebar_active_key, SECTION_CONFIG, NAV_ROUTES,
)


class TestRoutes:
    def test_routes_exist(self):
        for k in ("library", "albums", "artists", "genres", "folders"):
            assert k in NAV_ROUTES

    def test_configs_exist(self):
        for k in ("library", "albums", "artists", "genres", "folders", "library_hub"):
            assert k in SECTION_CONFIG


class TestSidebarKey:
    def test_hub(self):
        assert resolve_sidebar_active_key("library_hub") == "library_hub"

    def test_library(self):
        assert resolve_sidebar_active_key("library") == "library_hub"

    def test_albums(self):
        assert resolve_sidebar_active_key("albums") == "library_hub"

    def test_genres(self):
        assert resolve_sidebar_active_key("genres") == "genres"

    def test_folders(self):
        assert resolve_sidebar_active_key("folders") == "library_hub"
