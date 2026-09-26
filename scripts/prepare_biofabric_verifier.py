"""Prepare an LF-only operator copy of the pinned BioFabric verifier script.

This does not execute the verifier or reveal its private test payload. The
Windows checkout has CRLF endings, which Bash rejects inside Docker.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = REPO / "benchmarks/swe-marathon/tasks/biofabric-rust-rewrite/tests/test.sh"
OUTPUT = REPO / "root_runs/biofabric-rust-rewrite/.harness-runtime/operator-only/verifier/test.sh"
EXPECTED_SOURCE_SHA256 = "d861e3a455b0437177fe34d45e8aa19ae97b40a15f89d5066542cf7b5656ea6a"


def normalized_bytes(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise ValueError("pinned BioFabric verifier checkout hash differs")
    normalized = source.replace(b"\r\n", b"\n")
    if b"\r" in normalized:
        raise ValueError("unexpected carriage return in BioFabric verifier")
    return normalized


def main() -> int:
    result = normalized_bytes(SOURCE.read_bytes())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        if OUTPUT.read_bytes() != result:
            raise FileExistsError(f"refusing to overwrite existing verifier copy: {OUTPUT}")
    else:
        with OUTPUT.open("xb") as stream:
            stream.write(result)
    print(f"operator-only LF copy: {OUTPUT}")
    print(f"normalized SHA-256: {hashlib.sha256(result).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
