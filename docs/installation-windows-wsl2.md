# Installation Guide — Windows 11 + WSL2

Target: run the studio inside WSL2 Ubuntu with GPU pass-through.

## 1. Enable WSL2 and install Ubuntu

```powershell
# Run in PowerShell as Administrator
wsl --install -d Ubuntu-22.04
# Reboot when prompted
```

After reboot:

```powershell
wsl --set-default-version 2
wsl -d Ubuntu-22.04
```

## 2. Install NVIDIA driver on Windows

Download the latest Game Ready / Studio driver from:
https://www.nvidia.com/Download/index.aspx

Do **not** install the driver inside WSL2. WSL2 uses the host Windows driver via CUDA for WSL.

## 3. Install CUDA inside WSL2

```bash
# Inside WSL2 Ubuntu
sudo apt update
sudo apt install -y build-essential git git-lfs curl wget python3-pip python3-venv python3-tk

# CUDA toolkit (same commands as native Ubuntu; see docs/installation-ubuntu.md)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-4
```

## 4. Verify GPU inside WSL2

```bash
nvidia-smi
nvcc --version
```

## 5. Continue Ubuntu setup

From this point, follow `docs/installation-ubuntu.md` starting at step 3.

## 6. Windows-side helpers (optional)

- Install FFmpeg Windows build and add to Windows PATH if you want to preview outputs on host.
- Mount Windows folders from WSL2 using `/mnt/c/`.

## 7. Known WSL2 issues

- Long path limits: keep the repository path short, e.g., `~/Agentic-Video-maker`.
- File watcher performance: keep generated assets inside WSL2 filesystem (`/home/<user>/...`), not `/mnt/c`.
- GPU memory fragmentation: reboot WSL2 if OOM occurs:
  `wsl --shutdown` from PowerShell.

## Notes

- Commands are based on Microsoft WSL documentation and NVIDIA CUDA on WSL guide. Verify the latest instructions before running.
