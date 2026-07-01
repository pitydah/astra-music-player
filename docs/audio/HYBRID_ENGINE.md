# Hybrid Audio Engine — Michi Music Player

## Architecture

```
UI Layer
  → PlayerService (single facade)
    → HybridAudioManager (backend selector)
      ├── GStreamerBackend → GStreamerEngine (normal, DSP, visual)
      └── MpdBackend → MPD (Hi-Fi, bit-perfect, headless)
```

## Backend Selection

The active backend is chosen automatically based on the audio profile:

| Profile | Backend | Use Case |
|---------|---------|----------|
| `standard`, `hifi_pcm`, `bitperfect_pcm`, `dsd_to_pcm`, `streaming`, `pure_audio`, `studio_monitor`, `multiroom` | GStreamer | Normal playback, EQ, spectrum, radio |
| `michi_hifi_mpd`, `michi_bitperfect_mpd`, `michi_dsd_mpd`, `michi_server_renderer_mpd` | MPD | Bit-perfect, DSD/DoP, server mode |

## Fallback

If MPD is not installed or cannot connect, the manager falls back to GStreamer
and shows a warning. This is handled transparently — the UI never freezes.

## Queue

Michi maintains the canonical queue. When switching to MPD, the queue is
copied to MPD's playlist. When switching back, Michi's queue is restored.

## Key Files

| File | Purpose |
|------|---------|
| `audio/backends/base.py` | `AudioBackend` Protocol |
| `audio/backends/types.py` | `PlaybackSnapshot`, `BackendCapabilities`, `AudioDiagnostics` |
| `audio/backends/hybrid_audio_manager.py` | `HybridAudioManager` — backend selection and switching |
| `audio/backends/gstreamer_backend.py` | `GStreamerBackend` — wraps `GStreamerEngine` |
| `audio/backends/mpd_backend.py` | `MpdBackend` — implements AudioBackend via MPD |
| `audio/player_service.py` | `PlayerService` — facade that routes to HybridAudioManager |
| `audio/output_profiles.py` | 13 profiles including 4 MPD profiles |
