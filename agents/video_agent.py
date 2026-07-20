"""Video generation agent: image-to-video via Wan/LTX and fallback to MoviePy."""

from __future__ import annotations

import os

from tools.comfyui_client import queue_workflow

from .orchestrator import PipelineState


def video_node(state: PipelineState) -> PipelineState:
    """Generate video clips from storyboard keyframes using I2V diffusion."""
    project_dir = os.path.join("projects", state.project_id, "video_clips")
    os.makedirs(project_dir, exist_ok=True)

    video_paths = []
    for idx, image_path in enumerate(state.image_paths):
        filename = os.path.join(project_dir, f"clip_{idx + 1:03d}.mp4")
        strategy = state.storyboard[idx].get("animation_strategy", "wan_i2v")

        try:
            if strategy in ("wan_i2v", "ltx_i2v"):
                # TODO: load wan_i2v.json or ltx_i2v.json with camera motion and seed image
                queue_workflow(
                    "wan_i2v.json",
                    {
                        "image": image_path,
                        "prompt": state.storyboard[idx]["visual_prompt"],
                        "fps": 16,
                        "frames": 81,
                    },
                    filename,
                )
            else:
                # animation_node handles tooncrafter / moviepy paths
                pass
        except Exception as exc:
            state.error = f"Video generation failed for scene {idx + 1}: {exc}"

        video_paths.append(filename)

    state.video_paths = video_paths
    return state
