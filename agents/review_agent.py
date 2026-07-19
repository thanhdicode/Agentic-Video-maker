"""Review / QA agent: validates the final output and scores it."""

from __future__ import annotations

import os

from .orchestrator import PipelineState


def review_node(state: PipelineState) -> PipelineState:
    """Run quality checks on the final render and decide if it passes."""
    if not state.output_path or not os.path.exists(state.output_path):
        state.review = {"passed": False, "score": 0.0, "issues": ["No final video found"]}
        return state

    # TODO: run ffprobe for duration / audio levels, faster-whisper for subtitle sync,
    # CLIP embedding consistency, and LLM-based critique.
    state.review = {
        "passed": True,
        "score": 0.85,
        "issues": [],
        "notes": "Placeholder review. Replace with ffprobe + CLIP + LLM review.",
    }
    return state
