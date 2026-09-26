# Sealed score: labeled lean retry

- Frozen candidate: `root_runs/zstd-decoder-lean-retry-90m`, commit `45b41f6f2b59b66eb58a82538bd42e1da488ca87`; source SHA-256 `6c623765ce640e46ff8f70a41a4cd0332588f94471bce7e594c7fa18de1b6f71`.
- Pinned image ID: `sha256:3a43d4f3658c4a21115c518937b692692e9e721d3b6e4a3205972917b8bc2e8a`. Verifier SHA-256: `453aa960844288d914b2c2a094759ac761638ca8990a3a32c112e4c0a4d79bd8`.
- Scored only after every host-access ROOT exited. Source and public samples were copied to a disposable, network-disabled container, rebuilt with `make -B -C /app/src`, then tested by the pinned verifier. The container was removed. The verifier-copied source hash matches the frozen candidate.
- Raw result: 5/6 public, 25/37 hidden, 30/43 overall; `partial_score: 0.698`; binary reward `0`. Makefile and libzstd anti-cheat checks passed.
- At the user's request this started from an isolated pre-run source history with a stronger full-duration prompt. Nevertheless ROOT froze at 2,407.531 seconds (40m07.531s) with video still failing, well before the 90-minute deadline and against that prompt's explicit instruction. A fresh Priority/high validator identified the video Huffman/four-stream defect; ROOT retested but did not repair it.
- Exact ROOT-plus-four-worker-invocation usage: 28,999,363 input tokens (28,406,016 cached) and 139,992 output; 29,139,355 total, or 733,339 uncached input plus output. Zero unknown invocations; all actual invocations were Terra/high/Priority.

This was not interchangeable with the original matched lean arm: its prompt was strengthened and it overlapped only part of the targeted arm's runtime. Do not normalize the raw reward against the imperfect local oracle.
