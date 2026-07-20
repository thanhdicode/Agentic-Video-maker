"""Resolve-based final edit node for the AI Video Studio pipeline.

This agent drives DaVinci Resolve Studio to assemble, grade and deliver the
final trailer / devlog. It is opt-in via the ``AI_VIDEO_USE_RESOLVE=1``
environment variable; otherwise the FFmpeg edit node is used.

The Resolve API is lazy-loaded, so importing this module does **not** require
Resolve to be installed. Resolve itself must be running and external scripting
must be enabled (Preferences > General > External scripting using > Local).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.davinci_resolve import ClipInfo, ResolveController, ResolveError


def _load_resolve_config() -> dict[str, Any]:
    import yaml

    settings_path = Path("config/settings.yaml")
    if not settings_path.exists():
        return {}
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return {}
    return data.get("resolve", {}) or {}


def resolve_edit_node(state: PipelineState) -> PipelineState:
    """Assemble and render the final video in DaVinci Resolve Studio."""
    config = _load_resolve_config()

    project_dir = Path("projects") / state.project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    resolution = config.get("resolution", "1920x1080")
    width, height = map(int, resolution.split("x"))
    fps = str(config.get("fps", 30))
    color_science = config.get("color_science", "davinciYRGBColorManagedv2")
    render_format = config.get("render_format", "mp4")
    render_codec = config.get("render_codec", "H264")
    audio_codec = config.get("audio_codec", "aac")
    lut_path = config.get("lut_path")
    render_name = config.get("render_name", "final_resolve")
    target_dir = str(project_dir.resolve())

    # Studio-style bins for trailer / devlog organisation.
    bins = [
        "Gameplay_Raw",
        "Captures_Broll",
        "Audio_Music",
        "Audio_SFX",
        "VO",
        "Brand_Assets",
        "Exports",
    ]

    try:
        with ResolveController(project_name=state.project_id) as resolve:
            resolve.configure_project(
                width=width,
                height=height,
                frame_rate=fps,
                color_science=color_science,
            )
            resolve.create_bins(bins)

            # ---- Video assembly ---------------------------------------- #
            video_paths = [p for p in state.video_paths if p and Path(p).exists()]
            if not video_paths:
                raise ResolveError("No video clips available for Resolve assembly")

            video_clips = resolve.import_media(video_paths)
            video_infos = [ClipInfo(media_pool_item=c) for c in video_clips]
            timeline = resolve.create_timeline("Final", clip_infos=video_infos)

            # ---- Audio tracks ------------------------------------------ #
            audio_specs = [
                ("narration", 1),
                ("music", 2),
                ("sfx", 3),
            ]
            audio_files: list[Path] = []
            track_map: dict[int, int] = {}
            for key, track_index in audio_specs:
                path = state.audio_paths.get(key)
                if path and Path(path).exists():
                    audio_files.append(Path(path))
                    track_map[len(audio_files) - 1] = track_index

            if audio_files:
                audio_items = resolve.import_media(audio_files)
                audio_infos = [
                    ClipInfo(
                        media_pool_item=item,
                        media_type=2,
                        track_index=track_map.get(idx, 2),
                    )
                    for idx, item in enumerate(audio_items)
                ]
                resolve.append_clips(timeline, audio_infos)

            # ---- Colour pass ------------------------------------------- #
            if lut_path and Path(lut_path).exists():
                video_items = resolve.get_timeline_items("video", 1, timeline)
                if video_items:
                    for item in video_items:
                        resolve.apply_lut(item, lut_path)

            # ---- Render ------------------------------------------------ #
            resolve.set_render_format_codec(render_format, render_codec)
            resolve.set_render_job_settings(
                target_dir=target_dir,
                custom_name=render_name,
                width=width,
                height=height,
            )
            resolve.add_render_job()
            resolve.start_rendering()
            resolve.wait_for_render()

            state.output_path = str(project_dir / f"{render_name}.{render_format}")

    except ResolveError as exc:
        state.error = f"Resolve edit failed: {exc}"
    except Exception as exc:
        state.error = f"Resolve edit failed: {exc}"

    return state
