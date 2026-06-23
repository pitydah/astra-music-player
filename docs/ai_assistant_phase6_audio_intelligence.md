# Michi Assistant — Fase 6: Experimental Local Audio Intelligence

## Objetivo

Analisis acustico local, opcional y controlado para mejorar recomendaciones, busqueda por sonido y smart mixes en Michi Music Player. Sin enviar audio, rutas ni metadata privada fuera del equipo.

## Arquitectura

```
audio_analysis/
├── analysis_service.py      — Orchestrates extraction, similarity, cache
├── feature_extractor.py     — Dual backend: basic (numpy/tags) + librosa
├── feature_repository.py    — SQLite: audio_features.db
├── similarity_index.py      — Acoustic distance (BPM, energy, timbre)
├── acoustic_profile.py      — Heuristic classification (calm, energetic, etc.)
├── dependency_check.py      — Detects available backends
├── schemas.py               — AudioFeature, SimilarityResult, etc.
└── migrations/001.sql       — 4 tables
```

## Dual Backend

| Backend | Dependencias | Features |
|---------|-------------|----------|
| **basic** (default) | numpy (ya instalado) | BPM (tag), energy (replaygain), dynamic_range, duration |
| **librosa** (opcional) | `librosa>=0.10`, `soundfile>=0.12` | BPM real, energy, spectral centroid/rolloff, ZCR, MFCC, chroma |

## Features extraidas

| Feature | Basic | Librosa |
|---------|-------|---------|
| BPM | Tag (ID3/Vorbis) | Analisis real |
| BPM confidence | 0.5 | 0.85 |
| Energy | ReplayGain → heuristic | RMS del signal |
| Dynamic range | ReplayGain peak - gain | RMS + peak |
| Spectral centroid | — | librosa.feature |
| Spectral rolloff | — | librosa.feature |
| Zero crossing rate | — | librosa.feature |
| MFCC (13-dim) | — | librosa.feature.mfcc |
| Chroma (12-dim) | — | librosa.feature.chroma_stft |

## Privacidad

- **El audio nunca sale del proceso.** El extractor lee el archivo, extrae features, descarta el audio.
- **La DB guarda track_key hasheado** (SHA-256[:16]), nunca filepath.
- **El LLM recibe**: `{bpm: 124, energy_bucket: "high", acoustic_labels: ["energetic", "bright"]}`
- **El LLM NUNCA recibe**: `filepath`, `mfcc_json`, `chroma_json`, samples de audio, vectores completos.

## Settings

| Key | Default | Descripcion |
|-----|---------|-------------|
| `audio_analysis/enabled` | false | Enable analysis |
| `audio_analysis/use_librosa` | false | Use librosa if installed |
| `audio_analysis/use_embeddings` | false | Embeddings (Fase 7) |
| `audio_analysis/auto_analyze` | false | Auto-analyze new tracks |
| `audio_analysis/max_batch` | 50 | Max tracks per batch |
| `audio_analysis/sample_duration` | 90 | Seconds to analyze |
| `ai_assistant/use_audio_analysis` | false | AI can use analysis |
| `recommendation/use_acoustic_similarity` | false | Use acoustic in recommendations |

## Tools (7 expuestas al AI Assistant)

| Tool | Permission | Descripcion |
|------|-----------|-------------|
| `get_audio_analysis_status` | READ_ONLY | Backend, analyzed count, pending jobs |
| `explain_acoustic_features` | READ_ONLY | BPM, energy, acoustic labels |
| `find_sonically_similar` | READ_ONLY | Tracks that sound similar |
| `create_acoustic_mix` | READ_ONLY | Acoustic smart mix |
| `list_tracks_missing_features` | READ_ONLY | Tracks without analysis |
| `analyze_track_audio` | RESOURCE_INTENSIVE | Analyze one track (CPU confirmation) |
| `analyze_selected_tracks` | RESOURCE_INTENSIVE | Batch analysis (CPU confirmation) |

## MICHI_SAFE_MODE

When `MICHI_SAFE_MODE=1`, `AnalysisService.enabled` returns False. No new analysis jobs are created. Cached features remain readable but no new extraction occurs.

## Limitaciones

- **Sin embeddings neuronales**: MFCC/chroma son features clasicas de DSP, no requieren redes neuronales.
- **Backend basic es muy limitado**: Solo BPM tag + ReplayGain + duracion. Poco preciso.
- **CPU consumption**: Librosa puede consumir CPU significativa. El analisis se ejecuta en background via WorkerManager (max 1 worker por defecto).
- **Large files**: Solo se analizan los primeros `sample_duration` segundos (default 90s).

## Instalacion opcional (librosa)

```bash
pip install librosa soundfile
```

## What Phase 6 does NOT do

- Fingerprinting / Shazam-like identification
- Upload of audio or features
- Neural models (CLAP, etc.)
- Automatic metadata writing
- File renaming, moving, deletion
- Internet access for analysis
