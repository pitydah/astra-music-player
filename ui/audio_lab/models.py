"""Data models for Audio Lab — CD ripping, encoding, metadata, and tagging."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RipProfile:
    name: str = ""
    fmt: str = ""
    lossless: bool = False
    bitrate: int = 0
    outputs: list[str] = field(default_factory=list)
    recommended: bool = False
    description: str = ""
    available: bool = True


@dataclass
class RipJob:
    id: str = ""
    drive: str = ""
    profile: str = ""
    destination: str = ""
    extraction_mode: str = "fast"
    status: str = "idle"
    progress: float = 0.0
    current_track: int = 0
    total_tracks: int = 0


@dataclass
class DiscMetadata:
    artist: str = ""
    album: str = ""
    year: int = 0
    genre: str = ""
    tracks: list[TrackMetadata] = field(default_factory=list)
    cover_path: str = ""
    confidence: float = 0.0
    source: str = ""


@dataclass
class TrackMetadata:
    track_number: int = 0
    title: str = ""
    artist: str = ""
    duration: float = 0.0
    disc_number: int = 1
    composer: str = ""
    genre: str = ""
    year: int = 0


@dataclass
class TagSuggestion:
    field: str = ""
    current: str = ""
    suggested: str = ""
    confidence: float = 0.0
    source: str = ""
    apply: bool = False
    target_index: int | None = None
    scope: str = "track"


@dataclass
class AudioLabSettings:
    import_destination: str = ""
    default_rip_profile: str = "flac"
    default_extraction_mode: str = "fast"
    save_cover_file: bool = True
    embed_cover: bool = True
    create_portable_copy: bool = False
    use_ai_suggestions: bool = False
    ask_before_overwrite: bool = True
    organize_library: bool = False


@dataclass
class ExternalToolStatus:
    name: str = ""
    available: bool = False
    path: str = ""
    required: bool = False
    recommended_for: str = ""
    install_hint: str = ""


# ── Predefined rip profiles ──

RIP_PROFILES: list[RipProfile] = [
    RipProfile(
        name="WAV sin compresión", fmt="wav", lossless=True,
        description="Audio PCM sin comprimir. Máxima compatibilidad.",
    ),
    RipProfile(
        name="FLAC Hi-Fi", fmt="flac", lossless=True, recommended=True,
        description="Audio sin pérdida. Recomendado para archivado de calidad.",
        available=False,
    ),
    RipProfile(
        name="ALAC", fmt="alac", lossless=True,
        description="Apple Lossless. Compatible con dispositivos Apple.",
        available=False,
    ),
    RipProfile(
        name="MP3 320 kbps", fmt="mp3", bitrate=320,
        description="Compresión con pérdida. Compatible con todos los dispositivos.",
        available=False,
    ),
    RipProfile(
        name="Opus eficiente", fmt="opus", bitrate=192,
        description="Codec moderno de alta eficiencia a baja tasa de bits.",
        available=False,
    ),
    RipProfile(
        name="FLAC + MP3", fmt="flac", lossless=True,
        outputs=["flac", "mp3"],
        description="Master FLAC + copia MP3 portátil.",
        available=False,
    ),
]

# ── Extraction modes ──

EXTRACTION_MODES: list[tuple[str, str, str]] = [
    ("fast", "Rapido", "Para discos nuevos o en buen estado."),
    ("safe", "Seguro", "Verifica errores básicos durante la extracción."),
    ("accurate", "Preciso", "Modo avanzado para colecciónes importantes o discos dañados."),
]
