from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import docker_task_workspace as bridge


class DockerTaskWorkspaceTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.lane = (
            self.repo / "root_runs" / "biofabric-rust-rewrite"
            / ".harness-runtime" / "worktrees" / "epoch-1" / "lane-1"
        )
        self.lane.mkdir(parents=True)
        (self.lane / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")

    def test_one_mount_only_and_no_network(self) -> None:
        with patch.object(bridge, "REPO", self.repo):
            argv = bridge.docker_command("biofabric-rust-rewrite", self.lane, ["bash", "-lc", "true"])
        self.assertEqual(argv.count("--mount"), 1)
        self.assertIn("type=bind,source=" + str(self.lane) + ",target=/app", argv)
        self.assertEqual(argv[argv.index("--network") + 1], "none")
        self.assertNotIn(str(self.repo / "benchmarks"), " ".join(argv))

    def test_wrong_task_and_credential_are_rejected(self) -> None:
        with patch.object(bridge, "REPO", self.repo):
            with self.assertRaisesRegex(ValueError, "exact lane"):
                bridge.docker_command("find-network-alignments", self.lane, ["true"])
            auth = self.lane / ".codex" / "auth.json"
            auth.parent.mkdir()
            auth.write_text("fixture only", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "credential"):
                bridge.docker_command("biofabric-rust-rewrite", self.lane, ["true"])

    def test_zstd_lane_uses_pinned_image_and_one_mount(self) -> None:
        lane = (
            self.repo / "root_runs" / "zstd-decoder"
            / ".harness-runtime" / "worktrees" / "epoch-2" / "lane-2"
        )
        lane.mkdir(parents=True)
        (lane / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
        with patch.object(bridge, "REPO", self.repo):
            argv = bridge.docker_command("zstd-decoder", lane, ["bash", "-lc", "true"])
        self.assertEqual(argv.count("--mount"), 1)
        self.assertIn("type=bind,source=" + str(lane) + ",target=/app", argv)
        self.assertEqual(argv[argv.index("--network") + 1], "none")
        self.assertIn("swe-marathon-zstd-decoder:lf-20260925", argv)

    def test_registered_separate_zstd_workspace_is_exact(self) -> None:
        lane = (
            self.repo / "root_runs" / "zstd-decoder-lean-90m"
            / ".harness-runtime" / "worktrees" / "epoch-2" / "lane-2"
        )
        lane.mkdir(parents=True)
        (lane / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
        with patch.object(bridge, "REPO", self.repo):
            argv = bridge.docker_command(
                "zstd-decoder", lane, ["true"], "zstd-decoder-lean-90m"
            )
            with self.assertRaisesRegex(ValueError, "registered"):
                bridge.docker_command("zstd-decoder", lane, ["true"], "other")
            with self.assertRaisesRegex(ValueError, "exact lane"):
                bridge.docker_command("zstd-decoder", lane, ["true"])
        self.assertIn("type=bind,source=" + str(lane) + ",target=/app", argv)

    def test_registered_lean_root_can_run_public_checks_without_model_lane(self) -> None:
        root = self.repo / "root_runs" / "zstd-decoder-lean-90m"
        root.mkdir(parents=True)
        (root / ".git").mkdir()
        with patch.object(bridge, "REPO", self.repo):
            argv = bridge.docker_command("zstd-decoder", root, ["true"], "zstd-decoder-lean-90m")
        self.assertIn("type=bind,source=" + str(root) + ",target=/app", argv)
        self.assertEqual(argv.count("--mount"), 1)

if __name__ == "__main__":
    unittest.main()
