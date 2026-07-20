"""Script writing agent powered by Ollama / local LLM."""

from __future__ import annotations

from .orchestrator import PipelineState


def script_node(state: PipelineState) -> PipelineState:
    """Generate a structured script with hooks, segments, characters, props, labels, and voice cues."""
    # TODO: call Ollama Qwen3 / Llama3.3 with prompt engineering
    # For now, produce a structured educational cartoon script from the idea.
    topic = state.idea or state.script_path
    segments = [
        {
            "type": "hook",
            "text": f"Hey friends! Today we are going to learn something amazing about {topic}.",
            "duration": 5,
            "background_prompt": f"Bright classroom background, cartoon style",
            "characters": ["Host"],
            "props": [],
            "labels": ["Hook"],
        },
        {
            "type": "explain",
            "text": f"{topic} is super important because it helps us understand the world around us.",
            "duration": 8,
            "background_prompt": f"Colorful cartoon illustration of {topic}, simple shapes",
            "characters": ["Host"],
            "props": ["diagram"],
            "labels": [topic],
        },
        {
            "type": "example",
            "text": f"For example, imagine you see {topic} in action. It works like magic!",
            "duration": 8,
            "background_prompt": f"Fun cartoon scene showing {topic} in daily life",
            "characters": ["Host"],
            "props": ["example object"],
            "labels": ["Example"],
        },
        {
            "type": "recap",
            "text": f"So remember, {topic} is everywhere and now YOU know how it works!",
            "duration": 6,
            "background_prompt": f"Celebration background with cartoon confetti",
            "characters": ["Host"],
            "props": ["stars"],
            "labels": ["Recap"],
        },
    ]

    state.script = {
        "title": f"All About {topic}",
        "target_audience": "kids 6-10",
        "tone": "fun, educational, energetic",
        "hook": segments[0]["text"],
        "segments": segments,
        "total_duration": sum(s["duration"] for s in segments),
        "words_per_minute": 150,
    }
    return state
