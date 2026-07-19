# AI Video Studio Architecture

This repo implements the **Ultimate Local AI Video Making Studio** blueprint.

## Pipeline

```
[IDEA]
  │
  ▼
[Research Agent] ──► [Script Agent] ──► [Storyboard Agent]
  │                       │                    │
  ▼                       ▼                    ▼
[Image Gen]         [Voice Gen]         [Music / SFX Gen]
  │                       │                    │
  ▼                       ▼                    ▼
[Video Gen] ────────► [Lip Sync] ────────► [Audio Mix]
  │
  ▼
[Subtitle Gen] ──► [Video Edit] ──► [Upscale] ──► [Final Render]
```

## Agents

- `orchestrator.py` — LangGraph `StateGraph` wiring all nodes.
- `research_agent.py` — Context / source gathering.
- `script_agent.py` — Hook + problem/solution/result script structure.
- `storyboard_agent.py` — Converts script to scene JSON.
- `image_agent.py` — Drives ComfyUI FLUX workflows.
- `video_agent.py` — Drives ComfyUI Wan/LTX I2V workflows.
- `audio_agent.py` — TTS, MusicGen, AudioGen.
- `edit_agent.py` — FFmpeg assembly, subtitles, audio mixing.

## Tools

- `comfyui_client.py` — REST client for ComfyUI `/prompt` and `/view`.
- `ffmpeg_tools.py` — Concat, LUT, subtitle burn, audio mix.
- `whisper_tools.py` — faster-whisper transcription and SRT generation.
- `music_tools.py` — AudioCraft wrappers.
- `upscale_tools.py` — Real-ESRGAN + RIFE stubs.

## MCP

`mcp/mcp_config.json` registers filesystem, FFmpeg, and ComfyUI MCP servers.

## Docker

- `comfyui.dockerfile` — ComfyUI + FLUX nodes.
- `audio.dockerfile` — AudioCraft/F5-TTS service.
- `agents.dockerfile` — Main LangGraph pipeline runner.
- `docker-compose.yml` — Full stack.
