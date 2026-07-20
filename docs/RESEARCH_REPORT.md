# AI Animation Video Studio — Research Report

Date: 2026-07-19
Scope: deep research of open-source repositories and model weights for an autonomous 2D cartoon educational video studio.

## 1. Research method

- Ran targeted web searches across 15 functional groups (A–O).
- Deduplicated by `owner/repo`; removed forks without added value, mirrors, empty repos, and repos without runnable code.
- Audited README, LICENSE, model cards, and release notes for shortlisted repositories.
- Documented search queries, candidates, rejected items, benchmarks, and sources in `research/`.
- **Limitation**: this session did not run end-to-end benchmarks because the current environment has no GPU. Benchmark designs are recorded and must be executed on a CUDA workstation.

## 2. Reference video analysis

### 2.1 Dr. Binocs — How Your Brain Works
- Format: host character + animated explanation + trivia card + call-to-action.
- Pacing: fast, ~5–8 seconds per idea.
- Visual grammar: full-body host, close-up props, diagram overlays, text labels, zoom transitions.
- Audio: energetic narrator, background music, "ding" SFX at trivia.

### 2.2 Smile and Learn — Technology Vocabulary
- Format: vocabulary flashcards, object appears + label + narrator, recap sequence.
- Pacing: ~3–5 seconds per word.
- Visual grammar: static background, object animation (pop/slide), labels, recap grid.
- Audio: music loop, narrator, light SFX per object.

### Lessons for the agent
1. Hook in the first 3–5 seconds.
2. Use a recurring host character for continuity.
3. Alternate full-body host shots with object/infographic close-ups.
4. Keep text large and short.
5. Match music energy to segment type (calm explanation vs. upbeat hook/recap).
6. Use consistent SFX vocabulary (pop, ding, whoosh).

## 3. Architecture comparison

### Option A — Pure generative video
- Flow: script → prompt → text/image-to-video model → concatenate.
- Tools: Wan 2.1 / LTX-Video / HunyuanVideo.
- Strengths: cinematic motion, minimal manual asset work.
- Weaknesses: character consistency degrades over many shots; hands/face artifacts; long-form narrative drift; expensive at high resolution; limited editability.
- Verdict: not viable as the *only* architecture for a professional host-driven cartoon.

### Option B — Rigged 2D animation
- Flow: script → character sheet → layered/rigged character → keyframe animation + lip-sync → compositing.
- Tools: Blender Grease Pencil / OpenToonz / Synfig / Rive / custom SVG puppet.
- Strengths: perfect consistency, editable, fast to re-record voice/dialogue.
- Weaknesses: high manual asset prep; automated rigging from AI is still immature; motion quality depends on animator/keyframe pipeline.
- Verdict: ideal for recurring host segments, but requires automation bridge.

### Option C — Hybrid professional studio (recommended)
- Flow:
  1. AI generates character concepts, sheets, and key assets.
  2. Character master is converted into layered/rigged parts (Blender Grease Pencil or sprite atlas) for host/dialogue shots.
  3. Generative I2V (Wan/LTX/ToonCrafter) produces motion for complex scenes and background motion.
  4. Code-driven motion graphics (Motion Canvas / Manim / MoviePy) handles infographics, labels, transitions.
  5. Compositor assembles, adds subtitles, audio, SFX, and color grade.
  6. QA agent validates and triggers scene-level regeneration.
- Strengths: balances consistency and motion quality; each scene uses the right tool; highly editable.
- Weaknesses: more components to maintain; needs GPU and a model zoo.
- Verdict: selected.

## 4. Recommended production stack

| Layer | Selected tool | License | Role |
|-------|---------------|---------|------|
| Orchestration | LangGraph (Python) + custom job runner | MIT (LangGraph) | Agent DAG, state, retry, resume |
| Script / pre-production | Local LLM (Ollama Qwen3/Llama3.3) or API (Gemini/Claude) | Model dependent | Script breakdown, storyboard, shot list |
| Character consistency | CharForge + kohya-ss/sd-scripts + FLUX.1-schnell | MIT / Apache-2.0 (LoRA); FLUX schnell Apache-2.0 | Character sheet + LoRA training |
| Image generation | FLUX.1-schnell + ComfyUI | FLUX schnell Apache-2.0; ComfyUI GPL-3.0 | Backgrounds, props, keyframes |
| Image-to-video | Wan 2.1 (1.3B/14B) via ComfyUI | Apache-2.0 | General motion clips |
| Cartoon interpolation | ToonCrafter | Apache-2.0 | Keyframe-to-keyframe cartoon motion |
| Fast video | LTX-Video | Apache-2.0 | Longer/controlled motion clips |
| 2D rigging / host | Blender + Grease Pencil + Tiny 2D Rig Tools / COA Tools | Blender GPL; addons verify | Host character rig and lip-sync sprites |
| 2D lip-sync | Rhubarb Lip Sync | MIT | Phoneme-to-mouth-shape timing |
| Head/expression | LivePortrait | Apache-2.0 | Optional head motion/refinement |
| Motion graphics | Motion Canvas | MIT | Infographics, labels, transitions |
| Compositing | MoviePy 2.x + FFmpeg | MIT / LGPL-GPL | Timeline, audio mix, subtitles, encode |
| Narration TTS | Kokoro (English) / Fish Speech (multi-lingual incl. Vietnamese) | Apache-2.0 | Fast, commercial-safe narration |
| Voice cloning | F5-TTS (weights CC-BY-NC) or CosyVoice | Code MIT; weights NC / Apache-2.0 | Cloned host voice (non-commercial or use CosyVoice) |
| Music / SFX | AudioCraft MusicGen/AudioGen | Code MIT; weights CC-BY-NC | Background music and sound effects |
| Music alternative | Stable Audio 3 Small | Verify Stability AI terms | CPU-friendly music/SFX |
| Foley | FoleyCrafter | Apache-2.0 | Add synchronized sound to silent clips |
| Subtitles | WhisperX / faster-whisper | BSD-2 / MIT | Word-level timestamps + SRT/VTT |
| Upscale | Real-ESRGAN + Practical-RIFE | BSD-3 / MIT | Final resolution and frame interpolation |
| QA | FFmpeg probes + MVAD + UVQ + VMAF | MIT/Apache/BSD | Technical and perceptual checks |
| YouTube package | Custom LLM wrappers + thumbnail generator | — | Title, description, tags, thumbnail, chapters |

## 5. Three production profiles

### Profile 1 — Local Open-Source
- Hardware: RTX 3060 12GB or RTX 4060 Ti 16GB.
- RAM: 32 GB.
- Storage: 500 GB NVMe.
- OS: Windows 11 + WSL2 Ubuntu or native Ubuntu.
- Models: FLUX.1-schnell, Wan 2.1 1.3B, Kokoro, AudioCraft Small, Whisper base.
- Cost: hardware only; electricity.
- Render time per 1 min video: ~1–4 hours.
- Quality: good, limited to fast/small models.
- Limitations: no high-res I2V; voice cloning quality lower; music loops shorter.

### Profile 2 — Hybrid Professional (recommended default)
- Hardware: RTX 4090 24GB local + optional RunPod/Vast RTX A6000/H100 for heavy I2V.
- RAM: 64 GB.
- Storage: 1 TB NVMe + model cache.
- Models: FLUX.1-schnell/dev (for non-commercial use schnell for commercial), Wan 2.1 14B, LTX-Video, CharForge LoRA, Fish Speech / CosyVoice, AudioCraft.
- Cost: local GPU + ~$0.5–$3/min heavy cloud compute when needed.
- Render time per 1 min video: ~15–45 minutes locally, faster with cloud burst.
- Quality: professional; ready for YouTube with minor review.
- Fallback: use Wan 1.3B / LTX distilled when VRAM constrained.

### Profile 3 — Maximum Quality
- Hardware: 2× RTX 4090 or A6000 48GB; cloud H100 nodes.
- RAM: 128 GB.
- Storage: 2 TB NVMe.
- Models: FLUX.1-dev (non-commercial) or API image gen, Wan 2.1 14B, LTX 2.3, custom fine-tuned character LoRA, MuseTalk/LivePortrait for host, FoleyCrafter, custom music loops.
- Cost: $5–$20 per minute of video depending on cloud/API usage.
- Render time per 1 min video: ~30–90 minutes.
- Quality: near-studio, but requires human review and possible scene regeneration.
- Limitations: highest cost; some models non-commercial.

## 6. Workflow from script to MP4

| Stage | Agent | Input | Output | Tool | Cache key |
|-------|-------|-------|--------|------|-----------|
| 0. Intake | Producer | `project.yaml`, `script.md` | `production/project_manifest.json` | YAML parser | project id + file hash |
| 1. Script intelligence | Script Analyst | script | outline, scenes, shots, WPM | LLM | script text hash |
| 2. Creative direction | Director | outline + style | art direction, shot list, continuity rules | LLM | style seed |
| 3. Character production | Character Designer | character descriptions | character bible, sheet, LoRA, mouth sprites | CharForge / kohya-ss | character name + prompt hash |
| 4. Storyboard | Storyboard Artist | script + art direction | storyboard JSON + animatic | LLM + image gen | scene prompt hash |
| 5. Asset production | Asset Generator | storyboard | backgrounds, props, transparent PNGs | FLUX + ComfyUI + RMBG | asset id + seed |
| 6. Voice | Voice Director | script segments | per-scene WAV, phoneme timings | Kokoro/Fish Speech + WhisperX | text + voice profile hash |
| 7. Animation | Animator | storyboard + assets + voice | scene plates / motion clips | Blender (host) + Wan/LTX/ToonCrafter (scenes) + Motion Canvas (infographics) | scene config + seed |
| 8. Sound | Sound Designer | voice + scene cues | music, SFX, Foley, stems | AudioCraft + FoleyCrafter | cue list + seed |
| 9. Compositing | Compositor | all scene plates + audio | draft MP4 + SRT | MoviePy + FFmpeg | scene hashes + edit hash |
| 10. QA | QA Agent | draft + manifest | QA report + regenerate tickets | FFmpeg + MVAD + UVQ/VMAF + CLIP | output hash |
| 11. Final render | Compositor | approved draft | final 1080p MP4 + clean master + captions | FFmpeg | approved output hash |
| 12. Delivery | Publisher | final + metadata | thumbnail, title, description, tags, chapters | LLM + FLUX | title hash |

## 7. Repository reuse plan

| Repository | Reuse | Fork / Adapter | Custom code | Role |
|------------|-------|----------------|-------------|------|
| `langchain-ai/langgraph` | Direct dependency | No | State classes, node wrappers | Orchestrator |
| `comfyanonymous/ComfyUI` | Docker service + API | No | Workflow JSON loader, queue client | Diffusion backbone |
| `Wan-Video/Wan2.1` | Model weights + inference scripts | No | ComfyUI node / adapter | I2V/T2V generation |
| `Lightricks/LTX-Video` | Model weights | No | ComfyUI node / adapter | Fast video |
| `Doubiiu/ToonCrafter` | Model weights + inference | No | ComfyUI node / adapter | Cartoon interpolation |
| `black-forest-labs/flux` | Model weights via Hugging Face | No | Prompt wrapper | Keyframe generation |
| `RishiDesai/CharForge` | Adapt training script | Yes or local fork | Remove cloud caption/upscale deps; local LoRA training | Character LoRA |
| `kohya-ss/sd-scripts` | Direct dependency / Docker | No | Config generator, dataset prep | LoRA training backend |
| `Tencent-AILab/IP-Adapter` | ComfyUI custom nodes | No | Node setup | Character consistency |
| `ToTheBeginning/PuLID` | ComfyUI custom nodes | No | Node setup | Face consistency |
| `DanielSWolf/rhubarb-lip-sync` | Binary / pip | No | Sprite mapping wrapper | 2D lip-sync timing |
| `KwaiVGI/LivePortrait` | Direct install | No | Optional stylization pass | Head motion |
| `motion-canvas/motion-canvas` | Direct dependency | No | Component library (SceneContainer, CharacterRig, CaptionRenderer, etc.) | Infographics / transitions |
| `Zulko/moviepy` | Direct dependency | No | Compositing layer | Final assembly |
| `FFmpeg/FFmpeg` | System package | No | Python wrapper | Encoding/post-processing |
| `hexgrad/kokoro` | Direct dependency | No | Voice profile manager | English narration |
| `fishaudio/fish-speech` | Direct dependency / Docker | No | Voice profile manager | Multi-lingual narration |
| `SWivid/F5-TTS` | Direct dependency | No | Voice profile manager (non-commercial) | Voice cloning |
| `FunAudioLLM/CosyVoice` | Direct dependency | No | Voice profile manager | Cloned / expressive voice |
| `facebookresearch/audiocraft` | Direct dependency | No | Music/SFX cue generator | Music / SFX |
| `open-mmlab/FoleyCrafter` | Direct dependency / Docker | No | Scene-plate input wrapper | Foley |
| `m-bain/WhisperX` | Direct dependency | No | Subtitle formatter + word timing | Subtitles |
| `xinntao/Real-ESRGAN` | Direct dependency | No | Upscale wrapper | Post upscale |
| `GWD99/Practical-RIFE` | Direct dependency | No | Interpolation wrapper | Frame interpolation |
| `ChenFeng-Bristol/MVAD` | Direct dependency | No | Artifact detection node | Visual QA |
| `google/uvq` | Direct dependency | No | No-reference QA score | Perceptual QA |
| `Netflix/vmaf` | Direct dependency | No | Regression comparison | Reference QA |
| `ManimCommunity/manim` | Optional dependency | No | Infographic adapter | Educational diagram fallback |

## 8. License and commercial-use summary

| Asset | License | Commercial? | Notes |
|-------|---------|-------------|-------|
| LangGraph code | MIT | Yes | — |
| ComfyUI code | GPL-3.0 | Yes (copyleft) | Source distribution if modified |
| FLUX.1-schnell weights | Apache-2.0 | Yes | Recommended default |
| FLUX.1-dev weights | Non-commercial | No | Use only for research/prototype |
| Wan 2.1 weights | Apache-2.0 | Yes | — |
| LTX-Video weights | Apache-2.0 | Yes | — |
| ToonCrafter weights | Apache-2.0 | Yes | — |
| CharForge code | MIT | Yes | FLUX weights usage still applies |
| kohya-ss code | Apache-2.0 | Yes | — |
| IP-Adapter code/weights | Apache-2.0 / model dependent | Yes | Verify model card |
| PuLID code | Apache-2.0 | Yes | Model weights license verify |
| Rhubarb Lip Sync | MIT | Yes | — |
| LivePortrait | Apache-2.0 | Yes | — |
| Motion Canvas | MIT | Yes | — |
| MoviePy | MIT | Yes | — |
| FFmpeg | LGPL/GPL | Yes with correct build flags | Use LGPL build or distribute source if GPL |
| Kokoro | Apache-2.0 | Yes | — |
| Fish Speech | Apache-2.0 | Yes | Supports Vietnamese |
| F5-TTS code | MIT | Code yes | Weights CC-BY-NC: non-commercial |
| CosyVoice | Apache-2.0 | Yes | Multi-lingual |
| AudioCraft code | MIT | Code yes | Weights CC-BY-NC: non-commercial |
| Stable Audio 3 | Verify | Verify | Terms to confirm |
| FoleyCrafter | Apache-2.0 | Yes | — |
| WhisperX | BSD-2 | Yes | pyannote model verify |
| Real-ESRGAN | BSD-3 | Yes | — |
| Practical-RIFE | MIT | Yes | — |
| MVAD | MIT | Yes | — |
| UVQ | Apache-2.0 | Yes | — |
| VMAF | BSD-2-Clause-Patent | Yes | Patent clause |

## 9. Security and supply-chain measures

- Run all generative model servers inside Docker with non-root users.
- Pin model weights by SHA256 in `models/checksums.txt`.
- Use `pip`/`uv` lock files and Docker image digests.
- Scan `requirements.txt` and `package.json` with `pip-audit` / `npm audit`.
- Verify all downloaded model URLs against official Hugging Face / GitHub releases.
- Do not commit API keys; use `.env` and runtime secret injection.
- Isolate model inference from public network; use local ComfyUI / MCP server on localhost.
- Reject repos with pyinstaller false positives (e.g., REAL-Video-Enhancer binary) from automated install unless rebuilt from source.

## 10. Benchmark status

Benchmarks are designed in `research/repository_benchmarks.csv`. Execution is blocked on a GPU environment. First benchmark to run on a CUDA workstation:

1. Character consistency suite on CharForge + FLUX + IP-Adapter.
2. Lip-sync test with Rhubarb sprite pipeline and LivePortrait head motion.
3. I2V comparison: Wan 1.3B/14B, LTX, ToonCrafter on identical keyframes.
4. Audio mix test: Kokoro narration + MusicGen + AudioGen + ducking.
5. End-to-end 90-second cartoon from one script.

## 11. Next actions

1. Choose production profile and provision hardware / cloud GPU.
2. Build Docker Compose with ComfyUI, Ollama, Kokoro/Fish Speech, AudioCraft, WhisperX.
3. Download pinned model weights (FLUX schnell, Wan 1.3B or 14B, LTX, ToonCrafter, Real-ESRGAN, RIFE).
4. Implement/adapt CharForge for local captioning and LoRA training.
5. Build Blender Grease Pencil host character rig and mouth sprite pipeline.
6. Design `project.yaml` schema and CLI (`ai-studio`).
7. Run benchmark suite and adjust stack.
