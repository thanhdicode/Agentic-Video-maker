# RTX 4090 Local Setup Guide

One-command goal:

```bash
git clone https://github.com/thanhdicode/Agentic-Video-maker.git
cd Agentic-Video-maker
bash scripts/bootstrap-ubuntu.sh
bash scripts/install_comfyui_nodes.sh
python scripts/download_models.py --profile hybrid-professional
bash scripts/health-check.sh
python ai-studio.py init my-aumsum
# edit projects/my-aumsum/script.md
python ai-studio.py produce projects/my-aumsum/project.yaml
```

If all services are green, `ai-studio produce` will autonomously generate a 5–6 minute AumSum-style cartoon from a single script.

## 1. Hardware checklist

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | RTX 3090 24 GB | RTX 4090 24 GB or RTX A6000 48 GB |
| System RAM | 32 GB | 64–128 GB |
| Disk | 512 GB NVMe | 1–2 TB NVMe |
| PSU | 750 W | 850 W |
| OS | Windows 11 + WSL2 | Ubuntu 22.04/24.04 native |

## 2. OS choice

**Recommended:** native Ubuntu 22.04 or 24.04.

**Windows + WSL2** also works, but some ComfyUI custom nodes have path/permission issues in WSL. If you choose WSL2, make sure it is WSL **2** and GPU support is enabled:

```powershell
# PowerShell as Administrator
wsl --set-default-version 2
wsl --install -d Ubuntu-24.04
```

Inside WSL2, the guide below is identical.

## 3. NVIDIA driver + CUDA

For native Ubuntu, follow <https://developer.nvidia.com/cuda-downloads> or use the driver from the distribution:

```bash
# Remove old drivers
sudo apt purge nvidia* libnvidia*

# Install driver and CUDA (example for Ubuntu 24.04)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y nvidia-driver-565 cuda-toolkit-12-6
```

Reboot, then verify:

```bash
nvidia-smi
nvcc --version
```

For WSL2, install the **Windows NVIDIA driver** first, then install the WSL CUDA toolkit inside WSL2.

## 4. Clone repo and bootstrap

```bash
git clone https://github.com/thanhdicode/Agentic-Video-maker.git
cd Agentic-Video-maker
bash scripts/bootstrap-ubuntu.sh
```

This installs system packages, creates a Python virtual environment, installs Python dependencies, and sets up directory structure.

## 5. Install ComfyUI and custom nodes

```bash
bash scripts/install_comfyui_nodes.sh
```

This clones `ComfyUI` into `vendor/ComfyUI` and installs:
- ComfyUI Manager
- IP-Adapter Plus
- VideoHelperSuite
- WanVideoWrapper
- ComfyUI-LTXVideo
- ControlNet Aux

## 6. Download model weights

```bash
python scripts/download_models.py --profile hybrid-professional
```

Downloads approximately 150–250 GB of weights. You can pass `--hf-token <token>` for gated models such as `FLUX.1-dev`.

`download_models.py` also accepts:

- `local-open-source` — smaller, fully Apache/BSD weights.
- `hybrid-professional` — recommended (FLUX.1-schnell + Wan 14B + LTX + ToonCrafter).
- `maximum-quality` — largest quality-first set.

## 7. Start services

In separate terminals:

```bash
# Terminal 1 — ComfyUI
python vendor/ComfyUI/main.py --listen 0.0.0.0 --port 8188

# Terminal 2 — Ollama (if using local LLM)
ollama serve
ollama pull qwen3:32b
```

## 8. Health check

```bash
bash scripts/health-check.sh
```

Expected output (all green):

```
[OK] NVIDIA driver detected
[OK] CUDA available
[OK] Python dependencies
[OK] ComfyUI reachable at http://localhost:8188
[OK] Ollama reachable
[OK] FFmpeg installed
[OK] Model weights present
```

## 9. First production

```bash
python ai-studio.py init my-aumsum
```

Edit the generated files:
- `projects/my-aumsum/script.md` — the educational script.
- `projects/my-aumsum/project.yaml` — production profile, duration, voice, etc.

Then run:

```bash
python ai-studio.py produce projects/my-aumsum/project.yaml
```

The orchestrator will:
1. Expand the script into 30–60 scenes.
2. Generate/retrieve a consistent character.
3. Generate backgrounds, props, and keyframes with ComfyUI.
4. Animate with Wan/LTX/ToonCrafter.
5. Generate narration (Kokoro / CosyVoice / F5-TTS).
6. Generate background music and SFX (AudioCraft).
7. Burn subtitles with WhisperX.
8. Composite, upscale, and review in MoviePy/FFmpeg.
9. Export `projects/my-aumsum/output/final.mp4`.

## 10. Common issues

### `CUDA out of memory`

- Lower resolution in `project.yaml` (e.g., 1280x720, 30 fps).
- Use the `local-open-source` profile (Wan 1.3B instead of 14B).
- Enable `--highvram` or `--normalvram` in ComfyUI arguments.
- Quantize models to FP8 if your ComfyUI nodes support it.

### `nvidia-smi` works but `torch.cuda` is not available

PyTorch was installed for CPU. Force reinstall:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --force-reinstall
```

### ComfyUI cannot find a custom node

Re-run:

```bash
bash scripts/install_comfyui_nodes.sh
```

### Missing `git-lfs`

```bash
sudo apt install git-lfs
```

### Out of disk

Use an external NVMe or symlink `models/` to a larger drive:

```bash
mv models /mnt/bigdisk/models
ln -s /mnt/bigdisk/models models
```

## 11. Windows-only path (not WSL)

If you want to run directly on Windows without WSL:

1. Install Python 3.11/3.12 from python.org, check **Add Python to PATH**.
2. Install CUDA 12.x Toolkit.
3. Install Git and FFmpeg (e.g., via `winget` or gyan.dev FFmpeg builds).
4. Run the equivalent PowerShell/bootstrap script: `scripts/bootstrap-windows.ps1` (see `scripts/bootstrap-windows.ps1`).
5. Run `python scripts/download_models.py --profile hybrid-professional`.
6. Run `python ai-studio.py init ...` and `python ai-studio.py produce ...`.

WSL2 or native Ubuntu is strongly preferred because most model toolchains target Linux.

## 12. Notes on 5–6 minute videos

At AumSum pacing (~7 seconds per scene), a 5-minute video needs ~40 scenes and a 6-minute video needs ~50. The orchestrator automatically:

- splits the script,
- generates per-scene assets in parallel where possible,
- caches finished scenes so retries/resumes are cheap,
- concatenates and post-processes the final output.

Estimated total generation time on RTX 4090:
- 5-minute video: 2–6 hours (depends on quality profile and retries).
- 6-minute video: 3–8 hours.

## 13. Next after setup

Once setup is green, the project becomes a true autonomous studio:
- Drop a script into `projects/<name>/script.md`.
- Adjust `project.yaml` (resolution, quality, language).
- Run `python ai-studio.py produce projects/<name>/project.yaml`.
- Collect `output/final.mp4` + `output/youtube_metadata.json` + `output/thumbnail.png`.
