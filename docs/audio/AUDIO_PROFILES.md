# Audio Profiles — Michi Music Player

## List of Profiles (13 total)

| Key | Name | Backend | Bit-Perfect | DSP |
|-----|------|---------|-------------|-----|
| `standard` | Estándar | GStreamer | No | Full |
| `hifi_pcm` | Hi-Fi PCM | GStreamer | No | Optional |
| `bitperfect_pcm` | Bit-Perfect PCM | GStreamer | Yes | Blocked |
| `dsd_to_pcm` | DSD → PCM | GStreamer | No | Limited |
| `dop_experimental` | DoP (Experimental) | GStreamer | Yes | Blocked |
| `streaming` | Streaming | GStreamer | No | Limited |
| `pure_audio` | Pure Audio | GStreamer | Yes | Blocked |
| `studio_monitor` | Studio Monitor | GStreamer | No | Blocked |
| `multiroom` | Multiroom / Snapcast | GStreamer | No | Full |
| `michi_hifi_mpd` | Hi-Fi MPD | MPD | Yes | Blocked |
| `michi_bitperfect_mpd` | Bit-Perfect MPD | MPD | Yes | Blocked |
| `michi_dsd_mpd` | DSD / DoP (MPD) | MPD | Yes | Blocked |
| `michi_server_renderer_mpd` | Servidor MPD Remoto | MPD | Yes | Blocked |

## Profile Properties

Each profile defines:

| Property | Description |
|----------|-------------|
| `allows_volume_digital` | Software volume control |
| `allows_eq` | Graphic or parametric EQ |
| `allows_replaygain` | ReplayGain processing |
| `allows_spectrum` | Spectrum visualization |
| `allows_resample` | Sample rate conversion |
| `allows_convert` | Format conversion |
| `allows_transmit` | Network transmit |
| `bitperfect` | Bit-perfect mode (blocks all DSP) |
| `dsd_mode` | DSD handling: pcm / dop / native |
| `preferred_backend` | auto / alsa / mpd |

## File

Defined in `audio/output_profiles.py`. Access via:

```python
from audio.output_profiles import get_profile, PROFILES
profile = get_profile("standard")
print(profile.name, profile.allows_eq, profile.preferred_backend)
```
