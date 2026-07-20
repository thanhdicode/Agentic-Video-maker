"""Manim-based educational video agent.

Takes a YouTube URL or topic, generates a kid-friendly script, renders the
visuals as a Manim animation, and mixes in narration + optional music.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .orchestrator import PipelineState


def _load_ollama_config() -> dict[str, Any]:
    try:
        import yaml
    except ModuleNotFoundError:
        return {}

    settings_path = Path("config/settings.yaml")
    if not settings_path.exists():
        return {}
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return {}

    return {
        "host": data.get("ollama", {}).get("host", "http://localhost:11434"),
        "model": data.get("ollama", {}).get("default_model", "qwen3:32b"),
    }


def _topic_from_state(state: PipelineState) -> str:
    if state.idea:
        return state.idea

    meta = getattr(state, "source_metadata", {}) or {}
    title = meta.get("title", "")
    if title:
        return title

    return "fractions"


def _ffprobe_duration(path: Path) -> float:
    import subprocess

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip()) if result.returncode == 0 else 0.0


def manim_video_node(state: PipelineState) -> PipelineState:
    """Generate an educational explainer video using Manim."""
    from tools.edu_script_tools import generate_educational_script
    from tools.edu_visual_tools import assemble_edu_video
    from tools.manim_tools import render_from_script
    from tools.tts_tools import text_to_speech
    from tools.youtube_tools import YouTubeError, extract_transcript, get_video_info

    project_dir = Path("projects") / state.project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    # --- Ingest YouTube URL if provided ---
    if state.youtube_url:
        ingest_dir = project_dir / "ingest"
        try:
            state.source_metadata = get_video_info(state.youtube_url)
            state.source_transcript = ""
            srt_path = extract_transcript(state.youtube_url, ingest_dir)
            if srt_path:
                state.source_transcript = srt_path.read_text(encoding="utf-8")
        except YouTubeError as exc:
            state.error = f"YouTube ingestion failed: {exc}"
            return state

    ollama_cfg = _load_ollama_config()
    audience = getattr(state, "target_audience", "kids") or "kids"
    topic = _topic_from_state(state)
    transcript = getattr(state, "source_transcript", "") or ""

    # 1. Script
    try:
        script = generate_educational_script(
            topic=topic,
            transcript=transcript,
            audience=audience,
            model=ollama_cfg.get("model", ""),
            ollama_host=ollama_cfg.get("host", ""),
        )
    except Exception as exc:
        state.error = f"Educational script generation failed: {exc}"
        return state

    if not script:
        state.error = "Educational script is empty"
        return state

    # 2. TTS per segment and build timed segments for Manim
    audio_dir = project_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    timed_segments = []
    audio_files = []

    for i, segment in enumerate(script, start=1):
        narration = segment.get("narration", "")
        visual_text = segment.get("visual_text", narration[:60]) or narration[:60]
        if not narration:
            continue

        wav_path = audio_dir / f"narration_{i:02d}.wav"
        try:
            text_to_speech(narration, wav_path)
        except Exception as exc:
            state.error = f"TTS failed for scene {i}: {exc}"
            return state

        duration = _ffprobe_duration(wav_path)
        timed_segments.append({
            "narration": narration,
            "visual_text": visual_text,
            "duration": duration,
        })
        audio_files.append(wav_path)

    # Concatenate narration audio
    concat_audio = audio_dir / "narration_full.wav"
    list_file = audio_dir / "concat.txt"
    list_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in audio_files), encoding="utf-8"
    )

    import subprocess

    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file), "-c", "copy", str(concat_audio),
    ]
    result = subprocess.run(concat_cmd, capture_output=True, text=True)
    if result.returncode != 0 or not concat_audio.exists():
        state.error = f"Audio concatenation failed: {result.stderr}"
        return state

    # 3. Render Manim scene
    scene_dir = project_dir / "manim"
    scene_dir.mkdir(parents=True, exist_ok=True)
    scene_file = scene_dir / "scene.py"

    try:
        video_path = render_from_script(
            timed_segments,
            scene_file,
            class_name="EduScene",
            quality="l",
        )
    except Exception as exc:
        state.error = f"Manim render failed: {exc}"
        return state

    # 4. Assemble with music
    output_path = project_dir / "final_manim_video.mp4"
    music_path = state.audio_paths.get("music") if state.audio_paths else None
    if music_path and not Path(music_path).exists():
        music_path = Path(music_path).resolve()
    if music_path and not Path(music_path).exists():
        music_path = None

    try:
        assemble_edu_video(
            scene_paths=[video_path],
            output=output_path,
            music_path=music_path,
            music_volume=0.2,
        )
        state.output_path = str(output_path)
    except Exception as exc:
        state.error = f"Manim video assembly failed: {exc}"

    return state
