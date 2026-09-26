# Sealed score: targeted xhigh/Max pilot

- Frozen candidate: `root_runs/zstd-decoder-validated-90m`, commit `6ca8a8d8f8b8d5107e63e736779d75b919ae3021`; source SHA-256 `220bd20594a4569e8699da9b3fb23fc4d4ca44c148aafc4c55d0465b66acbfa4`.
- Pinned image ID: `sha256:3a43d4f3658c4a21115c518937b692692e9e721d3b6e4a3205972917b8bc2e8a`. Verifier SHA-256: `453aa960844288d914b2c2a094759ac761638ca8990a3a32c112e4c0a4d79bd8`.
- Scored only after every host-access ROOT exited. Source and public samples were copied to a disposable, network-disabled container, rebuilt with `make -B -C /app/src`, then tested by the pinned verifier. The container was removed. The verifier-copied source hash matches the frozen candidate.
- Raw result: 6/6 public, 27/37 hidden, 33/43 overall; `partial_score: 0.767`; binary reward `0`. Makefile and libzstd anti-cheat checks passed. This equals the pinned local oracle's public, hidden, and total pass **counts** (33/43, reward 0); the metrics alone do not prove the same individual hidden cases passed.
- ROOT exited after 2,770.875 seconds (46m10.875s), before the 90-minute watchdog. A fresh Priority/high validator found a plausible reverse-bit defect, but ROOT rejected its proposed fix after a regression. Two Priority/max coding workers produced candidate code, but isolated worker Git-metadata restrictions prevented their commits; ROOT independently integrated and tested their useful changes. The native runtime closed cleanly.
- Exact ROOT-plus-three-worker usage: 31,510,299 input tokens (30,714,368 cached) and 209,854 output; 31,720,153 total, or 1,005,785 uncached input plus output. Zero unknown invocations. The actual launch records show ROOT Terra/xhigh/Priority, two Terra/max/Priority workers, and one Terra/high/Priority validator.

The raw benchmark reward remains zero; local-oracle count parity is a separate verifier-risk reference, not a normalized benchmark pass.
