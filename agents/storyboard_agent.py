"""Storyboard generator: converts script segments into scenes with camera and animation plans."""

from __future__ import annotations

from .orchestrator import PipelineState


def storyboard_node(state: PipelineState) -> PipelineState:
    """Create a scene list with keyframes, camera motion, and audio/SFX cues."""
    segments = state.script.get("segments", [])
    style_tokens = state.assets.get("style_tokens", "2D cartoon, vibrant colors, thick clean outlines")

    state.storyboard = [
        {
            "scene_number": i + 1,
            "segment_type": seg.get("type", "explain"),
            "text": seg.get("text", ""),
            "duration": seg.get("duration", 4),
            "visual_prompt": f"{style_tokens}. {seg.get('background_prompt', '')}.",
            "characters": seg.get("characters", []),
            "props": seg.get("props", []),
            "labels": seg.get("labels", []),
            "voice_cue": seg.get("text", ""),
            "music_mood": "upbeat" if seg.get("type") in ("hook", "recap") else "calm",
            "sfx_cues": ["pop"] if seg.get("type") == "example" else [],
            "camera": "static" if seg.get("type") in ("hook", "recap") else "slow_zoom_in",
            "animation_strategy": "moviepy_ken_burns" if seg.get("type") == "explain" else "tooncrafter",
            "transition": "fade",
        }
        for i, seg in enumerate(segments)
    ]
    return state
