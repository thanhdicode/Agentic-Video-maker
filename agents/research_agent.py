"""Research agent using local LLM and optional web tools."""

from __future__ import annotations

from .orchestrator import PipelineState


def research_node(state: PipelineState) -> PipelineState:
    """Gather context and sources for the requested topic."""
    # TODO: integrate GPT-Researcher + Crawl4AI + Browser MCP
    state.research = {
        "topic": state.idea,
        "sources": [],
        "summary": f"Stub research summary for: {state.idea}",
        "keywords": ["AI", "video", "local", "open source"],
    }
    return state
