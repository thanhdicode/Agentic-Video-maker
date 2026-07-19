"""Minimal ComfyUI MCP server stub."""

from __future__ import annotations

import json
import sys


def send(message: dict) -> None:
    print(json.dumps(message), flush=True)


def handle_request(req: dict) -> dict:
    method = req.get("method")
    if method == "queue":
        workflow = req.get("params", {}).get("workflow")
        return {"status": "queued", "workflow": workflow}
    if method == "list_workflows":
        return {"workflows": ["flux_t2i.json", "wan_i2v.json", "animatediff.json", "upscale.json"]}
    return {"status": "error", "message": "Unknown method"}


def main() -> None:
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
            send({"jsonrpc": "2.0", "id": req.get("id"), "result": handle_request(req)})
        except json.JSONDecodeError as exc:
            send({"jsonrpc": "2.0", "error": {"code": -32700, "message": str(exc)}})


if __name__ == "__main__":
    main()
