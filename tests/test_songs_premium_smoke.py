"""Tests: Smoke imports for all Songs Premium modules."""


class TestSongsPremiumSmoke:

    def test_import_mediaitem_table_model(self):
        from library.mediaitem_table_model import MediaItemTableModel
        assert MediaItemTableModel is not None

    def test_import_songs_query_service(self):
        from library.songs_query_service import SongsQueryService
        assert SongsQueryService is not None

    def test_import_songs_status_service(self):
        from library.songs_status_service import SongsStatusService
        assert SongsStatusService is not None

    def test_import_songs_controller(self):
        from ui.controllers.songs_controller import SongsController
        assert SongsController is not None

    def test_import_songs_premium_page(self):
        from ui.library.songs_premium_page import SongsPremiumPage
        assert SongsPremiumPage is not None

    def test_import_filter_bar(self):
        from ui.library.songs_filter_bar import SongsFilterBar
        assert SongsFilterBar is not None

    def test_import_bulk_action_bar(self):
        from ui.library.songs_bulk_action_bar import SongsBulkActionBar
        assert SongsBulkActionBar is not None

    def test_import_detail_panel(self):
        from ui.library.songs_detail_panel import SongsDetailPanel
        assert SongsDetailPanel is not None

    def test_import_status_delegate(self):
        from ui.library.songs_status_delegate import SongsStatusDelegate
        assert SongsStatusDelegate is not None
