"""Diagnostics — server connectivity tests with user-friendly messages."""

from __future__ import annotations

import socket
import time
import urllib.request
from dataclasses import dataclass


@dataclass
class DiagnosticsResult:
    host: str = ""
    port: int = 0
    host_reachable: bool = False
    port_open: bool = False
    server_identified: bool = False
    server_type: str = "unknown"
    authentication_ok: bool = False
    library_available: bool = False
    latency_ms: float = 0.0
    error_code: str = ""
    user_message: str = ""
    technical_message: str = ""
    suggested_fix: str = ""


def run_diagnostics(host: str, port: int,
                    username: str = "", password: str = "",
                    server_type: str = "") -> DiagnosticsResult:
    result = DiagnosticsResult(host=host, port=port)

    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        ip = socket.gethostbyname(host)
        result.host_reachable = True
        result.latency_ms = (time.time() - start) * 1000

        if sock.connect_ex((ip, port)) == 0:
            result.port_open = True
            sock.close()
        else:
            sock.close()
            result.error_code = "PORT_CLOSED"
            result.user_message = f"No se pudo conectar al puerto {port}."
            result.suggested_fix = "Verifica que el servidor este ejecutandose y el puerto sea correcto."
            result.latency_ms = (time.time() - start) * 1000
            return result
    except socket.gaierror:
        result.error_code = "DNS_ERROR"
        result.user_message = f"No se pudo resolver el host '{host}'."
        result.suggested_fix = "Verifica la direccion del servidor."
        return result
    except Exception as e:
        result.error_code = "NETWORK_ERROR"
        result.user_message = f"Error de red: {e}"
        result.suggested_fix = "Verifica tu conexion de red."
        return result
    finally:
        result.latency_ms = (time.time() - start) * 1000

    classified = _identify_server(host, port)
    if classified:
        result.server_type = classified
        result.server_identified = True

    if username and password and classified:
        result.authentication_ok = _test_auth(host, port, classified, username, password)
        if not result.authentication_ok:
            result.user_message = "Usuario o contraseña incorrectos."

    return result


def _identify_server(host: str, port: int) -> str:
    tests = [
        (f"http://{host}:{port}/rest/ping", "navidrome"),
        (f"http://{host}:{port}/System/Info/Public", "jellyfin"),
        (f"http://{host}:{port}/api/", "home_assistant"),
    ]
    for url, srv_type in tests:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status < 500:
                    return srv_type
        except Exception:
            pass
    return ""


def _test_auth(host: str, port: int, server_type: str,
               username: str, password: str) -> bool:
    try:
        if server_type == "navidrome":
            import hashlib
            salt = f"{password}{username}" if password else ""
            token = hashlib.md5(salt.encode()).hexdigest()
            params = f"u={urllib.request.quote(username)}&t={token}&v=1.16.1&c=michi"
            url = f"http://{host}:{port}/rest/ping?{params}"
        elif server_type == "jellyfin":
            url = f"http://{host}:{port}/System/Info/Public"
        else:
            return False

        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status < 400
    except Exception:
        return False
