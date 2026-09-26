#!/usr/bin/env python3
"""Check only the navigational integrity of a modular specification package."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


BEHAVIOR_FILENAME = re.compile(
    r"^BEHAVIOR-(?P<number>[0-9]{2,})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$"
)
H1_HEADING = re.compile(r"^#\s+(?P<text>.+?)\s*$", re.MULTILINE)
BEHAVIOR_ID = re.compile(r"\bBEHAVIOR-[0-9]{2,}\b")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\((?P<target>[^)]+)\)")
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def markdown_links(text: str) -> list[str]:
    """Return Markdown link targets outside fenced code blocks."""
    targets: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        targets.extend(match.group("target").strip() for match in MARKDOWN_LINK.finditer(line))
    return targets


def local_target(source: Path, raw_target: str, package_root: Path) -> Path | None:
    """Resolve a package-local file target; ignore anchors and external sources."""
    target = raw_target.strip()
    if not target:
        return None
    if target.startswith("<"):
        closing = target.find(">")
        if closing == -1:
            return None
        target = target[1:closing]
    else:
        # Markdown permits an optional quoted title after an unbracketed target.
        target = target.split(maxsplit=1)[0]
    if not target or target.startswith("#") or SCHEME.match(target):
        return None
    path_text = unquote(target.split("#", 1)[0])
    if not path_text:
        return None
    candidate = (source.parent / path_text).resolve()
    try:
        candidate.relative_to(package_root)
    except ValueError:
        # A specification may cite governing material outside its own package.
        return None
    return candidate


def check_package(root: Path) -> tuple[list[str], list[str]]:
    """Return structural errors and nonblocking warnings for *root*."""
    errors: list[str] = []
    warnings: list[str] = []
    package_root = root.resolve()

    if not package_root.is_dir():
        return [f"specification directory does not exist: {root}"], warnings

    spec_path = package_root / "SPEC.md"
    if not spec_path.is_file():
        errors.append("missing root specification: SPEC.md")

    behavior_dir = package_root / "behaviors"
    if not behavior_dir.is_dir():
        errors.append("missing behavior directory: behaviors")
        behavior_files: list[Path] = []
    else:
        behavior_files = sorted(behavior_dir.glob("*.md"))

    canonical_files: list[Path] = []
    ids: dict[str, Path] = {}
    for path in behavior_files:
        filename_match = BEHAVIOR_FILENAME.fullmatch(path.name)
        if not filename_match:
            warnings.append(
                f"noncanonical Markdown file in behaviors/: {path.relative_to(package_root)}"
            )
            continue

        canonical_files.append(path)
        behavior_id = f"BEHAVIOR-{filename_match.group('number')}"
        previous = ids.get(behavior_id)
        if previous is not None:
            errors.append(
                f"duplicate behavior ID {behavior_id}: "
                f"{previous.relative_to(package_root)} and {path.relative_to(package_root)}"
            )
        else:
            ids[behavior_id] = path

        text = path.read_text(encoding="utf-8")
        heading_match = H1_HEADING.search(text)
        heading_ids = (
            set(BEHAVIOR_ID.findall(heading_match.group("text")))
            if heading_match is not None
            else set()
        )
        conflicting_ids = sorted(identity for identity in heading_ids if identity != behavior_id)
        if conflicting_ids:
            errors.append(
                f"behavior heading {', '.join(conflicting_ids)} contradicts filename "
                f"{behavior_id}: {path.relative_to(package_root)}"
            )

    if not canonical_files:
        errors.append("no canonical BEHAVIOR-* Markdown files found")

    markdown_files: list[Path] = []
    if spec_path.is_file():
        markdown_files.append(spec_path)
    markdown_files.extend(behavior_files)

    referenced_behaviors: set[Path] = set()
    for source in markdown_files:
        text = source.read_text(encoding="utf-8")
        for raw_target in markdown_links(text):
            target = local_target(source, raw_target, package_root)
            if target is None:
                continue
            if not target.is_file():
                errors.append(
                    f"broken package link in {source.relative_to(package_root)}: {raw_target}"
                )
                continue
            if source == spec_path and target in canonical_files:
                referenced_behaviors.add(target)

    for path in canonical_files:
        if path not in referenced_behaviors:
            errors.append(
                f"behavior file is not linked from SPEC.md: {path.relative_to(package_root)}"
            )

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check identities and package-local links in a modular specification."
    )
    parser.add_argument("spec_directory", type=Path)
    args = parser.parse_args(argv)

    errors, warnings = check_package(args.spec_directory)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        print(
            f"Found {len(errors)} local structural issue(s); valid specification "
            "content outside those references remains usable.",
            file=sys.stderr,
        )
        return 2

    if warnings:
        print(f"Specification structure is usable with {len(warnings)} warning(s).")
    else:
        print("Specification structure is usable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
