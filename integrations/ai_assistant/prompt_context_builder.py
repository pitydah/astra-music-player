"""PromptContextBuilder — build sanitized messages for Ollama prompts."""

from __future__ import annotations

from typing import Any

from core.context.context_snapshot import sanitize_snapshot
from integrations.ai_assistant.schemas import ToolResult


class PromptContextBuilder:
    def build(self, user_text: str, context_snapshot: dict[str, Any] | None = None, tool_result: ToolResult | None = None) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": "Eres Michi Assistant."}]
        section = context_snapshot or {}
        if section:
            safe_section = sanitize_snapshot(section)
            section_block = self._format_section_context(safe_section)
            messages.append({"role": "system", "content": f"Contexto actual:\n{section_block}"})
        if tool_result is not None and tool_result.success and tool_result.data:
            safe_data = sanitize_snapshot(tool_result.data)
            result_block = self._format_tool_data(tool_result.name, safe_data)
            messages.append({"role": "system", "content": f"Resultado de herramienta:\n{result_block}"})
        elif tool_result is not None and not tool_result.success:
            messages.append({"role": "system", "content": f"La herramienta '{tool_result.name}' fallo: {tool_result.error}"})
        messages.append({"role": "user", "content": user_text[:2000]})
        return messages

    def _format_section_context(self, safe_section: dict) -> str:
        lines = []
        section = safe_section.get("section", "desconocida")
        lines.append(f"Seccion: {section}")
        selection = safe_section.get("selection", {})
        if selection:
            scope = selection.get("scope", "ninguno")
            lines.append(f"Seleccion: {scope}")
        summary = safe_section.get("summary", {})
        if summary:
            parts = []
            for k in ("track_count", "album_count", "artist_count"):
                v = summary.get(k, 0)
                if v:
                    parts.append(f"{k.replace('_', ' ')}: {v}")
            if parts:
                lines.append("Resumen: " + " . ".join(parts))
        actions = safe_section.get("allowed_actions", [])
        if actions:
            lines.append(f"Acciones disponibles: {', '.join(actions[:5])}")
        return "\n".join(lines)

    def _format_tool_data(self, tool_name: str, safe_data: Any) -> str:
        if isinstance(safe_data, dict):
            parts = []
            for k, v in safe_data.items():
                if k in ("report", "diagnosis", "preview", "plan", "fix"):
                    v = self._truncate(v)
                parts.append(f"  {k}: {v}")
            return f"Herramienta: {tool_name}\n" + "\n".join(parts[:15])
        if isinstance(safe_data, list):
            return f"Herramienta: {tool_name}\nItems: {len(safe_data)}"
        return f"Herramienta: {tool_name}\n{safe_data}"

    def _truncate(self, value: Any, max_len: int = 500) -> Any:
        if isinstance(value, str) and len(value) > max_len:
            return value[:max_len] + "..."
        return value
