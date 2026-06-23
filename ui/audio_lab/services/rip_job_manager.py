"""Rip job manager — manages CD ripping jobs. STUB."""

from __future__ import annotations

import uuid

from ui.audio_lab.models import RipJob


class RipJobManager:
    def __init__(self):
        self._jobs: dict[str, RipJob] = {}

    def create_job(self, drive: str, profile: str, destination: str,
                   extraction_mode: str = "fast") -> RipJob:
        job = RipJob(
            id=str(uuid.uuid4())[:12],
            drive=drive, profile=profile, destination=destination,
            extraction_mode=extraction_mode,
            status="created", progress=0.0,
            current_track=0, total_tracks=0,
        )
        self._jobs[job.id] = job
        return job

    def start_job(self, job: RipJob):
        job.status = "running"

    def cancel_job(self, job_id: str):
        job = self._jobs.get(job_id)
        if job:
            job.status = "cancelled"

    def get_progress(self, job_id: str) -> dict:
        job = self._jobs.get(job_id)
        if job:
            return {
                "job_id": job.id, "status": job.status,
                "progress": job.progress, "current_track": job.current_track,
                "total_tracks": job.total_tracks,
            }
        return {}

    def get_job(self, job_id: str) -> RipJob | None:
        return self._jobs.get(job_id)
