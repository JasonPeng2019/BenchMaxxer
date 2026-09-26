from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from orchestrator_harness import controller, launch
from orchestrator_harness.token_budget_gate import TokenBudgetGateError, require_budget_headroom


class TokenBudgetGateTests(unittest.TestCase):
    def test_absent_configuration_does_not_invoke_collector(self) -> None:
        with patch.dict(os.environ, {}, clear=True), patch("subprocess.run") as run:
            require_budget_headroom()
        run.assert_not_called()

    def test_partial_configuration_fails_closed(self) -> None:
        with patch.dict(os.environ, {"SWE_TOKEN_TASK_FILE": "task.json"}, clear=True):
            with self.assertRaises(TokenBudgetGateError):
                require_budget_headroom()

    def test_exhausted_or_invalid_accounting_blocks_launch(self) -> None:
        environment = {"SWE_TOKEN_TASK_FILE": "task.json", "SWE_TOKEN_COLLECTOR": "collector.py"}
        for code in (2, 3):
            with self.subTest(exit_code=code), patch.dict(os.environ, environment, clear=True):
                with patch("subprocess.run", return_value=subprocess.CompletedProcess([], code, "blocked", "")):
                    with self.assertRaises(TokenBudgetGateError):
                        require_budget_headroom()

    def test_valid_headroom_invokes_read_only_gate(self) -> None:
        environment = {"SWE_TOKEN_TASK_FILE": "task.json", "SWE_TOKEN_COLLECTOR": "collector.py"}
        with patch.dict(os.environ, environment, clear=True), patch(
            "subprocess.run", return_value=subprocess.CompletedProcess([], 0, "allowed", "")
        ) as run:
            require_budget_headroom()
        argv = run.call_args.args[0]
        self.assertEqual(argv[1:], ["collector.py", "gate", "--task-file", "task.json"])

    def test_native_launch_checks_before_spawning_controller(self) -> None:
        lane = {"lane_id": "lane-1", "run_id": "run-1", "lifecycle": "prepared", "worktree_path": "X:/lane"}
        invocation = {
            "lane_id": "lane-1", "run_id": "run-1",
            "provider": {"id": "codex", "model": "model",
                         "launch_config": {"reasoning_effort": "high", "service_tier": "priority"}},
        }
        with (
            patch.object(launch, "find_harness_root", return_value=Path("X:/harness")),
            patch.object(launch, "load_config", return_value=SimpleNamespace(runtime_root=Path("X:/runtime"))),
            patch.object(launch, "read_runtime_state", return_value={"state": "OPEN"}),
            patch.object(launch, "find_active_lane", return_value=("epoch-1", lane)),
            patch.object(launch, "read_record", return_value=invocation),
            patch.object(launch, "_validate_provider_launch_config", return_value=invocation["provider"]["launch_config"]),
            patch.object(Path, "is_file", return_value=True),
            patch.object(launch, "require_budget_headroom", side_effect=TokenBudgetGateError("B reached")),
            patch.object(launch.processes, "spawn_detached") as spawn,
        ):
            result = launch.run_launch("lane-1")
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], launch.LAUNCH_TOKEN_BUDGET_BLOCKED)
        spawn.assert_not_called()

    def test_controller_checks_each_provider_attempt_before_spawn(self) -> None:
        with patch.object(controller, "require_budget_headroom", side_effect=TokenBudgetGateError("B reached")):
            with patch.object(controller.processes, "spawn_provider") as spawn:
                with self.assertRaises(TokenBudgetGateError):
                    controller._run_provider(
                        Path("X:/runtime"), "epoch-1", {"worktree_path": "X:/lane"},
                        {"provider": {"id": "codex"}}, object(), Path("X:/prompt.md"),
                    )
        spawn.assert_not_called()


if __name__ == "__main__":
    unittest.main()
