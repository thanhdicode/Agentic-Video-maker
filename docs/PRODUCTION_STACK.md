# Production Stack — Missing Repos, Models, and Install Guide

> This doc lists every piece of software the studio still needs for full "script → 5-6 min YouTube cartoon" production, with exact repos, commands, VRAM requirements, and fallbacks.

---

## 1. GPU baseline

A local RTX 4090 (24 GB VRAM) or cloud A6000/4090 can run the full stack. For 4K/5-6 min videos, 48 GB (A6000 Ada / 2x 4090) is safer.

| Tier | GPU | VRAM | What it can run |
|---|---|---|---|
| Entry | RTX 4070 Ti / 4060 Ti | 16 GB | Wan2.2-T2V-1.3B, LTX-2 2B distilled, CogVideoX-2B, SDXL LoRA |
| Recommended | RTX 4090 | 24 GB | Wan2.2-I2V-14B 480p, LTX-2 13B distilled, ToonCrafter 512p, FLUX.1-dev |
| Professional | RTX A6000 / 4090 x2 | 48 GB | Wan2.2-I2V-14B 720p, LTX-2 13B BF16, Wan-Animate, 4K upscale |

---

## 2. ComfyUI + custom nodes

ComfyUI is the recommended GPU orchestration layer because every model below already has a node pack.

### 2.1 Install ComfyUI

```bash
# Ubuntu / WSL2
cd /opt
# or inside project vendor/
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

### 2.2 Required custom nodes

| Node pack | Why | Install |
|---|---|---|
| **ComfyUI-Manager** | install other nodes from UI | `git clone https://github.com/ltdrdata/ComfyUI-Manager.git custom_nodes/ComfyUI-Manager` |
| **ComfyUI_IPAdapter_plus** | character face/style reference | `git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git custom_nodes/ComfyUI_IPAdapter_plus` |
| **comfyui_controlnet_aux** | DWPose/OpenPose/Depth/LineArt preprocessors | `git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git custom_nodes/comfyui_controlnet_aux` |
| **ComfyUI-VideoHelperSuite** | video load/save, batch nodes | `git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git custom_nodes/ComfyUI-VideoHelperSuite` |
| **ComfyUI-WanVideoWrapper** | Wan2.1 / Wan2.2 video models | `git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git custom_nodes/ComfyUI-WanVideoWrapper` |
| **ComfyUI-LTXVideo** | LTX-Video / LTX-2 | `git clone https://github.com/Lightricks/ComfyUI-LTXVideo.git custom_nodes/ComfyUI-LTXVideo` |
| **ComfyUI-DynamiCrafterWrapper** | ToonCrafter / Dynamicrafter I2V | `git clone https://github.com/kijai/ComfyUI-DynamiCrafterWrapper.git custom_nodes/ComfyUI-DynamiCrafterWrapper` |
| **ComfyUI-AnimateDiff-Evolved** | AnimateDiff motion modules | `git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git custom_nodes/ComfyUI-AnimateDiff-Evolved` |
| **comfyui-storyboard** | shot management inside ComfyUI | `git clone https://github.com/colorAi/comfyui-storyboard.git custom_nodes/comfyui-storyboard` |

### 2.3 Run ComfyUI

```bash
python main.py --listen 0.0.0.0 --port 8188
```

---

## 3. Model weights to download

Use `python scripts/download_models.py --profile hybrid-professional` once ready. The table below is the source of truth.

### 3.1 Image generation

| Model | Size | URL | Notes |
|---|---|---|---|
| FLUX.1-dev | ~23 GB | `https://huggingface.co/black-forest-labs/FLUX.1-dev` | Best quality, needs 24 GB for fp16 |
| FLUX.1-schnell | ~23 GB | `https://huggingface.co/black-forest-labs/FLUX.1-schnell` | Faster, slightly lower quality |
| SDXL base | ~7 GB | `https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0` | Lower VRAM fallback |
| SDXL VAE fix | ~3 GB | `https://huggingface.co/madebyollin/sdxl-vae-fp16-fix` | Use with SDXL |

### 3.2 Video generation

| Model | Size | URL | Notes |
|---|---|---|---|
| Wan2.2-I2V-14B-720P | ~28 GB | `https://huggingface.co/Wan-AI/Wan2.2-I2V-14B-720P` | Best open I2V |
| Wan2.2-I2V-14B-480P | ~28 GB | `https://huggingface.co/Wan-AI/Wan2.2-I2V-14B-480P` | Lower VRAM than 720p |
| Wan2.2-T2V-1.3B | ~3 GB | `https://huggingface.co/Wan-AI/Wan2.2-T2V-1.3B` | 8 GB GPU entry |
| Wan2.2-Animate-14B | ~28 GB | `https://huggingface.co/Wan-AI/Wan2.2-Animate-14B` | Character animation/replacement |
| LTX-Video 2B/13B | ~2-38 GB | `https://huggingface.co/Lightricks/LTX-Video` | Fast, keyframe extension |
| CogVideoX1.5-5B | ~20 GB | `https://huggingface.co/zai-org/CogVideoX1.5-5B` | Consumer GPU friendly |
| CogVideoX1.5-5B-I2V | ~20 GB | `https://huggingface.co/zai-org/CogVideoX1.5-5B-I2V` | Image-to-video |
| ToonCrafter 512 fp16 | ~8 GB | `https://huggingface.co/Kijai/DynamiCrafter_pruned/resolve/main/tooncrafter_512_interp-fp16.safetensors` | Cartoon interpolation |

### 3.3 Control / pose

| Model | URL |
|---|---|
| DWPose whole-body | `https://huggingface.co/yzd-v/DWPose` (or Baidu/Google Drive in `IDEA-Research/DWPose`) |
| ControlNet OpenPose / Depth / LineArt | `https://huggingface.co/lllyasviel/ControlNet-v1-1` |

### 3.4 Character consistency

| Component | URL |
|---|---|
| IP-Adapter models | `https://huggingface.co/h94/IP-Adapter` |
| PuLID models | `https://huggingface.co/ToTheBeginning/PuLID` |
| InsightFace models (for IP-Adapter face) | `https://github.com/deepinsight/insightface/releases` |

### 3.5 Audio

| Model | Size | URL |
|---|---|---|
| F5-TTS base | ~1.3 GB | `https://huggingface.co/SWivid/F5-TTS` |
| Kokoro-82M | ~300 MB | `https://huggingface.co/hexgrad/Kokoro-82M` |
| MusicGen small/medium/large | 300 MB / 1.5 GB / 3.3 GB | `https://huggingface.co/facebook/musicgen-small` etc. |
| AudioGen medium | ~1 GB | `https://huggingface.co/facebook/audiogen-medium` |
| FoleyCrafter | ~2-4 GB | `https://huggingface.co/ymzhang319/FoleyCrafter` |

### 3.6 Upscale / interpolate

| Model | URL |
|---|---|
| Real-ESRGAN x4plus | `https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth` |
| Real-ESRGAN x2plus | `https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth` |
| RIFE 4.25 | `https://github.com/hzwer/Practical-RIFE` |

---

## 4. Per-step software and commands

### 4.1 Character design (FLUX + IP-Adapter / LoRA)

**Option A — no training (fastest)**
```bash
# generate character sheet in ComfyUI using IP-Adapter with 1 reference image
# workflow: workflows/comfyui/character_consistency_ipadapter.json
```

**Option B — train a LoRA (best for long videos)**
```bash
# kohya_ss
git clone https://github.com/bmaltais/Kohya_GUI.git
cd Kohya_GUI
./setup.sh
# prepare 15-30 images of the mascot with captions
# train on 24 GB VRAM with network_dim=32, rank=16, batch=1
```

### 4.2 Keyframe → video (Wan2.2 I2V)

```bash
# inside Wan2.1/2.2 repo
python generate.py \
  --task i2v-14B \
  --size 1280*720 \
  --ckpt_dir ./Wan2.2-I2V-14B-720P \
  --image scene_01_start.png \
  --prompt "AumSum style 2D cartoon, mascot explains gravity, bright colors, smooth motion"
```

Or use ComfyUI `workflows/comfyui/scene_i2v_wan.json`.

### 4.3 Cartoon inbetweening (ToonCrafter)

```bash
# ComfyUI-DynamiCrafterWrapper
# place tooncrafter_512_interp-fp16.safetensors in ComfyUI/models/diffusion_models/
# workflow: workflows/comfyui/scene_tooncrafter.json
```

### 4.4 Lip-sync (Rhubarb 2D)

```bash
# Windows prebuilt binary
Invoke-RestMethod -Uri "https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/1.14.0/Rhubarb-Lip-Sync-1.14.0-Windows.zip" -OutFile rhubarb.zip
Expand-Archive rhubarb.zip -DestinationPath tools/rhubarb

# convert audio to wav, then run
tools/rhubarb/rhubarb.exe -o json audio.wav > lipsync.json
```

JSON output:
```json
{
  "metadata": {"soundFile":"audio.wav","duration":5.42},
  "mouthCues": [
    {"start":0.00,"end":0.12,"value":"X"},
    {"start":0.12,"end":0.28,"value":"A"},
    {"start":0.28,"end":0.45,"value":"C"}
  ]
}
```

### 4.5 Voice (F5-TTS)

```bash
pip install f5-tts
f5-tts-infer --ref_audio ref.wav --ref_text "reference text" --gen_text "script text" --output output.wav
```

### 4.6 Music (MusicGen)

```bash
pip install audiocraft
python - <<'PY'
from audiocraft.models import MusicGen
model = MusicGen.get_pretrained('facebook/musicgen-medium')
model.set_generation_params(duration=30)
wav = model.generate(['upbeat playful educational background music for kids cartoon'])
PY
```

### 4.7 SFX (FoleyCrafter)

```bash
git clone https://github.com/open-mmlab/FoleyCrafter.git
cd FoleyCrafter
python inference.py --input silent_video.mp4 --prompt "cartoon pop sound" --save_dir output/
```

### 4.8 Upscale + smooth (Real-ESRGAN + RIFE)

```bash
# Real-ESRGAN
python inference_realesrgan.py -n RealESRGAN_x4plus.pth -i frames/ -o upscaled/ --face_enhance

# RIFE 4x interpolation 24fps → 96fps
python inference_video.py --fps 96 --exp 2 --video final.mp4 --model RIFE_4.25.pth
```

---

## 5. Missing repo/software checklist

- [ ] ComfyUI runtime (`vendor/ComfyUI/`)
- [ ] ComfyUI-Manager
- [ ] ComfyUI_IPAdapter_plus
- [ ] comfyui_controlnet_aux
- [ ] ComfyUI-VideoHelperSuite
- [ ] ComfyUI-WanVideoWrapper
- [ ] ComfyUI-LTXVideo
- [ ] ComfyUI-DynamiCrafterWrapper
- [ ] ComfyUI-AnimateDiff-Evolved
- [ ] comfyui-storyboard
- [ ] Rhubarb Lip Sync binary
- [ ] F5-TTS / Kokoro
- [ ] AudioCraft / MusicGen / AudioGen
- [ ] FoleyCrafter
- [ ] Real-ESRGAN
- [ ] Practical-RIFE
- [ ] Model weights (see section 3)
- [ ] Docker Compose with all services
- [ ] Long-form chunking + QA agent
- [ ] YouTube metadata generator

---

## 6. CPU fallback verdict

On a CPU-only VM the studio can only run:
- `edge-tts`, `pydub`, `MoviePy`, `Pillow`, `rembg`, `Rhubarb`.
- Pollinations.ai for still images (video models require API key or unsupported on anonymous tier).

**Verdict**: CPU pipeline can produce 2-4 min "slideshow + puppet" videos with strong audio sync, but true smooth character animation requires GPU (Wan/LTX/ToonCrafter) or paid video APIs.
