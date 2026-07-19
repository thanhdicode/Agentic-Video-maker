"""Video generation agent: image-to-video via Wan/LTX/AnimateDiff."""

from __future__ import annotations

import os

from tools.comfyui_client import queue_workflow

from .orchestrator import PipelineState


def video_node(state: PipelineState) -> PipelineState:
    """Generate video clips from storyboard images."""
    project_dir = os.path.join("projects", state.project_id, "video_clips")
    os.makedirs(project_dir, exist_ok=True)

    video_paths = []
    for idx, image_path in enumerate(state.image_paths):
        filename = os.path.join(project_dir, f"clip_{idx + 1:03d}.mp4")
        # TODO: load wan_i2v.json workflow and seed image path
        try:
            queue_workflow("wan_i2v.json", {"image": image_path}, filename)
        except Exception as exc:
            state.error = f"Video generation failed: {exc}"
        video_paths.append(filename)

    state.video_paths = video_paths
    return state
