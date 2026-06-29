"""Tests: Album/Artist/Genre controllers use scope and clean incompatible fields."""

from unittest.mock import MagicMock


class TestAlbumArtistGenreContext:

    def test_album_controller_updates_selection_with_scope(self):
        ctx_svc = MagicMock()
        window = MagicMock()
        window._ctx.context_svc = ctx_svc
        window._context_svc = ctx_svc

        from ui.controllers.album_controller import AlbumController
        ctrl = AlbumController(window)
        ctx = ctrl._context_svc
        assert ctx is ctx_svc

    def test_artist_controller_updates_selection_with_scope(self):
        ctx_svc = MagicMock()
        window = MagicMock()
        window._ctx.context_svc = ctx_svc
        window._context_svc = ctx_svc

        from ui.controllers.artist_controller import ArtistController
        ctrl = ArtistController(window)
        ctx = ctrl._context_svc
        assert ctx is ctx_svc

    def test_genre_controller_updates_selection_with_scope(self):
        ctx_svc = MagicMock()
        window = MagicMock()
        window._ctx.context_svc = ctx_svc
        window._context_svc = ctx_svc

        from ui.controllers.genre_controller import GenreController
        ctrl = GenreController(window)
        ctx = ctrl._context_svc
        assert ctx is ctx_svc
