# Troubleshooting Guide

## Environment

### Python version errors

- The studio requires Python 3.11 or 3.12.
- If `python` points to 3.10, use `python3.11 -m venv venv`.

### `torch` CUDA not available

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If `False`:
- Reinstall torch with CUDA index:
  `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124`
- Verify `nvidia-smi` driver version >= 525.

### Out of memory during video generation

- Reduce resolution or use Wan 2.1 1.3B instead of 14B.
- Enable model offloading in ComfyUI or use `--lowvram`.
- Close other GPU processes.

### WSL2 OOM

```powershell
wsl --shutdown
```

Then restart WSL2.

## ComfyUI

### Custom node import errors

- Update ComfyUI and custom nodes:
  ```bash
  cd ComfyUI
  git pull
  cd custom_nodes/ComfyUI-Manager
  git pull
  ```
- Run `python main.py` and check console for missing dependency errors.

### Model not found

- Confirm model files are under `ComfyUI/models/` in the correct subfolder:
  - `checkpoints/` for SDXL/FLUX UNET
  - `diffusion_models/` for Wan/LTX
  - `vae/` for VAE
  - `loras/` for trained LoRA
- Use absolute paths in workflow JSON or symlink `models/` into ComfyUI root.

## Models

### FLUX.1-dev used commercially

- Replace with `FLUX.1-schnell` weights and update `config/model_config.yaml`.

### F5-TTS / AudioCraft weights are CC-BY-NC

- Use only for non-commercial output.
- For commercial use, switch to `Kokoro` / `Fish Speech` and `Stable Audio 3` with verified terms.

## TTS

### Voice sounds robotic

- Try `Kokoro` for English or `Fish Speech` for multi-lingual.
- For cloning, use at least 10 seconds of clean reference audio.

### Mispronounced words

- Add a pronunciation dictionary per language.
- Use CosyVoice/Fish Speech text normalization.

## Video generation

### Character drift between scenes

- Use the character LoRA consistently.
- Fix the seed for a scene batch.
- Use IP-Adapter/PuLID in every ComfyUI prompt.
- Increase denoise strength for I2V only when needed.

### Motion is flickery or inconsistent

- Add a de-flicker pass with FFmpeg.
- Use frame interpolation (Practical-RIFE) to smooth 24fps to 30/60fps.

## Output

### Subtitles overflow

- Reduce `max_chars_per_line` in `config/pipeline_config.yaml`.
- Use larger `safe_area_percent` in `project.yaml`.

### Audio clipping

- Lower SFX and music volumes (`music_volume_db`, `sfx_volume_db`).
- Add a limiter in the final FFmpeg pass.

## QA

### QA agent reports black frames

- Re-run the failing scene using `ai-studio regenerate --scene <id>`.
- Check that the output video exists and `ffprobe` returns valid metadata.

## Getting more help

- Check `research/source_index.md` for official documentation links.
- Run `python scripts/health-check.sh` and review output.
