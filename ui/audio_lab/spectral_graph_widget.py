"""SpectralGraphWidget — static spectrum graph for analysed WAV files.

Shows a log-spaced FFT magnitude plot for a single audio file.
Reuses the colour palette from audio/spectrum.py but without animation.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget

SPEC_BANDS = 60
SPEC_MIN_HZ = 20
SPEC_MAX_HZ = 20000
SPEC_FREQS = np.logspace(np.log10(SPEC_MIN_HZ), np.log10(SPEC_MAX_HZ), SPEC_BANDS)

SPECTRUM_PALETTE = [
    QColor("#8FB7FF"), QColor("#8FB7FF"), QColor("#2eb8e6"), QColor("#20c0e0"),
    QColor("#18c8d8"), QColor("#10d0cc"), QColor("#18d8b8"), QColor("#28e0a0"),
    QColor("#40e880"), QColor("#60f058"), QColor("#80f838"), QColor("#a0f820"),
    QColor("#c0f010"), QColor("#dce808"), QColor("#f0d800"), QColor("#f8c000"),
    QColor("#f8a800"), QColor("#f88800"), QColor("#f06800"), QColor("#e84800"),
]

FREQ_LABELS = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]


class SpectralGraphWidget(QWidget):
    """Static spectrum graph. Call set_data(magnitudes, sample_rate) to render."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._band_values: np.ndarray = np.zeros(SPEC_BANDS, dtype=np.float64)
        self._sample_rate = 44100
        self.setMinimumHeight(150)
        self.setMinimumWidth(300)
        self.setStyleSheet(
            "background: rgba(255,255,255,0.02); "
            "border: 1px solid rgba(255,255,255,0.04); "
            "border-radius: 8px;"
        )

    def set_data(self, samples: np.ndarray, sample_rate: int):
        """Compute and store FFT magnitude from PCM samples."""
        self._sample_rate = sample_rate or 44100
        if len(samples) < 256:
            self._band_values = np.zeros(SPEC_BANDS)
            self.update()
            return

        window = np.hanning(min(len(samples), 8192))
        segment = samples[:len(window)] * window
        fft = np.fft.rfft(segment)
        mag = np.abs(fft)
        mag_db = 20.0 * np.log10(mag + 1e-12)
        freqs = np.fft.rfftfreq(len(segment), 1.0 / self._sample_rate)

        values = np.zeros(SPEC_BANDS)
        for i in range(SPEC_BANDS):
            lo = SPEC_FREQS[i - 1] if i > 0 else 0
            hi = SPEC_FREQS[i + 1] if i < SPEC_BANDS - 1 else SPEC_MAX_HZ * 2
            mask = (freqs >= lo) & (freqs < hi)
            if mask.any():
                values[i] = np.max(mag_db[mask])
            else:
                values[i] = -100

        values = np.clip((values + 100) / 100.0, 0, 1)
        self._band_values = values
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        margin = 8
        plot_w = w - margin * 2
        plot_h = h - margin * 2
        bar_w = max(2, plot_w // SPEC_BANDS - 1)

        # Background
        painter.fillRect(self.rect(), QColor(9, 11, 17))

        # Grid lines
        painter.setPen(QPen(QColor(255, 255, 255, 15), 1))
        for fl in FREQ_LABELS:
            if fl <= self._sample_rate / 2:
                x = margin + int(
                    np.log10(fl / SPEC_MIN_HZ)
                    / np.log10(SPEC_MAX_HZ / SPEC_MIN_HZ) * plot_w
                )
                painter.drawLine(x, margin, x, h - margin)

        # Bars
        for i in range(SPEC_BANDS):
            val = float(self._band_values[i])
            if val <= 0:
                continue
            x = margin + i * (plot_w // SPEC_BANDS)
            bar_h = max(1, int(val * plot_h * 0.95))
            color = SPECTRUM_PALETTE[i % len(SPECTRUM_PALETTE)]
            painter.fillRect(x, h - margin - bar_h, bar_w, bar_h, color)

        # Labels
        painter.setPen(QPen(QColor(255, 255, 255, 60), 1))
        font = painter.font()
        font.setPointSize(7)
        painter.setFont(font)
        for fl in FREQ_LABELS:
            if fl <= self._sample_rate / 2:
                x = margin + int(
                    np.log10(fl / SPEC_MIN_HZ)
                    / np.log10(SPEC_MAX_HZ / SPEC_MIN_HZ) * plot_w
                )
                label = f"{fl // 1000}k" if fl >= 1000 else str(fl)
                painter.drawText(x - 10, h - 2, label)

        painter.end()
