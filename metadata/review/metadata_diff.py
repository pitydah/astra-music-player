"""Metadata diff — generate field-by-field change proposals from local vs KB data."""

from __future__ import annotations

from typing import Any

from metadata.review.metadata_matcher import (
    compare_artist,
    compare_album,
    compare_track,
)
from metadata.review.schemas import (
    MetadataFieldChange,
    MetadataProposal,
    generate_proposal_id,
    now_iso,
)


def generate_diff_for_artist(local_item: dict[str, Any],
                             kb_artist: dict[str, Any]) -> MetadataProposal | None:
    changes = compare_artist(local_item, kb_artist)
    if not changes:
        return None
    name = kb_artist.get("name", str(local_item.get("artist", "")))
    return MetadataProposal(
        proposal_id=generate_proposal_id(),
        entity_type="artist",
        entity_id=kb_artist.get("mbid", name.lower()),
        artist_name=name,
        title=name,
        changes=changes,
        source_summary={"musicbrainz": True},
        confidence=_avg_confidence(changes),
        created_at=now_iso(),
        status="pending",
    )


def generate_diff_for_album(local_item: dict[str, Any],
                            kb_album: dict[str, Any]) -> MetadataProposal | None:
    changes = compare_album(local_item, kb_album)
    if not changes:
        return None
    title = kb_album.get("title", str(local_item.get("album", "")))
    return MetadataProposal(
        proposal_id=generate_proposal_id(),
        entity_type="album",
        entity_id=kb_album.get("release_group_mbid", title.lower()),
        artist_name=kb_album.get("artist_name", str(local_item.get("artist", ""))),
        title=title,
        changes=changes,
        source_summary={"musicbrainz": True, "coverart": any(
            c.source == "coverart" for c in changes
        )},
        confidence=_avg_confidence(changes),
        created_at=now_iso(),
        status="pending",
    )


def generate_diff_for_track(local_item: dict[str, Any],
                            kb_recording: dict[str, Any]) -> MetadataProposal | None:
    changes = compare_track(local_item, kb_recording)
    if not changes:
        return None
    title = kb_recording.get("title", str(local_item.get("title", "")))
    return MetadataProposal(
        proposal_id=generate_proposal_id(),
        entity_type="track",
        track_id=int(local_item.get("id", 0) or 0),
        artist_name=str(local_item.get("artist", "")),
        title=title,
        changes=changes,
        source_summary={"musicbrainz": True},
        confidence=_avg_confidence(changes),
        created_at=now_iso(),
        status="pending",
    )


def generate_diff_from_gaps(local_item: dict[str, Any],
                            missing_fields: list[str]) -> MetadataProposal | None:
    changes: list[MetadataFieldChange] = []
    for field in missing_fields:
        if field in ("title", "artist", "album", "albumartist", "genre", "year"):
            changes.append(MetadataFieldChange(
                field=field,
                current_value="",
                suggested_value="",
                source="detected_gap",
                confidence=0.0,
                reason=f"Campo '{field}' vacio — necesita sugerencia externa",
            ))
    if not changes:
        return None
    return MetadataProposal(
        proposal_id=generate_proposal_id(),
        entity_type="track",
        track_id=int(local_item.get("id", 0) or 0),
        title=str(local_item.get("title", "")),
        artist_name=str(local_item.get("artist", "")),
        changes=changes,
        source_summary={"detected_gaps": True},
        confidence=1.0,
        created_at=now_iso(),
        status="gaps_detected",
    )


def _avg_confidence(changes: list[MetadataFieldChange]) -> float:
    if not changes:
        return 0.0
    return sum(c.confidence for c in changes) / len(changes)
