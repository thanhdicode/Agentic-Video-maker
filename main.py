"""CLI entry point for AI Video Studio."""

from __future__ import annotations

import argparse
import json

from agents.orchestrator import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Video Studio")
    parser.add_argument("--idea", required=True, help="Video topic or idea")
    parser.add_argument("--project-id", help="Project identifier (auto-generated if omitted)")
    parser.add_argument("--nodes", help="Comma-separated pipeline nodes to run")
    args = parser.parse_args()

    result = run_pipeline(args.idea, args.project_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
