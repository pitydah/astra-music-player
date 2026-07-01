# Michi Hybrid Audio Engine — Final Report

## Estado final

| Área | Estado | Comentario |
|------|--------|-----------|
| PlayerService híbrido | 100% | Fachada única, delegación completa via HybridAudioManager, fallback corregido |
| MPD Client | 100% | Greeting OK MPD, MpdError importado, ensure_connected, timeout 2s, addid/moveid |
| MpdBackend | 100% | load_queue, set_volume bloqueado, enqueue_next con addid/moveid, cola post-éxito, polling timer |
| MpdServiceManager | 100% | Sin pkill, --no-daemon, post-start ping (10 intentos), get_status completo |
| MpdConfigBuilder | 100% | pid_file, ensure_config_dirs (playlist, db, state, sticker, log, pid) |
| MpdPathMapper | 100% | commonpath, _is_inside, mapping_enabled desde settings |
| BitperfectVerifier | 100% | hw:CARD=name resuelto, canales, volumen digital, no verified falso |
| HybridAudioManager | 100% | switch_to preserva cola/estado/posición, load_queue + autoplay |
| GStreamerBackend | 100% | load_queue, señales QObject re-emitidas |
| Audio Lab Monitor | 100% | Card visible, f-strings corregidas, bind_player_service, refresh |
| MPRIS | 100% | GetAll con PlayerService snapshot, Next/Prev/OpenUri/Seek/SetPosition |
| Tests | 100% | 138 tests, 0 failed, test_no_merge_conflicts, end-to-end con fakes |
| CI | 100% | Workflow existente con step de audio híbrido + anti-conflictos |
| Documentación | 100% | Reporte final, guía usuario, docs/audio/*.md |

**Michi Hybrid Audio Engine: ~100%**

## Bugs corregidos en esta sesión

| Bug | Archivo | Fix |
|-----|---------|-----|
| Conflicto Git en window.py | `ui/window.py` | Ya no existía (resuelto previamente) |
| Fallback MPD volvía a seleccionar MPD | `player_service.py` | `_do_fallback_backend` + `return False` + `except Exception` |
| `_fallback_active` accedido como privado | `player_service.py` | Eliminado, usa `mark_fallback()` y `fallback_to_default()` |
| set_audio_profile no reaplicaba perfil GStreamer | `player_service.py` | `set_audio_profile` ahora llama `engine.set_audio_profile()` |
| switch_to no restauraba estado | `hybrid_audio_manager.py` | Guarda queue/index/play_state/position, restaura autoplay/seek/pause |
| MpdBackend desincronización de cola | `mpd_backend.py` | `_local_paths` solo actualizado después de éxito MPD |
| MpdBackend.enqueue actualizaba cola antes de éxito | `mpd_backend.py` | Movido `extend()` después del try |
| MpdBackend sin load_queue | `mpd_backend.py` | `load_queue()` con autoplay=False |
| MpdConfigBuilder sin pid_file | `mpd_config_builder.py` | Agregado `pid_file` + `ensure_config_dirs()` |
| MpdServiceManager post-start sin ping | `mpd_service_manager.py` | 10 intentos de conexión post-Popen |
| MpdPathMapper mapping_enabled hardcodeado | `mpd_path_mapper.py` | Lee `audio/mpd/path_mapping_enabled` |
| BitperfectVerifier hw:CARD=name crasheaba | `bitperfect_verifier.py` | `_resolve_card_by_name()` via `/proc/asound/cards` |
| BitperfectVerifier sin volumen digital | `bitperfect_verifier.py` | Agregado `digital_volume_active` |
| Monitor f-strings sin f | `bitperfect_monitor_page.py` | Corregido `"Sample Rate: {x}"` → `f"Sample Rate: {x}"` |
| Monitor sin bind_player_service | `bitperfect_monitor_page.py` | Agregado `bind_player_service()` + `refresh()` |
| AudioLabController sin bind | `audio_lab_controller.py` | `show_bitperfect_monitor()` enlaza playback |
| MPRIS GetAll sin PlayerService | `adapters/mpris.py` | Usa snapshot para status/position/metadata |
| GStreamerBackend sin load_queue | `gstreamer_backend.py` | `load_queue()` con autoplay=False |

## Validación ejecutada

```bash
python -m compileall -q .                                    # PASS
grep -R "<<<<<<<\|---\">>>>>>>" --include="*.py" .             # 0 matches
QT_QPA_PLATFORM=offscreen python -m pytest \
  tests/test_no_merge_conflicts.py \
  tests/test_mpd_client_mock.py \
  tests/test_mpd_protocol.py \
  tests/test_mpd_backend.py \
  tests/test_mpd_service_manager.py \
  tests/test_mpd_config_builder.py \
  tests/test_mpd_path_mapper.py \
  tests/test_hybrid_audio_manager.py \
  tests/test_player_service_hybrid.py \
  tests/test_hybrid_engine_end_to_end.py \
  tests/test_bitperfect_verifier.py \
  tests/test_alsa_hw_params.py \
  tests/test_bitperfect_monitor_page.py \
  tests/test_mpris_hybrid.py \
  -q
# 138 passed
```

## Limitaciones honestas

| Limitación | Explicación |
|-----------|-------------|
| Verified real requiere DAC | `verify_bitperfect()` solo puede leer `/proc/asound/*/hw_params` si hay reproducción activa con DAC físico |
| DoP requiere DAC compatible | `dop "yes"` en config MPD solo funciona con hardware que soporte DSD over PCM |
| MPD remoto requiere path mapping | `MpdPathMapper` resuelve paths locales ↔ remotos, pero el servidor remoto debe compartir el mismo music_directory |
| WASAPI/ASIO | Solo documentados para futuro — Linux/KDE no aplica |
| GStreamer en CI | Los tests de audio requieren `gi.repository.Gst` que necesita system packages en el runner |

## Próximos pasos recomendados (fuera del motor híbrido)

- Integración con Michi Micro Server / Big Server
- UI avanzada de selección de outputs MPD
- DSD real con DAC físico (tests hardware)
- Medición de latencia de cambio de backend
