#!/usr/bin/env bash
set -euo pipefail

# Bootstrap Ubuntu/WSL2 environment for the AI Video Studio.
# Run on a fresh Ubuntu 22.04/24.04 instance with internet access.

echo "[*] Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "[*] Installing base dependencies..."
sudo apt install -y \
  build-essential \
  git \
  git-lfs \
  curl \
  wget \
  python3-pip \
  python3-venv \
  python3-tk \
  ffmpeg \
  unzip \
  libgl1 \
  libglib2.0-0

echo "[*] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

echo "[*] Installing studio Python dependencies..."
pip install -r requirements.txt

echo "[*] Verifying FFmpeg..."
ffmpeg -version | head -n 1

echo "[*] Ollama install (optional, for local LLM)..."
if ! command -v ollama &> /dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "Ollama already installed."
fi

echo "[*] Creating model directory structure..."
mkdir -p models/comfyui/{checkpoints,diffusion_models,vae,loras,clip,controlnet,ipadapter,pulid}
mkdir -p models/{tts,music,whisper,upscalers,real-esrgan}

echo "[*] Bootstrap complete."
echo "Next steps:"
echo "  1. Install NVIDIA driver + CUDA (see docs/installation-ubuntu.md)."
echo "  2. Install ComfyUI and custom nodes (see docs/installation-ubuntu.md)."
echo "  3. Download model weights (see docs/model-installation.md)."
echo "  4. Run: python ai_studio/cli.py validate schemas/project.yaml"
