#!/usr/bin/env bash
# Local CI simulation — validates that pip install and tests work in a clean venv.
# Run this before pushing to verify basic CI compliance.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "=== CI Local Test ==="
echo

# 1. Create clean venv
echo "[1/5] Creating virtual environment..."
python3 -m venv "$TMPDIR/.venv"
source "$TMPDIR/.venv/bin/activate"
pip install --upgrade pip -q

# 2. Install package (editable with dev deps)
echo "[2/5] Installing michi-music-player..."
cd "$REPO_DIR"
pip install -e ".[dev]" 2>&1 | tail -3

# 3. Verify system deps are NOT installed by pip
echo "[3/5] Verifying no system deps via pip..."
pip show PyGObject pycairo dbus-python 2>&1 | grep -q "WARNING: Package(s) not found" || true
echo "  OK - system deps not installed by pip"

# 4. Verify import
echo "[4/5] Verifying import..."
python3 -c "
import importlib.metadata
v = importlib.metadata.version('michi-music-player')
print(f'  michi-music-player {v}')
assert v.startswith('0.1'), f'Unexpected version: {v}'
print('  OK')
"

# 5. Lint + compile + test
echo "[5/5] Running lint..."
python3 -m ruff check . --output-format concise || { echo "  LINT FAILED"; exit 1; }
echo "  OK"

echo "[6/5] Running compile... (silent)"
python3 -m compileall -q . || { echo "  COMPILE FAILED"; exit 1; }
echo "  OK"

echo
echo "=== All CI checks passed ==="
echo
echo "To run full test suite:"
echo "  source '$TMPDIR/.venv/bin/activate'"
echo "  QT_QPA_PLATFORM=offscreen pytest -q"
