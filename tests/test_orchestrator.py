"""Basic smoke tests for the orchestrator."""

import pytest

from agents.orchestrator import PipelineState, build_pipeline_graph, run_pipeline


def test_pipeline_state_serializes() -> None:
    state = PipelineState(project_id="p1", idea="test")
    data = state.to_dict()
    assert data["project_id"] == "p1"
    assert data["idea"] == "test"


def test_build_pipeline_graph_compiles() -> None:
    graph = build_pipeline_graph()
    assert graph is not None


def test_run_pipeline_creates_project(monkeypatch, tmp_path) -> None:
    import os

    monkeypatch.chdir(tmp_path)
    os.makedirs("config", exist_ok=True)
    with open("config/settings.yaml", "w") as f:
        f.write("project:\n  output_dir: projects\n")

    result = run_pipeline("test idea")
    assert result["project_id"]
    assert os.path.exists(os.path.join("projects", result["project_id"]))
