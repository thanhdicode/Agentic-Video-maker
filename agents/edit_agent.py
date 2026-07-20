"""Video editing agent: assemble clips, add subtitles, mix audio."""

from __future__ import annotations

import os

from tools.ffmpeg_tools import assemble_video, burn_subtitles, mix_audio
from tools.whisper_tools import generate_subtitles

from .orchestrator import PipelineState


def edit_node(state: PipelineState) -> PipelineState:
    """Assemble final video with audio, subtitles, and transitions."""
    engine = os.environ.get("AI_VIDEO_EDIT_ENGINE", "").lower()
    if engine == "resolve" or os.environ.get("AI_VIDEO_USE_RESOLVE", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        from .resolve_edit_agent import resolve_edit_node

        return resolve_edit_node(state)

    if engine == "blender" or os.environ.get("AI_VIDEO_USE_BLENDER", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        from .blender_edit_agent import blender_edit_node

        return blender_edit_node(state)

    project_dir = os.path.join("projects", state.project_id)
    os.makedirs(project_dir, exist_ok=True)

    draft_path = os.path.join(project_dir, "draft.mp4")
    final_path = os.path.join(project_dir, "final.mp4")
    srt_path = os.path.join(project_dir, "subtitles.srt")

    try:
        assemble_video(state.video_paths, draft_path)
        generate_subtitles(state.audio_paths.get("narration", ""), srt_path)
        burn_subtitles(draft_path, srt_path, final_path)
        mix_audio(final_path, state.audio_paths.get("music", ""), final_path)
    except Exception as exc:
        state.error = f"Edit failed: {exc}"

    state.subtitle_path = srt_path
    state.output_path = final_path
    return state
