"""Pytest configuration for E2E tests — real Micro Server mode."""
from __future__ import annotations

import os

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--real-micro",
        action="store_true",
        default=False,
        help="Run tests against a real Micro Server instead of mocks",
    )


@pytest.fixture(scope="session")
def micro_server_config(request):
    """Return Micro Server connection config from env vars or None."""
    real = request.config.getoption("--real-micro")
    if not real:
        return None

    host = os.environ.get("MICHI_MICRO_TEST_URL", "")
    port = int(os.environ.get("MICHI_MICRO_PORT", "53318"))
    token = os.environ.get("MICHI_MICRO_TOKEN", "")
    device_id = os.environ.get("MICHI_MICRO_DEVICE_ID", "")

    if not host:
        raise pytest.UsageError(
            "--real-micro requires MICHI_MICRO_TEST_URL environment variable")

    from integrations.michi_link.client import RemoteServerInfo
    return RemoteServerInfo(
        host=host,
        port=port,
        alias="MicroServer",
        server_device_id=device_id or f"micro_{host}",
        requires_pairing=bool(token),
        device_token=token,
        device_id=device_id or "player_e2e",
    )
