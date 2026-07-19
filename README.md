# AI Video Studio

Local-first, agentic video production pipeline built from the [Ultimate Local AI Video Making Studio blueprint](./docs/blueprint.md).

## Stack

- **Orchestration:** LangGraph + Ollama
- **Research:** GPT-Researcher / Crawl4AI stubs
- **Script:** Ollama (Qwen3 / Llama3.3)
- **Image:** ComfyUI + FLUX.1
- **Video:** Wan 2.2 / LTX-Video / AnimateDiff
- **Audio:** F5-TTS / Kokoro + AudioCraft (MusicGen / AudioGen)
- **Editing:** FFmpeg + MoviePy + Auto-Editor
- **Workflow:** n8n (optional)
- **MCP:** Filesystem, FFmpeg, ComfyUI, Browser MCP servers

## Project Structure

```
ai-video-studio/
├── agents/              # LangGraph agents
├── tools/               # Client wrappers for external services
├── mcp/                 # MCP server implementations and config
├── workflows/           # ComfyUI + n8n workflow JSON
├── docker/              # Container definitions
├── config/              # YAML settings
├── projects/            # Generated project outputs
├── docs/                # Blueprint and docs
└── tests/               # Unit tests
```

## Quick Start

```bash
# 1. Use Python 3.11
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Configure
# Edit config/settings.yaml and config/model_config.yaml

# 3. Run orchestrator example
python -m agents.orchestrator --idea "How local AI replaces stock footage"
```

## Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

## License

MIT where possible. Some recommended models use non-commercial licenses; see `config/model_config.yaml`.
