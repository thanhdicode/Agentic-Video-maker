"""Minimal ComfyUI API client."""

from __future__ import annotations

import json
import os
import time
import urllib.request
import uuid
from typing import Any

import yaml


def load_settings() -> dict[str, Any]:
    with open("config/settings.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def queue_workflow(workflow_name: str, overrides: dict[str, Any], output_path: str) -> str:
    """Queue a ComfyUI workflow and poll for completion."""
    settings = load_settings()
    host = settings["comfyui"]["host"]
    workflow_dir = settings["comfyui"]["workflow_dir"]
    workflow_path = os.path.join(workflow_dir, workflow_name)

    if not os.path.exists(workflow_path):
        raise FileNotFoundError(f"Workflow not found: {workflow_path}")

    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # Apply overrides naively by searching for keys in node inputs
    for node_id, node in workflow.items():
        inputs = node.get("inputs", {})
        for key, value in overrides.items():
            if key in inputs:
                inputs[key] = value

    prompt = {"prompt": workflow, "client_id": str(uuid.uuid4())}
    data = json.dumps(prompt).encode("utf-8")
    req = urllib.request.Request(
        f"{host}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    # Stub polling / file download
    prompt_id = result.get("prompt_id", "")
    time.sleep(2)
    return f"{host}/view?filename={output_path}&subfolder=&type=output"


def get_workflow_names() -> list[str]:
    """List available workflow JSON files."""
    workflow_dir = load_settings()["comfyui"]["workflow_dir"]
    if not os.path.exists(workflow_dir):
        return []
    return [f for f in os.listdir(workflow_dir) if f.endswith(".json")]
