# AI Video Studio

Local-first, agentic video production pipeline for professional 2D cartoon educational videos.

See the deep research report at [docs/RESEARCH_REPORT.md](./docs/RESEARCH_REPORT.md) and the studio design at [docs/STUDIO_DESIGN.md](./docs/STUDIO_DESIGN.md).

## Selected architecture

- **Hybrid professional studio**: AI asset generation + rigged 2D host + generative I2V for complex motion + code-driven motion graphics.
- **Orchestration:** LangGraph
- **Character consistency:** CharForge + kohya-ss + IP-Adapter + PuLID
- **Image:** FLUX.1-schnell (commercial-safe) via ComfyUI
- **Video:** Wan 2.1 + LTX-Video + ToonCrafter
- **TTS:** Kokoro (English) / Fish Speech (multi-lingual, incl. Vietnamese)
- **Music/SFX/foley:** AudioCraft + FoleyCrafter
- **Edit/compose:** Motion Canvas + MoviePy + FFmpeg
- **QA:** MVAD + UVQ + VMAF + FFmpeg probes
- **Subtitles:** WhisperX
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

# 2. Start a project
python ai-studio.py init my-video
# Edit projects/my-video/project.yaml and script.md

# 3. Validate and produce
python ai-studio.py validate projects/my-video/project.yaml
python ai-studio.py produce projects/my-video/project.yaml
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
