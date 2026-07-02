"""LibraryOrganizeService — safe, tracked file organization with rollback."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

from library.library_mutation_service import LibraryMutationService

logger = logging.getLogger("michi.library_organize")


@dataclass
class OrganizeChange:
    old_path: str
    new_path: str
    sidecars: list[str] = field(default_factory=list)
    status: str = "pending"


@dataclass
class OrganizePreview:
    changes: list[OrganizeChange] = field(default_factory=list)
    collisions: list[str] = field(default_factory=list)
    cross_root: list[str] = field(default_factory=list)
    total_size: int = 0


@dataclass
class OrganizeResult:
    applied: int = 0
    failed: int = 0
    rolled_back: int = 0
    errors: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)


@dataclass
class OrganizePlan:
    changes: list[OrganizeChange]
    library_roots: list[str]
    preview: OrganizePreview


class LibraryOrganizeService:
    _SIDECAR_EXTS = {".cue", ".log", ".m3u", ".jpg", ".jpeg", ".png", ".gif",
                     ".bmp", ".tiff", ".tif", ".pdf", ".txt", ".md"}

    def __init__(self, db=None, mutation_service: LibraryMutationService | None = None,
                 safe_ops=None):
        self._db = db
        self._mutation = mutation_service
        self._safe_ops = safe_ops

    def preview(self, changes: list[OrganizeChange],
                library_roots: list[str] | None = None) -> OrganizePreview:
        preview = OrganizePreview()
        seen_targets: set[str] = set()
        for change in changes:
            change.sidecars = self._detect_sidecars(change.old_path)
            preview.total_size += 1
            if change.new_path in seen_targets:
                preview.collisions.append(change.new_path)
            seen_targets.add(change.new_path)
            if os.path.exists(change.new_path):
                preview.collisions.append(f"target exists: {change.new_path}")
            if library_roots:
                old_root = self._find_root(change.old_path, library_roots)
                new_root = self._find_root(change.new_path, library_roots)
                if old_root != new_root:
                    preview.cross_root.append(
                        f"{change.old_path} -> {change.new_path}")
            preview.changes.append(change)
        return preview

    def validate(self, preview: OrganizePreview) -> bool:
        return not preview.collisions

    def execute(self, plan: OrganizePlan) -> OrganizeResult:
        result = OrganizeResult()
        completed: list[tuple[str, str]] = []

        for change in plan.changes:
            try:
                for sidecar in change.sidecars:
                    new_side = os.path.join(
                        os.path.dirname(change.new_path),
                        os.path.basename(sidecar))
                    try:
                        self._safe_rename(sidecar, new_side)
                    except Exception:
                        pass
                self._safe_rename(change.old_path, change.new_path)
                if self._mutation:
                    sub = self._mutation.update_filepath(change.old_path, change.new_path)
                    if sub.errors:
                        raise RuntimeError(f"DB update failed: {sub.errors[0]}")
                change.status = "done"
                result.applied += 1
                result.changed_paths.extend([change.old_path, change.new_path])
                completed.append((change.old_path, change.new_path))
            except Exception as e:
                change.status = "failed"
                result.failed += 1
                result.errors.append(f"{change.old_path}: {e}")
                for old, new in reversed(completed):
                    try:
                        self._safe_rename(new, old)
                        if self._mutation:
                            self._mutation.update_filepath(new, old)
                    except Exception as rb_e:
                        result.errors.append(f"Rollback failed {new}->{old}: {rb_e}")
                        result.rolled_back += 1
                return result

        if self._mutation and result.applied > 0 and not result.errors:
            try:
                self._mutation.sync_genres()
            except Exception:
                pass

        return result

    def _safe_rename(self, src: str, dst: str):
        import shutil
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)

    @staticmethod
    def _detect_sidecars(filepath: str) -> list[str]:
        base, _ = os.path.splitext(filepath)
        return [base + ext for ext in LibraryOrganizeService._SIDECAR_EXTS
                if os.path.isfile(base + ext)]

    @staticmethod
    def _find_root(filepath: str, roots: list[str]) -> str | None:
        norm = os.path.normpath(filepath)
        for root in roots:
            r = os.path.normpath(root)
            if norm.startswith(r + os.sep) or norm == r:
                return root
        return None
