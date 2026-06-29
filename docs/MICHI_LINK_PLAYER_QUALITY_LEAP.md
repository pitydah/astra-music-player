# Michi Link — Player Quality Leap

## Overview

This document tracks the quality leap that elevates Michi Music Player from beta-ready to a certified server for Mobile and a real client for Micro Server.

## What was done

### New services layer (integrations/michi_link/services/)

| Service | File | Purpose |
|---------|------|---------|
| MicroServerService | `services/micro_server_service.py` | Discover, pair, library, search, playback, queue |
| ImportToServerService | `services/import_to_server_service.py` | Session-based track import to Micro Server |
| ContinueOnServerService | `services/continue_on_server_service.py` | Queue transfer + remote playback control |
| RemoteLibraryService | `services/remote_library_service.py` | Read-only remote library as browsable source |
| DiagnosticsService | `services/diagnostics_service.py` | Full health report generation |

All services use `ServiceResult` (success/error_code/error_message) — never raise to caller, never depend on Qt.

### E2E tests (tests/e2e/)

| Test file | Tests | Scope |
|-----------|-------|-------|
| `test_mobile_player_flow.py` | 19 | Full Mobile→Player lifecycle |
| `test_player_micro_import_flow.py` | 18 | Full Player→Micro import lifecycle |

### Controller stubs (ui/controllers/michi/)

| Controller | Purpose |
|-----------|---------|
| MichiServerController | Server lifecycle, devices, account |
| MichiImportController | Import from Micro Server |
| MichiContinueController | Handoff playback to Micro Server |

## Contract verified

- No file_path exposed in any v1 response
- All v1 errors use `{error: {code, message, details}}`
- stream supports 200 (no Range), 206 (Range), 404 with details
- artwork supports 200 with mime + Cache-Control, 404
- playback/control accepts `command` (official) and `action` (fallback)
- playback/control seek accepts `position_ms` (official), `seek_ms`/`value` (fallback)
- volume validated to 0-100
- Queue does not expose file_path

## Conservative features

| Feature | Value | Rationale |
|---------|-------|-----------|
| events | false | SSE not implemented |
| token_refresh | false | Not implemented |
| receivers | false | No receiver integration |
| rooms | false | No multi-room |

## Blockers for official beta

1. **Mobile integration test** — actual device testing needed
2. **Micro Server import** — real HTTP round-trip with Micro Server
3. **Continue on Server** — Micro Server must implement /api/v1/queue/transfer
4. **Events/SSE** — low priority, polling works
5. **UI wiring** — connect controllers to window.py menus
