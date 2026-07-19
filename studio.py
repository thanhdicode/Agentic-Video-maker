"""Professional AI Video Studio entry point.

Reads a script or prompt and runs the full LangGraph pipeline:
script -> character design -> assets -> storyboard -> keyframes ->
animation -> video -> audio -> edit -> review.
"""

from __future__ import annotations

import argparse
import json
import os

from agents.orchestrator import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Video Studio — professional 2D animation pipeline")
    parser.add_argument("--idea", help="Video topic / idea / one-line prompt")
    parser.add_argument("--script", help="Path to a script file (plain text or markdown)")
    parser.add_argument("--project-id", help="Project identifier")
    parser.add_argument("--nodes", help="Comma-separated pipeline nodes to run")
    args = parser.parse_args()

    if not args.idea and not args.script:
        parser.error("Provide --idea or --script")

    idea = args.idea or ""
    if args.script:
        with open(args.script, "r", encoding="utf-8") as f:
            idea = f.read().strip() if not idea else idea

    enabled = args.nodes.split(",") if args.nodes else None
    result = run_pipeline(idea, args.project_id, args.script, enabled)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
