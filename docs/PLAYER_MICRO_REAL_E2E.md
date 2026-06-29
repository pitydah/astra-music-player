# Player ↔ Micro Server Real E2E Testing

## Overview

This document describes how to run compatibility tests against a **real** Michi Micro Server.

## Prerequisites

- A running Michi Micro Server reachable on the network
- (Optional) A paired device token for authenticated endpoints

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MICHI_MICRO_TEST_URL` | **Yes** | — | IP or hostname of the Micro Server |
| `MICHI_MICRO_PORT` | No | `53318` | HTTP port |
| `MICHI_MICRO_TOKEN` | No | `""` | Paired device token (Bearer auth) |
| `MICHI_MICRO_DEVICE_ID` | No | `player_e2e` | X-Michi-Device-Id header value |

## Quick start

```bash
# Set environment
export MICHI_MICRO_TEST_URL=192.168.1.100
export MICHI_MICRO_PORT=53318
export MICHI_MICRO_TOKEN="your_paired_token"
export MICHI_MICRO_DEVICE_ID="player_e2e"

# Run all real-micro tests
python -m pytest tests/e2e/test_real_micro_compatibility.py --real-micro -v

# Run specific check
python -m pytest tests/e2e/test_real_micro_compatibility.py \
  -k "test_supports_preflight" --real-micro -v
```

## Report

After running the tests, a JSON report is saved to:

```
reports/player_micro_compatibility_report.json
```

Example report:

```json
{
  "server_info": {
    "alias": "MicroServer",
    "features": { "library": true, ... }
  },
  "preflight": {
    "status": "CONTRACT_OK",
    "format": "new"
  },
  "upload_mapping": {
    "status": "CONTRACT_OK",
    "returns_mapping": true
  },
  "commit_mapping": {
    "status": "ENDPOINT_MISSING",
    "fallback": "local commit only"
  },
  "queue_transfer": {
    "status": "CONTRACT_OK"
  },
  "remote_playback_confirmation": {
    "status": "CONTRACT_OK",
    "state_field": "state"
  }
}
```

## Status codes

| Code | Meaning |
|------|---------|
| `CONTRACT_OK` | Endpoint exists and returns expected format |
| `CONTRACT_PARTIAL` | Endpoint exists but legacy/alternative format |
| `CONTRACT_MISMATCH` | Endpoint exists but unexpected response format |
| `ENDPOINT_MISSING` | Endpoint returns 404 |
| `FALLBACK_AVAILABLE` | Endpoint returns 404, fallback method exists |

## Files

| File | Purpose |
|------|---------|
| `tests/e2e/test_real_micro_compatibility.py` | Real Micro Server test runner |
| `tests/e2e/conftest.py` | `--real-micro` flag + env var parsing |
| `reports/player_micro_compatibility_report.json` | Generated report output |
| `integrations/michi_link/services/compatibility_report.py` | `PlayerMicroCompatibilityReport` service |
