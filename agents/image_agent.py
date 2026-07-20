"""Image generation agent: drives ComfyUI / FLUX workflows for backgrounds, props, and keyframes."""

from __future__ import annotations

import os

from tools.comfyui_client import queue_workflow

from .orchestrator import PipelineState


def image_node(state: PipelineState) -> PipelineState:
    """Generate keyframes for each storyboard scene using FLUX / ComfyUI."""
    project_dir = os.path.join("projects", state.project_id, "assets", "keyframes")
    os.makedirs(project_dir, exist_ok=True)

    image_paths = []
    for scene in state.storyboard:
        filename = os.path.join(project_dir, f"scene_{scene['scene_number']:03d}_key.png")
        # TODO: load ComfyUI flux_t2i.json workflow and apply character consistency
        # (IP-Adapter, character LoRA, negative prompt)
        try:
            queue_workflow(
                "flux_t2i.json",
                {
                    "prompt": scene["visual_prompt"],
                    "width": 1280,
                    "height": 720,
                    "seed": 42,
                },
                filename,
            )
        except Exception as exc:
            state.error = f"Image generation failed: {exc}"
        image_paths.append(filename)

    state.image_paths = image_paths
    return state
