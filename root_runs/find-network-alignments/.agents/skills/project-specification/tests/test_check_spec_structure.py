from __future__ import annotations

import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_spec_structure.py"
SPEC = importlib.util.spec_from_file_location("check_spec_structure", SCRIPT)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class SpecStructureTests(unittest.TestCase):
    def make_valid_package(self, root: Path) -> Path:
        behaviors = root / "behaviors"
        behaviors.mkdir(parents=True)
        (root / "SPEC.md").write_text(
            "# Example specification\n\n"
            "## Behavior map\n\n"
            "[Sign in](behaviors/BEHAVIOR-01-sign-in.md#acceptance-scenarios)\n",
            encoding="utf-8",
        )
        (behaviors / "BEHAVIOR-01-sign-in.md").write_text(
            "# User signs in\n\n"
            "## Any semantically useful heading\n\n"
            "Detailed behavior.\n",
            encoding="utf-8",
        )
        return root

    def test_valid_package_is_usable_without_exact_section_policing(self):
        with tempfile.TemporaryDirectory() as directory:
            errors, warnings = checker.check_package(
                self.make_valid_package(Path(directory))
            )
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_missing_root_and_behavior_directory_are_local_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            errors, _ = checker.check_package(Path(directory))
            self.assertTrue(any("SPEC.md" in error for error in errors))
            self.assertTrue(any("behaviors" in error for error in errors))

    def test_duplicate_behavior_ids_are_ambiguous(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_valid_package(Path(directory))
            second = root / "behaviors" / "BEHAVIOR-01-use-passkey.md"
            second.write_text(
                "# BEHAVIOR-01 - User uses a passkey\n", encoding="utf-8"
            )
            (root / "SPEC.md").write_text(
                (root / "SPEC.md").read_text(encoding="utf-8")
                + "[Passkey](behaviors/BEHAVIOR-01-use-passkey.md)\n",
                encoding="utf-8",
            )
            errors, _ = checker.check_package(root)
            self.assertTrue(any("duplicate behavior ID" in error for error in errors))

    def test_heading_that_claims_an_identity_must_not_contradict_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_valid_package(Path(directory))
            behavior = root / "behaviors" / "BEHAVIOR-01-sign-in.md"
            behavior.write_text("# BEHAVIOR-02 - User signs in\n", encoding="utf-8")
            errors, _ = checker.check_package(root)
            self.assertTrue(any("contradicts filename" in error for error in errors))

    def test_link_titles_and_alternative_heading_style_are_not_policed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_valid_package(Path(directory))
            (root / "SPEC.md").write_text(
                "# Example specification\n\n"
                "[Sign in](<behaviors/BEHAVIOR-01-sign-in.md> \"primary behavior\")\n"
                "[Empty optional link]( )\n",
                encoding="utf-8",
            )
            behavior = root / "behaviors" / "BEHAVIOR-01-sign-in.md"
            behavior.write_text("# BEHAVIOR-01: User signs in\n", encoding="utf-8")
            errors, warnings = checker.check_package(root)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_orphan_behavior_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_valid_package(Path(directory))
            orphan = root / "behaviors" / "BEHAVIOR-02-sign-out.md"
            orphan.write_text("# BEHAVIOR-02 - User signs out\n", encoding="utf-8")
            errors, _ = checker.check_package(root)
            self.assertTrue(any("not linked from SPEC.md" in error for error in errors))

    def test_broken_package_link_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_valid_package(Path(directory))
            behavior = root / "behaviors" / "BEHAVIOR-01-sign-in.md"
            behavior.write_text(
                behavior.read_text(encoding="utf-8")
                + "\n[Missing shared rule](../missing.md)\n",
                encoding="utf-8",
            )
            errors, _ = checker.check_package(root)
            self.assertTrue(any("broken package link" in error for error in errors))

    def test_noncanonical_extra_markdown_is_only_a_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_valid_package(Path(directory))
            (root / "behaviors" / "notes.md").write_text(
                "# Notes\n", encoding="utf-8"
            )
            errors, warnings = checker.check_package(root)
            self.assertEqual(errors, [])
            self.assertTrue(any("noncanonical" in warning for warning in warnings))

    def test_cli_exit_code_reflects_only_structural_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_valid_package(Path(directory))
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(checker.main([str(root)]), 0)
                (root / "behaviors" / "BEHAVIOR-02-orphan.md").write_text(
                    "# BEHAVIOR-02 - Orphan behavior\n", encoding="utf-8"
                )
                self.assertEqual(checker.main([str(root)]), 2)


if __name__ == "__main__":
    unittest.main()
