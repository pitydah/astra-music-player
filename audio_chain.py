"""Audio chain builder — GStreamer pipelines with DSP, DAC config, bit-perfect, EQ."""

from dataclasses import dataclass, field
import numpy as np

from eq_biquad import compute_biquad, FILTER_TYPES


@dataclass
class DacConfig:
    device: str = "default"          # ALSA device name
    mode: str = "standard"           # standard | bitperfect | dop
    target_rate: int = 0             # 0 = auto-match source
    target_format: str = "auto"      # auto | S16LE | S24_3LE | S32LE
    buffer_ms: int = 100
    period_count: int = 4

    @property
    def alsa_device_str(self) -> str:
        if self.mode == "bitperfect" and self.device == "default":
            return "hw:0,0"  # force hardware for bitperfect
        return self.device

    @classmethod
    def from_settings(cls, settings) -> "DacConfig":
        return cls(
            device=settings.get("audio/device", "default"),
            mode=settings.get("audio/mode", "standard"),
            target_rate=settings.get("audio/target_rate", 0),
            target_format=settings.get("audio/target_format", "auto"),
            buffer_ms=settings.get("audio/buffer_ms", 100),
        )


def build_audio_sink(dac: DacConfig, has_video: bool = False) -> str:
    """Build GStreamer audio-sink pipeline suffix based on DAC config."""

    parts = []

    if dac.mode == "bitperfect":
        # Match source exactly — no resampling, no conversion beyond what's needed
        parts.append("audioconvert")
        # Use exact alsasink
        parts.append(f"alsasink device={dac.alsa_device_str} "
                     f"buffer-time={dac.buffer_ms * 1000}")

    elif dac.mode == "dop":
        # DSD over PCM: force S32LE at half rate
        parts.append("audioconvert")
        parts.append("audio/x-raw,format=S32LE")
        parts.append(f"alsasink device={dac.alsa_device_str}")

    else:
        # Standard: audioconvert + audioresample, let PipeWire/PulseAudio handle
        parts.append("audioconvert")
        parts.append("audioresample")
        parts.append(f"alsasink device={dac.alsa_device_str}")

    return " ! ".join(parts)


def build_dsd_pipeline(filepath: str, dac: DacConfig, is_dsf: bool) -> str:
    """Build GStreamer pipeline string for DSD playback."""

    sink = build_audio_sink(dac)

    if is_dsf:
        # playbin handles avdemux_dsf → avdec_dsd_lsbf automatically
        return (
            f"playbin uri=file://{filepath} "
            f"audio-sink=\"{sink}\""
        )

    # DFF: need manual pipeline with appsrc
    from dff_parser import parse_dff
    header = parse_dff(filepath)

    caps = (
        f"audio/x-dsd,format=DSDU8,reversed-bytes=false,"
        f"layout=interleaved,channels={header.channels},"
        f"rate={header.sample_rate}"
    )

    return (
        f"appsrc name=dsdsrc emit-signals=true format=time caps={caps} "
        f"! avdec_dsd_msbf "
        f"! {sink}"
    )


def get_quality_label(filepath: str) -> tuple[str, str]:
    """Return (label, color_hex) for audio quality badge."""
    import os
    ext = os.path.splitext(filepath)[1].lower()

    if ext in (".dsf", ".dff"):
        try:
            from dff_parser import parse_dff
            header = parse_dff(filepath) if ext == ".dff" else None
            rate = header.sample_rate if header else 2822400
            dsd_speed = rate // 44100
            return (f"DSD{dsd_speed} · {rate/1e6:.1f}MHz", "#ffd54f")
        except Exception:
            return ("DSD", "#ffd54f")

    if ext == ".flac":
        return ("FLAC", "#4caf50")
    if ext == ".mp3":
        return ("MP3", "#ff9800")
    if ext == ".opus":
        return ("Opus", "#42a5f5")
    if ext == ".ogg":
        return ("OGG", "#42a5f5")
    if ext == ".wav":
        return ("WAV", "#4caf50")
    if ext in (".aiff", ".aif"):
        return ("AIFF", "#4caf50")
    if ext in (".m4a", ".aac"):
        return ("AAC", "#42a5f5")
    return ("", "")


# ═══════════════════════════════════════════════
#  EQ Pipeline Builders
# ═══════════════════════════════════════════════

def build_eq_graphic_sink(bands_db: list[float], dac: DacConfig) -> str:
    """Build audio-sink with 31-band graphic equalizer."""
    parts = []
    parts.append("equalizer-nbands")
    for i, db in enumerate(bands_db[:31]):
        parts.append(f"band{i}={db:.1f}")
    parts.append("audioconvert")
    parts.append("audioresample")
    parts.append(f"alsasink device={dac.alsa_device_str}")
    return " ! ".join(parts)


def build_eq_parametric_sink(bands: list[dict], preamp_db: float,
                              dac: DacConfig) -> str:
    """Build audio-sink with parametric EQ (biquads via audioiirfilter)."""
    parts = []
    # Preamp: adjust volume upstream
    if abs(preamp_db) > 0.01:
        parts.append(f"volume volume={10.0 ** (preamp_db / 20.0):.6f}")

    # Biquad filters in series
    for i, band in enumerate(bands):
        coefs = compute_biquad(
            band.get("type", "Peak"), band.get("freq", 1000.0),
            band.get("gain", 0.0), band.get("Q", 1.41))
        b0, b1, b2, a0, a1, a2 = coefs
        parts.append(
            f"audioiirfilter name=eqband{i} "
            f"b0={b0:.10f} b1={b1:.10f} b2={b2:.10f} "
            f"a0={a0:.10f} a1={a1:.10f} a2={a2:.10f}"
        )

    parts.append("audioconvert")
    parts.append("audioresample")
    parts.append(f"alsasink device={dac.alsa_device_str}")
    return " ! ".join(parts) if parts else f"alsasink device={dac.alsa_device_str}"


def build_eq_sink(bands: list[float] | list[dict], dac: DacConfig,
                  is_parametric: bool = False, preamp_db: float = 0.0) -> str:
    """Unified EQ sink builder. Returns GStreamer pipeline suffix."""
    if is_parametric:
        return build_eq_parametric_sink(bands, preamp_db, dac)
    return build_eq_graphic_sink(bands, dac)


def build_spectrum_branch() -> str:
    """Build spectrum capture branch (tee + appsink)."""
    return (
        "tee name=spectrum_tee "
        "spectrum_tee. ! queue ! appsink name=spectrum_sink emit-signals=true "
        "max-buffers=10 drop=true sync=false"
    )
