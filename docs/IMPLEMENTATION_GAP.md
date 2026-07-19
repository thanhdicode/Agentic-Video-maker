# Implementation Gap Analysis — AI Video Studio

Date: 2026-07-19
Scope: determine what is missing to go from the current repo to a fully autonomous 5–6 minute AumSum-style educational cartoon studio.

## Current state

What works today:
- Deep repository research and stack selection (`research/`, `docs/RESEARCH_REPORT.md`).
- Studio design and workflow (`docs/STUDIO_DESIGN.md`, `docs/AUMSUM_STYLE.md`).
- `project.yaml` schema + `ai-studio` CLI (`ai_studio/cli.py`, `schemas/`).
- CPU-only demo v2 that generates a 25–30 second AumSum-style video from a script using:
  - Pollinations free image generation
  - `rembg` background removal
  - Edge TTS narration
  - MoviePy compositing + simple bounce/breathe animation

What does **not** work end-to-end yet:
- No locally installed generative models (FLUX, Wan, LTX, ToonCrafter, AudioCraft, etc.).
- No GPU or model weights.
- No working ComfyUI node workflows.
- No character consistency pipeline (LoRA / IP-Adapter / PuLID).
- No 2D rigging, lip-sync, or frame interpolation.
- No automatic music/SFX/foley mixing.
- No QA/review loop.
- No YouTube metadata/thumbnail package.

## Goal

A user opens the project on a local/Cloud GPU machine, runs:

```bash
python ai-studio.py init my-video
# edit script.md
python ai-studio.py produce projects/my-video/project.yaml
```

and receives a 5–6 minute, professional, AumSum/Dr. Binocs-style educational cartoon ready for YouTube upload.

## Gap 1 — Hardware / compute

| Requirement | Why | Minimum | Recommended |
|-------------|-----|---------|-------------|
| NVIDIA GPU | FLUX, Wan, LTX, ToonCrafter, AudioCraft require CUDA | RTX 3060 12GB | RTX 4090 24GB or RTX A6000 48GB |
| System RAM | Loading multiple models simultaneously | 32 GB | 64–128 GB |
| Disk | Model weights + cache | 500 GB NVMe | 1–2 TB NVMe |
| OS | CUDA ecosystem best on Linux/WSL2 | Windows 11 + WSL2 Ubuntu | Ubuntu 22.04/24.04 |
| Internet | Download weights, Pollinations fallback | 100 Mbps | 1 Gbps |

**Status**: missing on current VM (CPU only). Cannot be solved in code alone; must provision hardware or cloud GPU.

## Gap 2 — Base services and model weights

| Service / Model | Role | Size | Where to get | Status |
|-----------------|------|------|--------------|--------|
| ComfyUI + manager | Diffusion node backend | ~500 MB code | GitHub `comfyanonymous/ComfyUI` | not installed |
| FLUX.1-schnell | Image generation | ~23 GB | Hugging Face `black-forest-labs/FLUX.1-schnell` | not downloaded |
| FLUX.1-dev | Non-commercial image gen (optional) | ~23 GB | Hugging Face `black-forest-labs/FLUX.1-dev` | not downloaded |
| Wan 2.1 1.3B I2V | Fast image-to-video | ~6 GB | Hugging Face `Wan-AI/Wan2.1-I2V-1.3B-480P` | not downloaded |
| Wan 2.1 14B I2V | High-quality I2V | ~30 GB | Hugging Face `Wan-AI/Wan2.1-I2V-14B-480P` | not downloaded |
| LTX-Video | Longer motion clips | ~8–30 GB | Hugging Face `Lightricks/LTX-Video` | not downloaded |
| ToonCrafter | Cartoon interpolation | ~13 GB | Hugging Face `Doubiiu/ToonCrafter` | not downloaded |
| Real-ESRGAN x4+ | Upscale | ~65 MB | GitHub release | not downloaded |
| Practical-RIFE | Frame interpolation | ~18 MB | GitHub `GWD99/Practical-RIFE` | not downloaded |
| Kokoro | English TTS | ~350 MB | pip `kokoro` + onnx models | not installed |
| Fish Speech | Multi-lingual TTS (Vietnamese) | ~2 GB | Hugging Face `fishaudio/fish-speech-1.5` | not downloaded |
| F5-TTS | Voice cloning (weights NC) | ~4 GB | Hugging Face `SWivid/F5-TTS` | not downloaded |
| CosyVoice | Multi-lingual expressive TTS | ~4 GB | Hugging Face `FunAudioLLM/CosyVoice` | not downloaded |
| AudioCraft MusicGen | Background music | ~3.7 GB | pip `audiocraft` + model | not downloaded |
| AudioCraft AudioGen | SFX | ~3.7 GB | pip `audiocraft` + model | not downloaded |
| FoleyCrafter | Video foley | ~1.5 GB | GitHub `open-mmlab/FoleyCrafter` | not installed |
| WhisperX | Subtitles/alignment | ~3 GB | pip `whisperx` + faster-whisper | not installed |
| Ollama + Qwen3/Llama3.3 | Local LLM for script/storyboard | 20–40 GB | `ollama pull` | not installed |

**Estimated total disk**: 150–300 GB depending on chosen profile.

## Gap 3 — ComfyUI workflows

Current `workflows/comfyui/*.json` are placeholders. Real workflows needed:

| Workflow | Purpose | Custom nodes required |
|----------|---------|-----------------------|
| `flux_t2i.json` | Character/background/prop generation | ComfyUI core, IP-Adapter, PuLID nodes |
| `wan_i2v.json` | Image-to-video motion | `ComfyUI-WanVideoWrapper` or native nodes |
| `ltx_i2v.json` | Alternative I2V | `ComfyUI-LTXVideo` |
| `tooncrafter_i2v.json` | Cartoon keyframe interpolation | `ToonCrafter` ComfyUI node |
| `upscale.json` | Real-ESRGAN + RIFE | `ComfyUI-VideoHelperSuite`, `ComfyUI_UltimateSDUpscale` |
| `character_consistency.json` | FLUX + IP-Adapter + PuLID + LoRA | `ComfyUI_IPAdapter_plus`, PuLID nodes, LoRA loader |

Status: workflows need to be built and node IDs calibrated against an actual ComfyUI install.

## Gap 4 — Character consistency

A 5–6 minute AumSum video needs the same character across 30–60 scenes. Options:

| Approach | Tool | Effort | Quality | Recommendation |
|----------|------|--------|---------|----------------|
| LoRA fine-tune | CharForge / kohya-ss | Medium | Best | Primary |
| IP-Adapter face/body reference | `IP-Adapter` ComfyUI nodes | Low | Good | Fallback |
| PuLID identity | `PuLID` ComfyUI nodes | Low | Face only | Add-on |
| Reusable 2D puppet | Blender Grease Pencil + sprite atlas | High | Perfect for host | Hybrid |

Status: CharForge has been identified but not adapted to local use; no LoRA weights exist for a custom AumSum-like mascot yet.

## Gap 5 — 2D rigging / lip-sync / animation

For a professional host that talks continuously, current static-image bounce is not enough.

| Component | Tool | Status |
|-----------|------|--------|
| Mouth shapes from audio | Rhubarb Lip Sync | identified, not integrated |
| Head/expression motion | LivePortrait | identified, not integrated |
| 2D body rig | Blender Grease Pencil + `Tiny-2D-Rig-Tools` | not set up |
| Full body animation | Motion Canvas / Manim for infographics; Blender for character | not set up |
| Frame interpolation | Practical-RIFE / ToonCrafter | not set up |

## Gap 6 — Music / SFX / Foley

| Component | Tool | Gap |
|-----------|------|-----|
| Background music | AudioCraft MusicGen | weights NC; needs commercial-safe alternative or fine-tune |
| SFX library | AudioCraft AudioGen | same NC issue |
| SFX timing | FoleyCrafter / manual cue list | not integrated |
| Audio ducking | MoviePy / FFmpeg | simple code, not yet written |

Status: AudioCraft code can be installed, but weights are CC-BY-NC. For YouTube monetization, use `Stable Audio 3 Small` (terms to verify), paid royalty-free loops, or train a custom music LoRA.

## Gap 7 — MCP servers

Current `mcp/` directory has stubs. Real MCP servers needed:

| Server | Responsibility | Status |
|--------|---------------|--------|
| `filesystem_mcp_server.py` | Read/write project files, assets | stub |
| `comfyui_mcp_server.py` | Queue ComfyUI workflows, poll results | stub |
| `ffmpeg_mcp_server.py` | Encode, probe, cut, mix | stub |
| `browser_mcp_server.py` | YouTube upload / metadata research | stub |

Status: MCP servers need to be implemented or replaced with direct Python tool calls inside the agents. For an autonomous local studio, direct tool calls are simpler and faster than MCP.

## Gap 8 — Long-form (5–6 minute) orchestration

A 5–6 minute video at AumSum pacing (~7 s/scene) needs ~40–50 scenes. Missing:

- Scene chunking from script with WPM timing.
- Per-scene asset cache (so regenerating one scene does not rebuild all).
- Retry/regenerate loop when QA fails a scene.
- Parallel generation where dependencies allow.
- Resume from checkpoint after crash.

The current `orchestrator.py` is a linear LangGraph DAG; it needs checkpointing (`LangGraphPersistence`) and per-scene subgraphs.

## Gap 9 — QA / review

| Check | Tool | Status |
|-------|------|--------|
| Technical (black frames, audio sync) | FFmpeg ffprobe | not automated |
| Artifact detection | MVAD | not installed |
| Perceptual quality | UVQ / VMAF | not installed |
| Text safety / brand check | CLIP + local LLM | not written |
| Scene consistency | CLIP embedding similarity | not written |

## Gap 10 — YouTube package

| Asset | Status |
|-------|--------|
| Thumbnail | not generated |
| Title / description / tags | not generated |
| Chapters / timestamps | not generated |
| SRT / VTT | not exported from subtitle agent |
| End-screen / cards | not designed |

## Recommended implementation phases

| Phase | Goal | Time (with GPU) | Deliverable |
|-------|------|-----------------|-------------|
| 1. Environment | Install base stack on RTX 4090 / cloud | 2–4 hours | Docker Compose + `scripts/health-check.sh` green |
| 2. Models | Download and verify weights | 4–8 hours | `models/` populated with checksums |
| 3. ComfyUI workflows | Build 5–6 working workflow JSONs | 1–2 days | `workflows/comfyui/*.json` tested |
| 4. Character pipeline | Train/adapt LoRA for mascot | 1–2 days | `character_lora/` weights + character sheet |
| 5. Animation | Integrate I2V + RIFE + lip-sync stubs | 2–3 days | Scene-level motion clips |
| 6. Sound | Music/SFX/foley pipeline | 1–2 days | Mixed stems per scene |
| 7. Edit/QA | Compositing, subtitle, review loop | 1–2 days | `edit_agent.py` + `review_agent.py` working |
| 8. YouTube package | Metadata + thumbnail | 1 day | `publisher_agent.py` |
| 9. End-to-end | 90-second pilot, then 5–6 min | 2–3 days | `final.mp4` + YouTube package |

**Total realistic timeline (one engineer + RTX 4090)**: 10–14 days for a working 5–6 minute pipeline, assuming no major model issues.

## What the user should do next

1. **Provision hardware**: local RTX 4090, RunPod RTX 4090/A6000, Vast.ai, or Lambda Labs.
2. **Run the bootstrap script** (Linux/WSL2):
   ```bash
   scripts/bootstrap-ubuntu.sh
   ```
3. **Download weights** per `docs/model-installation.md`.
4. **Start ComfyUI** and install custom nodes per `docs/installation-ubuntu.md`.
5. **Run health check**:
   ```bash
   scripts/health-check.sh
   ```
6. **Run the first pilot**:
   ```bash
   python ai-studio.py init my-aumsum
   # edit project.yaml and script.md
   python ai-studio.py produce projects/my-aumsum/project.yaml
   ```

## Conclusion

The current repo is a **solid architecture, research base, and proof-of-concept**. It is **not yet a turnkey autonomous studio**. The missing pieces are primarily:
- GPU hardware,
- model weights,
- working ComfyUI workflows,
- character consistency training,
- animation/lip-sync integration,
- long-form orchestration with QA/retry,
- YouTube packaging.

With the recommended stack and phases above, the project can become a fully autonomous 5–6 minute educational cartoon studio in 10–14 days of focused implementation on a capable GPU machine.
