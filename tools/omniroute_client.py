"""Minimal OpenAI-compatible client for OmniRoute and similar routers.

Set `OMNIROUTE_BASE_URL` (default: http://localhost:20128/v1) and `OMNIROUTE_API_KEY`
(default: omniroute) to route LLM calls through OmniRoute's free-tier/fallback proxy.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def _default_base_url() -> str:
    return os.environ.get("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")


def _default_api_key() -> str:
    return os.environ.get("OMNIROUTE_API_KEY", "omniroute")


def chat(
    prompt: str,
    model: str = "",
    base_url: str = "",
    api_key: str = "",
    system: str = "",
    timeout: int = 120,
) -> str:
    """Send a single prompt to an OpenAI-compatible endpoint and return text."""
    base_url = base_url or _default_base_url()
    api_key = api_key or _default_api_key()
    model = model or os.environ.get("OMNIROUTE_MODEL", "auto")

    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"OmniRoute HTTP {exc.code}: {body}") from exc

    if "choices" not in result or not result["choices"]:
        raise RuntimeError(f"Unexpected OmniRoute response: {result}")

    return str(result["choices"][0]["message"]["content"])


def is_configured() -> bool:
    """Return True when an OmniRoute endpoint appears to be configured."""
    return bool(os.environ.get("OMNIROUTE_BASE_URL"))
