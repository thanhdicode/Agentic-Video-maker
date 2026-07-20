"""Shotcut / MLT final-edit node for the AI Video Studio pipeline.

This node drives the Shotcut/MLT `melt` command-line renderer to assemble
video clips, add cross-fades, and mix audio. It is opt-in via the
``AI_VIDEO_EDIT_ENGINE=shotcut`` or ``AI_VIDEO_USE_SHOTCUT=1`` environment
variable.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def _load_shotcut_config() -> dict[str, Any]:
    import yaml

    settings_path = Path("config/settings.yaml")
    if not settings_path.exists():
        return {}
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return {}
    return data.get("shotcut", {}) or {}


def shotcut_edit_node(state: Any) -> Any:
    """Assemble and render the final video with Shotcut/MLT."""
    from tools.shotcut_edit import (
        ShotcutEditor,
        ShotcutNotFoundError,
        ShotcutRenderError,
    )

    config = _load_shotcut_config()

    project_dir = Path("projects") / state.project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    resolution = config.get("resolution", "1920x1080")
    width, height = map(int, resolution.split("x"))
    fps = int(config.get("fps", 30))
    transition_frames = int(config.get("transition_frames", 0))
    executable = config.get("executable") or os.environ.get("SHOTCUT_MELT") or None

    music_volume = float(config.get("music_volume", 0.3))
    narration_volume = float(config.get("narration_volume", 1.0))

    video_clips = [p for p in state.video_paths if p and Path(p).exists()]
    if not video_clips:
        state.error = "Shotcut edit failed: no video clips available"
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
                    "path": str(Path(path).resolve()),
                    "volume": volume,
                    "fit_to_timeline": fit,
                }
            )

    output_path = project_dir / "final_shotcut.mp4"

    try:
        editor = ShotcutEditor(executable=executable) if executable else ShotcutEditor()
        editor.assemble(
            video_paths=video_clips,
            output=output_path,
            audio_clips=audio_clips,
            resolution=(width, height),
            fps=fps,
            transition_frames=transition_frames,
        )
        state.output_path = str(output_path)
    except (ShotcutNotFoundError, ShotcutRenderError) as exc:
        state.error = f"Shotcut edit failed: {exc}"
    except Exception as exc:
        state.error = f"Shotcut edit failed: {exc}"

    return state
