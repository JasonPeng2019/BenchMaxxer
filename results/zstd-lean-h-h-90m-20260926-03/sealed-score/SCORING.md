# Sealed score: original lean `-03`

- Frozen candidate: `root_runs/zstd-decoder-lean-90m`, commit `50e41aa95be2bbf876db5d879921541e3ebd6dfd`; source SHA-256 `dd686dc654238a791bc9590bcea93488bf8d42e74ceff7112684c9e798a7bd63`.
- Pinned image ID: `sha256:3a43d4f3658c4a21115c518937b692692e9e721d3b6e4a3205972917b8bc2e8a`. Verifier SHA-256: `453aa960844288d914b2c2a094759ac761638ca8990a3a32c112e4c0a4d79bd8`.
- Scored only after every host-access ROOT exited. Source and public samples were copied to a disposable, network-disabled container, rebuilt with `make -B -C /app/src`, then tested by the pinned verifier. The container was removed. The verifier-copied source hash matches the frozen candidate.
- Raw result: 2/6 public, 5/37 hidden, 7/43 overall; `partial_score: 0.163`; binary reward `0`. Makefile and libzstd anti-cheat checks passed.
- ROOT exited early after 531.375 seconds (8m51.375s) despite a 90-minute watchdog and unfinished task. Its fresh Priority/high validator found a real frame-content-size endian defect, which ROOT corrected and retested, but major decoder paths remained incomplete.
- Exact ROOT-plus-worker usage: 4,153,752 input tokens (3,977,216 cached) and 38,686 output; 4,192,438 total, or 215,222 uncached input plus output. Zero unknown invocations; both actual invocations were Terra/high/Priority.

This is the original early-finish result, not the separately labeled retry. Do not normalize the raw reward against the imperfect local oracle.
