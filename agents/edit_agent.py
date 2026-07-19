"""Video editing agent: assemble clips, add labels, subtitles, music, and SFX."""

from __future__ import annotations

import os

from tools.ffmpeg_tools import assemble_video, burn_subtitles, mix_audio
from tools.whisper_tools import generate_subtitles

from .orchestrator import PipelineState


def edit_node(state: PipelineState) -> PipelineState:
    """Assemble final video with audio, subtitles, labels, transitions, and color grade."""
    project_dir = os.path.join("projects", state.project_id)
    os.makedirs(project_dir, exist_ok=True)

    draft_path = os.path.join(project_dir, "draft.mp4")
    final_path = os.path.join(project_dir, "final.mp4")
    srt_path = os.path.join(project_dir, "subtitles.srt")

    try:
        assemble_video(state.video_paths, draft_path, transition="fade")
        generate_subtitles(state.audio_paths.get("narration", ""), srt_path)

        # TODO: overlay labels, lower-thirds, and character poses before burning subtitles
        burn_subtitles(draft_path, srt_path, final_path)

        # Layer music and SFX under narration
        if state.audio_paths.get("music"):
            mix_audio(final_path, state.audio_paths["music"], final_path, music_db=-18.0)

        # TODO: add SFX ducking per cue, color grade LUT, intro/outro cards
    except Exception as exc:
        state.error = f"Edit failed: {exc}"

    state.subtitle_path = srt_path
    state.output_path = final_path
    return state
