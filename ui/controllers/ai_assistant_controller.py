"""AI Assistant controller — bridges UI panel with AIAssistantService (Fase 2)."""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from core.settings_manager import (
    get_bool, get_str, get_int,
)

logger = logging.getLogger("michi.ai_assistant.controller")


class AiAssistantController(QObject):
    state_changed = Signal(str)
    response_received = Signal(object)
    navigate_to = Signal(str)

    def __init__(self, db: Any, worker_manager: Any = None,
                 playback: Any = None,
                 parent: QObject | None = None):
        super().__init__(parent)
        self._db = db
        self._worker_mgr = worker_manager
        self._playback = playback
        self._service = None
        self._pending = False

    def is_enabled(self) -> bool:
        return get_bool("ai_assistant/enabled")

    def model(self) -> str:
        return get_str("ai_assistant/model") or "llama3.1:8b"

    def base_url(self) -> str:
        return get_str("ai_assistant/base_url") or "http://127.0.0.1:11434"

    def _get_service(self):
        if self._service is not None:
            return self._service

        from integrations.ai_assistant.service import AIAssistantService

        self._service = AIAssistantService(
            db=self._db,
            model=self.model(),
            base_url=self.base_url(),
            save_history=get_bool("ai_assistant/save_history"),
            max_results=get_int("ai_assistant/max_results") or 30,
            allow_write=get_bool("ai_assistant/allow_write_actions"),
            offline_strict=get_bool("ai_assistant/offline_strict"),
            ollama_timeout=get_int("ai_assistant/ollama_timeout") or 30,
            playback=self._playback,
            allow_reversible=get_bool("ai_assistant/allow_reversible_actions"),
            require_confirmation=get_bool("ai_assistant/require_confirmation"),
            action_log_enabled=get_bool("ai_assistant/action_log_enabled"),
            max_action_tracks=get_int("ai_assistant/max_action_tracks") or 100,
            max_playlist_tracks=get_int("ai_assistant/max_playlist_draft_tracks") or 50,
        )
        return self._service

    def check_health(self) -> bool:
        try:
            svc = self._get_service()
            return svc.ollama_available
        except Exception:
            return False

    def send_message(self, text: str):
        if self._pending:
            return
        if not text.strip():
            return
        self._pending = True
        self.state_changed.emit("thinking")

        if self._worker_mgr is not None:
            self._worker_mgr.run_task(
                "ai_assistant_chat",
                self._do_process,
                text,
                on_done=self._on_response,
                on_error=self._on_error,
            )
        else:
            try:
                result = self._do_process(text)
                self._on_response(result)
            except Exception as e:
                self._on_error(str(e))

    def _do_process(self, text: str) -> dict:
        svc = self._get_service()
        return svc.process_message(text)

    def _on_response(self, result: dict | str):
        self._pending = False
        self.state_changed.emit("ready")
        self.response_received.emit(result)

    def _on_error(self, error: str):
        self._pending = False
        self.state_changed.emit("error")
        self.response_received.emit({
            "reply": (
                f"Error: {error}\n\n"
                f"Verifica que Ollama este ejecutandose en {self.base_url()} "
                f"y que el modelo '{self.model()}' este instalado."
            ),
            "pending": None,
        })

    def confirm_action(self, action_id: str):
        if self._worker_mgr is not None:
            self._worker_mgr.run_task(
                "ai_assistant_confirm",
                self._do_confirm,
                action_id,
                on_done=self._on_response,
                on_error=self._on_error,
            )
        else:
            try:
                result = self._do_confirm(action_id)
                self._on_response(result)
            except Exception as e:
                self._on_error(str(e))

    def _do_confirm(self, action_id: str) -> dict:
        svc = self._get_service()
        return svc.confirm_action(action_id)

    def cancel_action(self, action_id: str):
        svc = self._get_service()
        result = svc.cancel_action(action_id)
        self.response_received.emit(result)

    def clear_conversation(self):
        if self._service:
            self._service.clear()

    @property
    def is_pending(self) -> bool:
        return self._pending
