"""Optional experiment telemetry gate at the native Codex launch boundary.

The harness remains the only worker launcher. The collector is a short-lived,
read-only accounting check; it starts no provider or controller process.
Normal harness use is unchanged when the two experiment variables are absent.
"""

from __future__ import annotations

import os
import subprocess
import sys


class TokenBudgetGateError(RuntimeError):
    pass


def require_budget_headroom() -> None:
    task_file = os.environ.get("SWE_TOKEN_TASK_FILE")
    collector = os.environ.get("SWE_TOKEN_COLLECTOR")
    if not task_file and not collector:
        return
    if not task_file or not collector:
        raise TokenBudgetGateError("token budget gate is only partially configured")
    try:
        result = subprocess.run(
            [sys.executable, collector, "gate", "--task-file", task_file],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise TokenBudgetGateError(f"token budget check could not complete: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise TokenBudgetGateError(
            f"token budget gate refused provider launch (exit {result.returncode}): {detail}"
        )
