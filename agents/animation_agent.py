"""Animation agent: turns keyframes/storyboard into motion clips."""

from __future__ import annotations

import os

from .orchestrator import PipelineState


def animation_node(state: PipelineState) -> PipelineState:
    """Generate animated clips using image-to-video or cartoon interpolation."""
    project_dir = os.path.join("projects", state.project_id, "video_clips")
    os.makedirs(project_dir, exist_ok=True)

    video_paths = []
    for i, scene in enumerate(state.storyboard):
        clip_path = os.path.join(project_dir, f"clip_{i + 1:03d}.mp4")
        strategy = scene.get("animation_strategy", "moviepy_ken_burns")

        # TODO: dispatch to the right engine per strategy:
        # - tooncrafter: keyframe interpolation for 2D cartoon motion
        # - wan_i2v / ltx_i2v: image-to-video camera/person motion
        # - moviepy_ken_burns: pan/zoom on still assets (CPU fallback)
        # - remotion: programmatic motion graphics
        try:
            if strategy == "tooncrafter":
                pass  # tools.tooncrafter_client.interpolate(...)
            elif strategy == "wan_i2v":
                pass  # tools.comfyui_client.queue_workflow("wan_i2v.json", ...)
            elif strategy == "moviepy_ken_burns":
                pass  # tools.moviepy_tools.ken_burns(...)
        except Exception as exc:
            state.error = f"Animation failed for scene {i + 1}: {exc}"

        video_paths.append(clip_path)

    state.video_paths = video_paths
    return state
