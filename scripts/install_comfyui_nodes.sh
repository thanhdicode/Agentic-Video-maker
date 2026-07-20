#!/usr/bin/env bash
set -euo pipefail

# Install ComfyUI and essential custom nodes for the AI Video Studio.
# Run after scripts/bootstrap-ubuntu.sh and inside the project root.

COMFYUI_DIR="${COMFYUI_DIR:-vendor/ComfyUI}"

if [[ ! -d "$COMFYUI_DIR" ]]; then
  echo "[*] Cloning ComfyUI..."
  mkdir -p vendor
  git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_DIR"
else
  echo "[*] ComfyUI already exists; pulling latest..."
  cd "$COMFYUI_DIR" && git pull && cd - >/dev/null
fi

echo "[*] Installing ComfyUI Python dependencies..."
pip install -r "$COMFYUI_DIR/requirements.txt"

CUSTOM_NODES=(
  "https://github.com/ltdrdata/ComfyUI-Manager.git"
  "https://github.com/cubiq/ComfyUI_IPAdapter_plus.git"
  "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git"
  "https://github.com/kijai/ComfyUI-WanVideoWrapper.git"
  "https://github.com/Lightricks/ComfyUI-LTXVideo.git"
  "https://github.com/Fannovel16/comfyui_controlnet_aux.git"
  "https://github.com/kijai/ComfyUI-DynamiCrafterWrapper.git"
  "https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git"
  "https://github.com/colorAi/comfyui-storyboard.git"
)

NODES_DIR="$COMFYUI_DIR/custom_nodes"
mkdir -p "$NODES_DIR"

echo "[*] Installing custom nodes..."
for repo in "${CUSTOM_NODES[@]}"; do
  name=$(basename "$repo" .git)
  target="$NODES_DIR/$name"
  if [[ ! -d "$target" ]]; then
    echo "  - Cloning $name"
    git clone "$repo" "$target"
  else
    echo "  - Pulling $name"
    cd "$target" && git pull && cd - >/dev/null
  fi
  if [[ -f "$target/requirements.txt" ]]; then
    pip install -r "$target/requirements.txt"
  fi
done

echo "[*] ComfyUI custom nodes installed."
echo "Start ComfyUI with: python $COMFYUI_DIR/main.py --listen 0.0.0.0 --port 8188"
