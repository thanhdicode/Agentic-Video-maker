"""Image generation agent: drives ComfyUI / FLUX workflows."""

from __future__ import annotations

import os

from tools.comfyui_client import queue_workflow

from .orchestrator import PipelineState


def image_node(state: PipelineState) -> PipelineState:
    """Generate still images for each storyboard scene."""
    project_dir = os.path.join("projects", state.project_id, "assets")
    os.makedirs(project_dir, exist_ok=True)

    image_paths = []
    for scene in state.storyboard:
        filename = os.path.join(project_dir, f"scene_{scene['scene_number']:03d}.png")
        # TODO: load ComfyUI flux_t2i.json workflow and replace prompt node
        try:
            queue_workflow("flux_t2i.json", {"prompt": scene["visual_prompt"]}, filename)
        except Exception as exc:
            state.error = f"Image generation failed: {exc}"
        image_paths.append(filename)

    state.image_paths = image_paths
    return state
