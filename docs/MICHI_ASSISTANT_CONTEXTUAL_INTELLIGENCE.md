# Michi Assistant — Contextual Intelligence Layer

## Objetivo

Proveer una capa de inteligencia contextual local que permita a Michi Assistant saber en qué sección está el usuario, qué elemento tiene seleccionado, qué acciones son posibles y qué sugerencias ofrecer, todo sin llamar a Ollama para acciones simples.

## Arquitectura

```
UI Layer
├── ContextSuggestionBar (ui/assistant/context_suggestion_bar.py)
├── SuggestionCard (ui/assistant/suggestion_card.py)
└── EcosystemPage (ui/ecosystem/)

Contextual Intelligence Layer
├── SectionContextProvider (core/context/section_context_provider.py)
├── SectionContextRegistry (core/context/section_context_registry.py)
├── 10 providers (core/context/providers/*.py)
├── ContextualSuggestionEngine (integrations/ai_assistant/contextual_suggestion_engine.py)
├── IntentRouter (integrations/ai_assistant/intent_router.py)
└── PromptContextBuilder (integrations/ai_assistant/prompt_context_builder.py)

Michi Assistant Core
├── AIAssistantService (integrations/ai_assistant/service.py)
├── ToolRegistry (integrations/ai_assistant/tool_registry.py)
├── OllamaClient (integrations/ai_assistant/ollama_client.py)
└── Permissions (integrations/ai_assistant/permissions.py)
```

## Providers (10)

| Provider | Section Key | Contexto |
|----------|-------------|----------|
| LibraryContextProvider | library_hub | tracks, albums, artists, genres, lossless/hires/lossy counts |
| AudioLabContextProvider | audio_lab | analysis status, missing features, conversion availability |
| MixContextProvider | mix_hub | library health, favorites, history sufficiency |
| PlaylistContextProvider | playlists | playlist count, total tracks |
| PlaybackContextProvider | playback_hub | now playing, queue length, source |
| ConnectionsContextProvider | connections_hub | sync active, paired devices, micro server config |
| DevicesContextProvider | devices | device count, paired devices list |
| MetadataContextProvider | metadata_editor | missing metadata, missing genre/year counts |
| HomeAudioContextProvider | home_audio | snapcast active, zones, clients |
| SettingsContextProvider | settings | ollama model, sync/analysis enabled, offline_strict |

## Privacidad

- Todos los snapshots pasan por sanitize_snapshot()
- Las sugerencias nunca llaman a Ollama
- Los providers solo acceden a servicios existentes (nunca a widgets)
