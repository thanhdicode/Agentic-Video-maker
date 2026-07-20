# Educational Video Workflow

Turn a YouTube link (or any topic) into a short kid-friendly explainer video.

## Pipeline

1. **Ingest** – `yt-dlp` downloads the source video and extracts automatic captions.
2. **Research / Script** – an LLM (local Ollama by default, or the fallback template)
   writes a scene-by-scene narration with on-screen text prompts.
3. **Narration** – `tools/tts_tools.py` renders the script to WAV via pyttsx3 or
   Windows SAPI.
4. **Visuals** – each scene becomes a colored background clip with large text
   burned in using FFmpeg.
5. **Assembly** – `tools/edu_visual_tools.py` concatenates scenes and mixes
   optional background music.

## Usage

From a topic (fallback/template mode, works without Ollama):

```cmd
python -m agents.orchestrator --nodes edu_video --idea "fractions" --audience kids
```

From a YouTube URL (requires `yt-dlp` and a local Ollama or fallback topic):

```cmd
python -m agents.orchestrator --youtube "https://www.youtube.com/watch?v=..." --audience kids
```

Output: `projects/<project_id>/final_edu_video.mp4`

## Requirements

- `yt-dlp` for YouTube ingestion.
- FFmpeg for rendering and assembly.
- Optional: Ollama running for LLM-generated scripts; otherwise the pipeline
  uses the built-in template.
- Optional: `pyttsx3` or Windows with .NET System.Speech for TTS.

## Notes

- The default visual style is text-on-color for portability. Replace
  `generate_visual_clip` with your own image/video generation backend
  (ComfyUI/FLUX, Manim, etc.) for richer visuals.
- Captions and metadata are saved under `projects/<project_id>/ingest/`.
