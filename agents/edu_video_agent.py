"""Educational video agent.

Turns a YouTube URL or a free-form topic into a short explainer video for kids.
The flow is:

1. Ingest YouTube video (if provided) -> transcript + metadata.
2. Generate kid-friendly script with scene breakdowns.
3. Synthesize narration audio per scene.
4. Render simple visual clips (colored background + text).
5. Assemble final video with transitions/background music.
"""

from __future__ import annotations

import os
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
        "fallback_model": data.get("ollama", {}).get("fallback_model", "llama3.3:70b"),
    }


def _topic_from_state(state: PipelineState) -> str:
    """Derive the lesson topic from idea, youtube metadata, or a default."""
    if state.idea:
        return state.idea

    meta = getattr(state, "source_metadata", {}) or {}
    title = meta.get("title", "")
    if title:
        return title

    return "fractions"


def edu_video_node(state: PipelineState) -> PipelineState:
    """Generate an educational explainer video."""
    from tools.edu_script_tools import generate_educational_script
    from tools.edu_visual_tools import assemble_edu_video, generate_visual_clip
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

    # 2. Audio + visual clips per scene
    scene_dir = project_dir / "edu_scenes"
    scene_dir.mkdir(parents=True, exist_ok=True)

    colors = ["0x3B82F6", "0x10B981", "0xF59E0B", "0xEF4444", "0x8B5CF6", "0x06B6D4"]
    scene_paths: list[Path] = []

    for i, segment in enumerate(script, start=1):
        narration = segment.get("narration", "")
        visual_text = segment.get("visual_text", narration[:60]) or narration[:60]
        if not narration:
            continue

        wav_path = scene_dir / f"scene_{i:02d}.wav"
        clip_path = scene_dir / f"scene_{i:02d}.mp4"

        try:
            text_to_speech(narration, wav_path)
            generate_visual_clip(
                visual_text=visual_text,
                audio_path=wav_path,
                output=clip_path,
                bg_color=colors[(i - 1) % len(colors)],
            )
            scene_paths.append(clip_path)
        except Exception as exc:
            state.error = f"Scene {i} failed: {exc}"
            return state

    # 3. Assemble
    output_path = project_dir / "final_edu_video.mp4"
    music_path = state.audio_paths.get("music") if state.audio_paths else None
    if music_path and not Path(music_path).exists():
        # Try resolving relative to the repo root.
        music_path = Path(music_path).resolve()
    if music_path and not Path(music_path).exists():
        music_path = None

    try:
        assemble_edu_video(
            scene_paths=scene_paths,
            output=output_path,
            music_path=music_path,
            music_volume=0.2,
        )
        state.output_path = str(output_path)
    except Exception as exc:
        state.error = f"Educational video assembly failed: {exc}"

    return state
