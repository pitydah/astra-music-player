"""Tests for LibraryOrganizeService."""
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from library.library_organize_service import (
    LibraryOrganizeService, OrganizeChange, OrganizePlan, OrganizePreview,
)


class TestDetectSidecars:
    def test_found(self):
        with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as f:
            pass
        base = f.name
        sc = os.path.splitext(base)[0] + ".cue"
        Path(sc).write_text("sidecar")
        try:
            assert LibraryOrganizeService._detect_sidecars(base)
        finally:
            Path(base).unlink(missing_ok=True)
            Path(sc).unlink(missing_ok=True)

    def test_not_found(self):
        assert LibraryOrganizeService._detect_sidecars("/nope.flac") == []


class TestFindRoot:
    def test_found(self):
        assert LibraryOrganizeService._find_root("/m/a/t.flac", ["/m"]) == "/m"

    def test_not_found(self):
        assert LibraryOrganizeService._find_root("/o/f.flac", ["/m"]) is None


class TestPreview:
    def test_collisions(self):
        svc = LibraryOrganizeService()
        p = svc.preview([
            OrganizeChange(old_path="/a.flac", new_path="/x.flac"),
            OrganizeChange(old_path="/b.flac", new_path="/x.flac"),
        ])
        assert p.collisions

    def test_empty(self):
        assert LibraryOrganizeService().preview([]).total_size == 0


class TestValidate:
    def test_valid(self):
        assert LibraryOrganizeService().validate(OrganizePreview())

    def test_invalid(self):
        assert not LibraryOrganizeService().validate(
            OrganizePreview(collisions=["/x.flac"]))


class TestExecute:
    def test_success(self):
        m = MagicMock()
        m.update_filepath.return_value = MagicMock(errors=[])
        svc = LibraryOrganizeService(mutation_service=m)
        with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as f:
            old = f.name
            f.write(b"test")
        new = old + ".moved"
        plan = OrganizePlan(changes=[OrganizeChange(old_path=old, new_path=new)],
                            library_roots=[os.path.dirname(old)], preview=OrganizePreview())
        r = svc.execute(plan)
        assert r.applied == 1
        Path(old).unlink(missing_ok=True)
        Path(new).unlink(missing_ok=True)

    def test_failure(self):
        svc = LibraryOrganizeService()
        plan = OrganizePlan(changes=[OrganizeChange(old_path="/nope.flac", new_path="/x.flac")],
                            library_roots=["/"], preview=OrganizePreview())
        assert svc.execute(plan).failed > 0
