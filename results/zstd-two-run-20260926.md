# Concurrent ZSTD two-run pilot

Both counted ROOT processes started at 2026-09-26 18:24:30 UTC with continuous
90-minute watchdogs and no token caps. They share the pinned ZSTD image
`sha256:3a43d4f3658c4a21115c518937b692692e9e721d3b6e4a3205972917b8bc2e8a`,
the same 13-file task baseline exported from `c1c5a00cac9e58af70fb4289b9c0c49a67774f31`,
the same public-test bridge and sealed scoring rules. Concurrent execution on
one six-CPU, approximately 16-GiB Docker VM is a throughput choice and may
create resource contention; elapsed time is therefore not a clean isolated
latency comparison. These are matched 90-minute **pilots**, not five-hour
upstream-faithful trials.

| Arm | Counted run ID | ROOT | Fresh setup commit | Harness clone |
| --- | --- | --- | --- | --- |
| Lean | `zstd-lean-h-h-90m-20260926-03` | Terra/high/Priority | `bd3888c31d68b940069a926d3cca44e0fbb6617a` | `harness-zstd-lean-90m` |
| Targeted | `zstd-targeted-xh-90m-20260926-03` | Terra/xhigh/Priority | `2d7272e4e40b82fd1228742aec1e4fbad0575b96` | `harness-zstd-validated-90m` |

Both prompts and `AGENTS.md` require the native harness and a fresh validation
worker after an integrated candidate has public-test evidence, followed by
ROOT disposition and a deterministic retest. Run 2 additionally uses the
on-demand `scripts/zstd_progress_record.py` fact record and eligible high/max
role routing. Only harness operational skills are installed; neither task
checkout contains the project specification/topology suite.

The initial `-01` launch IDs in each arm exited before Codex started due to
Windows `.cmd` executable resolution. The `-02` ROOTs started but native worker
launches failed because Windows cannot directly launch the npm `.cmd` shim via
the suspended-process worker adapter. These four launch IDs are retained as
invalid infrastructure evidence, not counted trials. The collector and both
harness adapters were repaired and offline-tested before these `-03` starts.
A separate non-benchmark native smoke successfully launched the packaged
`codex.exe` as a Priority Terra/high worker, recorded provider tokens, and
closed its lane. Both counted arms use harness commit
`e8f2446ef5afe13ed155e30546f1620ab80eae02` for the Windows launcher fix.

Operator acceptance after ROOT exits: verify one actual late validation lane,
its independent finding, ROOT's disposition and public retest, closed native
runtime, complete ROOT/worker token usage, frozen source, then score in
separate disposable no-network verifier containers. Preserve raw benchmark
partial score and binary reward without oracle normalization.

## Lean retry (separate from the original pair)

The original lean `-03` ROOT exited successfully after 531.375 seconds with a
2/6 public partial candidate. Its Priority/high native validator found a real
frame-content-size endian bug, which ROOT fixed and retested, but ROOT froze
with four public failures and major RFC work still missing. Keep that trial as
an early-finish result. At the user's explicit request, a **labeled retry**
`zstd-lean-retry-h-h-90m-20260926-01` started at 18:37:48 UTC in isolated
`root_runs/zstd-decoder-lean-retry-90m`, with a separately configured harness
`harness-zstd-lean-retry-90m`. Its source history stops at the pre-run scaffold;
the first candidate commit is not present, and no run artifacts were copied.
Setup commit: `b1187017a09e8fe149f67457ddc4f07d6b85d17f`.

The retry keeps Terra/high/Priority for ROOT and every worker, the same pinned
task image, 90-minute continuous watchdog, no token cap, and required native
validation. The only deliberate prompt change is stronger time use: do not
finish before minute 80 while any public case or RFC coverage is incomplete;
validate the strongest integrated candidate around minute 65-75. This retry
is not interchangeable with the originally matched lean arm and will overlap
only part of the targeted arm's runtime.

## Finished arm evidence (sealed score pending)

The targeted `-03` arm exited at 19:10:41 UTC after 2,770.875 seconds
(46m10.875s), without watchdog expiry. ROOT froze clean source commit
`6ca8a8d8f8b8d5107e63e736779d75b919ae3021`; the C source SHA-256 is
`220bd20594a4569e8699da9b3fb23fc4d4ca44c148aafc4c55d0465b66acbfa4`.
Final pinned public bridge output is `progress/public-007.txt` (SHA-256
`c7bd9be32d58b0d955b90f0ac297abbe416b2efc898cb8667ea562b2bbce54c2`),
6/6. Native runtime is CLOSED. Its exact ROOT-plus-three-worker ledger has
31,510,299 input tokens (30,714,368 cached) and 209,854 output tokens:
31,720,153 total, or 1,005,785 uncached input plus output. All four
invocations actually launched Terra on Priority, with ROOT xhigh, two max
workers, and one high validation worker; usage is complete with zero unknowns.
Two coding workers could not commit from their isolated worktrees because Git
metadata was outside their permitted write scope. ROOT rejected their
procedural lane outcomes, independently integrated and tested their code.
The validator's proposed reverse-bit fix was rejected after it regressed a
public case; the final Huffman-FSE repair passed all six public cases. Do not
interpret that public result as the sealed verifier score.

The original lean `-03` arm's exact ROOT-plus-one-worker ledger has 4,153,752
input tokens (3,977,216 cached) and 38,686 output tokens: 4,192,438 total,
or 215,222 uncached input plus output. It remains an early-finish 2/6 trial;
its sealed score was delayed until all host-access ROOTs exited.

## Final frozen results

Every scoring container used the same pinned image and verifier, had networking
disabled, was removed afterward, and produced a source artifact matching the
frozen repo's SHA-256. Every native runtime closed. The verifier's Makefile
and libzstd anti-cheat checks passed for each candidate.

| Arm | Elapsed | Public | Hidden | Raw total / partial | Reward | Total tokens | Uncached input + output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Original lean `-03` | 8m51s | 2/6 | 5/37 | 7/43 / 0.163 | 0 | 4,192,438 | 215,222 |
| Labeled lean retry | 40m08s | 5/6 | 25/37 | 30/43 / 0.698 | 0 | 29,139,355 | 733,339 |
| Targeted `-03` | 46m11s | 6/6 | 27/37 | 33/43 / 0.767 | 0 | 31,720,153 | 1,005,785 |

The targeted arm matches the known pinned local oracle's 33/43 aggregate
(6 public and 27 hidden; raw reward 0), but its metrics do not prove identical
hidden-case outcomes. Do not call 33/43 a benchmark pass or change the raw
partial/reward. The original lean and targeted arms were simultaneously
launched matched pilots, but the original lean arm voluntarily ended early.
The user-requested lean retry used a stronger prompt and began later, so it is
not a second simultaneous matched arm. It too voluntarily ended before the
90-minute deadline despite explicit instructions to continue while incomplete.
Those early stops and the isolated workers' Git-index permissions are material
interpretation caveats. Detailed sealed evidence is in each run's
`sealed-score/SCORING.md`, `verifier/metrics.json`, `verifier/reward.txt`, and
source artifact; exact invocation ledgers are in sibling `-ledger/` folders.
