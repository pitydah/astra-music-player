# Michi Ecosystem Doctor

## Objetivo

Diagnosticar, monitorear y configurar el ecosistema Michi completo.

## Arquitectura

integrations/michi_ecosystem/
- ecosystem_models.py -> Dataclasses
- ecosystem_registry.py -> Fachada agregadora
- ecosystem_diagnostics.py -> Diagnostico por servicio
- ecosystem_health_graph.py -> Grafo de salud
- ecosystem_fix_suggester.py -> Sugerencias de fix
- ecosystem_config_planner.py -> Planes de configuracion
- ecosystem_actions.py -> Acciones seguras/confirmables

## Issue Codes

| Code | Significado |
|------|-------------|
| NO_PAIRED_DEVICES | Sin dispositivos emparejados |
| SYNC_STOPPED | Sincronizacion detenida |
| MICRO_UNREACHABLE | Micro Server no responde |
| PAIRING_REQUIRED | Token expirado o no emparejado |

## Planes de Configuracion

| Plan | Descripcion |
|------|-------------|
| setup_mobile_sync | Activar sincronizacion |
| setup_micro_server_remote | Perfil remoto Opus 128-160k |
| setup_mobile_space_saver_profile | Perfil mobile ahorro espacio |
| setup_hifi_profile | Perfil Hi-Fi PCM |
| setup_remote_light_streaming_profile | Opus 128k remoto |

## Seguridad

- apply_plan() requiere confirmed=True
- rollback_plan() requiere confirmed=True
- No se ejecutan comandos del sistema
