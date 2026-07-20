"""Master LangGraph orchestrator for the AI Video Studio."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from langgraph.graph import END, StateGraph

from . import (
    animation_node,
    asset_node,
    audio_node,
    character_node,
    edit_node,
    image_node,
    research_node,
    review_node,
    script_node,
    storyboard_node,
    video_node,
)


@dataclass
class PipelineState:
    """Central state passed through every LangGraph node."""

    project_id: str = ""
    idea: str = ""  # user prompt / script text
    script_path: str = ""  # optional: path to a user script file
    creative_brief: dict = field(default_factory=dict)
    youtube_url: str = ""
    target_audience: str = "kids"
    research: dict = field(default_factory=dict)
    script: dict = field(default_factory=dict)
    characters: dict = field(default_factory=dict)
    assets: dict = field(default_factory=dict)
    storyboard: list = field(default_factory=list)
    image_paths: list = field(default_factory=list)
    video_paths: list = field(default_factory=list)
    audio_paths: dict = field(default_factory=dict)
    source_metadata: dict = field(default_factory=dict)
    source_transcript: str = ""
    subtitle_path: str = ""
    output_path: str = ""
    review: dict = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "idea": self.idea,
            "script_path": self.script_path,
            "creative_brief": self.creative_brief,
            "youtube_url": self.youtube_url,
            "target_audience": self.target_audience,
            "research": self.research,
            "script": self.script,
            "characters": self.characters,
            "assets": self.assets,
            "storyboard": self.storyboard,
            "image_paths": self.image_paths,
            "video_paths": self.video_paths,
            "audio_paths": self.audio_paths,
            "source_metadata": self.source_metadata,
            "source_transcript": self.source_transcript,
            "subtitle_path": self.subtitle_path,
            "output_path": self.output_path,
            "review": self.review,
            "error": self.error,
        }


def build_pipeline_graph(
    enabled_nodes: Optional[list[str]] = None,
) -> Any:
    """Build the LangGraph state machine for professional 2D animation production."""
    graph = StateGraph(PipelineState)

    from .edu_video_agent import edu_video_node
    from .manim_video_agent import manim_video_node

    nodes: dict[str, Callable[[PipelineState], PipelineState]] = {
        "research": research_node,
        "script": script_node,
        "character_design": character_node,
        "asset_generation": asset_node,
        "storyboard": storyboard_node,
        "image_gen": image_node,
        "animation": animation_node,
        "video_gen": video_node,
        "audio_gen": audio_node,
        "edit": edit_node,
        "review": review_node,
        "edu_video": edu_video_node,
        "manim_video": manim_video_node,
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


def run_pipeline(
    idea: str,
    project_id: Optional[str] = None,
    script_path: Optional[str] = None,
    enabled_nodes: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Run the full pipeline from an idea or a script."""
    project_id = project_id or f"project_{hash(idea) & 0xFFFFFFFF:08x}"
    project_dir = os.path.join("projects", project_id)
    os.makedirs(project_dir, exist_ok=True)

    state = PipelineState(
        project_id=project_id,
        idea=idea,
        script_path=script_path or "",
    )
    graph = build_pipeline_graph(enabled_nodes)

    final_state = graph.invoke(state)
    summary_path = os.path.join(project_dir, "state.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(final_state.to_dict(), f, indent=2, ensure_ascii=False)

    return final_state.to_dict()


def run_edu_pipeline(
    idea: str,
    youtube_url: str = "",
    audience: str = "kids",
    project_id: Optional[str] = None,
) -> dict[str, Any]:
    """Run the educational-video pipeline from a topic or YouTube URL."""
    project_id = project_id or f"edu_{hash(idea or youtube_url) & 0xFFFFFFFF:08x}"
    project_dir = os.path.join("projects", project_id)
    os.makedirs(project_dir, exist_ok=True)

    state = PipelineState(
        project_id=project_id,
        idea=idea,
        youtube_url=youtube_url,
        target_audience=audience,
        audio_paths={"music": "test_clips/music_long.mp3"},
    )
    graph = build_pipeline_graph(["edu_video"])

    final_state = graph.invoke(state)
    summary_path = os.path.join(project_dir, "state.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(final_state.to_dict(), f, indent=2, ensure_ascii=False)

    return final_state.to_dict()


def run_manim_pipeline(
    idea: str,
    youtube_url: str = "",
    audience: str = "kids",
    project_id: Optional[str] = None,
) -> dict[str, Any]:
    """Run the Manim educational-video pipeline from a topic or YouTube URL."""
    project_id = project_id or f"manim_{hash(idea or youtube_url) & 0xFFFFFFFF:08x}"
    project_dir = os.path.join("projects", project_id)
    os.makedirs(project_dir, exist_ok=True)

    state = PipelineState(
        project_id=project_id,
        idea=idea,
        youtube_url=youtube_url,
        target_audience=audience,
        audio_paths={"music": "test_clips/music_long.mp3"},
    )
    graph = build_pipeline_graph(["manim_video"])

    final_state = graph.invoke(state)
    summary_path = os.path.join(project_dir, "state.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(final_state.to_dict(), f, indent=2, ensure_ascii=False)

    return final_state.to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Video Studio orchestrator")
    parser.add_argument("--idea", default="", help="Video topic / idea")
    parser.add_argument("--script", default="", help="Path to a script file (plaintext/markdown)")
    parser.add_argument("--youtube", default="", help="YouTube URL to ingest")
    parser.add_argument("--audience", default="kids", help="Target audience (e.g. kids)")
    parser.add_argument("--project-id", help="Project identifier")
    parser.add_argument("--nodes", help="Comma-separated list of nodes to run")
    parser.add_argument(
        "--manim", action="store_true", help="Use the Manim educational video pipeline"
    )
    args = parser.parse_args()

    if args.manim or args.nodes == "manim_video":
        result = run_manim_pipeline(
            idea=args.idea,
            youtube_url=args.youtube,
            audience=args.audience,
            project_id=args.project_id,
        )
    elif args.youtube or args.nodes == "edu_video":
        result = run_edu_pipeline(
            idea=args.idea,
            youtube_url=args.youtube,
            audience=args.audience,
            project_id=args.project_id,
        )
    else:
        if not args.idea and not args.script:
            parser.error("Provide --idea or --script")
        enabled = args.nodes.split(",") if args.nodes else None
        idea = args.idea or (args.script if args.script else "")
        result = run_pipeline(
            idea=idea,
            project_id=args.project_id,
            script_path=args.script or "",
            enabled_nodes=enabled,
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
