"""Schemas for metadata review — proposals, field changes, reviews."""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MetadataFieldChange:
    field: str
    current_value: str = ""
    suggested_value: str = ""
    source: str = ""
    confidence: float = 0.0
    reason: str = ""
    accepted: bool = False


@dataclass(slots=True)
class MetadataProposal:
    proposal_id: str
    entity_type: str = ""
    entity_id: str = ""
    track_id: int = 0
    album_key: str = ""
    artist_name: str = ""
    title: str = ""
    changes: list[MetadataFieldChange] = field(default_factory=list)
    source_summary: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    created_at: str = ""
    status: str = "pending"


@dataclass(slots=True)
class MetadataReview:
    review_id: str
    proposals: list[MetadataProposal] = field(default_factory=list)
    created_at: str = ""
    status: str = "pending"
    requires_confirmation: bool = True
    reversible: bool = True
    apply_target: str = "local_db"


def generate_proposal_id() -> str:
    return f"mp_{uuid.uuid4().hex[:12]}"


def generate_review_id() -> str:
    return f"mr_{uuid.uuid4().hex[:12]}"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")
