"""Ollama HTTP client — lightweight, urllib-only, localhost enforced."""

from __future__ import annotations

import json
import urllib.request
import urllib.error


class OllamaError(Exception):
    pass


class OllamaNotAvailable(OllamaError):
    pass


class ModelNotFound(OllamaError):
    pass


class OllamaTimeout(OllamaError):
    pass


_LOCALHOST_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


def _is_localhost(url: str) -> bool:
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower().strip("[]")
    return host in _LOCALHOST_HOSTS


class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434",
                 timeout: int = 30, offline_strict: bool = True):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._offline_strict = offline_strict

    @property
    def base_url(self) -> str:
        return self._base_url

    def check_health(self) -> bool:
        if not _is_localhost(self._base_url):
            return False
        try:
            self._request("GET", "/api/tags", json_body=None, timeout=5)
            return True
        except Exception:
            return False

    def list_models(self) -> list[str]:
        data = self._request("GET", "/api/tags", json_body=None)
        return [m.get("name", "") for m in data.get("models", [])]

    def chat(self, model: str, messages: list[dict[str, str]],
             max_tokens: int = 500) -> str:
        if self._offline_strict and not _is_localhost(self._base_url):
            raise OllamaNotAvailable(
                "URL externa bloqueada por offline_strict. "
                "Solo se permite localhost."
            )
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        data = self._request("POST", "/api/chat", payload)
        return data.get("message", {}).get("content", "")

    def _request(self, method: str, path: str,
                 json_body: dict | None = None, timeout: int | None = None
                 ) -> dict:
        url = f"{self._base_url}{path}"
        req_data = None
        if json_body is not None:
            req_data = json.dumps(json_body).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=req_data,
            method=method,
            headers={"Content-Type": "application/json"} if req_data else {},
        )

        timeout_val = timeout if timeout is not None else self._timeout

        try:
            with urllib.request.urlopen(req, timeout=timeout_val) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ModelNotFound(
                    f"Modelo no encontrado en {self._base_url}. "
                    f"Ejecuta 'ollama pull <modelo>'."
                ) from e
            raise OllamaError(f"HTTP {e.code}: {e.reason}") from e
        except urllib.error.URLError:
            raise OllamaNotAvailable(
                f"No se puede conectar a Ollama en {self._base_url}. "
                f"Verifica que Ollama este ejecutandose."
            ) from None
        except TimeoutError:
            raise OllamaTimeout(
                f"Timeout al conectar con Ollama en {self._base_url}."
            ) from None
        except Exception as e:
            raise OllamaError(str(e)) from e
