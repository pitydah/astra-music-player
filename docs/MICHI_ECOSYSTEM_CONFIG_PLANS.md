# Michi Ecosystem — Configuration Plans

## Ciclo de Vida
1. Crear -> create_ecosystem_config_plan(plan_type) -> plan_id
2. Previsualizar -> preview_ecosystem_config_plan(plan_id) -> cambios
3. Aplicar -> apply_ecosystem_config_plan(plan_id, confirmed=True) -> ejecuta
4. Revertir -> rollback_ecosystem_config_plan(plan_id, confirmed=True) -> deshace

## Planes Disponibles
| Plan | Cambio | Riesgo |
|------|--------|--------|
| setup_mobile_sync | sync/enabled: false -> true | Bajo |
| setup_micro_server_remote | michi_link/streaming_profile: "" -> "remote" | Bajo |
| setup_mobile_space_saver_profile | sync/mobile_profile: "" -> "space_saver" (Opus 128k) | Bajo |
| setup_hifi_profile | audio/output_profile: "" -> "hifi_pcm" | Bajo |
| setup_remote_light_streaming_profile | michi_link/streaming_profile: "" -> "remote_light" | Bajo |

## Seguridad
- confirmed=False siempre deniega
- Todos los planes son reversibles
- Solo modifican settings, no archivos ni sistema
