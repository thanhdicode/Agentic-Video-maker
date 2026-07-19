"""Storyboard generator: converts script segments to scene JSON."""

from __future__ import annotations

from .orchestrator import PipelineState


def storyboard_node(state: PipelineState) -> PipelineState:
    """Create a scene list from the script."""
    segments = state.script.get("segments", [])
    state.storyboard = [
        {
            "scene_number": i + 1,
            "text": seg.get("text", ""),
            "duration": seg.get("duration", 4),
            "visual_prompt": f"Cinematic illustration of: {seg.get('text', '')}",
            "voice_cue": seg.get("text", ""),
            "music_mood": "upbeat",
            "transition": "fade",
        }
        for i, seg in enumerate(segments)
    ]
    return state
