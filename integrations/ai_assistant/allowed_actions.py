"""Per-section allowed actions for Michi Assistant."""

ALLOWED_ACTIONS_BY_SECTION: dict[str, list[str]] = {
    "home": [
        "diagnose_ecosystem",
        "open_library",
        "open_connections",
        "open_audio_lab",
        "create_ecosystem_config_plan",
        "get_library_stats",
    ],
    "library_hub": [
        "search_library",
        "find_metadata_gaps",
        "draft_playlist",
        "recommend_music",
        "get_library_stats",
        "send_to_audio_lab",
    ],
    "audio_lab": [
        "explain_audio_format",
        "recommend_conversion_profile",
        "suggest_mobile_audio_profile",
        "suggest_micro_server_streaming_profile",
        "suggest_hifi_audio_profile",
        "analyze_track_audio",
        "list_tracks_missing_features",
        "create_smart_mix",
    ],
    "connections_hub": [
        "diagnose_ecosystem",
        "diagnose_mobile_sync",
        "diagnose_micro_server",
        "diagnose_micro_contract",
        "diagnose_home_audio",
        "create_ecosystem_config_plan",
        "suggest_ecosystem_fix",
        "preview_ecosystem_config_plan",
    ],
    "devices": [
        "diagnose_mobile_sync",
        "explain_mobile_pairing_status",
        "suggest_mobile_sync_profile",
    ],
    "mix_hub": [
        "recommend_music",
        "create_smart_mix",
        "draft_playlist",
        "explain_recommendation",
    ],
    "playback_hub": [
        "recommend_from_track",
        "find_sonically_similar",
        "add_tracks_to_queue",
        "play_track",
        "explain_current_track_quality",
    ],
    "settings": [
        "explain_settings",
        "create_ecosystem_config_plan",
        "preview_ecosystem_config_plan",
    ],
    "metadata_editor": [
        "find_metadata_gaps",
        "suggest_metadata_for_track",
        "suggest_metadata_for_album",
        "refresh_artist_metadata",
        "refresh_album_metadata",
    ],
    "playlists": [
        "create_playlist",
        "export_playlist",
        "detect_duplicates",
        "create_mobile_version",
    ],
}


def get_allowed_actions(section_key: str) -> list[str]:
    return ALLOWED_ACTIONS_BY_SECTION.get(section_key, [])
