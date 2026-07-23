"""Educational script generation for kids from a topic or video transcript."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def _load_omniroute_client() -> Any | None:
    """Load the OmniRoute client from the same tools directory."""
    spec = importlib.util.spec_from_file_location(
        "omniroute_client", Path(__file__).resolve().parent / "omniroute_client.py"
    )
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod
    return None


class ScriptGenerationError(Exception):
    """Raised when an educational script cannot be generated."""

    pass


def _query_omniroute(prompt: str, model: str = "") -> str:
    """Send a prompt through an OpenAI-compatible OmniRoute endpoint."""
    client = _load_omniroute_client()
    if client is None:
        raise ScriptGenerationError("OmniRoute client module not found")
    if not client.is_configured():
        raise ScriptGenerationError("OMNIROUTE_BASE_URL not configured")
    try:
        return client.chat(
            prompt,
            model=model or "auto",
            system="You are a helpful scriptwriter for short educational videos.",
        )
    except Exception as exc:
        raise ScriptGenerationError(f"OmniRoute call failed: {exc}") from exc


def _query_ollama(prompt: str, model: str = "qwen3:32b", host: str = "http://localhost:11434") -> str:
    """Send a prompt to the local Ollama API and return the generated text."""
    url = f"{host}/api/generate"
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise ScriptGenerationError(f"Ollama call failed: {exc}") from exc

    return data.get("response", "")


def _fallback_script(topic: str, audience: str = "kids") -> list[dict[str, Any]]:
    """Return a generic kid-friendly explainer template for any topic."""
    return [
        {
            "scene": 1,
            "narration": f"Lets learn about {topic}!",
            "visual_text": f"Lets Learn {topic.title()}!",
            "visual_prompt": f"colorful title card for {topic}",
            "duration": 3.0,
        },
        {
            "scene": 2,
            "narration": f"{topic} is something we can understand by looking at parts of a whole.",
            "visual_text": f"What is {topic}?",
            "visual_prompt": f"simple diagram explaining {topic}",
            "duration": 6.0,
        },
        {
            "scene": 3,
            "narration": f"When we split something into equal parts, each part is a small piece of the whole.",
            "visual_text": "Equal Parts",
            "visual_prompt": f"equal parts diagram for {topic}",
            "duration": 6.0,
        },
        {
            "scene": 4,
            "narration": f"So remember, {topic} is all about parts and wholes. Keep practicing!",
            "visual_text": "Keep Practicing!",
            "visual_prompt": f"fun summary illustration for {topic}",
            "duration": 5.0,
        },
    ]


def _parse_script(raw: str) -> list[dict[str, Any]]:
    """Try to parse a JSON or loose numbered script returned by an LLM."""
    raw = raw.strip()

    if raw.startswith("["):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

    segments: list[dict[str, Any]] = []
    current: dict[str, Any] = {}

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        m = re.match(r"^\s*scene\s*(\d+)[:)]\s*(.*)", line, re.IGNORECASE)
        if m:
            if current:
                segments.append(current)
            current = {"scene": int(m.group(1)), "narration": m.group(2).strip()}
            continue

        if current:
            key = ""
            if line.lower().startswith("visual:"):
                key = "visual_text"
                line = line.split(":", 1)[1].strip()
            elif line.lower().startswith("text:"):
                key = "visual_text"
                line = line.split(":", 1)[1].strip()
            elif line.lower().startswith("duration:"):
                key = "duration"
                line = line.split(":", 1)[1].strip()
            else:
                key = "narration"

            if key == "narration":
                current["narration"] = current.get("narration", "") + " " + line
            else:
                try:
                    current[key] = float(line) if key == "duration" else line
                except ValueError:
                    current[key] = line

    if current:
        segments.append(current)

    return segments if segments else []


def generate_educational_script(
    topic: str,
    transcript: str = "",
    audience: str = "kids",
    model: str = "",
    ollama_host: str = "",
) -> list[dict[str, Any]]:
    """Generate a kid-friendly explainer script with scene breakdowns.

    Tries OmniRoute first (if OMNIROUTE_BASE_URL is set), then local Ollama,
    then falls back to a generic template.
    """
    if not model:
        model = os.environ.get("OMNIROUTE_MODEL", "qwen3:32b")
    if not ollama_host:
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    prompt = (
        f"Write a short, engaging educational video script about '{topic}' for {audience}.\n"
        "Return ONLY a JSON list. Each item must have: scene (number), "
        "narration (text to speak), visual_text (short text to show on screen), "
        "visual_prompt (image description), and duration (seconds).\n"
    )
    if transcript:
        prompt += f"\nUse this source transcript as inspiration:\n{transcript[:4000]}\n"

    # 1. Try OmniRoute if configured.
    if os.environ.get("OMNIROUTE_BASE_URL"):
        try:
            response = _query_omniroute(prompt, model=model)
            script = _parse_script(response)
            if script:
                return script
        except ScriptGenerationError:
            pass

    # 2. Try local Ollama.
    try:
        response = _query_ollama(prompt, model=model, host=ollama_host)
        script = _parse_script(response)
        if script:
            return script
    except ScriptGenerationError:
        pass

    return _fallback_script(topic, audience)
