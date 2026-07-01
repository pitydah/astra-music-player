# Michi Home / Centro de Situación

## Objetivo

Mostrar un dashboard de un vistazo con el estado real de la aplicación y del ecosistema Michi.

## Arquitectura

```
HomePage (ui/hubs/home_page.py)
  └── HomeController (ui/controllers/home_controller.py)
       └── HomeDashboardService (core/home/home_dashboard_service.py)
            ├── LibraryHomeBuilder
            ├── PlaybackHomeBuilder
            ├── AudioHomeBuilder
            ├── EcosystemHomeBuilder → MichiEcosystemDoctor
            ├── AlertsHomeBuilder
            ├── AssistantSuggestionsHomeBuilder
            └── ActionsHomeBuilder
```

## Servicios reutilizados

- ContextService (`core/context/`)
- DiagnosticsService (`integrations/michi_link/services/`)
- MicroServerService
- Sync Manager
- Settings Manager (`core/settings_manager.py`)

## Privacidad

- No se exponen rutas absolutas
- No se exponen tokens
- No se exponen contraseñas
- Los snapshots se sanitizan automáticamente
