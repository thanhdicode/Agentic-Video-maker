#Requires -RunAsAdministrator
# Bootstrap Windows 11 + RTX 4090 environment for the AI Video Studio.
# This is a best-effort native Windows setup. WSL2 Ubuntu is strongly preferred.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command -Name $Name -ErrorAction SilentlyContinue)
}

Write-Host "[*] AI Video Studio - Windows Bootstrap" -ForegroundColor Cyan

# 1. Check GPU
Write-Host "[*] Checking NVIDIA GPU..."
if (-not (Test-Command "nvidia-smi")) {
    Write-Host "[WARN] nvidia-smi not found. Install the latest Game Ready or Studio driver from https://www.nvidia.com/drivers/"
} else {
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
}

# 2. Check CUDA
Write-Host "[*] Checking CUDA..."
$nvcc = "$env:ProgramFiles\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\nvcc.exe"
if (-not (Test-Path $nvcc)) {
    Write-Host "[WARN] CUDA 12.6 nvcc not found at $nvcc. Install CUDA Toolkit from https://developer.nvidia.com/cuda-downloads?target_os=Windows"
} else {
    & $nvcc --version
}

# 3. Check Python
Write-Host "[*] Checking Python..."
if (-not (Test-Command "python")) {
    Write-Host "[ERROR] Python not found. Install Python 3.11/3.12 from https://python.org and check 'Add Python to PATH'."
    exit 1
}
python --version

# 4. Check Git
if (-not (Test-Command "git")) {
    Write-Host "[ERROR] Git not found. Install from https://git-scm.com/download/win"
    exit 1
}

# 5. Check FFmpeg
if (-not (Test-Command "ffmpeg")) {
    Write-Host "[WARN] FFmpeg not found. Install from https://www.gyan.dev/ffmpeg/builds/ and add to PATH."
}

# 6. Create venv
Write-Host "[*] Creating Python virtual environment..."
$VenvPath = "$RepoRoot\venv"
if (-not (Test-Path $VenvPath)) {
    python -m venv "$VenvPath"
}
& "$VenvPath\Scripts\python.exe" -m pip install --upgrade pip

# 7. Install requirements
Write-Host "[*] Installing Python dependencies..."
& "$VenvPath\Scripts\python.exe" -m pip install -r "$RepoRoot\requirements.txt"

# 8. Install Ollama (optional)
Write-Host "[*] Checking Ollama..."
if (-not (Test-Command "ollama")) {
    Write-Host "[INFO] Ollama not found. Install from https://ollama.com/download/windows"
}

# 9. Create directory structure
Write-Host "[*] Creating directories..."
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\comfyui\checkpoints" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\comfyui\diffusion_models" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\comfyui\vae" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\comfyui\loras" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\comfyui\clip" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\comfyui\controlnet" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\comfyui\ipadapter" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\comfyui\pulid" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\tts" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\music" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\whisper" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\models\upscalers" | Out-Null
New-Item -ItemType Directory -Force -Path "$RepoRoot\projects" | Out-Null

Write-Host "[*] Windows bootstrap complete." -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "  1. Install NVIDIA driver and CUDA Toolkit if not already present."
Write-Host "  2. Install ComfyUI + custom nodes manually or via scripts/install_comfyui_nodes.ps1"
Write-Host "  3. Download weights: .\venv\Scripts\python.exe scripts\download_models.py --profile hybrid-professional"
Write-Host "  4. Start production: .\venv\Scripts\python.exe ai-studio.py init my-aumsum"
