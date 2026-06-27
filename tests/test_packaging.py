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

    def test_requirements_txt_no_system_deps_active(self):
        """requirements.txt must not have PyGObject/pycairo/dbus-python as active lines."""
        repo_root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(repo_root, "requirements.txt")
        with open(path) as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                pkg_name = stripped.split(">")[0].split("<")[0].split("=")[0].strip()
                assert not pkg_name.startswith("PyGObject"), \
                    f"PyGObject found as active line in requirements.txt: {stripped}"
                assert not pkg_name.startswith("pycairo"), \
                    f"pycairo found as active line in requirements.txt: {stripped}"
                assert not pkg_name.startswith("dbus-python"), \
                    f"dbus-python found as active line in requirements.txt: {stripped}"

    def test_ci_yml_has_pip_install_editable(self):
        """ci.yml must install with pip install -e .[dev]."""
        repo_root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(repo_root, ".github/workflows/ci.yml")
        with open(path) as f:
            content = f.read()
        assert 'pip install -e ".[dev]"' in content, \
            "ci.yml missing pip install -e .[dev]"

    def test_ci_yml_has_gi_require_version(self):
        """ci.yml must verify gi/Gst explicitly."""
        repo_root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(repo_root, ".github/workflows/ci.yml")
        with open(path) as f:
            content = f.read()
        assert 'gi.require_version("Gst", "1.0")' in content, \
            "ci.yml missing gi/Gst verification"

    def test_ci_yml_has_pytest_q(self):
        """ci.yml must run pytest -q."""
        repo_root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(repo_root, ".github/workflows/ci.yml")
        with open(path) as f:
            content = f.read()
        assert "pytest -q" in content, "ci.yml missing pytest -q"

    def test_ci_local_sh_has_system_site_packages(self):
        """ci_local.sh must use --system-site-packages."""
        repo_root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(repo_root, "scripts/ci_local.sh")
        with open(path) as f:
            content = f.read()
        assert "--system-site-packages" in content, \
            "ci_local.sh missing --system-site-packages"

    def test_ci_local_sh_has_gi_require_version(self):
        """ci_local.sh must verify gi/Gst explicitly."""
        repo_root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(repo_root, "scripts/ci_local.sh")
        with open(path) as f:
            content = f.read()
        assert 'gi.require_version("Gst", "1.0")' in content, \
            "ci_local.sh missing gi/Gst verification"

    def test_ci_local_sh_has_pytest_q(self):
        """ci_local.sh must run pytest -q."""
        repo_root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(repo_root, "scripts/ci_local.sh")
        with open(path) as f:
            content = f.read()
        assert "python3 -m pytest -q" in content, \
            "ci_local.sh missing pytest -q"

    def test_ci_local_sh_has_test_env_vars(self):
        """ci_local.sh must set MICHI_TEST_* env vars for pytest."""
        repo_root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(repo_root, "scripts/ci_local.sh")
        with open(path) as f:
            content = f.read()
        assert "MICHI_TEST_DATA_DIR" in content, \
            "ci_local.sh missing MICHI_TEST_DATA_DIR"
        assert "MICHI_TEST_CACHE_DIR" in content, \
            "ci_local.sh missing MICHI_TEST_CACHE_DIR"
        assert "MICHI_TEST_CONFIG_DIR" in content, \
            "ci_local.sh missing MICHI_TEST_CONFIG_DIR"
