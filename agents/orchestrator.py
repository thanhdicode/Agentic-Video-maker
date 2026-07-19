"""Master LangGraph orchestrator for the AI Video Studio."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from langgraph.graph import END, StateGraph

from . import (
    audio_node,
    edit_node,
    image_node,
    research_node,
    script_node,
    storyboard_node,
    video_node,
)


@dataclass
class PipelineState:
    project_id: str = ""
    idea: str = ""
    research: dict = field(default_factory=dict)
    script: dict = field(default_factory=dict)
    storyboard: list = field(default_factory=list)
    image_paths: list = field(default_factory=list)
    video_paths: list = field(default_factory=list)
    audio_paths: dict = field(default_factory=dict)
    subtitle_path: str = ""
    output_path: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "idea": self.idea,
            "research": self.research,
            "script": self.script,
            "storyboard": self.storyboard,
            "image_paths": self.image_paths,
            "video_paths": self.video_paths,
            "audio_paths": self.audio_paths,
            "subtitle_path": self.subtitle_path,
            "output_path": self.output_path,
            "error": self.error,
        }


def build_pipeline_graph(
    enabled_nodes: Optional[list[str]] = None,
) -> StateGraph:
    """Build the LangGraph state machine for video production."""
    graph = StateGraph(PipelineState)

    nodes: dict[str, Callable[[PipelineState], PipelineState]] = {
        "research": research_node,
        "script": script_node,
        "storyboard": storyboard_node,
        "image_gen": image_node,
        "video_gen": video_node,
        "audio_gen": audio_node,
        "edit": edit_node,
    }

    if enabled_nodes:
        nodes = {k: v for k, v in nodes.items() if k in enabled_nodes}

    for name, func in nodes.items():
        graph.add_node(name, func)

    ordered = list(nodes.keys())
    if not ordered:
        return graph

    graph.set_entry_point(ordered[0])
    for a, b in zip(ordered, ordered[1:]):
        graph.add_edge(a, b)
    graph.add_edge(ordered[-1], END)

    return graph.compile()


def run_pipeline(idea: str, project_id: Optional[str] = None) -> dict[str, Any]:
    """Run the full pipeline from an idea."""
    project_id = project_id or f"project_{hash(idea) & 0xFFFFFFFF:08x}"
    project_dir = os.path.join("projects", project_id)
    os.makedirs(project_dir, exist_ok=True)

    state = PipelineState(project_id=project_id, idea=idea)
    graph = build_pipeline_graph()

    final_state = graph.invoke(state)
    summary_path = os.path.join(project_dir, "state.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(final_state.to_dict(), f, indent=2, ensure_ascii=False)

    return final_state.to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Video Studio orchestrator")
    parser.add_argument("--idea", required=True, help="Video topic / idea")
    parser.add_argument("--project-id", help="Project identifier")
    parser.add_argument("--nodes", help="Comma-separated list of nodes to run")
    args = parser.parse_args()

    enabled = args.nodes.split(",") if args.nodes else None
    graph = build_pipeline_graph(enabled)
    result = run_pipeline(args.idea, args.project_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
