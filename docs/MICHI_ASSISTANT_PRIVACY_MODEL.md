# Michi Assistant — Privacy Model

## Principios Absolutos

1. Local por defecto -> Ollama en localhost:11434
2. Sin datos a internet -> No telemetria, no servicios cloud
3. Sin rutas absolutas -> sanitize_snapshot() elimina paths
4. Sin filepaths -> Las tools nunca devuelven rutas
5. Sin biblioteca completa -> Solo conteos y metadata agregada
6. Sin archivos de audio -> Las tools reciben features, no archivos
7. Sin tokens ni secretos -> No se incluyen en prompts
8. Sin escritura sin confirmacion -> Toda accion requiere PendingAction
9. Sin acceso directo a SQLite desde Ollama -> Solo via tools registradas

## Niveles de Permiso

| Nivel | Ejemplos | Confirmacion |
|-------|----------|-------------|
| READ_ONLY | search, stats, diagnose, explain_format | Ninguna |
| REVERSIBLE | create_playlist, add_to_queue, apply_config_plan | Simple |
| RESOURCE_INTENSIVE | analyze_track_audio | Simple |

## Capas de Sanitizacion

1. ContextService -> sanitize_snapshot() en events y snapshots
2. PrivacyFilter -> sanitize_media_item(), sanitize_text(), sanitize_for_prompt()
3. PromptContextBuilder -> Construccion manual de prompts sin datos crudos
4. ToolRegistry -> Permission-gated execution

## Datos que NUNCA salen

- Rutas absolutas, URIs completas, Tokens de API
- Contrasenas, Claves de pairing, Bibliotecas completas
- Archivos de audio, Configuracion del sistema
