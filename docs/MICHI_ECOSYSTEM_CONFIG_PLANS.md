# Michi Ecosystem — Configuration Plans

## Ciclo de Vida
1. Crear → `create_ecosystem_config_plan(plan_type)` → `plan_id`
2. Previsualizar → `preview_ecosystem_config_plan(plan_id)` → cambios
3. Aplicar → `apply_ecosystem_config_plan(plan_id, confirmed=True)` → ejecuta
4. Revertir → `rollback_ecosystem_config_plan(plan_id, confirmed=True)` → deshace

## Planes Disponibles
| Plan | Cambio | Riesgo |
|------|--------|--------|
| `setup_mobile_sync` | Activar sync | Bajo |
| `setup_micro_server_remote` | Perfil remoto | Bajo |
| `setup_tailscale_streaming` | Opus para Tailscale | Bajo |
| `setup_mobile_space_saver_profile` | Opus 128k | Bajo |
| `setup_hifi_profile` | Perfil Hi-Fi | Bajo |
| `setup_home_audio` | Activar HA + Snapcast | Bajo |

## Seguridad
- `confirmed=False` siempre deniega
- Todos los planes son reversibles
- Solo modifican settings, no archivos ni sistema
- No se ejecutan comandos del sistema
