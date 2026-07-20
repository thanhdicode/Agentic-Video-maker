# AI Video Studio — Professional 2D Animation Design

Mục tiêu: Xây dựng một **AI agent tự sản xuất video hoạt hình 2D chuyên nghiệp**, từ script → character design → storyboard → assets → animation → voice/SFX/music → edit → upload-ready MP4.

Đầu vào: một kịch bản hoặc prompt từ người dùng.

Đầu ra: video hoạt hình 2D hoàn chỉnh, sẵn sàng upload YouTube.

---

## 1. Phân tích video mẫu

### Video 1: Dr. Binocs — “How Your Brain Works”
- Thể loại: educational cartoon cho trẻ em.
- Cấu trúc: hook → giải thích từng phần (cerebrum, cerebellum, brain stem, amygdala) → trivia → câu hỏi kết.
- Thị giác: nhân vật host (Dr. Binocs) giới thiệu, sau đó chuyển sang minh họa 2D/infographic với chữ và hình ảnh đơn giản, màu sắc tươi.
- Âm thanh: giọng narrator tự tin, nền nhạc vui, hiệu ứng “zoom in”, “ding” trivia.
- Điểm cần tái tạo: host character, minh họa kiến thức, chú thích lớn, recap/trivia.

### Video 2: Smile and Learn — “Technology Vocabulary”
- Thể loại: vocabulary flashcard video cho trẻ em.
- Cấu trúc: từng từ vựng xuất hiện với hình minh họa, đọc to, ví dụ ngắn, cuối cùng recap toàn bộ.
- Thị giác: background cố định, từng object xuất hiện, text label, animation nhẹ.
- Âm thanh: nhạc nền lặp, narrator đọc từ, hiệu ứng pop/ding khi object xuất hiện.
- Điểm cần tái tạo: object assets, text labels, appear/pop transitions, recap sequence.

### Đặc điểm chung để agent học
1. Phong cách visual: 2D cartoon, màu tươi, đường nét rõ, character đơn giản.
2. Pacing: nhanh, ~3-6 giây một ý, không để hình tĩnh quá lâu.
3. Cấu trúc lặp lại: intro → nội dung từng mục → recap/outro.
4. Âm thanh: narrator rõ ràng, nhạc nền vui, SFX đúng lúc.
5. On-screen text: tiêu đề, label, captions/subtitles.

---

## 2. Kiến trúc tổng thể (Agent A-Z)

```text
User Script / Prompt
        │
        ▼
┌───────────────────────────────────────┐
│  CREATIVE DIRECTOR AGENT               │
│  (reasoning LLM: script → creative plan)│
└───────┬───────────────────────────────┘
        │
        ▼
[SCRIPT BREAKDOWN] → scene list, shot list, assets list
        │
        ▼
┌───────────────────────────────────────┐
│  CHARACTER DESIGN AGENT                │
│  generate character sheets, LoRA, refs │
└───────┬───────────────────────────────┘
        │
        ▼
[ASSET GENERATION AGENT]
- backgrounds
- props / objects
- character poses / expressions
- UI elements (title cards, labels)
        │
        ▼
[STORYBOARD AGENT]
- keyframes per scene
- camera motion (pan/zoom/ken burns)
- timing per shot
- SFX/music cues
        │
        ▼
┌───────────────────────────────────────┐
│  ANIMATION AGENT                       │
│  image-to-video, interpolation,        │
│  rigging/2D motion, lip sync           │
└───────┬───────────────────────────────┘
        │
        ▼
[VOICE / AUDIO AGENT]
- narration TTS
- background music
- sound effects per cue
        │
        ▼
[EDIT & COMPOSITE AGENT]
- assemble timeline
- burn subtitles
- color grade / LUT
- transitions
        │
        ▼
[REVIEW / QA AGENT]
- validate length, audio levels, sync
- score & self-critique → loop back
        │
        ▼
[FINAL RENDER]
        MP4 + thumbnail + metadata
```

---

## 3. Stack công nghệ được chọn

### Orchestration
- **LangGraph**: state machine + multi-agent pipeline.
- **OpenMontage pattern**: reference video analysis → tool path → cost estimate.

### LLM / Reasoning
- Local: **Ollama + Qwen3-32B / Llama 3.3 70B**.
- Cloud (nếu có key): **Gemini 2.5 Pro / Claude 4 / GPT-5/4o** cho character design, code generation, storyboard.

### Character & Asset Consistency
- **CharForge** (MIT): train character LoRA từ 1 ảnh; tạo character sheet và giữ nhân vật nhất quán trong nhiều scene.
- **FLUX.1-dev / FLUX.1-schnell** + IP-Adapter + InstantID.
- **SVG / vector assets** với DiffusionSVG hoặc AI-generated PNG + RMBG-2.0/BiRefNet để remove background.

### 2D Animation
- **ToonCrafter** (Apache 2.0): cartoon interpolation giữa 2 keyframes → tạo motion.
- **AnimateDiff** (Apache 2.0): animate still images theo prompt.
- **LTX-Video 2.3 / Wan 2.2**: image-to-video/text-to-video cho camera motion và nhân vật.
- **Remotion** / **MoviePy**: programmatic animation, camera pan/zoom, Ken Burns, particles.
- **Rive** (open runtime): 2D character state machine + animation (nếu dùng rig đơn giản).

### Talking Head / Lip Sync (host character)
- **MuseV + MuseTalk**: nếu host là ảnh chân dung hoặc 3D render.
- **LivePortrait**: head motion + expression.
- **Rhubarb Lip Sync** (open source): tự động sinh mouth shapes từ audio cho 2D character.
- **Wav2Lip** / **VideoReTalking**: lip sync trên video có sẵn.

### Narration / TTS
- **F5-TTS** (MIT): zero-shot voice cloning, chất lượng cao.
- **Kokoro-82M** (Apache 2.0): nhanh, gọn, commercial-safe.
- **CosyVoice 3.0** (Apache 2.0): multi-lingual, emotion control.

### Music / SFX
- **AudioCraft** (Meta): MusicGen cho background music, AudioGen cho SFX.
- **Stable Audio Open** (Apache 2.0): alternative cho music/SFX.

### Editing / Subtitles
- **MoviePy 2.x** + **FFmpeg**.
- **faster-whisper** cho word-level subtitle.
- **Auto-Editor** cho silence removal / pacing.

### MCP Servers cho agent
- `filesystem`, `comfyui`, `ffmpeg`, `browser`, `python`, `shell`.

---

## 4. Workflow chi tiết cho agent

### 4.1 Creative Director Agent
**Input**: user script hoặc prompt.
**Output**:
- `creative_brief.json`: target audience, tone, visual style, pacing, duration.
- `script_segments.json`: mỗi segment có `{id, text, duration, visual_note, audio_note, sfx_note}`.
- `asset_manifest.json`: list characters, props, backgrounds cần generate.

### 4.2 Character Design Agent
**Input**: character descriptions from asset manifest.
**Output**:
- `character_sheets/{name}/`: reference images, front/side/3-4/back views, expression poses.
- `character_sheets/{name}/lora/`: trained LoRA weights.
- `character_prompts.json`: base prompt + negative + style tokens để tái sử dụng.

**Tools**:
1. Generate character concept với FLUX (text-to-image).
2. Upscale với Real-ESRGAN.
3. Remove background với RMBG-2.0.
4. (Optional) Train LoRA với CharForge/kohya_ss.

### 4.3 Asset Generation Agent
**Input**: asset manifest + character prompts.
**Output**:
- `assets/backgrounds/`
- `assets/props/`
- `assets/characters/{pose}/`
- `assets/ui/` (title cards, lower thirds, labels)

**Quy tắc**:
- Mỗi background/ prop/ pose phải dùng cùng style prompt để đồng nhất.
- PNG transparent cho props & characters.

### 4.4 Storyboard Agent
**Input**: script segments + assets.
**Output**:
- `storyboard.json`: list scenes, mỗi scene có:
  - `scene_id`, `segment_ids`
  - `keyframes`: list keyframe image paths + prompt
  - `camera`: `static`, `pan`, `zoom_in`, `zoom_out`, `ken_burns`
  - `duration`
  - `audio_cues`: music/SFX cue names

### 4.5 Animation Agent
**Input**: storyboard + keyframes.
**Output**: `video_clips/clip_{scene_id}.mp4`.

**Strategies tùy theo cảnh**:
1. **Talking host**: generate host talking video với MuseV/MuseTalk hoặc LivePortrait + lip sync.
2. **Object/label flashcard**: MoviePy animation (slide in, pop, bounce) + SFX.
3. **Story/illustration motion**: ToonCrafter hoặc Wan/LTX I2V giữa 2 keyframes.
4. **Camera motion**: MoviePy/Remotion pan/zoom/parallax trên still assets.

### 4.6 Voice / Audio Agent
**Input**: script segments.
**Output**:
- `audio/narration.wav`: TTS tổng hợp.
- `audio/music.wav`: background music loop.
- `audio/sfx/{cue}.wav`: sound effects.

**Tools**:
- TTS: F5-TTS / Kokoro.
- Music: MusicGen.
- SFX: AudioGen.

### 4.7 Edit & Composite Agent
**Input**: video clips, audio tracks, storyboard timing.
**Output**: `final.mp4` + `final.srt`.

**Bước**:
1. Concatenate clips theo storyboard.
2. Layer narration, music (volume ducking), SFX.
3. Burn subtitles (faster-whisper → ASS/SRT).
4. Add intro/outro, title cards, transitions.
5. Color grade với LUT/FFmpeg.
6. Export H.264 / H.265 1080p 30fps.

### 4.8 Review / QA Agent
**Input**: final.mp4, creative brief.
**Output**: `review.json` với score và gợi ý sửa.

**Metrics**:
- Duration vs target.
- Audio level (LUFS).
- Subtitle sync accuracy.
- Visual consistency check (CLIP embedding similarity between scenes).
- Hook retention (first 5s có text/visual kéo chăng).

Nếu score < threshold, loop về Animation Agent hoặc Edit Agent.

---

## 5. Prompt mẫu cho Perplexity / ChatGPT khi nghiên cứu

```text
You are a senior AI video production architect. I want to build a fully automated AI agent studio that produces 2D cartoon educational videos similar to "Dr. Binocs Show" and "Smile and Learn" on YouTube.

Given a user script, the agent must:
1. Design consistent 2D cartoon characters and generate character sheets.
2. Generate backgrounds, props, and UI labels.
3. Build a storyboard with keyframes and camera motion.
4. Animate scenes using image-to-video/interpolation, 2D motion, and lip sync.
5. Generate narration, background music, and sound effects.
6. Edit everything into a final MP4 with subtitles.

Recommend the best open-source GitHub repositories for each step as of 2026. Prioritize:
- Apache 2.0 or MIT license.
- Local GPU execution (not cloud-only).
- Python-native and Docker-friendly.
- Agent-compatible APIs or CLI.

Return the answer as a structured table: Step | Best Tool | GitHub | License | VRAM | Why.
Also provide a complete agent workflow diagram and a sample project folder structure.
```

---

## 6. Cấu hình phần cứng / runtime đề xuất

| Tier | GPU | VRAM | RAM | Use case |
|------|-----|------|-----|----------|
| Dev / CPU | CPU + 16GB RAM | — | 32GB | Test pipeline với placeholder / low-res |
| Entry GPU | RTX 3060 12GB | 12GB | 32GB | FLUX schnell, Wan 1.3B, audio, TTS |
| Pro | RTX 4090 / 3090 | 24GB | 64GB | FLUX dev, Wan 2.2 14B, LTX 2.3, ToonCrafter |
| Studio | 2x RTX 4090 or A6000 | 48GB | 128GB | Full pipeline parallel, 4K output |

### Cloud options nếu không có GPU local
- **RunPod / Vast.ai**: thuê RTX 4090/A6000/H100 theo giờ.
- **Modal / Replicate**: serverless inference cho từng step.
- **Skybox / fal.ai**: API cho image/video gen.

### Lưu ý về license thương mại
- **F5-TTS**: CC-BY-NC (không commercial). Nếu bán/YouTube monetize → dùng **Kokoro** hoặc **CosyVoice** (Apache 2.0).
- **FLUX.1-dev**: non-commercial. Commercial → **FLUX.1-schnell** (Apache 2.0) hoặc các finetune cho phép commercial.
- **AudioCraft models**: weights CC-BY-NC; code MIT.

---

## 7. Các bước triển khai trong repo này

1. Cài đặt base: Python 3.11, CUDA 12.x, ComfyUI, Docker.
2. Setup ComfyUI với custom nodes: VideoHelperSuite, AnimateDiff-Evolved, IPAdapter, ControlNet, Wan/LTX/ToonCrafter nodes.
3. Tải models: FLUX, Wan 2.2 1.3B/14B, LTX 2.3, ToonCrafter, F5-TTS/Kokoro, MusicGen/AudioGen.
4. Chạy `python main.py --script scripts/my_script.txt`.
5. Agent tự động sinh toàn bộ assets và render.
