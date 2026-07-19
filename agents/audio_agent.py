"""Audio generation agent: TTS, music, and SFX."""

from __future__ import annotations

import os

from tools.music_tools import generate_music

from .orchestrator import PipelineState


def audio_node(state: PipelineState) -> PipelineState:
    """Synthesize narration, background music, and sound effects."""
    project_dir = os.path.join("projects", state.project_id, "audio")
    os.makedirs(project_dir, exist_ok=True)

    narration_segments = []
    for scene in state.storyboard:
        # TODO: call F5-TTS / Kokoro via local API
        narration_segments.append({"scene": scene["scene_number"], "text": scene["voice_cue"]})

    music_path = os.path.join(project_dir, "background_music.wav")
    try:
        generate_music("upbeat background music for AI tech video", music_path)
    except Exception as exc:
        state.error = f"Music generation failed: {exc}"

    state.audio_paths = {
        "narration": os.path.join(project_dir, "narration.wav"),
        "music": music_path,
        "sfx": [],
    }
    return state
