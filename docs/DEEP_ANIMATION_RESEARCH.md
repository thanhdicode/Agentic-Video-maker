# Deep Research: AI-Driven 2D Educational Cartoon Production

> Goal: understand exactly how AumSum / Dr. Binocs / Smile and Learn / StoryBots / Kurzgesagt style videos are made, and map every technique to an open-source repo / workflow that can be added to this studio.

---

## 1. What these YouTube channels actually look like

| Channel | Visual style | Motion grammar | Audio | Why kids watch |
|---|---|---|---|---|
| **AumSum** | Round-headed turquoise mascot, big eyes, simple flat vector, bold black outlines, bright saturated colors, one prop per scene, large topic label + bottom captions. | Fast cuts (2-4 s/scene), mascot bobs/breathes, props float, camera slowly zooms, text pops. | AI TTS (clear, upbeat), constant background music, occasional "boing"/"whoosh" SFX. | Curiosity hook, simple question → surprising answer, friendly character. |
| **Dr. Binocs** | Binocular-eyed host + kid sidekicks, flat 2D, frequent cutaways to objects/animals, title cards. | Host points/zooms, object close-ups, smooth slide transitions, character enters/exits. | Energetic narrator, music beds, SFX matched to object movement. | Relatable host, "Little Kitty" sidekick, clear voice. |
| **Smile and Learn** | Softer palette, songs/chants, interactive prompts, expressive animal/children characters. | Choreographed dance-like motion, repetition, call-and-response, slower pace. | Songs, nursery-rhyme style melodies, claps. | Music + interactivity, emotional learning. |
| **StoryBots** | Mixed media (2D, CG, stop-motion, puppets), each character has a distinct personality. | Varied styles per episode, quick gags, live-action inserts. | Comedy timing, celebrity voices, music. | Variety and humor. |
| **Kurzgesagt** | Flat vector, abstract shapes, limited character animation, highly polished motion graphics. | Slow pans, shape morphing, particle systems, data viz. | Calm narrator, orchestral/electronic music. | Older kids/adults, complex topics visualized. |

**Common production rules across successful channels**
1. **Hook in the first 3 seconds** – title card + mascot reaction.
2. **One idea per scene** – one prop, one action, one sentence.
3. **Character first** – the mascot reacts to the information (surprise, point, thumbs-up).
4. **Motion every 0.5-1.5 s** – something must change on screen (prop, text, camera, character pose).
5. **Audio-visual sync** – SFX hit on cuts, music tempo drives pace, voice lip-sync is ideal.
6. **Repetition + recap** – summarize at the end, call-to-action (like/subscribe).

---

## 2. What a professional AI studio pipeline looks like in 2026

Based on public code, papers, and community workflows (AnimeLoom, ai-comic-drama, Wind-Comic, 2dimg2motion, mor-o/comfyui-2d-character-pipeline, ComfyUI storyboards).

```
Script (.md)
    │
    ▼
StoryDecomposer (LLM) ──► per-shot JSON
    │
    ├──► Character Designer ──► character sheet (front / 3/4 / side / expressions) + LoRA/IP-Adapter
    │
    ├──► Background / Prop Generator ──► FLUX / SDXL keyframes
    │
    ├──► Storyboard ──► shot list with camera, timing, asset refs
    │
    ├──► Video Generator ──► Wan2.2-I2V / LTX-2 / ToonCrafter / AnimateDiff
    │
    ├──► Lip-Sync / Expression ──► Rhubarb / Wav2Lip / LivePortrait
    │
    ├──► Voice / Music / SFX ──► F5-TTS / Kokoro / AudioCraft / FoleyCrafter
    │
    ▼
Editor (FFmpeg / MoviePy / Remotion / Blender) ──► final MP4 + YouTube metadata
```

---

## 3. Technology map

### 3.1 Character consistency (the hardest problem for long videos)

| Technique | What it does | Repo / tool | VRAM / cost |
|---|---|---|---|
| **LoRA fine-tuning** | Train a small adapter so the same character appears in every frame. | `kohya-ss/kohya_ss`, `bmaltais/Kohya_GUI`, `AI-Toolkit` | 8-24 GB, hours of training |
| **IP-Adapter** | Use reference images to lock face/style without training. | `cubiq/ComfyUI_IPAdapter_plus` | 2-8 GB at inference |
| **PuLID** | Stronger identity preservation than IP-Adapter for faces. | `ToTheBeginning/PuLID` | 8-16 GB |
| **CharForge / anime LoRA workflows** | Character sheet + I2V with identity lock. | `JoelJohnsonThomas/AnimeLoom` (concept) | RTX 4090 class |
| **Layered sprite sheets** | Generate separable body parts (hair, eyes, mouth, clothes) for 2D puppet animation. | `mor-o/comfyui-2d-character-pipeline` | CPU-friendly once generated |
| **2D sprite motion from one image** | Redraw key poses for a sprite loop. | `WU-HAOTIAN34/2dimg2motion` | API / GPU image gen |

**Best practice for this studio**
- On CPU prototype: use one Pollinations-generated mascot per video and animate it with code (squash/stretch, particles, props). Acceptable for short demos.
- On GPU production: train a LoRA for the mascot, generate a character sheet, and use IP-Adapter/PuLID in every FLUX/Wan generation.

### 3.2 Image / keyframe generation

| Model | Type | Best for | Repo / HF | VRAM |
|---|---|---|---|---|
| **FLUX.1-dev/schnell** | text-to-image | High-quality backgrounds, character keyframes. | `black-forest-labs/FLUX.1-dev` | 12-24 GB (dev), 8-16 GB (schnell) |
| **SDXL + LoRA** | text-to-image | Lower VRAM, good with trained character LoRAs. | `stabilityai/stable-diffusion-xl-base-1.0` | 6-12 GB |
| **ToonCrafter** | keyframe interpolation | Generate in-betweens between two cartoon poses. | `Doubiiu/ToonCrafter` | 16-27 GB |
| **2dimg2motion** | sprite generation | Generate game-style sprite sheets from one image. | `WU-HAOTIAN34/2dimg2motion` | API / image model |

### 3.3 Video / motion generation

| Model | Type | Best for | Repo / HF | VRAM |
|---|---|---|---|---|
| **Wan2.1 / Wan2.2** | T2V, I2V, FLF2V, Animate | High-quality long-form video; best open-source Sora competitor. | `Wan-AI/Wan2.1`, `Wan-AI/Wan2.2-Animate` | 14B: 24-40 GB; 1.3B: 8-12 GB |
| **LTX-Video / LTX-2** | DiT T2V/I2V | Fast, real-time capable, keyframe extension. | `Lightricks/LTX-Video` | 13B: 16-24 GB; 2B distilled: 6-10 GB |
| **CogVideoX 1.5** | T2V/I2V | Works on consumer GPUs. | `zai-org/CogVideo` | 5B: 8-16 GB; 2B: 4-8 GB |
| **ToonCrafter** | cartoon interpolation | Smooth motion between 2 keyframes. | `Doubiiu/ToonCrafter` | 16-27 GB |
| **AnimateDiff** | motion module for SD | Short animated clips with ControlNet. | `guoyww/AnimateDiff` | 6-12 GB |
| **AnimateAnyone / MagicAnimate** | human pose-driven I2V | Animate a character with a driving pose video. | `HumanAIGC/AnimateAnyone`, `magic-research/magic-animate` | 12-24 GB |
| **Wan-Animate** | character replacement + animation | Replicate expression/body motion of a reference video onto a character. | `wan-animate/wananimate` | 14B: 24-40 GB |

### 3.4 Pose / motion control

| Tool | What it does | Repo |
|---|---|---|
| **OpenPose** | 2D body keypoints for ControlNet. | `CMU-Perceptual-Computing-Lab/openpose` |
| **DWPose** | Better whole-body/keypoint extraction. | `IDEA-Research/DWPose` |
| **MediaPipe Pose** | 33 landmarks, runs on CPU/webcam. | `google-ai-edge/mediapipe` |
| **ControlNet** | Guide diffusion with pose/depth/edge. | `lllyasviel/ControlNet-v1-1-nightly` |

### 3.5 Lip-sync / face animation

| Tool | Type | Best for | Repo | Notes |
|---|---|---|---|---|
| **Rhubarb Lip Sync** | 2D phoneme timings | Classic 2D cartoon mouth shapes (A-F). | `DanielSWolf/rhubarb-lip-sync` | CPU, fast, 6-9 mouth shapes |
| **Wav2Lip** | face video lip-sync | Sync real face video to audio. | `Rudrabha/Wav2Lip` | CPU/GPU, needs face |
| **VideoRetalking** | high-quality lip-sync | Face video with expression control. | `vinthony/video-retalking` | GPU |
| **LivePortrait** | head/face animation | Animate portrait from audio or driving video. | `KwaiVGI/LivePortrait` | GPU |

### 3.6 Voice

| Tool | Type | Best for | Repo | VRAM |
|---|---|---|---|---|
| **F5-TTS** | TTS (flow matching) | Natural, controllable, multi-lingual. | `SWivid/F5-TTS` | 4-8 GB |
| **Kokoro** | Tiny TTS | Very fast, 82M params, good quality. | `hexgrad/kokoro` | CPU/GPU |
| **ChatTTS** | Conversational TTS | Expressive, Chinese/English. | `2noise/ChatTTS` | 4-8 GB |
| **edge-tts** | Free cloud TTS | CPU demo, no GPU. | `rany2/edge-tts` | 0 |

### 3.7 Music / SFX

| Tool | Type | Best for | Repo | VRAM |
|---|---|---|---|---|
| **AudioCraft / MusicGen** | text-to-music | Background loops, genre control. | `facebookresearch/audiocraft` | 6-16 GB |
| **AudioGen** | text-to-SFX | Short sound effects. | inside AudioCraft | 6-16 GB |
| **FoleyCrafter** | video-to-foley | Add realistic SFX synchronized to video. | `open-mmlab/FoleyCrafter` | 8-16 GB |
| **Stable Audio** | music/SFX | Commercial-quality, open weights. | `Stability-AI/stable-audio-tools` | 8-16 GB |

### 3.8 Upscaling / frame interpolation

| Tool | Function | Repo | VRAM |
|---|---|---|---|
| **Real-ESRGAN** | image/video 2x/4x upscale | `xinntao/Real-ESRGAN` | 2-8 GB |
| **RIFE / Practical-RIFE** | 2x-8x frame interpolation | `hzwer/practical-rife` | 2-8 GB |
| **GMFSS** | interpolation | `98mxr/GMFSS_Fortuna` | 4-8 GB |
| **REAL-Video-Enhancer** | all-in-one (upscale + interpolate + denoise) | `TNTwise/REAL-Video-Enhancer` | GPU |

### 3.9 Storyboard / editing

| Tool | Function | Repo / URL |
|---|---|---|
| **ComfyUI Storyboard** | Manage shots inside ComfyUI. | `colorAi/comfyui-storyboard` |
| **FairyTaler** | Conversation → 3 scenes. | `IIEleven11/ComfyUI-FairyTaler` |
| **AI-storyboard-generator** | Gemini + ComfyUI storyboard. | `dseditor/AI-storyboard-generator` |
| **ai-comic-drama** | Full pipeline script → video. | `YJH-Lab/ai-comic-drama` |
| **Wind-Comic** | Multi-agent novel → short drama. | `ChrisChen667788/wind-comic` |
| **Remotion** | React-based programmable video. | `remotion-dev/remotion` |
| **MoviePy** | Python video edit. | `Zulko/moviepy` |
| **Blender Python API** | 2D/3D animation, rigging. | `blender/blender` |
| **FFmpeg** | Final encode, filters, SRT burn. | `FFmpeg/FFmpeg` |

---

## 4. Recommended production architecture

### 4.1 CPU-only demo path (current VM)

Use free remote image generation + Python compositing. Best achievable without GPU:
- Pollinations.ai for character/background/props (`nologo`, `negative_prompt`).
- `rembg` for character transparency.
- `edge-tts` for voice.
- `pydub` for procedural music/SFX.
- `MoviePy` + `Pillow` for animation (squash/stretch, particles, Ken Burns, transitions, lip-sync overlays).
- Rhubarb for mouth timing (download prebuilt binary).

Limitations: character does not redraw every frame; motion is code-driven transforms of a static AI asset. It will never look like Wan2.2 I2V, but it can be highly engaging with proper easing, audio sync, and props.

### 4.2 GPU production path (RTX 4090 / A6000 / cloud)

```
Script
  │
  ▼
ComfyUI workflow 1: Character Sheet (FLUX + IP-Adapter + PuLID)
  │
  ▼
ComfyUI workflow 2: Per-shot Keyframes (FLUX + LoRA + ControlNet pose)
  │
  ▼
ComfyUI workflow 3: I2V / Animate (Wan2.2-I2V or LTX-2 or ToonCrafter)
  │
  ▼
Lip-sync (Rhubarb for 2D mouth, Wav2Lip for realistic face)
  │
  ▼
Audio (F5-TTS voice + MusicGen background + FoleyCrafter SFX)
  │
  ▼
Edit (MoviePy + FFmpeg) + upscale (Real-ESRGAN + RIFE)
  │
  ▼
YouTube metadata (title, description, thumbnail, chapters)
```

### 4.3 Cloud API fallback path

If no local GPU, use paid/limited APIs:
- **Pollinations.ai video models**: `veo`, `seedance`, `seedance-2.0`, `wan`, `wan-fast`, `ltx-2` (requires API key from `https://enter.pollinations.ai`).
- **Replicate / fal.ai / Runway** for FLUX + video endpoints.
- **Hugging Face Spaces** via `gradio_client` for public demos (rate-limited, unreliable for production).

---

## 5. What is currently missing in this repo

The repo has the orchestrator scaffold and a working CPU prototype, but lacks:

1. **GPU model weights** – FLUX, Wan2.2, LTX-2, ToonCrafter, TTS, music, whisper, upscale.
2. **ComfyUI runtime + custom nodes** – IP-Adapter, ControlNet, AnimateDiff, LTX, Wan wrappers, VideoHelperSuite.
3. **Character consistency pipeline** – LoRA training script or IP-Adapter/PuLID workflow.
4. **2D puppet / lip-sync integration** – Rhubarb binary, mouth sprite generation, Wav2Lip.
5. **Real video generation wrappers** – Wan, LTX, ToonCrafter, AnimateDiff clients in `tools/`.
6. **Audio generation** – AudioCraft/MusicGen, FoleyCrafter, F5-TTS/Kokoro.
7. **Long-form chunking** – 5-6 min requires scene retry, checkpointing, and QA.
8. **Quality evaluation** – MVAD/UVQ/VMAF/CLIP score, optical flow smoothness.
9. **YouTube package** – thumbnail, title, tags, chapters, end screen.
10. **Docker / one-click setup verified on RTX 4090** – `docker-compose` with all services, not just stubs.

---

## 6. Practical next steps

1. **Immediate (CPU VM)**: finish `demo_aumsum_v4.py` with better puppet animation, lip-sync, longer script, and transitions.
2. **Short term (RTX 4090 local)**: run `scripts/setup-rtx4090-wsl2.ps1`, install ComfyUI + nodes, download models, validate Wan2.2-I2V 14B at 720p.
3. **Medium term**: build LoRA training workflow for the mascot, connect IP-Adapter + ControlNet pose, generate first 30 s GPU clip.
4. **Long term**: integrate FoleyCrafter + MusicGen, QA scoring, YouTube metadata, automated chunked rendering for 5-6 min videos.
