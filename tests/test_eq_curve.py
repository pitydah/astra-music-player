"""Tests for frequency response curve computation (pure math, no widget rendering)."""
import numpy as np
import pytest
from audio.eq_curve import EqCurveWidget
from audio.eq_biquad import eval_response


class TestEqCurveDataFlow:
    def test_set_bands_updates_response(self):
        widget = EqCurveWidget()
        bands = [{"type": "Peak", "freq": 1000, "gain": 6.0, "Q": 1.41}]
        widget.set_bands(bands, 0.0)
        assert widget._response is not None
        assert len(widget._response) == 512
        assert np.any(widget._response > 0)

    def test_set_bands_with_preamp(self):
        widget = EqCurveWidget()
        widget.set_bands([], 3.0)
        assert widget._response[0] == pytest.approx(3.0, abs=1e-6)

    def test_set_bands_empty(self):
        widget = EqCurveWidget()
        widget.set_bands([])
        assert np.allclose(widget._response, 0.0)

    def test_response_matches_eval_directly(self):
        widget = EqCurveWidget()
        bands = [{"type": "LowShelf", "freq": 80, "gain": 4.0, "Q": 0.7}]
        widget.set_bands(bands, 0.0)
        expected = eval_response(bands, widget._freqs, 0.0)
        assert widget._response == pytest.approx(expected, rel=1e-6)

    def test_freqs_is_log_spaced(self):
        widget = EqCurveWidget()
        assert widget._freqs[0] == pytest.approx(20.0, abs=1)
        assert widget._freqs[-1] == pytest.approx(20000.0, abs=500)
        assert len(widget._freqs) == 512

    def test_set_bands_multiple_calls(self):
        widget = EqCurveWidget()
        bands1 = [{"type": "Peak", "freq": 100, "gain": 3.0, "Q": 1.0}]
        bands2 = [{"type": "Peak", "freq": 10000, "gain": -3.0, "Q": 1.0}]
        widget.set_bands(bands1)
        r1 = widget._response.copy()
        widget.set_bands(bands2)
        r2 = widget._response
        assert not np.allclose(r1, r2)

    def test_complex_multi_band_response(self):
        widget = EqCurveWidget()
        bands = [
            {"type": "LowShelf", "freq": 80, "gain": 4.0, "Q": 0.7},
            {"type": "Peak", "freq": 250, "gain": -2.0, "Q": 1.2},
            {"type": "Peak", "freq": 2500, "gain": 4.0, "Q": 1.5},
            {"type": "HighShelf", "freq": 10000, "gain": 2.0, "Q": 0.7},
        ]
        widget.set_bands(bands, -1.5)
        assert widget._preamp_db == -1.5
        assert widget._bands == bands
        assert np.all(np.isfinite(widget._response))

    def test_preamp_db_propagation(self):
        widget = EqCurveWidget()
        widget.set_bands([], -4.2)
        assert widget._preamp_db == -4.2
        assert widget._response[100] == pytest.approx(-4.2, abs=1e-6)
