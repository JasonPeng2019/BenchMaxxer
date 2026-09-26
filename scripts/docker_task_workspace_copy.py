#!/usr/bin/env python3
"""Run public ZSTD checks from an exact lean checkout without a host bind mount.

Docker Desktop does not share every sibling workspace. This bridge validates
the same exact checkout as docker_task_workspace.py, copies only task-visible
inputs into a short-lived, no-network container, and never copies results or
runtime state back into the host checkout.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from docker_task_workspace import IMAGES, docker_command


def copy_sources(worktree: Path) -> list[Path]:
    required = ["src", "test_artifacts", "rfc8878.txt", "test.sh", "timer.sh"]
    sources = [worktree / name for name in required]
    if not all(path.exists() for path in sources):
        raise ValueError("task-visible ZSTD inputs are missing")
    scratch = worktree / "scratch"
    if scratch.is_dir():
        sources.append(scratch)
    return sources


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, choices=("zstd-decoder",))
    parser.add_argument("--workspace-name", required=True, choices=("zstd-decoder-lean-90m",))
    parser.add_argument("--worktree", required=True, type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    worktree = args.worktree.resolve(strict=True)
    # Reuse the strict registered ROOT/lane and credential validation.
    docker_command(args.task, worktree, command, args.workspace_name)
    sources = copy_sources(worktree)
    image, expected = IMAGES[args.task]
    inspect = subprocess.run(
        ["docker", "image", "inspect", image, "--format", "{{.Id}}"],
        capture_output=True, text=True, check=False,
    )
    if inspect.returncode or inspect.stdout.strip() != expected:
        raise RuntimeError("pinned task image unavailable or changed")
    created = subprocess.run(
        ["docker", "create", "--network", "none", "--cpus", "4",
         "--memory", "16g", "--pids-limit", "512", image,
         "bash", "-lc", "sleep 1200"],
        capture_output=True, text=True, check=True,
    )
    container = created.stdout.strip()
    if not container or not all(char in "0123456789abcdef" for char in container):
        raise RuntimeError("Docker did not return an exact container ID")
    try:
        subprocess.run(["docker", "start", container], check=True, capture_output=True, text=True)
        subprocess.run(["docker", "exec", container, "mkdir", "-p", "/app"], check=True)
        for path in sources:
            subprocess.run(["docker", "cp", str(path), f"{container}:/app/"], check=True)
        print(json.dumps({"task": args.task, "image_id": expected,
                          "worktree": str(worktree), "container": container,
                          "copied": [path.name for path in sources],
                          "command": command}), flush=True)
        return subprocess.run(["docker", "exec", "--workdir", "/app", container,
                               *command], check=False).returncode
    finally:
        subprocess.run(["docker", "rm", "-f", container], check=False,
                       capture_output=True, text=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
