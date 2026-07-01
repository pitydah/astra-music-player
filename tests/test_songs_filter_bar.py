"""Tests: SongsFilterBar — current_state emits correct fields."""

from unittest.mock import MagicMock, patch

from library.songs_view_state import SongsFilterState


class TestSongsFilterBar:

    @patch("ui.library.songs_filter_bar.SongsFilterBar._emit")
    def test_current_state_has_missing_cover(self, mock_emit):
        from ui.library.songs_filter_bar import SongsFilterBar
        bar = SongsFilterBar.__new__(SongsFilterBar)
        bar._format_combo = MagicMock()
        bar._format_combo.currentData.return_value = ""
        bar._quality_combo = MagicMock()
        bar._quality_combo.currentData.return_value = ""
        bar._genre_combo = MagicMock()
        bar._genre_combo.currentData.return_value = ""
        bar._year_min = MagicMock()
        bar._year_min.text.return_value = ""
        bar._year_max = MagicMock()
        bar._year_max.text.return_value = ""
        bar._sr_input = MagicMock()
        bar._sr_input.text.return_value = ""
        bar._br_input = MagicMock()
        bar._br_input.text.return_value = ""
        bar._fav_check = MagicMock()
        bar._fav_check.isChecked.return_value = False
        bar._meta_check = MagicMock()
        bar._meta_check.isChecked.return_value = False
        bar._cover_check = MagicMock()
        bar._cover_check.isChecked.return_value = True
        bar._missing_check = MagicMock()
        bar._missing_check.isChecked.return_value = False
        bar._al_check = MagicMock()
        bar._al_check.isChecked.return_value = False

        state = bar.current_state()
        assert isinstance(state, SongsFilterState)
        assert state.only_missing_cover is True

    @patch("ui.library.songs_filter_bar.SongsFilterBar._emit")
    def test_current_state_has_al_warning(self, mock_emit):
        from ui.library.songs_filter_bar import SongsFilterBar
        bar = SongsFilterBar.__new__(SongsFilterBar)
        bar._format_combo = MagicMock()
        bar._format_combo.currentData.return_value = ""
        bar._quality_combo = MagicMock()
        bar._quality_combo.currentData.return_value = ""
        bar._genre_combo = MagicMock()
        bar._genre_combo.currentData.return_value = ""
        bar._year_min = MagicMock()
        bar._year_min.text.return_value = ""
        bar._year_max = MagicMock()
        bar._year_max.text.return_value = ""
        bar._sr_input = MagicMock()
        bar._sr_input.text.return_value = ""
        bar._br_input = MagicMock()
        bar._br_input.text.return_value = ""
        bar._fav_check = MagicMock()
        bar._fav_check.isChecked.return_value = False
        bar._meta_check = MagicMock()
        bar._meta_check.isChecked.return_value = False
        bar._cover_check = MagicMock()
        bar._cover_check.isChecked.return_value = False
        bar._missing_check = MagicMock()
        bar._missing_check.isChecked.return_value = False
        bar._al_check = MagicMock()
        bar._al_check.isChecked.return_value = True

        state = bar.current_state()
        assert state.only_audio_lab_warning is True

    @patch("ui.library.songs_filter_bar.SongsFilterBar._emit")
    def test_sample_rate_conversion(self, mock_emit):
        from ui.library.songs_filter_bar import SongsFilterBar
        bar = SongsFilterBar.__new__(SongsFilterBar)
        bar._format_combo = MagicMock()
        bar._format_combo.currentData.return_value = ""
        bar._quality_combo = MagicMock()
        bar._quality_combo.currentData.return_value = ""
        bar._genre_combo = MagicMock()
        bar._genre_combo.currentData.return_value = ""
        bar._year_min = MagicMock()
        bar._year_min.text.return_value = ""
        bar._year_max = MagicMock()
        bar._year_max.text.return_value = ""
        bar._sr_input = MagicMock()
        bar._sr_input.text.return_value = "96"
        bar._br_input = MagicMock()
        bar._br_input.text.return_value = ""
        bar._fav_check = MagicMock()
        bar._fav_check.isChecked.return_value = False
        bar._meta_check = MagicMock()
        bar._meta_check.isChecked.return_value = False
        bar._cover_check = MagicMock()
        bar._cover_check.isChecked.return_value = False
        bar._missing_check = MagicMock()
        bar._missing_check.isChecked.return_value = False
        bar._al_check = MagicMock()
        bar._al_check.isChecked.return_value = False

        state = bar.current_state()
        assert state.sample_rate_min == 96000
