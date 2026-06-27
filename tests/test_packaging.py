"""Tests for pyproject.toml packaging integrity."""
import os
import sys

import pytest


class TestPyProjectPackaging:
    @pytest.fixture
    def pyproject(self):
        repo_root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(repo_root, "pyproject.toml")
        assert os.path.exists(path), f"pyproject.toml not found at {path}"
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            import tomli as tomllib
        with open(path, "rb") as f:
            return tomllib.load(f)

    def test_no_system_only_deps_in_pip(self, pyproject):
        """PyGObject, pycairo, dbus-python must NOT be in pip dependencies.

        These packages cannot be installed via pip and must come from the
        system package manager. They should not appear in [project.dependencies]."""
        deps = pyproject["project"]["dependencies"]
        for dep in deps:
            dep_name = dep.split(">")[0].split("<")[0].split("=")[0].strip()
            assert not dep_name.startswith("PyGObject"), \
                f"PyGObject found in pip dependencies: {dep}"
            assert not dep_name.startswith("pycairo"), \
                f"pycairo found in pip dependencies: {dep}"
            assert not dep_name.startswith("dbus-python"), \
                f"dbus-python found in pip dependencies: {dep}"

    def test_core_deps_present(self, pyproject):
        """Core pip-installable deps must be present."""
        deps = pyproject["project"]["dependencies"]
        dep_names = [d.split(">")[0].split("<")[0].split("=")[0].strip() for d in deps]
        assert "PySide6" in dep_names, "PySide6 missing from dependencies"
        assert "mutagen" in dep_names, "mutagen missing from dependencies"
        assert "numpy" in dep_names, "numpy missing from dependencies"

    def test_python_min_311(self, pyproject):
        """Requires-Python must be >=3.11."""
        req = pyproject["project"]["requires-python"]
        assert req == ">=3.11", f"requires-python should be >=3.11, got {req}"

    def test_no_python_310_classifier(self, pyproject):
        """Python 3.10 classifier should not be present."""
        classifiers = pyproject["project"]["classifiers"]
        for c in classifiers:
            assert "3.10" not in c, f"Python 3.10 classifier found: {c}"
