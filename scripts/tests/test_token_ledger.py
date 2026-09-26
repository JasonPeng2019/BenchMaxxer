from __future__ import annotations

import json
import argparse
import hashlib
import io
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from token_ledger import LedgerError, build_snapshot, extract_usage, finalize, normalize_usage
from collect_codex_usage import prepare_resume, run_codex, stop_process_tree, write_stdout_safe


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


def events(thread: str, usage: dict) -> list[dict]:
    return [
        {"type": "thread.started", "thread_id": thread},
        {"type": "turn.started"},
        {"type": "turn.completed", "usage": usage},
    ]


class TokenLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.run_dir = self.base / "run-1"
        self.run_dir.mkdir()
        self.runtime = self.base / "root" / ".harness-runtime"
        self.root_events = self.run_dir / "codex-events.jsonl"
        self.task_file = self.run_dir / "task.json"

    def make_task(self, *, arm: str = "raw", budget: int | None = 200, root_total: int = 20, finished: bool = True) -> None:
        launch = {
            "schema": "codex-token-run/v1",
            "run_id": "run-1", "task": "fixture-task", "arm": arm,
            "model": "gpt-5.6-terra", "reasoning_effort": "max",
            "service_tier": "priority", "started_at_utc": "2026-09-22T10:00:00+00:00",
            "budget_tokens": budget,
            "harness_runtime": str(self.runtime) if arm == "harness" else None,
            "command": [
                "codex", "exec", "-m", "gpt-5.6-terra",
                "-c", 'model_reasoning_effort="max"',
                "-c", 'service_tier="priority"',
            ],
        }
        write_json(self.run_dir / "launch.json", launch)
        if finished:
            write_json(self.run_dir / "manifest.json", {
                **launch, "ended_at_utc": "2026-09-22T10:10:00+00:00", "exit_code": 0,
            })
        write_jsonl(self.root_events, events("root-thread", {
            "input_tokens": root_total - 5, "cached_input_tokens": 3,
            "output_tokens": 5, "total_tokens": root_total,
        }))
        task = {
            "schema": "codex-token-task/v1", "run_id": "run-1",
            "task": "fixture-task", "arm": arm, "budget_tokens": budget,
            "root_run_dir": str(self.run_dir),
        }
        if arm == "harness":
            task["harness_runtime"] = str(self.runtime)
        write_json(self.task_file, task)

    def make_worker(self, totals: list[int], *, same_thread: bool = True, replay_last: bool = False) -> None:
        workspace = self.runtime / "worktrees" / "epoch-1" / "lane-1" / ".agent-workspace"
        workspace.mkdir(parents=True)
        write_json(workspace / "invocation.json", {
            "schema": "controller-invocation/v1", "lane_id": "lane-1",
            "run_id": "worker-run", "created_at": "2026-09-22T10:01:00+00:00",
            "provider": {"id": "codex", "model": "gpt-5.6-terra",
                         "launch_config": {"reasoning_effort": "high", "service_tier": "priority"}},
            "paths": {
                "transcript": str(workspace / "provider-transcript.jsonl"),
                "attempts": str(workspace / "controller.attempts.jsonl"),
            },
        })
        attempts = [{"schema": "controller-attempts/v1"}]
        controller_events = [{"schema": "controller-events/v1"}]
        for index, total in enumerate(totals, 1):
            transcript = (
                workspace / "provider-transcript.jsonl" if index == 1
                else workspace / "attempts" / f"attempt-{index}" / "provider-transcript.jsonl"
            )
            if replay_last and index == len(totals):
                prior = workspace / "attempts" / f"attempt-{index - 1}" / "provider-transcript.jsonl"
                transcript.parent.mkdir(parents=True, exist_ok=True)
                transcript.write_bytes(prior.read_bytes())
            else:
                write_jsonl(transcript, events("worker-thread" if same_thread else f"worker-thread-{index}", {
                    "input_tokens": total - 10, "cached_input_tokens": 4,
                    "output_tokens": 10, "total_tokens": total,
                }))
            attempts.append({
                "attempt": index, "argv": ["codex", "exec"] + (["resume", "worker-thread"] if index > 1 else []) + [
                    "-m", "gpt-5.6-terra", "-c", 'model_reasoning_effort="high"',
                    "-c", 'service_tier="priority"',
                ],
                "transcript_path": str(transcript), "exit_code": 0,
                "at": f"2026-09-22T10:0{index + 1}:00+00:00",
            })
            controller_events.append({
                "event_type": "provider_started", "ts": f"2026-09-22T10:0{index}:00+00:00",
            })
        write_jsonl(workspace / "controller.attempts.jsonl", attempts)
        write_jsonl(workspace / "controller.events.jsonl", controller_events)

    def test_selects_last_terminal_not_largest_or_nested_item_usage(self) -> None:
        write_jsonl(self.root_events, [
            {"type": "item.completed", "item": {"usage": {"total_tokens": 9999}}},
            *events("thread", {"input_tokens": 80, "output_tokens": 20, "total_tokens": 100}),
            {"type": "turn.completed", "usage": {
                "input_tokens": 60, "cached_input_tokens": 40,
                "output_tokens": 10, "reasoning_output_tokens": 6, "total_tokens": 70,
            }},
        ])
        result = extract_usage(self.root_events)
        self.assertEqual(result["comparison_total_tokens"], 70)
        self.assertEqual(result["cached_input_tokens"], 40)
        self.assertEqual(result["reasoning_output_tokens"], 6)
        self.assertEqual(result["terminal_records"], 2)

    def test_derived_total_does_not_add_cached_or_reasoning(self) -> None:
        result = normalize_usage({
            "input_tokens": 120, "cached_input_tokens": 80,
            "output_tokens": 30, "reasoning_output_tokens": 12,
        })
        self.assertEqual(result["comparison_total_tokens"], 150)
        self.assertEqual(result["comparison_total_source"], "derived_input_plus_output")
        self.assertIsNone(result["reported_total_tokens"])
        reported = normalize_usage({"input_tokens": 120, "output_tokens": 30, "total_tokens": 151})
        self.assertEqual(reported["comparison_total_tokens"], 151)
        self.assertEqual(reported["comparison_total_source"], "provider_reported_total_tokens")
        with self.assertRaises(LedgerError):
            normalize_usage({"input_tokens": 12.5, "output_tokens": 3})
        with self.assertRaises(LedgerError):
            normalize_usage({"input_tokens": 10, "cached_input_tokens": 11, "output_tokens": 2})

    def test_raw_snapshot_and_budget_gate(self) -> None:
        self.make_task(budget=20)
        report = build_snapshot(self.task_file)
        self.assertEqual(report["known_total_tokens"], 20)
        self.assertFalse(report["gate_allows_new_work"])
        self.assertEqual(report["overshoot_tokens"], 0)
        command = [sys.executable, str(Path(__file__).resolve().parents[1] / "collect_codex_usage.py"),
                   "gate", "--task-file", str(self.task_file)]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 3)

    def test_resumed_cumulative_usage_and_exact_replay(self) -> None:
        self.make_task(arm="harness", budget=200)
        self.make_worker([100, 150, 150], replay_last=True)
        report = build_snapshot(self.task_file)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["known_total_tokens"], 170)
        self.assertEqual(report["aggregate_components"]["input_tokens"], 155)
        self.assertEqual(report["aggregate_components"]["cached_input_tokens"], 7)
        self.assertEqual(report["aggregate_components"]["output_tokens"], 15)
        self.assertIsNone(report["aggregate_components"]["reasoning_output_tokens"])
        workers = sorted((row for row in report["rows"] if row["role"] == "worker"), key=lambda row: row["attempt"])
        self.assertEqual([row["charged_tokens"] for row in workers], [100, 50, 0])
        self.assertEqual(workers[1]["charge_source"], "session_cumulative_delta")
        self.assertEqual(workers[2]["charge_source"], "exact_transcript_replay")

    def test_resume_lane_restarts_controller_and_appends_one_transcript(self) -> None:
        self.make_task(arm="harness", budget=None)
        self.make_worker([100, 150, 175])
        workspace = self.runtime / "worktrees" / "epoch-1" / "lane-1" / ".agent-workspace"
        shared = workspace / "provider-transcript.jsonl"
        shared.write_bytes(shared.read_bytes() + b"".join(
            (workspace / "attempts" / f"attempt-{index}" / "provider-transcript.jsonl").read_bytes()
            for index in (2, 3)
        ))
        for index in (2, 3):
            (workspace / "attempts" / f"attempt-{index}" / "provider-transcript.jsonl").unlink()
        attempts_path = workspace / "controller.attempts.jsonl"
        attempts = [json.loads(line) for line in attempts_path.read_text(encoding="utf-8").splitlines()]
        for row in attempts[1:]:
            row["attempt"] = 1
            row["transcript_path"] = str(shared)
        write_jsonl(attempts_path, attempts)
        events_path = workspace / "controller.events.jsonl"
        controller_events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        for index, event in enumerate(controller_events[1:], 1):
            event["run_id"] = f"controller-{index}"
        write_jsonl(events_path, controller_events)

        complete_transcript = shared.read_bytes()
        write_jsonl(shared, [json.loads(line) for line in complete_transcript.decode().splitlines()[:-3]])
        write_jsonl(attempts_path, attempts[:-1])
        in_flight = build_snapshot(self.task_file)
        self.assertEqual(in_flight["errors"], [])
        self.assertEqual(in_flight["in_flight_invocations"], 1)
        self.assertEqual(in_flight["known_total_tokens"], 170)
        shared.write_bytes(complete_transcript)
        write_jsonl(attempts_path, attempts)

        report = build_snapshot(self.task_file)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["known_total_tokens"], 195)
        workers = [row for row in report["rows"] if row["role"] == "worker"]
        self.assertEqual([row["charged_tokens"] for row in workers], [100, 50, 25])
        self.assertEqual([row["transcript_segment_index"] for row in workers], [1, 2, 3])
        self.assertEqual(len({row["invocation_id"] for row in workers}), 3)
        self.assertEqual(len({row["transcript_segment_sha256"] for row in workers}), 3)
        archived = finalize(self.task_file, self.base / "appended-archive")
        self.assertEqual(archived["known_total_tokens"], 195)

    def test_resumed_thread_without_baseline_fails_closed(self) -> None:
        self.make_task(arm="harness")
        self.make_worker([100, 150])
        first = self.runtime / "worktrees" / "epoch-1" / "lane-1" / ".agent-workspace" / "provider-transcript.jsonl"
        first.unlink()
        report = build_snapshot(self.task_file)
        self.assertFalse(report["gate_allows_new_work"])
        self.assertTrue(any("no prior baseline" in error for error in report["errors"]))

    def test_decreasing_session_total_fails_closed(self) -> None:
        self.make_task(arm="harness")
        self.make_worker([100, 80])
        report = build_snapshot(self.task_file)
        self.assertFalse(report["gate_allows_new_work"])
        self.assertTrue(any("decreased" in error for error in report["errors"]))

    def test_worker_launch_configuration_mismatch_fails_closed(self) -> None:
        self.make_task(arm="harness")
        self.make_worker([100])
        record = self.runtime / "worktrees" / "epoch-1" / "lane-1" / ".agent-workspace" / "controller.attempts.jsonl"
        rows = [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines()]
        rows[1]["argv"][rows[1]["argv"].index("-m") + 1] = "wrong-model"
        write_jsonl(record, rows)
        report = build_snapshot(self.task_file)
        self.assertFalse(report["gate_allows_new_work"])
        self.assertTrue(any("launch argv differs" in error for error in report["errors"]))

    def test_malformed_or_missing_terminal_usage_is_not_a_pass(self) -> None:
        self.make_task()
        self.root_events.write_text('{"type":"turn.completed","usage":{"input_tokens":1}}\nnot json\n', encoding="utf-8")
        with self.assertRaises(LedgerError):
            build_snapshot(self.task_file)
        write_jsonl(self.root_events, [{"type": "thread.started", "thread_id": "root-thread"}])
        report = build_snapshot(self.task_file)
        self.assertFalse(report["gate_allows_new_work"])
        self.assertTrue(report["errors"])

    def test_failed_final_turn_does_not_look_complete(self) -> None:
        self.make_task()
        write_jsonl(self.root_events, [
            *events("root-thread", {"input_tokens": 10, "output_tokens": 3}),
            {"type": "turn.failed", "error": {"message": "failed"}},
        ])
        report = build_snapshot(self.task_file)
        self.assertFalse(report["gate_allows_new_work"])
        self.assertTrue(any("terminal_failure_after_usage" in error for error in report["errors"]))

    def test_live_partial_tail_is_ignored_until_complete(self) -> None:
        self.make_task(finished=False)
        with self.root_events.open("ab") as stream:
            stream.write(b'{"type":"turn.compl')
        result = extract_usage(self.root_events, completed=False)
        self.assertEqual(result["comparison_total_tokens"], 20)
        with self.assertRaises(LedgerError):
            extract_usage(self.root_events, completed=True)

    def test_in_flight_and_final_overshoot_are_reported(self) -> None:
        self.make_task(arm="harness", budget=100, root_total=20, finished=False)
        self.make_worker([95])
        report = build_snapshot(self.task_file)
        self.assertEqual(report["known_total_tokens"], 115)
        self.assertEqual(report["overshoot_tokens"], 15)
        self.assertEqual(report["in_flight_invocations"], 1)
        self.assertFalse(report["gate_allows_new_work"])
        with self.assertRaises(LedgerError):
            finalize(self.task_file, self.base / "archive")

    def test_archive_is_write_once_and_hashes_source(self) -> None:
        self.make_task(arm="harness")
        self.make_worker([100, 150])
        destination = self.base / "archive"
        summary = finalize(self.task_file, destination)
        self.assertEqual(summary["known_total_tokens"], 170)
        ledger = json.loads((destination / "ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(len(ledger["rows"]), 3)
        for row in ledger["rows"]:
            self.assertTrue((destination / row["archived_transcript"]).is_file())
            self.assertTrue(row["source_manifest_sha256"])
        with self.assertRaises(FileExistsError):
            finalize(self.task_file, destination)

    def test_run_capture_records_task_and_keeps_stderr_out_of_jsonl(self) -> None:
        prompt = self.base / "prompt.md"
        prompt.write_text("offline fixture prompt\n", encoding="utf-8")
        workspace = self.base / "workspace"
        workspace.mkdir()
        runtime = workspace / ".harness-runtime"
        runtime.mkdir()
        arguments = argparse.Namespace(
            prompt_file=str(prompt), cwd=str(workspace), budget_tokens=100,
            arm="harness", harness_runtime=str(runtime),
            results_dir=str(self.base / "results"), run_id="capture-1", task="fixture-task",
            sandbox="workspace-write", model="gpt-5.6-terra", reasoning_effort="max",
            service_tier="priority", watchdog_hours=15,
        )

        class FakeProcess:
            def __init__(self) -> None:
                self.stdout = io.StringIO("".join(json.dumps(item) + "\n" for item in events(
                    "capture-thread", {"input_tokens": 10, "output_tokens": 2}
                )))

            def wait(self, timeout=None) -> int:
                return 0

        with patch.dict("collect_codex_usage.os.environ", {
            "SWE_TOKEN_TASK_FILE": "stale-task", "SWE_TOKEN_COLLECTOR": "stale-collector",
        }):
            with patch("collect_codex_usage.subprocess.Popen", return_value=FakeProcess()) as popen:
                with patch("sys.stdout", new_callable=io.StringIO):
                    self.assertEqual(run_codex(arguments), 0)
        directory = self.base / "results" / "capture-1"
        task = json.loads((directory / "task.json").read_text(encoding="utf-8"))
        self.assertEqual(task["budget_tokens"], 100)
        self.assertEqual(task["harness_runtime"], str(runtime))
        self.assertEqual(extract_usage(directory / "codex-events.jsonl")["comparison_total_tokens"], 12)
        self.assertEqual((directory / "codex-stderr.txt").read_text(encoding="utf-8"), "")
        environment = popen.call_args.kwargs["env"]
        command = popen.call_args.args[0]
        self.assertIn("--sandbox", command)
        self.assertIn("workspace-write", command)
        self.assertIn('approval_policy="never"', command)
        self.assertEqual(environment["SWE_TOKEN_TASK_FILE"], str(directory / "task.json"))
        self.assertEqual(environment["SWE_TOKEN_COLLECTOR"], str(Path(__file__).resolve().parents[1] / "collect_codex_usage.py"))

    def test_collector_stdout_escapes_unicode_missing_from_cp1252(self) -> None:
        sink = io.BytesIO()
        terminal = io.TextIOWrapper(sink, encoding="cp1252", write_through=True)
        with patch("sys.stdout", terminal):
            write_stdout_safe('{"message":"\u009d"}\n')
        self.assertEqual(sink.getvalue().replace(b"\r\n", b"\n"), b'{"message": "\\u009d"}\n')

    def test_uncapped_usage_still_counts_and_does_not_install_launch_gate(self) -> None:
        self.make_task(arm="harness", budget=None, root_total=37)
        self.make_worker([19])
        report = build_snapshot(self.task_file)
        self.assertEqual(report["known_total_tokens"], 56)
        self.assertIsNone(report["budget_tokens"])
        self.assertIsNone(report["remaining_tokens"])
        self.assertIsNone(report["overshoot_tokens"])
        self.assertTrue(report["gate_allows_new_work"])
        prompt = self.base / "uncapped-prompt.md"
        prompt.write_text("offline fixture prompt\n", encoding="utf-8")
        workspace = self.base / "uncapped-workspace"
        workspace.mkdir()
        runtime = workspace / ".harness-runtime"
        runtime.mkdir()
        arguments = argparse.Namespace(
            prompt_file=str(prompt), cwd=str(workspace), budget_tokens=None,
            arm="harness", harness_runtime=str(runtime),
            results_dir=str(self.base / "results"), run_id="uncapped-capture", task="fixture-task",
            sandbox="danger-full-access", model="gpt-5.6-terra", reasoning_effort="max",
            service_tier="priority", watchdog_hours=15, inhibit_sleep=False,
        )

        class FakeProcess:
            stdout = io.StringIO("".join(json.dumps(item) + "\n" for item in events(
                "uncapped-thread", {"input_tokens": 10, "output_tokens": 2}
            )))

            def wait(self, timeout=None) -> int:
                return 0

        with patch.dict("collect_codex_usage.os.environ", {
            "SWE_TOKEN_TASK_FILE": "stale-task", "SWE_TOKEN_COLLECTOR": "stale-collector",
        }):
            with patch("collect_codex_usage.subprocess.Popen", return_value=FakeProcess()) as popen:
                with patch("sys.stdout", new_callable=io.StringIO):
                    self.assertEqual(run_codex(arguments), 0)
        environment = popen.call_args.kwargs["env"]
        self.assertNotIn("SWE_TOKEN_TASK_FILE", environment)
        self.assertNotIn("SWE_TOKEN_COLLECTOR", environment)

    def test_two_offline_root_resumes_keep_one_task_and_cumulative_tokens(self) -> None:
        self.make_task(arm="harness", budget=None, root_total=20)
        original = json.loads((self.run_dir / "launch.json").read_text(encoding="utf-8"))
        original.update({
            "sandbox": "danger-full-access", "workspace": str(self.runtime.parent),
            "watchdog_hours": 10,
        })
        write_json(self.run_dir / "launch.json", original)
        task = json.loads(self.task_file.read_text(encoding="utf-8"))
        task["interruption_policy"] = "planned_resume"
        write_json(self.task_file, task)
        write_json(self.run_dir / "manifest.json", {
            **original, "ended_at_utc": "2026-09-22T10:10:00+00:00",
            "exit_code": 0, "elapsed_seconds": 600, "watchdog_expired": False,
        })
        self.runtime.mkdir(parents=True)
        write_json(self.runtime / "RUNTIME_STATE.json", {"state": "CLOSED"})
        prompt = self.base / "resume-prompt.md"
        prompt.write_text("Continue from the saved plan.\n", encoding="utf-8")

        class FakeProcess:
            def __init__(self, total: int) -> None:
                self.stdout = io.StringIO("".join(json.dumps(item) + "\n" for item in events(
                    "root-thread", {"input_tokens": total - 5, "output_tokens": 5,
                                    "total_tokens": total}
                )))

            def wait(self, timeout=None) -> int:
                return 0

        for number, total in ((2, 30), (3, 45)):
            args = argparse.Namespace(resume_task_file=str(self.task_file), prompt_file=str(prompt), inhibit_sleep=False)
            with patch("collect_codex_usage.subprocess.Popen", return_value=FakeProcess(total)) as popen:
                with patch("sys.stdout", new_callable=io.StringIO):
                    self.assertEqual(run_codex(args), 0)
            command = popen.call_args.args[0]
            self.assertEqual(command[:3], ["codex", "exec", "resume"])
            self.assertIn("root-thread", command)
            self.assertIn('sandbox_mode="danger-full-access"', command)
            directory = self.run_dir / "segments" / f"{number:04d}"
            self.assertTrue((directory / "manifest.json").is_file())
            remaining = json.loads((directory / "launch.json").read_text())["watchdog_hours"]
            self.assertGreater(remaining, 9.8)
            self.assertLess(remaining, 10)
        report = build_snapshot(self.task_file)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["known_total_tokens"], 45)
        self.assertEqual(report["resume_count"], 2)
        self.assertEqual(report["interruption_policy"], "planned_resume")
        self.assertEqual([row["charged_tokens"] for row in report["rows"]], [20, 10, 15])
        self.assertEqual(len([row for row in report["rows"] if row["role"] == "root"]), 3)
        archived = finalize(self.task_file, self.base / "resumed-archive")
        self.assertEqual(archived["known_total_tokens"], 45)

    def test_resume_refuses_open_harness_runtime(self) -> None:
        self.make_task(arm="harness", budget=None)
        original = json.loads((self.run_dir / "launch.json").read_text())
        original.update({"sandbox": "danger-full-access", "workspace": str(self.runtime.parent), "watchdog_hours": 5})
        write_json(self.run_dir / "launch.json", original)
        task = json.loads(self.task_file.read_text(encoding="utf-8"))
        task["interruption_policy"] = "planned_resume"
        write_json(self.task_file, task)
        write_json(self.run_dir / "manifest.json", {**original, "ended_at_utc": "2026-09-22T10:10:00+00:00", "exit_code": 0, "elapsed_seconds": 600})
        self.runtime.mkdir(parents=True)
        write_json(self.runtime / "RUNTIME_STATE.json", {"state": "OPEN"})
        prompt = self.base / "resume-prompt.md"
        prompt.write_text("Continue\n", encoding="utf-8")
        args = argparse.Namespace(resume_task_file=str(self.task_file), prompt_file=str(prompt), inhibit_sleep=False)
        with self.assertRaisesRegex(LedgerError, "close the native harness runtime"):
            run_codex(args)
        self.assertFalse((self.run_dir / "segments").exists())

    def test_resume_allows_explicit_quiescent_open_review_only(self) -> None:
        self.make_task(arm="harness", budget=None)
        original = json.loads((self.run_dir / "launch.json").read_text())
        original.update({"sandbox": "danger-full-access", "workspace": str(self.runtime.parent), "watchdog_hours": 5})
        write_json(self.run_dir / "launch.json", original)
        task = json.loads(self.task_file.read_text(encoding="utf-8"))
        task["interruption_policy"] = "planned_resume"
        write_json(self.task_file, task)
        write_json(self.run_dir / "manifest.json", {
            **original, "ended_at_utc": "2026-09-22T10:10:00+00:00",
            "exit_code": 0, "elapsed_seconds": 600,
        })
        write_json(self.runtime / "RUNTIME_STATE.json", {"state": "OPEN"})
        lane_path = self.runtime / "epochs" / "epoch-1" / "lanes" / "lane-1" / "lane.json"
        status_path = self.runtime / "worktrees" / "epoch-1" / "lane-1" / "controller.status.json"
        write_json(lane_path, {
            "lifecycle": "review_pending", "run_id": "worker-run",
            "controller_status_path": str(status_path),
        })
        write_json(status_path, {
            "run_id": "worker-run", "recorded_status": "review_pending",
            "controller_state": "exited", "cleanup_proven": True,
            "provider_state": {"state": "exited"},
        })
        args = argparse.Namespace(resume_task_file=str(self.task_file), continue_open_runtime=True)
        segment, number, session, remaining = prepare_resume(args)
        self.assertEqual((segment.name, number, session), ("0002", 2, "root-thread"))
        self.assertGreater(remaining, 4.8)
        write_json(status_path, {
            "run_id": "worker-run", "recorded_status": "review_pending",
            "controller_state": "exited", "cleanup_proven": False,
            "provider_state": {"state": "exited"},
        })
        with self.assertRaisesRegex(LedgerError, "quiescent open review"):
            prepare_resume(args)
        write_json(lane_path, {
            "lifecycle": "running", "run_id": "worker-run",
            "controller_status_path": str(status_path),
        })
        with self.assertRaisesRegex(LedgerError, "quiescent open review"):
            prepare_resume(args)

    def test_terminated_unmetered_worker_can_resume_with_explicit_gap(self) -> None:
        self.make_task(arm="harness", budget=None)
        launch = json.loads((self.run_dir / "launch.json").read_text())
        launch.update({
            "sandbox": "danger-full-access", "workspace": str(self.runtime.parent),
            "watchdog_hours": 10,
        })
        write_json(self.run_dir / "launch.json", launch)
        write_json(self.run_dir / "manifest.json", {
            **launch, "ended_at_utc": "2026-09-22T10:10:00+00:00",
            "elapsed_seconds": 600, "exit_code": 0, "watchdog_expired": False,
        })
        task = json.loads(self.task_file.read_text())
        task["interruption_policy"] = "planned_resume"
        write_json(self.task_file, task)
        write_json(self.runtime / "RUNTIME_STATE.json", {"state": "CLOSED"})
        epoch = self.runtime / "epochs" / "epoch-1"
        closed_at = "2026-09-22T10:09:00+00:00"
        write_json(epoch / "epoch-state.json", {"lifecycle": "closed", "closed_at": closed_at})
        write_json(epoch / "lanes" / "lane-1" / "lane.json", {
            "lifecycle": "retired", "run_id": "worker-run",
        })
        workspace = self.runtime / "worktrees" / "epoch-1" / "lane-1" / ".agent-workspace"
        transcript = workspace / "provider-transcript.jsonl"
        write_jsonl(transcript, [
            {"type": "thread.started", "thread_id": "failed-worker"},
            {"type": "turn.started"},
            {"type": "error", "message": "network disconnected"},
        ])
        write_json(workspace / "invocation.json", {
            "schema": "controller-invocation/v1", "lane_id": "lane-1",
            "run_id": "worker-run",
            "provider": {"id": "codex", "model": "gpt-5.6-terra",
                         "launch_config": {"reasoning_effort": "high", "service_tier": "priority"}},
            "paths": {"transcript": str(transcript)},
        })
        write_jsonl(workspace / "controller.events.jsonl", [
            {"event_type": "provider_started", "ts": "2026-09-22T10:01:00+00:00"},
        ])
        before = build_snapshot(self.task_file)
        self.assertEqual(before["in_flight_invocations"], 1)
        self.assertFalse(before["token_total_is_exact"])
        gap = {
            "invocation_id": "run-1.epoch-1.lane-1.worker-run.attempt-1",
            "epoch_id": "epoch-1", "lane_id": "lane-1", "lane_run_id": "worker-run",
            "epoch_closed_at": closed_at,
            "transcript_sha256": hashlib.sha256(transcript.read_bytes()).hexdigest(),
            "reason": "provider network failure before terminal usage",
            "operator_observed_absent_at_utc": "2026-09-22T10:11:00+00:00",
        }
        write_json(self.run_dir / "usage-gaps.json", {
            "schema": "codex-usage-gaps/v1", "run_id": "run-1", "gaps": [gap],
        })
        write_json(epoch / "epoch-state.json", {"lifecycle": "open", "closed_at": closed_at})
        with self.assertRaisesRegex(LedgerError, "closed epoch and retired lane"):
            build_snapshot(self.task_file)
        write_json(epoch / "epoch-state.json", {"lifecycle": "closed", "closed_at": closed_at})
        write_json(epoch / "lanes" / "lane-1" / "lane.json", {
            "lifecycle": "running", "run_id": "worker-run",
        })
        with self.assertRaisesRegex(LedgerError, "closed epoch and retired lane"):
            build_snapshot(self.task_file)
        write_json(epoch / "lanes" / "lane-1" / "lane.json", {
            "lifecycle": "retired", "run_id": "worker-run",
        })
        after = build_snapshot(self.task_file)
        self.assertEqual(after["errors"], [])
        self.assertEqual(after["in_flight_invocations"], 0)
        self.assertEqual(after["unknown_usage_invocations"], 1)
        self.assertFalse(after["token_total_is_exact"])
        self.assertEqual(after["known_total_tokens"], 20)
        self.assertEqual(after["rows"][-1]["status"], "terminated_usage_unknown")
        args = argparse.Namespace(resume_task_file=str(self.task_file))
        segment, number, session, remaining = prepare_resume(args)
        self.assertEqual((segment.name, number, session, remaining), ("0002", 2, "root-thread", 10))
        archive = self.base / "gap-archive"
        summary = finalize(self.task_file, archive)
        self.assertEqual(summary["unknown_usage_invocations"], 1)
        self.assertFalse(summary["token_total_is_exact"])
        self.assertTrue((archive / "ledger.json").is_file())
        transcript.write_text(transcript.read_text() + '{"type":"error"}\n', encoding="utf-8")
        with self.assertRaisesRegex(LedgerError, "usage-gap transcript hash"):
            build_snapshot(self.task_file)

    def test_usage_gap_rejects_unknown_invocation(self) -> None:
        self.make_task(arm="harness", budget=None)
        write_json(self.run_dir / "usage-gaps.json", {
            "schema": "codex-usage-gaps/v1", "run_id": "run-1", "gaps": [{
                "invocation_id": "unknown", "epoch_id": "epoch-1", "lane_id": "lane-1",
                "lane_run_id": "worker-run", "epoch_closed_at": "2026-09-22T10:09:00+00:00",
                "transcript_sha256": "0" * 64, "reason": "network failure",
                "operator_observed_absent_at_utc": "2026-09-22T10:11:00+00:00",
            }],
        })
        with self.assertRaisesRegex(LedgerError, "unknown worker invocation"):
            build_snapshot(self.task_file)

    def test_worker_is_attributed_to_correct_root_segment_and_pause_is_empty(self) -> None:
        self.make_task(arm="harness", budget=None, root_total=20)
        task = json.loads(self.task_file.read_text())
        task["interruption_policy"] = "planned_resume"
        write_json(self.task_file, task)
        second = self.run_dir / "segments" / "0002"
        original = json.loads((self.run_dir / "launch.json").read_text())
        next_launch = {
            **original, "started_at_utc": "2026-09-22T11:00:00+00:00",
            "segment_number": 2, "resume_session_id": "root-thread",
            "command": ["codex", "exec", "resume", "root-thread", "-m", "gpt-5.6-terra",
                        "-c", 'model_reasoning_effort="max"', "-c", 'service_tier="priority"'],
        }
        write_json(second / "launch.json", next_launch)
        write_json(second / "manifest.json", {
            **next_launch, "ended_at_utc": "2026-09-22T11:10:00+00:00", "exit_code": 0,
        })
        write_jsonl(second / "codex-events.jsonl", events("root-thread", {
            "input_tokens": 24, "output_tokens": 6, "total_tokens": 30,
        }))
        self.make_worker([15])
        worker = self.runtime / "worktrees" / "epoch-1" / "lane-1" / ".agent-workspace"
        write_jsonl(worker / "controller.events.jsonl", [
            {"event_type": "provider_started", "ts": "2026-09-22T11:01:00+00:00"},
        ])
        attempts_path = worker / "controller.attempts.jsonl"
        attempts = [json.loads(line) for line in attempts_path.read_text().splitlines()]
        attempts[1]["at"] = "2026-09-22T11:02:00+00:00"
        write_jsonl(attempts_path, attempts)
        report = build_snapshot(self.task_file)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["known_total_tokens"], 45)
        self.assertEqual(report["paused_wall_seconds"], 3000)
        worker_row = next(row for row in report["rows"] if row["role"] == "worker")
        self.assertEqual(worker_row["parent_id"], "run-1.root.segment-2")
        write_jsonl(worker / "controller.events.jsonl", [
            {"event_type": "provider_started", "ts": "2026-09-22T10:30:00+00:00"},
        ])
        with self.assertRaisesRegex(LedgerError, "worker activity occurred during paused interval"):
            build_snapshot(self.task_file)

    def test_existing_epoch_attempts_before_this_root_run_are_excluded(self) -> None:
        self.make_task(arm="harness", budget=None, root_total=37)
        self.make_worker([19])
        workspace = self.runtime / "worktrees" / "epoch-1" / "lane-1" / ".agent-workspace"
        write_jsonl(workspace / "controller.events.jsonl", [
            {"event_type": "provider_started", "ts": "2026-09-22T09:00:00+00:00"},
        ])
        report = build_snapshot(self.task_file)
        self.assertEqual(report["known_total_tokens"], 37)
        self.assertEqual(len(report["rows"]), 1)
        self.assertEqual(report["errors"], [])

    def test_other_epochs_do_not_force_a_manual_epoch_id(self) -> None:
        self.make_task(arm="harness", budget=None, root_total=37)
        self.make_worker([19])
        old = self.runtime / "worktrees" / "old-epoch" / "old-lane" / ".agent-workspace"
        old.mkdir(parents=True)
        write_json(old / "invocation.json", {
            "schema": "controller-invocation/v1", "lane_id": "old-lane", "run_id": "old-run",
            "provider": {"id": "codex", "model": "gpt-5.6-terra",
                         "launch_config": {"reasoning_effort": "high", "service_tier": "priority"}},
        })
        write_jsonl(old / "controller.events.jsonl", [
            {"event_type": "provider_started", "ts": "2026-09-21T09:00:00+00:00"},
        ])
        write_jsonl(old / "controller.attempts.jsonl", [
            {"attempt": 1, "argv": ["codex", "exec"], "exit_code": 1,
             "at": "2026-09-21T09:01:00+00:00"},
        ])
        report = build_snapshot(self.task_file)
        self.assertEqual(report["known_total_tokens"], 56)
        self.assertEqual(report["errors"], [])

    def test_watchdog_expires_and_records_a_hard_stop(self) -> None:
        prompt = self.base / "prompt.md"
        prompt.write_text("offline watchdog fixture\n", encoding="utf-8")
        workspace = self.base / "workspace"
        workspace.mkdir()
        stopped = threading.Event()

        class BlockingOutput:
            def __iter__(self):
                return self

            def __next__(self):
                if not stopped.wait(timeout=5):
                    raise AssertionError("watchdog did not stop the process")
                raise StopIteration

        class FakeProcess:
            stdout = BlockingOutput()

            def poll(self):
                return 137 if stopped.is_set() else None

            def wait(self, timeout=None):
                return 137

        arguments = argparse.Namespace(
            prompt_file=str(prompt), cwd=str(workspace), budget_tokens=100,
            arm="raw", harness_runtime=None, results_dir=str(self.base / "results"),
            run_id="watchdog-fixture", task="fixture-task", sandbox="workspace-write",
            model="gpt-5.6-terra", reasoning_effort="max", service_tier="priority",
            watchdog_hours=0.00003, inhibit_sleep=False,
        )
        with patch("collect_codex_usage.subprocess.Popen", return_value=FakeProcess()):
            with patch("collect_codex_usage.stop_process_tree", side_effect=lambda _: stopped.set()) as stop:
                with patch("sys.stdout", new_callable=io.StringIO):
                    self.assertEqual(run_codex(arguments), 124)
        self.assertTrue(stop.called)
        manifest = json.loads((self.base / "results" / "watchdog-fixture" / "manifest.json").read_text())
        self.assertTrue(manifest["watchdog_expired"])
        self.assertEqual(manifest["watchdog_stop_errors"], [])

    def test_process_tree_stop_terminates_a_real_child(self) -> None:
        process = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            start_new_session=sys.platform != "win32",
        )
        try:
            stop_process_tree(process)
            self.assertIsNotNone(process.wait(timeout=5))
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)

    def test_watchdog_stops_detached_harness_lane_after_root_exits(self) -> None:
        prompt = self.base / "prompt.md"
        prompt.write_text("offline detached-lane fixture\n", encoding="utf-8")
        workspace = self.base / "workspace"
        workspace.mkdir()
        runtime = workspace / ".harness-runtime"
        runtime.mkdir()

        class ExitedRoot:
            stdout = io.StringIO("".join(json.dumps(item) + "\n" for item in events(
                "detached-root", {"input_tokens": 10, "output_tokens": 2}
            )))

            def poll(self):
                return 0

            def wait(self, timeout=None):
                return 0

        arguments = argparse.Namespace(
            prompt_file=str(prompt), cwd=str(workspace), budget_tokens=100,
            arm="harness", harness_runtime=str(runtime), results_dir=str(self.base / "results"),
            run_id="detached-fixture", task="fixture-task", sandbox="workspace-write",
            model="gpt-5.6-terra", reasoning_effort="max", service_tier="priority",
            watchdog_hours=0.00003, inhibit_sleep=False,
        )
        with patch("collect_codex_usage.subprocess.Popen", return_value=ExitedRoot()):
            with patch("collect_codex_usage.active_harness_lanes", return_value=True):
                with patch("collect_codex_usage.shutdown_harness_runtime", return_value=None) as shutdown:
                    with patch("collect_codex_usage.time.sleep", return_value=None):
                        with patch("sys.stdout", new_callable=io.StringIO):
                            self.assertEqual(run_codex(arguments), 124)
        self.assertTrue(shutdown.called)
        manifest = json.loads((self.base / "results" / "detached-fixture" / "manifest.json").read_text())
        self.assertTrue(manifest["watchdog_expired"])


if __name__ == "__main__":
    unittest.main()
