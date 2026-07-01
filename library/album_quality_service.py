"""AlbumQualityService — album-level quality analysis reusing Audio Lab diagnostics.

Fast mode: heuristics by extension + cached diagnostics.
Full mode: runs analyse_file per track with progress callback.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger("michi.album_quality")


@dataclass
class AlbumQualityDetail:
    dominant_format: str = ""
    dominant_quality: str = "unknown"
    dominant_sample_rate: int = 0
    dominant_bit_depth: int = 0
    average_bitrate: int = 0
    has_mixed_quality: bool = False
    has_hires: bool = False
    has_lossless: bool = False
    has_lossy: bool = False
    has_dsd: bool = False
    tracks_analyzed: int = 0
    total_tracks: int = 0
    warnings: list[str] = field(default_factory=list)


ProgressCallback = Callable[[int, int], None]


class AlbumQualityService:
    """Quality analysis for album tracks, reusing diagnostics_service."""

    def summarize_fast(self, tracks: list) -> AlbumQualityDetail:
        """Fast quality summary using heuristics and cached diagnostics."""
        from library.album_repository import AlbumRepository
        repo = AlbumRepository()
        repo.build(tracks)
        groups = repo.list_groups()
        if not groups:
            return AlbumQualityDetail()
        q = groups[0].quality
        return AlbumQualityDetail(
            dominant_format=q.dominant_format,
            dominant_quality=q.dominant_quality,
            dominant_sample_rate=q.dominant_sample_rate,
            dominant_bit_depth=q.dominant_bit_depth,
            average_bitrate=q.average_bitrate,
            has_mixed_quality=q.has_mixed_quality,
            has_hires=q.has_hires,
            has_lossless=q.has_lossless,
            has_lossy=q.has_lossy,
            has_dsd=q.has_dsd,
            tracks_analyzed=len(tracks),
            total_tracks=len(tracks),
            warnings=q.warnings,
        )

    def analyze_album(self, tracks: list, progress_cb: ProgressCallback | None = None) -> AlbumQualityDetail:
        """Full analysis using Audio Lab diagnostics_service per track."""
        from core.audio_lab.diagnostics_service import analyse_file

        formats = {}
        sample_rates = {}
        bit_depths = {}
        total_bitrate = 0
        quality_kinds = {}
        total = len(tracks)
        analyzed = 0
        has_dsd = False

        for i, t in enumerate(tracks):
            fp = str(getattr(t, "filepath", "") or "")
            if fp and os.path.isfile(fp):
                try:
                    result = analyse_file(fp, use_cache=True)
                    fi = result.get("format_info", {})
                    q = result.get("quality", {})
                    ext = fi.get("container", os.path.splitext(fp)[1].lstrip(".")).upper()
                    formats[ext] = formats.get(ext, 0) + 1
                    sr = fi.get("sample_rate", 0) or int(getattr(t, "sample_rate", 0) or 0)
                    bd = fi.get("bit_depth", 0) or int(getattr(t, "bit_depth", 0) or 0)
                    br = fi.get("bitrate", 0) or int(getattr(t, "bitrate", 0) or 0)
                    if sr:
                        sample_rates[sr] = sample_rates.get(sr, 0) + 1
                    if bd:
                        bit_depths[bd] = bit_depths.get(bd, 0) + 1
                    if br:
                        total_bitrate += br
                    kind = q.get("category", "unknown")
                    quality_kinds[kind] = quality_kinds.get(kind, 0) + 1
                    has_dsd = has_dsd or ext in ("DSF", "DFF", "DSD")
                    analyzed += 1
                except Exception as e:
                    logger.debug("analyse_file failed for %s: %s", fp, e)
            if progress_cb:
                progress_cb(i + 1, total)

        dominant_fmt = max(formats, key=formats.get) if formats else ""
        dominant_sr = max(sample_rates, key=sample_rates.get) if sample_rates else 0
        dominant_bd = max(bit_depths, key=bit_depths.get) if bit_depths else 0
        avg_br = total_bitrate // analyzed if analyzed and total_bitrate else 0

        has_lossless = any(e in ("FLAC", "ALAC", "WAV", "AIFF") for e in formats)
        has_lossy = any(e in ("MP3", "AAC", "OGG", "OPUS") for e in formats)
        has_mixed = has_lossless and has_lossy
        has_hires = any(sr > 48000 for sr in sample_rates)

        quality = "lossless" if has_lossless else "lossy" if has_lossy else "unknown"
        if has_dsd:
            quality = "dsd"
        elif has_hires and has_lossless:
            quality = "hires"

        warnings = []
        if has_mixed:
            warnings.append("Calidad mixta (lossless + lossy)")
        if has_dsd:
            warnings.append("Audio DSD detectado")
        if len(tracks) > analyzed:
            warnings.append(f"{len(tracks) - analyzed} pistas no analizadas")

        return AlbumQualityDetail(
            dominant_format=dominant_fmt,
            dominant_quality=quality,
            dominant_sample_rate=dominant_sr,
            dominant_bit_depth=dominant_bd,
            average_bitrate=avg_br,
            has_mixed_quality=has_mixed,
            has_hires=has_hires,
            has_lossless=has_lossless,
            has_lossy=has_lossy,
            has_dsd=has_dsd,
            tracks_analyzed=analyzed,
            total_tracks=total,
            warnings=warnings,
        )
