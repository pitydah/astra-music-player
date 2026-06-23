"""Analysis service — orchestrates audio feature extraction with WorkerManager, pause/cancel."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from audio_analysis.acoustic_profile import to_safe_labels
from audio_analysis.dependency_check import check_dependencies
from audio_analysis.feature_extractor import extract_features, make_track_key
from audio_analysis.feature_repository import FeatureRepository
from audio_analysis.schemas import (
    AudioFeature,
    AnalysisStatus,
    SimilarityResult,
)
from audio_analysis.similarity_index import compute_similarity
from core.settings_manager import get_bool, get_str, get_int

logger = logging.getLogger("michi.audio_analysis.service")


class AnalysisService:
    def __init__(self, db: Any, worker_mgr: Any = None):
        self._db = db
        self._worker_mgr = worker_mgr
        self._repo = FeatureRepository()
        self._deps = check_dependencies()
        self._enabled = get_bool("audio_analysis/enabled")
        self._backend = get_str("audio_analysis/backend") or self._deps["backend"]
        self._use_librosa = get_bool("audio_analysis/use_librosa")
        self._max_batch = get_int("audio_analysis/max_batch") or 50
        self._sample_duration = get_int("audio_analysis/sample_duration") or 90
        self._paused = False
        self._active_jobs: dict[str, str] = {}

    @property
    def enabled(self) -> bool:
        if os.environ.get("MICHI_SAFE_MODE") == "1":
            return False
        return self._enabled

    @property
    def backend(self) -> str:
        if self._use_librosa and self._deps["backend"] == "librosa":
            return "librosa"
        return self._backend

    @property
    def available(self) -> bool:
        return self._deps["available"]

    def get_status(self) -> AnalysisStatus:
        return AnalysisStatus(
            backend=self.backend,
            available=self.available,
            enabled=self.enabled,
            total_analyzed=self._repo.count_features(),
            pending_jobs=len(self._repo.get_pending_jobs(1000)),
            active_jobs=self._repo.count_active_jobs(),
            missing_deps=self._deps.get("missing", []),
        )

    def has_features(self, track_key: str) -> bool:
        return self._repo.has_features(track_key)

    def get_features(self, track_key: str) -> AudioFeature | None:
        return self._repo.get_feature(track_key)

    def get_safe_labels(self, track_key: str) -> dict:
        feat = self._repo.get_feature(track_key)
        if feat and feat.status == "completed":
            return to_safe_labels(feat)
        return {"bpm": 0, "bpm_confidence": 0, "energy_bucket": "unknown", "acoustic_labels": ["no_data"], "dynamic_range_db": 0}

    def analyze_track(self, track_id: int) -> dict:
        if not self.available:
            return {"status": "error", "error": self._deps["message"]}
        if not self.enabled:
            return {"status": "disabled", "error": "Analisis acustico desactivado."}

        filepath = self._resolve_filepath(track_id)
        if not filepath:
            return {"status": "error", "error": "Track no encontrado."}

        track_key = make_track_key(filepath)
        feat = extract_features(filepath, backend=self.backend, sample_duration=self._sample_duration, db=self._db)
        self._repo.upsert_feature(track_key, feat)
        return {"status": feat.status, "track_key": track_key, "backend": feat.backend}

    def analyze_tracks_async(self, track_ids: list[int]) -> str:
        batch_id = f"batch_{int(time.time())}"
        if not self.available or not self.enabled:
            return batch_id

        for tid in track_ids[:self._max_batch]:
            filepath = self._resolve_filepath(tid)
            if not filepath:
                continue
            track_key = make_track_key(filepath)
            if self._repo.has_features(track_key):
                continue
            job_id = self._repo.add_job(track_key)
            self._active_jobs[job_id] = track_key

        self._process_queue()
        return batch_id

    def find_sonically_similar(self, track_id: int, limit: int = 30) -> list[dict]:
        filepath = self._resolve_filepath(track_id)
        if not filepath:
            return []
        seed_key = make_track_key(filepath)
        seed_feat = self._repo.get_feature(seed_key)
        if not seed_feat:
            return []

        cached = self._repo.get_similarity_cache(seed_key, "acoustic")
        if cached:
            return cached[:limit]

        all_features = self._repo.get_all_features()
        results: list[SimilarityResult] = []
        for feat in all_features:
            if feat.track_key == seed_key:
                continue
            result = compute_similarity(seed_feat, feat)
            results.append(result)

        results.sort(key=lambda x: x.score, reverse=True)
        safe_results = self._enrich_results(results[:limit])
        self._repo.cache_similarity(seed_key, "acoustic", safe_results)
        return safe_results

    def list_missing_features(self, limit: int = 50) -> list[dict]:
        items = self._db.get_all() if hasattr(self._db, "get_all") else []
        missing = []
        for item in items:
            if len(missing) >= limit:
                break
            fp = getattr(item, "filepath", "")
            if not fp:
                continue
            track_key = make_track_key(fp)
            if not self._repo.has_features(track_key):
                missing.append({
                    "track_id": getattr(item, "id", 0),
                    "title": str(getattr(item, "title", "") or ""),
                    "artist": str(getattr(item, "artist", "") or ""),
                })
        return missing

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        self._process_queue()

    def cancel(self, job_id: str = ""):
        if job_id:
            self._repo.update_job(job_id, "cancelled")
            self._active_jobs.pop(job_id, None)
        else:
            for jid in list(self._active_jobs):
                self._repo.update_job(jid, "cancelled")
            self._active_jobs.clear()

    def _process_queue(self):
        if self._paused or not self._worker_mgr:
            return
        jobs = self._repo.get_pending_jobs(5)
        for job in jobs:
            jid = job["job_id"]
            tkey = job["track_key"]
            if jid not in self._active_jobs:
                self._active_jobs[jid] = tkey
            self._repo.update_job(jid, "running")
            if self._worker_mgr:
                self._worker_mgr.run_task(
                    f"audio_analysis_{jid}",
                    self._analyze_one,
                    tkey,
                    on_done=lambda r, j=jid: self._on_job_done(j, r),
                    on_error=lambda e, j=jid: self._on_job_error(j, e),
                )

    def _analyze_one(self, track_key: str) -> dict:
        fp = self._resolve_filepath_by_key(track_key)
        if not fp:
            return {"status": "error", "error": "Filepath not found"}
        feat = extract_features(fp, backend=self.backend, sample_duration=self._sample_duration, db=self._db)
        self._repo.upsert_feature(track_key, feat)
        return {"status": feat.status, "track_key": track_key}

    def _on_job_done(self, job_id: str, result: dict):
        self._repo.update_job(job_id, result.get("status", "completed"))
        self._active_jobs.pop(job_id, None)
        self._process_queue()

    def _on_job_error(self, job_id: str, error: str):
        self._repo.update_job(job_id, "error", error)
        self._active_jobs.pop(job_id, None)

    def _resolve_filepath(self, track_id: int) -> str:
        try:
            item = self._db.get_media_item_by_id(track_id)
            if item:
                return getattr(item, "filepath", "")
        except Exception:
            pass
        return ""

    def _resolve_filepath_by_key(self, track_key: str) -> str:
        items = self._db.get_all() if hasattr(self._db, "get_all") else []
        for item in items:
            if make_track_key(getattr(item, "filepath", "")) == track_key:
                return getattr(item, "filepath", "")
        return ""

    def _enrich_results(self, results: list[SimilarityResult]) -> list[dict]:
        items = self._db.get_all() if hasattr(self._db, "get_all") else []
        key_map = {}
        for item in items:
            fp = getattr(item, "filepath", "")
            if fp:
                key_map[make_track_key(fp)] = item

        enriched = []
        for r in results:
            item = key_map.get(r.track_key)
            if item:
                enriched.append({
                    "track_id": getattr(item, "id", 0),
                    "title": str(getattr(item, "title", "") or ""),
                    "artist": str(getattr(item, "artist", "") or ""),
                    "album": str(getattr(item, "album", "") or ""),
                    "score": r.score,
                    "reasons": r.reasons,
                    "bpm_diff": r.bpm_diff,
                    "energy_diff": r.energy_diff,
                })
        return enriched
