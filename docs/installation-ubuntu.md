# Installation Guide — Ubuntu (Native or WSL2)

Tested target: Ubuntu 22.04/24.04 with NVIDIA GPU and CUDA 12.x.

## 1. System requirements

- NVIDIA GPU with 12GB+ VRAM (24GB recommended).
- 64GB RAM (32GB minimum).
- 500GB free NVMe storage (1TB recommended).
- CUDA 12.1 or 12.4 compatible driver.

## 2. Install NVIDIA driver and CUDA

```bash
# Update and install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git git-lfs curl wget python3-pip python3-venv python3-tk

# Add NVIDIA package repositories (example for CUDA 12.4)
# Verify the latest commands at https://developer.nvidia.com/cuda-downloads
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-4

# Add CUDA to PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Verify driver and CUDA
nvidia-smi
nvcc --version
```

## 3. Install Python, uv/pip

```bash
# Recommended: use uv for fast environment management
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env (uv)

# Or use venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

## 4. Clone and setup the studio

```bash
git clone https://github.com/thanhdicode/Agentic-Video-maker.git
cd Agentic-Video-maker

# Install Python dependencies
pip install -r requirements.txt

# Or with uv
uv pip install -r requirements.txt
```

## 5. Install FFmpeg

```bash
sudo apt install -y ffmpeg
# Optional: build with VMAF support for QA
# sudo apt install -y libvmaf-dev
```

## 6. Install Ollama (for local LLM)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:32b
# or ollama pull llama3.3:70b
```

## 7. Install ComfyUI (manual or Docker)

### Manual

```bash
cd vendor  # or external path
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

### Docker

```bash
docker pull ghcr.io/comfyanonymous/comfyui:latest
# Run with GPU
docker run --gpus all -p 8188:8188 -v $(pwd)/models:/models ghcr.io/comfyanonymous/comfyui:latest
```

## 8. Install custom nodes (essential)

```bash
cd ComfyUI/custom_nodes

git clone https://github.com/ltdrdata/ComfyUI-Manager.git

git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git

git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git

git clone https://github.com/Lightricks/ComfyUI-LTXVideo.git

git clone https://github.com/ToonCrafter/ToonCrafter.git  # verify node packaging

cd ..
```

## 9. Install model weights

See `docs/model-installation.md`.

## 10. Verify installation

```bash
python ai_studio/cli.py validate schemas/project.yaml
python ai_studio/cli.py --help
```

## 11. Start production

```bash
python ai_studio/cli.py init my-video
# Edit projects/my-video/project.yaml and script.md
python ai_studio/cli.py produce projects/my-video/project.yaml
```

## Notes

- Commands are based on official Ubuntu/CUDA documentation. Verify URLs and package versions before production use.
- For WSL2, enable CUDA in WSL and install the same packages inside the Ubuntu WSL instance.
- Windows native Python is supported but many generative model wheels are better tested on Linux/WSL2.
