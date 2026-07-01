# Bit-Perfect Verification — Michi Music Player

## Overview

Michi can verify bit-perfect playback by comparing the source file format
against the actual ALSA hardware parameters read from `/proc/asound`.

This is NOT declarative — it reads real kernel-level data.

## States

| State | Meaning |
|-------|---------|
| `off` | Profile is not bit-perfect |
| `requested` | User requested bit-perfect, but no active playback |
| `not_verified` | Cannot read hw_params or confirm the route |
| `verified` | Sample rate, format, channels match; no DSP in path |
| `broken` | Resampling, DSP, wrong device, or format mismatch detected |

## What breaks bit-perfect

- EQ (any mode)
- ReplayGain
- Spectrum visualization
- Digital volume
- Resampling
- `plughw` (ALSA conversion layer)
- PipeWire or PulseAudio (signal modification possible)
- Software mixer

## Files

| File | Purpose |
|------|---------|
| `audio/diagnostics/alsa_hw_params.py` | Read and parse `/proc/asound/*/hw_params` |
| `audio/diagnostics/bitperfect_report.py` | `BitperfectReport` dataclass |
| `audio/diagnostics/bitperfect_verifier.py` | `verify_bitperfect()` function |
| `ui/audio_lab/bitperfect_monitor_page.py` | UI widget showing live status |

## Usage

```python
from audio.diagnostics.bitperfect_verifier import verify_bitperfect
report = verify_bitperfect(input_format, profile, diagnostics)
print(report.status)    # "verified", "broken", etc.
print(report.reasons)   # list of issues found
```

## ALSA hw_params format

Example `/proc/asound/card0/pcm0p/sub0/hw_params`:
```
access: MMAP_INTERLEAVED
format: S16_LE
channels: 2
rate: 44100 (44100/1)
period_size: 1024
buffer_size: 8192
```

The parser extracts sample rate, format, channels, access mode, period/buffer size.
Format depth mapping: S16_LE=16, S24_LE=24, S24_3LE=24, S32_LE=32.
