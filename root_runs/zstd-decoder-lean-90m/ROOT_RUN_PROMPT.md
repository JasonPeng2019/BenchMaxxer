# Authorized ZSTD decoder run: lean optional-use harness

Run ID: `zstd-lean-h-h-90m-20260926-01`. You are a Terra/high/priority ROOT
coder. The operator starts this run with a hard, continuous **90-minute
wall-clock limit** and no token cap. This is a pilot, not a five-hour matched
SWE-Marathon run. Work on the entire decoder, not a convenient partial slice.
Continue improving and testing until there is credible full-feature evidence
or the deadline forces a truthful partial result. Target shutdown by minute
87 to leave watchdog margin.

Implement the from-scratch C99 Zstandard decoder described by the bundled
RFC 8878. The required CLI is
`/app/src/zstd_decompress <input.zst> <output> [dictionary]` with byte-identical
output. Cover normal frame headers and content sizes, skippable and
concatenated frames, checksums, raw/RLE/compressed blocks, raw/RLE/Huffman
and treeless literals, one- and four-stream Huffman, FSE predefined/RLE/custom
and repeat tables, sequences with repeat offsets and overlapping matches,
and trained-dictionary frames with preloaded entropy and offset state.

Keep a short task contract for yourself and start coding promptly. The
native harness at `../../harness-lean-zstd` is available if useful. You may
use lanes as bounded coding workers, fresh reviewers, or test-design helpers;
you decide whether and when to launch them. There is **no mandatory skill
suite**, no required SPEC/PLAN/goal artifact, no forced lane count, and no
formal stall reviewer in this arm. If you use a task-specific skill, identify
it in the final report. Run deterministic build and public-test commands
yourself, without commissioning a model just to execute them.

The harness installation is separate and its `harness-config.json` must
select this exact ROOT workspace. Read its `AGENTS.md`, `QUICK_RULES.md`, and
`QUICK_START.md` before any live harness use. From that harness directory,
run `python -m orchestrator_harness.operator_launch harness setup` before
bootstrapping. Any Codex lane must explicitly pass `--model gpt-5.6-terra`,
`--provider-option reasoning_effort=high`, and
`--provider-option service_tier=priority`; check the signed invocation,
generated `worker-isolated` sandbox, and native `scan --no-write` before
launch. ROOT owns integration and review; never treat worker self-report as
acceptance. Retire lanes and shut down the native runtime before finishing.
After `resume-lane`, explicitly call `lane launch` and verify the new process
identity; `launch_pending: true` means no provider has started.

The pinned no-network public-test bridge is
`python ../../scripts/docker_task_workspace_copy.py --task zstd-decoder
--workspace-name zstd-decoder-lean-90m --worktree <this-ROOT-or-exact-lane-worktree>
-- <command>` from this workspace. It copies only task-visible files from
this exact ROOT checkout or one of its exact native lanes into a short-lived
container at `/app`; it does not mount another run or copy runtime state.
Build with `make -C /app/src`. Run the six public samples by feeding
`/app/test.sh` through `tr -d '\r'` into Bash, leaving the protected script
unchanged. You can run deterministic checks against your ROOT checkout
without launching any model worker. Do not alter the bridge yourself.

Use only this task's visible code, RFC, samples, and public tests. No network,
package manager, container interpreter, libzstd linking/dlopen/subprocess,
copied decompressor, edits to protected files, hidden verifier, or other run
artifacts. Report the final source revision, exact public checks and failures,
any optional harness roles or skills used, incomplete features, elapsed time,
and native runtime state. The operator will run the sealed verifier after
you stop.
