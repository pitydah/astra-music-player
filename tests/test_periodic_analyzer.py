"""Tests for PeriodicAnalyzer."""

from unittest.mock import MagicMock, patch

from core.audio_lab.periodic_analyzer import PeriodicAnalyzer


class TestPeriodicAnalyzer:
    def test_start_does_nothing_if_disabled(self):
        db = MagicMock()
        pa = PeriodicAnalyzer(db)
        with patch("core.audio_lab.periodic_analyzer.get", return_value=False):
            pa.start()
            assert not pa.is_running

    def test_start_enabled_starts_timer(self):
        db = MagicMock()
        pa = PeriodicAnalyzer(db)
        def fake_get(key):
            if key == "audio_lab/auto_analyze":
                return True
            if key == "audio_lab/interval_hours":
                return 24
            return None
        with patch("core.audio_lab.periodic_analyzer.get", side_effect=fake_get):
            pa.start()
            assert pa.is_running

    def test_stop_stops_timer(self):
        db = MagicMock()
        pa = PeriodicAnalyzer(db)
        pa._running = True
        pa._timer = MagicMock()
        pa.stop()
        assert not pa.is_running
        pa._timer.stop.assert_called_once()

    def test_set_interval_updates_setting(self):
        db = MagicMock()
        pa = PeriodicAnalyzer(db)
        with patch("core.audio_lab.periodic_analyzer.set_") as mock_set:
            pa.set_interval(12)
            mock_set.assert_called_once_with("audio_lab/interval_hours", 12)

    def test_set_enabled_false_stops(self):
        db = MagicMock()
        pa = PeriodicAnalyzer(db)
        pa._running = True
        pa._timer = MagicMock()
        pa.set_enabled(False)
        assert not pa.is_running
        pa._timer.stop.assert_called_once()

    def test_set_enabled_true_starts(self):
        db = MagicMock()
        pa = PeriodicAnalyzer(db)
        pa._timer = MagicMock()
        with patch("core.audio_lab.periodic_analyzer.get", return_value=True):
            pa.set_enabled(True)
            assert pa.is_running
            pa._timer.start.assert_called_once()

    def test_property_is_running(self):
        db = MagicMock()
        pa = PeriodicAnalyzer(db)
        assert not pa.is_running
        pa._running = True
        assert pa.is_running
