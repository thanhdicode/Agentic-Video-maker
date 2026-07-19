"""Character design agent: generates character sheets and LoRA references."""

from __future__ import annotations

import json
import os

from .orchestrator import PipelineState


def character_node(state: PipelineState) -> PipelineState:
    """Design characters from the script/asset manifest and persist reference data."""
    project_dir = os.path.join("projects", state.project_id)
    char_dir = os.path.join(project_dir, "character_sheets")
    os.makedirs(char_dir, exist_ok=True)

    # Derive characters from script segments and asset manifest
    segments = state.script.get("segments", [])
    characters = {}

    for seg in segments:
        for char_name in seg.get("characters", []):
            if char_name not in characters:
                characters[char_name] = {
                    "name": char_name,
                    "description": seg.get("character_descriptions", {}).get(
                        char_name, f"A friendly 2D cartoon {char_name}."
                    ),
                    "style": "2D cartoon, vibrant colors, thick clean outlines, white background",
                    "poses": ["front", "3-4", "side"],
                    "expressions": ["neutral", "happy", "surprised"],
                    "lora_path": "",
                    "refs": [],
                }

    # Fallback host character for educational videos
    if not characters:
        characters["Host"] = {
            "name": "Host",
            "description": "A friendly cartoon teacher with big eyes, simple shapes, warm smile",
            "style": "2D cartoon, vibrant colors, thick clean outlines, white background",
            "poses": ["front", "3-4"],
            "expressions": ["neutral", "happy", "excited"],
            "lora_path": "",
            "refs": [],
        }

    # TODO: call CharForge / FLUX + IP-Adapter to generate sheets and train LoRA
    for name, data in characters.items():
        ref_path = os.path.join(char_dir, f"{name.lower().replace(' ', '_')}_concept.png")
        data["refs"].append(ref_path)

    state.characters = characters

    manifest_path = os.path.join(char_dir, "characters.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(characters, f, indent=2, ensure_ascii=False)

    return state
