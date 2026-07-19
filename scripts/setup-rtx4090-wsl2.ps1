#Requires -RunAsAdministrator
# One-click WSL2 + Ubuntu 24.04 + RTX 4090 setup for the AI Video Studio.
# Run this in PowerShell as Administrator on Windows 11.
# If WSL is not enabled, the script enables it and asks for a reboot.

$ErrorActionPreference = "Stop"

Write-Host "=== AI Video Studio — RTX 4090 WSL2 Setup ===" -ForegroundColor Cyan
Write-Host "This script will enable WSL2, install Ubuntu 24.04, install CUDA, and prepare the studio."

# 1. Administrator check
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Please right-click PowerShell and choose 'Run as Administrator'."
    exit 1
}

# 2. NVIDIA driver check
if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] NVIDIA driver not found." -ForegroundColor Red
    Write-Host "Install the latest RTX 4090 driver from: https://www.nvidia.com/drivers/"
    exit 1
}
Write-Host "[OK] NVIDIA driver detected:" -ForegroundColor Green
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader

# 3. Enable required Windows features
$wslFeature = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -ErrorAction SilentlyContinue
$vmFeature = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -ErrorAction SilentlyContinue

if ($wslFeature.State -ne "Enabled" -or $vmFeature.State -ne "Enabled") {
    Write-Host "[*] Enabling WSL2 and Virtual Machine Platform..."
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart -All
    Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart -All
    Write-Host "[WARN] Windows features installed. Please REBOOT now, then re-run this script." -ForegroundColor Yellow
    exit 0
}

# 4. Set WSL default version to 2
wsl --set-default-version 2 | Out-Null

# 5. Install Ubuntu 24.04 if not present
$distroList = wsl --list --quiet 2>$null
if ($distroList -notcontains "Ubuntu-24.04") {
    Write-Host "[*] Installing Ubuntu 24.04..."
    wsl --install -d Ubuntu-24.04 --no-launch
} else {
    Write-Host "[OK] Ubuntu-24.04 already installed."
}

# 6. Make sure Ubuntu-24.04 is the default
wsl --set-default Ubuntu-24.04

# 7. Test WSL
Write-Host "[*] Testing WSL..."
wsl -d Ubuntu-24.04 -u root -- bash -c "echo 'WSL is ready'"

# 8. Write the Linux setup script into WSL
$linuxSetup = @'
#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/thanhdicode/Agentic-Video-maker.git"
BRANCH="devin/add-demo-script"
STUDIO_DIR="/opt/agentic-video-studio"

echo "[*] Updating Ubuntu packages..."
export DEBIAN_FRONTEND=noninteractive
apt update && apt upgrade -y

echo "[*] Installing NVIDIA CUDA toolkit for WSL..."
if ! dpkg -l cuda-keyring 2>/dev/null | grep -q '^ii'; then
    wget -q https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb -O /tmp/cuda-keyring.deb
    dpkg -i /tmp/cuda-keyring.deb
    apt update
fi
apt install -y cuda-toolkit-12-6 || apt install -y cuda-toolkit-12-5 || apt install -y cuda-toolkit-12-4

# Verify CUDA
if command -v nvcc &>/dev/null; then
    nvcc --version
else
    echo "[WARN] nvcc not found in PATH; adding /usr/local/cuda/bin to PATH."
    echo 'export PATH=/usr/local/cuda/bin:$PATH' >> /root/.bashrc
    export PATH=/usr/local/cuda/bin:$PATH
fi

echo "[*] Verifying NVIDIA inside WSL..."
nvidia-smi

echo "[*] Installing system dependencies..."
apt install -y \
    build-essential git git-lfs curl wget \
    python3 python3-pip python3-venv python3-tk \
    ffmpeg libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev \
    tmux htop unzip p7zip-full

echo "[*] Cloning / updating studio repository..."
if [[ -d "$STUDIO_DIR/.git" ]]; then
    cd "$STUDIO_DIR"
    git fetch
    git checkout "$BRANCH" || true
    git pull
else
    git clone --branch "$BRANCH" "$REPO_URL" "$STUDIO_DIR"
    cd "$STUDIO_DIR"
fi

echo "[*] Running bootstrap..."
bash scripts/bootstrap-ubuntu.sh

echo "[*] Activating venv for the rest of setup..."
source venv/bin/activate

echo "[*] Installing ComfyUI + custom nodes..."
bash scripts/install_comfyui_nodes.sh

echo "[*] Creating model directories..."
mkdir -p models/comfyui/{checkpoints,diffusion_models,vae,clip,loras,controlnet,ipadapter,pulid}
mkdir -p models/{tts,music,whisper,upscalers,real-esrgan,practical-rife}

echo "[*] Running health check..."
bash scripts/health-check.sh || true

echo "[*] Running a quick CPU prototype to verify the pipeline (no GPU models downloaded yet)..."
python ai-studio.py init demo-verify || true
python ai-studio.py produce projects/demo-verify/project.yaml || true

echo ""
echo "===================================================="
echo "Studio environment is ready at: $STUDIO_DIR"
echo "Next steps:"
echo "  1. Download model weights: python scripts/download_models.py --profile hybrid-professional"
echo "  2. Start ComfyUI: python vendor/ComfyUI/main.py --listen 0.0.0.0 --port 8188"
echo "  3. Start production: python ai-studio.py init my-aumsum"
echo "                       python ai-studio.py produce projects/my-aumsum/project.yaml"
echo "===================================================="
'@

$tmpFile = "$env:TEMP\ai-studio-wsl-setup.sh"
Set-Content -Path $tmpFile -Value $linuxSetup -Encoding UTF8
Copy-Item -Path $tmpFile -Destination "\\wsl$\Ubuntu-24.04\tmp\ai-studio-wsl-setup.sh" -Force

# 9. Run the setup script inside WSL as root
Write-Host "[*] Running studio setup inside WSL (this can take 10-30 minutes)..." -ForegroundColor Cyan
wsl -d Ubuntu-24.04 -u root -- bash /tmp/ai-studio-wsl-setup.sh

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "Open WSL Ubuntu-24.04 and run:"
Write-Host "  cd /opt/agentic-video-studio"
Write-Host "  source venv/bin/activate"
Write-Host "  python ai-studio.py init my-aumsum"
