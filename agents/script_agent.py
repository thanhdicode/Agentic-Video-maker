"""Script writing agent powered by Ollama / local LLM."""

from __future__ import annotations

from .orchestrator import PipelineState


def script_node(state: PipelineState) -> PipelineState:
    """Generate a structured script with hooks, segments, and voice cues."""
    # TODO: call Ollama Qwen3 / Llama3.3 with prompt engineering
    state.script = {
        "title": f"Video about {state.idea}",
        "hook": f"In the next 60 seconds, you'll learn why {state.idea} changes everything.",
        "segments": [
            {"type": "hook", "text": state.script.get("hook", ""), "duration": 5},
            {"type": "problem", "text": "People waste hours on manual video editing.", "duration": 10},
            {"type": "solution", "text": "Local AI pipelines automate the entire workflow.", "duration": 15},
            {"type": "result", "text": "You get studio-quality videos without subscriptions.", "duration": 10},
        ],
        "total_duration": 40,
        "words_per_minute": 150,
    }
    return state
