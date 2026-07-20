"""Asset generation agent: backgrounds, props, labels, UI cards."""

from __future__ import annotations

import json
import os

from .orchestrator import PipelineState


def asset_node(state: PipelineState) -> PipelineState:
    """Generate the asset manifest and placeholder paths for all scene assets."""
    project_dir = os.path.join("projects", state.project_id)
    asset_dir = os.path.join(project_dir, "assets")
    for sub in ["backgrounds", "props", "characters", "ui"]:
        os.makedirs(os.path.join(asset_dir, sub), exist_ok=True)

    # Collect assets from storyboard or script segments
    segments = state.script.get("segments", [])
    assets = {
        "backgrounds": [],
        "props": [],
        "labels": [],
        "style_tokens": "2D cartoon, vibrant colors, thick clean outlines, flat shading",
    }

    for i, seg in enumerate(segments):
        scene_id = f"scene_{i + 1:03d}"
        bg = {
            "id": f"{scene_id}_bg",
            "prompt": seg.get("background_prompt", f"Simple cartoon background for: {seg.get('text', '')}"),
            "path": os.path.join(asset_dir, "backgrounds", f"{scene_id}_bg.png"),
        }
        assets["backgrounds"].append(bg)

        for prop in seg.get("props", []):
            assets["props"].append(
                {
                    "id": f"{scene_id}_{prop}",
                    "name": prop,
                    "prompt": f"Cartoon {prop}, white background, 2D flat style",
                    "path": os.path.join(asset_dir, "props", f"{scene_id}_{prop}.png"),
                }
            )

        for label in seg.get("labels", []):
            assets["labels"].append(
                {
                    "id": f"{scene_id}_{label}",
                    "text": label,
                    "style": "bold cartoon label",
                }
            )

    # TODO: call FLUX/IP-Adapter/RMBG to generate actual transparent PNGs
    state.assets = assets
    manifest_path = os.path.join(asset_dir, "assets.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(assets, f, indent=2, ensure_ascii=False)

    return state
