from __future__ import annotations

import os


def supports_spectral_analysis(filepath: str) -> bool:
    """Check if a file can be analysed spectrally.

    Supports WAV and FLAC — both can be decoded losslessly for FFT analysis.
    """
    ext = os.path.splitext(filepath)[1].lower()
    return ext in (".wav", ".flac")
