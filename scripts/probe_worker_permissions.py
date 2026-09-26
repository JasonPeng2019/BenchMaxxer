"""Read-only native sandbox probe for one prepared Codex worker lane.

Usage: python scripts/probe_worker_permissions.py <worktree> <verifier-file> <task-file>
The probe opens files only to test access; it never prints their contents.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path


def toml_inline(value: object) -> str:
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, dict):
        return "{" + ", ".join(
            f"{json.dumps(str(key))} = {toml_inline(child)}"
            for key, child in value.items()
        ) + "}"
    raise TypeError(f"unsupported permission value: {type(value).__name__}")


def main() -> int:
    lane = Path(sys.argv[1]).resolve()
    verifier = Path(sys.argv[2]).resolve()
    task_file = Path(sys.argv[3]).resolve()
    if not task_file.is_relative_to(lane) or not task_file.is_file():
        raise ValueError("task file must exist inside the selected worktree")
    config = tomllib.loads((lane / ".codex" / "config.toml").read_text(encoding="utf-8"))
    profile = config["permissions"]["worker-isolated"]
    read_probe = """import pathlib, sys
targets = {'task': pathlib.Path(sys.argv[1]), 'verifier': pathlib.Path(sys.argv[2]),
           'auth': pathlib.Path(sys.argv[3])}
for name, path in targets.items():
    try:
        with path.open('rb'):
            pass
        print(name + '-readable')
    except OSError:
        print(name + '-denied')
"""
    base = [
        "codex", "sandbox", "-P", "worker-inline", "-C", str(lane),
        "-c", 'permissions.worker-inline.extends=":workspace"',
        "-c", "permissions.worker-inline.filesystem=" + toml_inline(profile["filesystem"]),
        "-c", 'windows.sandbox="elevated"',
    ]
    command = [
        *base, sys.executable, "-c", read_probe,
        str(task_file), str(verifier), str(Path.home() / ".codex" / "auth.json"),
    ]
    files = subprocess.run(command, check=False, capture_output=True, text=True)
    print(files.stdout, end="")
    if files.returncode or set(files.stdout.splitlines()) != {
        "task-readable", "verifier-denied", "auth-denied"
    }:
        print(files.stderr, file=sys.stderr)
        return 1
    docker = shutil.which("docker")
    if docker is None:
        raise RuntimeError("Docker CLI missing")
    daemon = subprocess.run(
        [*base, docker, "info", "--format", "{{.ServerVersion}}"],
        check=False, capture_output=True, text=True,
    )
    if daemon.returncode == 0 or "permission denied" not in daemon.stderr.lower():
        print(daemon.stderr or daemon.stdout, file=sys.stderr)
        return 1
    print("docker-denied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
