#!/usr/bin/env bash
set -euo pipefail

# Bootstrap Ubuntu/WSL2 environment for the AI Video Studio.
# Run on a fresh Ubuntu 22.04/24.04 instance with an NVIDIA GPU (RTX 4090 recommended).

echo "[*] Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "[*] Installing base dependencies..."
sudo apt install -y \
  build-essential \
  git \
  git-lfs \
  curl \
  wget \
  python3 \
  python3-pip \
  python3-venv \
  python3-tk \
  ffmpeg \
  libgl1 \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender-dev

# Initialize git-lfs
sudo -u "$USER" git lfs install || true

echo "[*] Verifying NVIDIA GPU..."
if ! command -v nvidia-smi &> /dev/null; then
  echo "[WARN] nvidia-smi not found. Install NVIDIA driver + CUDA manually:"
  echo "  https://docs.nvidia.com/cuda/cuda-installation-guide-linux/"
  echo "Continuing with CPU-only tools; GPU models will not run."
fi

echo "[*] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

echo "[*] Installing studio Python dependencies..."
pip install -r requirements.txt

echo "[*] Verifying FFmpeg..."
ffmpeg -version | head -n 1

echo "[*] Installing Ollama (optional, for local LLM)..."
if ! command -v ollama &> /dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh
  echo "Pull a model with: ollama pull qwen3:32b"
else
  echo "Ollama already installed."
fi

echo "[*] Creating model directory structure..."
mkdir -p models/comfyui/{checkpoints,diffusion_models,vae,loras,clip,controlnet,ipadapter,pulid}
mkdir -p models/{tts,music,whisper,upscalers,real-esrgan,practical-rife}

echo "[*] Bootstrap complete."
echo "Next steps:"
echo "  1. Install NVIDIA driver + CUDA (see docs/SETUP_RTX4090.md)."
echo "  2. Install ComfyUI + custom nodes: bash scripts/install_comfyui_nodes.sh"
echo "  3. Download model weights: python scripts/download_models.py --profile hybrid-professional"
echo "  4. Run health check: bash scripts/health-check.sh"
echo "  5. Start production: python ai-studio.py init my-video"
