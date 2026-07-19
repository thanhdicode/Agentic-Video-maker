"""Audio generation agent: TTS, music, and SFX."""

from __future__ import annotations

import os

from tools.music_tools import generate_music, generate_sfx

from .orchestrator import PipelineState


def audio_node(state: PipelineState) -> PipelineState:
    """Synthesize narration, background music, and sound effects per scene cue."""
    project_dir = os.path.join("projects", state.project_id, "audio")
    os.makedirs(project_dir, exist_ok=True)

    narration_segments = []
    for scene in state.storyboard:
        # TODO: call F5-TTS / Kokoro / CosyVoice via local API
        # Use scene voice_cue and character voice profile
        narration_segments.append(
            {"scene": scene["scene_number"], "text": scene["voice_cue"], "character": scene.get("characters", ["Host"])[0]}
        )

    music_path = os.path.join(project_dir, "background_music.wav")
    sfx_paths = []

    try:
        generate_music("upbeat background music for kids educational cartoon", music_path)
        for i, scene in enumerate(state.storyboard):
            for cue in scene.get("sfx_cues", []):
                sfx_path = os.path.join(project_dir, f"sfx_{i + 1:03d}_{cue}.wav")
                generate_sfx(cue, sfx_path)
                sfx_paths.append(sfx_path)
    except Exception as exc:
        state.error = f"Audio generation failed: {exc}"

    state.audio_paths = {
        "narration": os.path.join(project_dir, "narration.wav"),
        "music": music_path,
        "sfx": sfx_paths,
    }
    return state
