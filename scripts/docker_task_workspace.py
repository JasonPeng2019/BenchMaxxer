#!/usr/bin/env python3
"""Run an agent-visible task command with exactly one Docker bind mount.

This operator bridge never mounts the benchmark checkout, verifier, harness
source, workflow source, host home, or credentials. It is not an agent runner.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IMAGES = {
    "biofabric-rust-rewrite": (
        "swe-marathon-biofabric-rust-rewrite:host-lock-20260925",
        "sha256:375a34a80ed17c7d577d7896edd346331bb4bda2e550868806b0e37d6554c9dc",
    ),
    "find-network-alignments": (
        "swe-marathon-find-network-alignments:lf-20260925",
        "sha256:848b52ed2e1bae448d683769088b7c71bdfd782dce9b1f39578d766165bfa046",
    ),
    "zstd-decoder": (
        "swe-marathon-zstd-decoder:lf-20260925",
        "sha256:3a43d4f3658c4a21115c518937b692692e9e721d3b6e4a3205972917b8bc2e8a",
    ),
}
EXTRA_WORKSPACES = {"zstd-decoder": {"zstd-decoder-lean-90m"}}


def docker_command(task: str, worktree: Path, command: list[str],
                   workspace_name: str | None = None) -> list[str]:
    if task not in IMAGES:
        raise ValueError(f"unknown task: {task}")
    workspace_name = workspace_name or task
    if workspace_name != task and workspace_name not in EXTRA_WORKSPACES.get(task, set()):
        raise ValueError("workspace name is not registered for this task")
    lane = worktree.resolve(strict=True)
    parent = (REPO / "root_runs" / workspace_name / ".harness-runtime" / "worktrees").resolve()
    lean_root = (REPO / "root_runs" / "zstd-decoder-lean-90m").resolve()
    root_checkout = (task == "zstd-decoder" and workspace_name == "zstd-decoder-lean-90m"
                     and lane == lean_root and (lane / ".git").is_dir())
    native_lane = lane.parent.parent == parent and (lane / ".git").is_file()
    if not lane.is_dir() or not (root_checkout or native_lane):
        raise ValueError("worktree must be the registered lean ROOT or one exact lane beneath its runtime")
    if (lane / ".codex" / "auth.json").exists():
        raise ValueError("credential file found in lane; refusing Docker mount")
    if not command or command[0] == "--":
        raise ValueError("a container command is required")
    image, _ = IMAGES[task]
    return [
        "docker", "run", "--rm", "--network", "none", "--cpus", "4",
        "--memory", "16g", "--pids-limit", "512", "--mount",
        f"type=bind,source={lane},target=/app", "--workdir", "/app",
        image, *command,
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, choices=tuple(IMAGES))
    parser.add_argument("--workspace-name", help="registered separate ROOT workspace name")
    parser.add_argument("--worktree", required=True, type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    argv = docker_command(args.task, args.worktree, command, args.workspace_name)
    image, expected = IMAGES[args.task]
    inspect = subprocess.run(
        ["docker", "image", "inspect", image, "--format", "{{.Id}}"],
        capture_output=True, text=True, check=False,
    )
    if inspect.returncode or inspect.stdout.strip() != expected:
        raise RuntimeError(f"pinned task image unavailable or changed: {image}")
    print(json.dumps({"task": args.task, "image_id": expected,
                      "worktree": str(args.worktree.resolve()), "argv": argv}), flush=True)
    return subprocess.run(argv, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
