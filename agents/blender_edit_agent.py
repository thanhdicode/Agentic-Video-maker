"""Blender VSE final-edit node for the AI Video Studio pipeline.

This node drives Blender in headless mode to assemble video clips, audio and
text overlays. It is opt-in via the `AI_VIDEO_EDIT_ENGINE=blender` environment
variable or `AI_VIDEO_USE_BLENDER=1`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from tools.blender_edit import BlenderNotFoundError, BlenderRenderError, BlenderVideoEditor


def _load_blender_config() -> dict[str, Any]:
    import yaml

    settings_path = Path("config/settings.yaml")
    if not settings_path.exists():
        return {}
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return {}
    return data.get("blender", {}) or {}


def blender_edit_node(state: Any) -> Any:
    """Assemble and render the final video with Blender VSE."""
    config = _load_blender_config()
    project_dir = Path("projects") / state.project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    resolution = config.get("resolution", "1920x1080")
    width, height = map(int, resolution.split("x"))
    fps = int(config.get("fps", 30))
    transition_frames = int(config.get("transition_frames", 0))
    executable = config.get("executable") or os.environ.get("BLENDER_EXECUTABLE") or None

    music_volume = float(config.get("music_volume", 0.3))
    narration_volume = float(config.get("narration_volume", 1.0))

    text_enabled = bool(config.get("text_overlay_enabled", True))
    text_content = config.get("text_overlay_text") or getattr(state, "idea", "")[:60]
    text_font_size = int(config.get("text_overlay_font_size", 80))
    text_duration = float(config.get("text_overlay_duration_sec", 2.0))
    text_location = config.get("text_overlay_location", [0.5, 0.85])
    text_color = config.get("text_overlay_color", [1.0, 1.0, 1.0, 1.0])

    video_clips = [
        {"path": str(Path(p).resolve().as_posix()), "name": Path(p).stem}
        for p in state.video_paths
        if p and Path(p).exists()
    ]
    if not video_clips:
        state.error = "Blender edit failed: no video clips available"
        return state

    audio_clips: list[dict[str, Any]] = []
    for key, volume, fit in [
        ("narration", narration_volume, False),
        ("music", music_volume, True),
        ("sfx", 1.0, False),
    ]:
        path = state.audio_paths.get(key)
        if path and Path(path).exists():
            audio_clips.append(
                {
                    "path": str(Path(path).resolve().as_posix()),
                    "name": key.capitalize(),
                    "volume": volume,
                    "fit_to_timeline": fit,
                }
            )

    text_overlays: list[dict[str, Any]] = []
    if text_enabled and text_content:
        text_overlays.append(
            {
                "text": str(text_content),
                "start_sec": 0,
                "duration_sec": text_duration,
                "font_size": text_font_size,
                "location": text_location,
                "color": text_color,
            }
        )

    output_path = project_dir / "final_blender.mp4"
    work_dir = project_dir / "blender_vse"
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        editor = BlenderVideoEditor(executable=executable) if executable else BlenderVideoEditor()
        editor.render(
            {
                "resolution": [width, height],
                "fps": fps,
                "transition_frames": transition_frames,
                "video_clips": video_clips,
                "audio_clips": audio_clips,
                "text_overlays": text_overlays,
                "output": str(output_path.resolve().as_posix()),
            },
            work_dir=str(work_dir),
        )
        state.output_path = str(output_path)
    except (BlenderNotFoundError, BlenderRenderError) as exc:
        state.error = f"Blender edit failed: {exc}"
    except Exception as exc:
        state.error = f"Blender edit failed: {exc}"

    return state
