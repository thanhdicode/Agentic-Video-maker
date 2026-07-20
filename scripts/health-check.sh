#!/usr/bin/env bash
set -euo pipefail

# Health check for the AI Video Studio environment.

PASS=0
FAIL=0

check() {
  if eval "$2" &> /dev/null; then
    echo "[PASS] $1"
    PASS=$((PASS + 1))
  else
    echo "[FAIL] $1"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== AI Video Studio Health Check ==="

check "Python 3.11+" "python3 --version | grep -E 'Python 3\.(11|12)'"
check "venv exists" "test -d venv"
check "FFmpeg installed" "ffmpeg -version"
check "Git LFS installed" "git-lfs version"
check "NVIDIA driver" "nvidia-smi"
check "CUDA nvcc" "nvcc --version"
check "Python dependencies" "source venv/bin/activate && python -c 'import moviepy, langgraph, yaml'"
check "ComfyUI directory" "test -d ComfyUI || test -d vendor/ComfyUI"
check "Models directory" "test -d models"

echo ""
echo "Results: $PASS passed, $FAIL failed."

if [[ $FAIL -gt 0 ]]; then
  echo "Review failed items before running production."
  exit 1
fi

exit 0
