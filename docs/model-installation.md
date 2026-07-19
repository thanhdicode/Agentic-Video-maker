# Model Installation Guide

All weights should be downloaded from official Hugging Face or GitHub releases and verified against published checksums where available.

## 1. Directory layout

```text
models/
├── comfyui/
│   ├── checkpoints/
│   ├── diffusion_models/
│   ├── vae/
│   ├── loras/
│   ├── clip/
│   └── controlnet/
├── tts/
├── music/
├── whisper/
└── upscalers/
```

## 2. Image generation

### FLUX.1-schnell (recommended, commercial-safe)

```bash
mkdir -p models/comfyui/unet models/comfyui/clip models/comfyui/vae
huggingface-cli download black-forest-labs/FLUX.1-schnell --local-dir models/flux-schnell
```

Files to place in ComfyUI `models/`:
- `unet/flux1-schnell.safetensors`
- `clip/flux_text_encoders/` (t5xxl + clip_l)
- `vae/ae.safetensors`

### FLUX.1-dev (non-commercial)

```bash
huggingface-cli download black-forest-labs/FLUX.1-dev --local-dir models/flux-dev
```

Use only for research/non-commercial prototypes.

## 3. Image-to-video

### Wan 2.1

```bash
huggingface-cli download Wan-AI/Wan2.1-I2V-14B-480P --local-dir models/comfyui/diffusion_models/Wan2.1-I2V-14B-480P
huggingface-cli download Wan-AI/Wan2.1-I2V-1.3B-14B-480P --local-dir models/comfyui/diffusion_models/Wan2.1-I2V-1.3B-480P
```

### LTX-Video

```bash
huggingface-cli download Lightricks/LTX-Video --local-dir models/comfyui/diffusion_models/LTX-Video
```

### ToonCrafter

```bash
huggingface-cli download Doubiiu/ToonCrafter --local-dir models/comfyui/diffusion_models/ToonCrafter
```

## 4. Character consistency

### IP-Adapter and PuLID

```bash
# IP-Adapter FLUX
huggingface-cli download h94/IP-Adapter --local-dir models/comfyui/ipadapter

# PuLID FLUX
huggingface-cli download guozinan/PuLID --local-dir models/comfyui/pulid
```

### LoRA training

No pre-downloaded weights; train with `kohya-ss/sd-scripts` or `CharForge` from reference images.

## 5. TTS

### Kokoro

Installed automatically by `pip install kokoro`. Weights download on first run.

### Fish Speech

```bash
huggingface-cli download fishaudio/fish-speech-1.5 --local-dir models/fish-speech
```

### F5-TTS

```bash
huggingface-cli download SWivid/F5-TTS --local-dir models/f5-tts
```

### CosyVoice

```bash
huggingface-cli download FunAudioLLM/CosyVoice3-0.5B-2512 --local-dir models/cosyvoice
```

## 6. Music / SFX

### AudioCraft

Installed by `pip install audiocraft`. Models download on first call.

### Stable Audio 3

```bash
huggingface-cli download stabilityai/stable-audio-3-small-music --local-dir models/stable-audio-3
```

## 7. Whisper

```bash
# WhisperX will download faster-whisper models on first use
mkdir -p models/whisper
# Optional: pre-download large-v2
huggingface-cli download Systran/faster-whisper-large-v2 --local-dir models/whisper/large-v2
```

## 8. Upscale / Interpolation

### Real-ESRGAN

```bash
mkdir -p models/real-esrgan
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth -P models/real-esrgan
```

### Practical-RIFE

Model checkpoints auto-download on first run or via script in `tools/rife_client.py`.

## 9. Checksums

Store SHA256 sums in `models/checksums.txt` and verify after download:

```bash
sha256sum -c models/checksums.txt
```

## 10. Notes

- Use `huggingface-cli` or `hf_transfer` for large files.
- Keep `models/` outside the git repo; add to `.gitignore`.
- Total storage requirement: ~200GB–500GB depending on profile.
