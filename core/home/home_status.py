from __future__ import annotations

import dataclasses
import time
from typing import Optional


@dataclasses.dataclass
class LibraryHomeStatus:
    track_count: int = 0
    album_count: int = 0
    artist_count: int = 0
    genre_count: int = 0
    active_roots_count: int = 0
    last_scan: Optional[str] = None
    index_error_count: int = 0
    missing_file_count: int = 0
    missing_metadata_count: int = 0
    missing_cover_count: int = 0
    tracks_without_audio_features: int = 0
    new_tracks_count: int = 0
    is_empty: bool = True
    is_healthy: bool = True


@dataclasses.dataclass
class PlaybackHomeStatus:
    has_current_track: bool = False
    current_title: str = ""
    current_artist: str = ""
    current_album: str = ""
    current_cover_id: str = ""
    current_position: float = 0.0
    current_duration: float = 0.0
    queue_active: bool = False
    queue_count: int = 0
    last_track_title: str = ""
    last_track_artist: str = ""
    can_continue: bool = False
    can_continue_remote: bool = False
    source: str = ""
    state: str = "stopped"  # playing, paused, stopped, unknown


@dataclasses.dataclass
class AudioHomeStatus:
    output_device: str = ""
    output_profile: str = ""
    dac_active: bool = False
    replaygain_enabled: bool = False
    eq_enabled: bool = False
    dsp_active: bool = False
    bitperfect_state: str = "not_available"
    bitperfect_intended: bool = False
    format_label: str = ""
    sample_rate: int = 0
    bit_depth: int = 0
    warnings: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class EcosystemHomeStatus:
    micro_server_state: str = "not_configured"
    micro_server_name: str = ""
    micro_server_issue_code: str = ""
    micro_server_contract_ok: bool = False
    micro_server_can_continue: bool = False
    remote_music_server_state: str = "not_configured"
    remote_music_server_count: int = 0
    remote_music_server_name: str = ""
    mobile_sync_state: str = "no_device"
    mobile_device_count: int = 0
    api_state: str = "unknown"
    home_audio_state: str = "disabled"
    big_server_state: str = "not_configured"
    stream_receiver_count: int = 0
    last_sync: Optional[str] = None
    diagnostics_available: bool = False
    overall_ecosystem_status: str = "unknown"
    warning_count: int = 0
    error_count: int = 0


@dataclasses.dataclass
class HomeAlert:
    severity: str = "info"  # critical, warning, info
    kind: str = ""  # missing_files, index_errors, audio_output, micro_server, metadata, covers, audio_features, playlists, sync, safe_mode
    title: str = ""
    message: str = ""
    count: int = 0
    target_route: str = ""
    action_label: str = ""
    dismissible: bool = True


@dataclasses.dataclass
class AssistantSuggestion:
    title: str = ""
    message: str = ""
    target_route: str = ""
    action_kind: str = ""
    requires_confirmation: bool = False
    priority: int = 0


@dataclasses.dataclass
class HomeAction:
    label: str = ""
    target_route: str = ""
    icon_key: str = ""
    priority: int = 0


@dataclasses.dataclass
class HomeCardError:
    card_name: str = ""
    error_message: str = ""
    is_fatal: bool = False


@dataclasses.dataclass
class HomeDashboardSnapshot:
    overall_state: str = "ready"
    headline: str = ""
    subtitle: str = ""
    library: LibraryHomeStatus = dataclasses.field(default_factory=LibraryHomeStatus)
    playback: PlaybackHomeStatus = dataclasses.field(default_factory=PlaybackHomeStatus)
    audio: AudioHomeStatus = dataclasses.field(default_factory=AudioHomeStatus)
    ecosystem: EcosystemHomeStatus = dataclasses.field(default_factory=EcosystemHomeStatus)
    alerts: list[HomeAlert] = dataclasses.field(default_factory=list)
    assistant_suggestions: list[AssistantSuggestion] = dataclasses.field(default_factory=list)
    actions: list[HomeAction] = dataclasses.field(default_factory=list)
    errors: list[HomeCardError] = dataclasses.field(default_factory=list)
    generated_at: float = dataclasses.field(default_factory=time.time)
