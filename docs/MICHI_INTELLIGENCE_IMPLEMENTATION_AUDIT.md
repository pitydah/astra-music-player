# Michi Intelligence Core — Implementation Audit

## Estado actual

### Home / Centro de Situación Michi (100%)
- `HomeDashboardService` completamente estabilizado
- Builders separados por responsabilidad en `core/home/builders/`
- Settings keys correctas: `audio/profile`, `audio/replaygain_enabled`, `home_audio/michi_api_enabled`
- Playback state normalizado (string/enum/None → playing/paused/stopped/unknown)
- Micro Server separado de servidores remotos (Subsonic/Navidrome/Jellyfin)
- Home Audio usa `get_str("home_audio/ha_base_url")` y `get_bool("home_audio/enabled")`
- `_safe_build` tolera fallos parciales por card
- `_safe_float_attr` soporta múltiples nombres de atributo/método
- Queue no expone paths
- Alertas con severidad correcta

### Michi Ecosystem Doctor (95%)
- `MichiEcosystemDoctor` creado como fachada sobre Michi Link
- Reusa `DiagnosticsService`, `MicroServerService`, `PlayerMicroCompatibilityReport`
- Constants centralizadas en `constants.py`
- Sanitizer robusto (tokens, paths, strings largos, dataclasses)
- `diagnose_micro_server()` con 3 fuentes: michi_link_ctrl, host explícito, settings
- `diagnose_home_audio()` soporta HA client real y snapcast_manager
- `diagnose_assistant_runtime()` con validación de localhost
- Pendiente: integración con michi_link_ctrl real

### Michi Assistant contextual (90%)
- `allowed_actions.py` con acciones por sección
- `contextual_suggestion_engine.py` sin llamadas a Ollama
- `intent_router.py` con reglas híbridas
- `prompt_context_builder.py` con sanitización
- Tools: ecosystem_tools (10), audio_conversion_tools (5)
- Registradas en AIAssistantService
- Pendiente: wiring completo de suggestion bar en UI

### UI Michi Ecosystem (85%)
- `EcosystemPage` con health panel, device/issue/plan cards
- `EcosystemController` con wiring de botones y diagnóstico
- `ContextSuggestionBar` + `SuggestionCard` creados
- `SuggestionBarController` integrado en `HubRouteController._lazy()`
- Pendiente: botones de EcosystemPage conectados visualmente

### Privacidad y seguridad (100%)
- No se envían datos a internet
- Ollama bloqueado a localhost
- Sanitizer elimina tokens, paths, contraseñas
- apply/rollback requieren confirmed=True
- Tools de conversión solo recomiendan

### Tests (95%)
- 214 tests pasan
- Home: 58 tests
- Ecosystem Doctor: 21 tests nuevos
- Assistant: ~76 tests
- Context: ~59 tests
- Pendiente: tests de UI smoke

## Riesgos
- `album_controller.py` tiene error de sintaxis preexistente
- `conversion_page.py` tiene F821 (QMessageBox no importado) preexistente
- No hay CI/CD para detectar regresiones automáticamente

## Decisiones de implementación
1. No se duplicó Michi Link — se creó fachada
2. No se creó otro DiagnosticsService
3. HomeDashboardService refactorizado sin romper API pública
4. Builders son funciones, no clases (simplicidad)
5. Settings keys validadas contra `core/settings_manager.py`
