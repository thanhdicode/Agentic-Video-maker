"""ai-studio CLI — one-command production interface for the AI Video Studio."""

from __future__ import annotations

import argparse
import json
import os
import sys

# Ensure repo root is on path regardless of invocation method.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import yaml

from agents.orchestrator import run_pipeline


def _load_project(project_yaml: str) -> dict:
    with open(project_yaml, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _project_dir(project_yaml: str) -> str:
    return os.path.dirname(os.path.abspath(project_yaml))


def init(args: argparse.Namespace) -> int:
    """Initialize a new project from a template."""
    target = args.name
    out_dir = os.path.join("projects", target)
    os.makedirs(out_dir, exist_ok=True)

    project_path = os.path.join(out_dir, "project.yaml")
    script_path = os.path.join(out_dir, "script.md")

    if not os.path.exists(project_path):
        template = os.path.join("schemas", "project.yaml")
        with open(template, "r", encoding="utf-8") as f:
            content = f.read().replace("brain-explained", target)
        with open(project_path, "w", encoding="utf-8") as f:
            f.write(content)

    if not os.path.exists(script_path):
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(f"# {target}\n\nWrite your script here.\n")

    print(f"Initialized project at {out_dir}")
    print(f"  - {project_path}")
    print(f"  - {script_path}")
    return 0


def validate(args: argparse.Namespace) -> int:
    """Validate a project YAML against the JSON schema."""
    import jsonschema

    project = _load_project(args.project_yaml)
    with open("schemas/project_schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)

    try:
        jsonschema.validate(project, schema)
        print("project.yaml is valid.")
        return 0
    except jsonschema.ValidationError as exc:
        print(f"Validation error: {exc.message}")
        return 1


def plan(args: argparse.Namespace) -> int:
    """Generate production plan without rendering."""
    project = _load_project(args.project_yaml)
    project_id = project["project"]["id"]
    script_path = os.path.join(_project_dir(args.project_yaml), project["content"]["script_path"])

    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    state = run_pipeline(script, project_id=project_id, enabled_nodes=["research", "script", "character_design", "asset_generation", "storyboard"])
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return 0


def produce(args: argparse.Namespace) -> int:
    """Run the full production pipeline."""
    project = _load_project(args.project_yaml)
    project_id = project["project"]["id"]
    script_path = os.path.join(_project_dir(args.project_yaml), project["content"]["script_path"])

    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()

    state = run_pipeline(script, project_id=project_id)
    output = state.get("output_path", "")
    print(f"Output: {output}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Video Studio CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("name", help="Project name / id")
    init_parser.set_defaults(func=init)

    validate_parser = subparsers.add_parser("validate", help="Validate project.yaml")
    validate_parser.add_argument("project_yaml", help="Path to project.yaml")
    validate_parser.set_defaults(func=validate)

    plan_parser = subparsers.add_parser("plan", help="Generate production plan up to storyboard")
    plan_parser.add_argument("project_yaml", help="Path to project.yaml")
    plan_parser.set_defaults(func=plan)

    produce_parser = subparsers.add_parser("produce", help="Produce full video")
    produce_parser.add_argument("project_yaml", help="Path to project.yaml")
    produce_parser.add_argument("--mode", choices=["auto", "approval"], default="auto")
    produce_parser.set_defaults(func=produce)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
