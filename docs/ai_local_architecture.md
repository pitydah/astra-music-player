# AI Local Architecture — Privacy-First Music Assistant Design

## Principle: The AI never touches the internet

All external data flows through a MetadataBroker that enforces privacy rules.

## MetadataBroker (future implementation)

### Allowed sources (allowlist)
- MusicBrainz (artist, album, release metadata)
- Cover Art Archive (album covers by MBID)
- Wikipedia / Wikidata (artist bios, images)
- ListenBrainz (optional, user opt-in)

### Forbidden
- No general web search
- No AI model calling external APIs directly
- No user listening history sent anywhere
- No local file paths in external requests
- No audio fingerprint data sent without user consent

### Rules
1. **Allowlist only** — requests go only to pre-approved endpoints
2. **No paths** — external requests use MBIDs and names, never filepaths
3. **No history** — listening history stays local
4. **Cache everything** — external results cached locally, shared across sessions
5. **Sanitize** — text from external sources is sanitized before use
6. **Offline mode** — `artist_enrichment/offline_strict` blocks all external access
7. **Rate limit** — respects MusicBrainz 1 req/s, Cover Art Archive policies
8. **User consent** — ListenBrainz and any analytics require explicit opt-in

### AI constraints (when implemented)
- The AI model runs **locally** (no cloud API)
- The AI's tools **call the MetadataBroker**, never the internet directly
- The AI **cannot**:
  - Delete files
  - Edit metadata without user confirmation
  - Read authentication tokens
  - Receive the full library (only metadata relevant to the current context)
  - Receive absolute file paths

### Future integration points
- `core/metadata_broker.py` — implements the allowlist broker
- `core/ai_constraints.py` — rules engine for AI tool permissions
- Settings: `ai/enabled`, `ai/model_path`, `ai/local_only`

## Current state (June 2026)

Astra has no AI integration. The enrichment pipeline already respects:
- `artist_enrichment/enabled` — master switch
- `artist_enrichment/online_enabled` — blocks all HTTP when false
- `artist_enrichment/coverart_enabled` — blocks Cover Art Archive
- `artist_enrichment/offline_strict` — blocks everything external

These settings provide the foundation for safe AI integration.
