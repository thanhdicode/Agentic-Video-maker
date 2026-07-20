# AI Video Studio

Local-first, agentic video production pipeline for professional 2D cartoon educational videos.

See the deep research report at [docs/RESEARCH_REPORT.md](./docs/RESEARCH_REPORT.md) and the studio design at [docs/STUDIO_DESIGN.md](./docs/STUDIO_DESIGN.md).

## Stack

- **Orchestration:** LangGraph + Ollama
- **Research:** GPT-Researcher / Crawl4AI stubs
- **Script:** Ollama (Qwen3 / Llama3.3)
- **Image:** ComfyUI + FLUX.1
- **Video:** Wan 2.2 / LTX-Video / AnimateDiff / ToonCrafter
- **Audio:** F5-TTS / Kokoro + AudioCraft (MusicGen / AudioGen)
- **Editing:** FFmpeg + MoviePy + Auto-Editor + optional DaVinci Resolve Studio, Blender VSE, or Shotcut/MLT
- **Educational videos:** YouTube ingestion -> script -> TTS -> text-on-color visuals (FFmpeg) OR Manim animation -> final cut
- **MCP:** Filesystem, FFmpeg, ComfyUI, Browser MCP servers

## Project Structure

```
Agentic-Video-maker/
├── agents/              # LangGraph agents
├── ai_studio/           # ai-studio CLI
├── tools/               # Client wrappers for external services
├── mcp/                 # MCP server implementations and config
├── workflows/           # ComfyUI + n8n workflow JSON
├── docker/              # Container definitions
├── config/              # YAML settings
├── schemas/             # project.yaml schema
├── research/            # Repository audit CSVs + search log
├── projects/            # Generated project outputs
├── scripts/             # Bootstrap and health-check scripts
├── docs/                # Blueprint, design, research, install guides
└── tests/               # Unit tests
```

## Quick Start

```bash
# 1. Use Python 3.11+
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Configure
# Edit config/settings.yaml and config/model_config.yaml

# 3a. Start a project with the ai-studio CLI
python ai-studio.py init my-video
# Edit projects/my-video/project.yaml and script.md
python ai-studio.py validate projects/my-video/project.yaml
python ai-studio.py produce projects/my-video/project.yaml

# 3b. Or run the orchestrator directly
python -m agents.orchestrator --idea "How local AI replaces stock footage"

# Optional: render the final cut with DaVinci Resolve Studio
# Requires Resolve running with external scripting enabled.
set AI_VIDEO_USE_RESOLVE=1
python -m agents.orchestrator --idea "Game launch trailer"

# Or render with Blender VSE (works headless without a GPU)
set AI_VIDEO_USE_BLENDER=1
python -m agents.orchestrator --idea "Game launch trailer"

# Or render with Shotcut/MLT (headless, fast CPU cuts/transitions)
set AI_VIDEO_USE_SHOTCUT=1
python -m agents.orchestrator --idea "Game launch trailer"

# Generate an educational explainer from a topic or YouTube URL
python -m agents.orchestrator --nodes edu_video --idea "fractions" --audience kids
python -m agents.orchestrator --youtube "https://www.youtube.com/watch?v=..." --audience kids

# Generate an explainer using Manim animations
python -m agents.orchestrator --manim --idea "fractions" --audience kids
python -m agents.orchestrator --manim --youtube "https://www.youtube.com/watch?v=..." --audience kids
```

For full setup (GPU required), see:
- [docs/installation-ubuntu.md](./docs/installation-ubuntu.md)
- [docs/installation-windows-wsl2.md](./docs/installation-windows-wsl2.md)
- [docs/model-installation.md](./docs/model-installation.md)
- [docs/troubleshooting.md](./docs/troubleshooting.md)

## Demo

A CPU-only demo is included in `demo.py` and produces `projects/demo_output/final_demo.mp4`.

## Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

## License

MIT where possible. Some recommended model weights use non-commercial licenses; see `docs/RESEARCH_REPORT.md` Section 8.
