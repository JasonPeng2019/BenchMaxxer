# Token ledger implementation contract

1. **Evidence and identity.** Capture the ROOT/raw `codex exec --json` stream in a
   unique run directory. Discover each native harness worker attempt from its
   `invocation.json`, `controller.attempts.jsonl`, and separate provider transcript.
   Identify a process by task run ID, lane run ID, and attempt number. Retain role,
   parent, effective launch configuration, timing, exit status, and source hashes.
2. **Counting.** Read only top-level `turn.completed.usage`; select the final
   completed event in each process transcript. Use provider `total_tokens` when
   present, otherwise derive `input_tokens + output_tokens`. Cached input and
   reasoning output are components, never additional tokens. Because Codex's
   JSON stream reports cumulative *session* usage, subtract the previous
   attempt's final total when a process resumes the same thread. Reject a
   decreasing cumulative total; deduplicate exact transcript replays.
3. **Accounting and archive.** A read-only snapshot reports known consumption
   and incomplete processes. Reportable runs are uncapped by explicit user
   choice: no native token gate is installed. An optional diagnostic
   `--budget-tokens` retains the old launch gate for tests only. Finished
   evidence is copied once into a new per-task archive with hashes, a ledger,
   and aggregate usage. No background meter, extra agent, or replacement
   scheduler is added.
4. **Offline proof.** Fixture tests cover reported and derived totals, final
   terminal selection, cache/reasoning treatment, resumed session deltas,
   duplicate replay, malformed or missing usage, gate decisions, run-window
   attribution, and archive write-once behavior. The live Terra/max ROOT plus
   Terra/high worker preflight validated the provider fields and launch wiring.

The optional diagnostic gate can only act on usage already emitted by Codex.
It is not part of the uncapped reportable protocol.

For the selected ZSTD-decoder H-H run, override the historical examples below:
pass `--model gpt-5.6-terra --reasoning-effort high --watchdog-hours 10`
explicitly to the ROOT collector, and bootstrap every worker with Terra/high.
The upstream ZSTD task specifies a five-hour agent horizon; the user's local
harness treatment explicitly extends this to 10 hours of cumulative active
wall-clock time across planned interruptions. Docker File Sharing and the
exact lane bridge smoke passed; the user accepted the documented oracle risk.
The raw partial score must remain intact, with 0.767 as a separate local 100%
oracle-relative reference. A reportable launch still needs separate authority.
The ZSTD treatment is now deliberately interrupted: pass `--interrupted-run`
on the initial `run`, use `resume --task-file ... --prompt-file ...` after each
clean power-off pause, and inspect the shared ledger before finalization.
`INTERRUPTED_ZSTD_RUN.md` is the exact operator runbook. This is an active-time
10-hour harness pilot, not a continuous benchmark reproduction. Conditional
raw controls retain their five-hour continuous limit.

## Historical BioFabric/Find operator example (not the ZSTD launch command)

Run the ROOT through `collect_codex_usage.py run` with an explicit `--run-id`,
`--task`, `--arm harness`, `--cwd`, `--prompt-file`, `--model`,
`--reasoning-effort`, `--service-tier`, `--sandbox danger-full-access`,
`--watchdog-hours 15`, and `--harness-runtime <ROOT>/.harness-runtime`. Omit
`--budget-tokens`: this captures ROOT and discovers native worker transcripts
without limiting either role. The ROOT-only host access was explicitly
approved; workers use an elevated Windows `worker-isolated` profile with
host auth/verifier read denials. A raw control uses `--arm raw`, omits
`--harness-runtime`, and uses `--watchdog-hours 10`.

The run creates `<results-dir>/<run-id>/task.json`. Inspect current accounting
with `snapshot --task-file <task.json>`; the optional diagnostic `gate` exits 0
for headroom, 3 at its cap, and 2 for invalid evidence. After all processes exit,
use `finalize --task-file <task.json> --output <new-archive-directory>`.
The archive contains `ledger.json`, aggregate `usage.json`, a copy of the task
file, each process JSONL, and hashed source records. An existing archive path
is never overwritten. `self-test` runs only offline fixtures.

`--watchdog-hours` now enforces a wall-clock stop in the collector. On Windows,
the collector temporarily inhibits idle sleep while it is alive and restores
normal power behavior afterward. At expiry it stops the ROOT process tree and
asks the native harness to shut down detached worker lanes; it remains alive
while such lanes are running after ROOT exits. Offline tests cover expiry,
process termination, and the detached-lane case. A live multi-role native-harness
smoke has now validated the totals and detached-worker wait. A forced live
watchdog expiry has not been performed.

## 2026-09-25 multi-role preflight

The non-reportable `root-worker-elevated` run archived distinct Terra/max ROOT
and Terra/high worker JSONL files. ROOT used 36,275 derived tokens and the
worker 322,223, for 358,498 aggregate tokens with no ledger errors. The
worker completed a valid no-op result. Native Windows `elevated` sandboxing
was necessary for the worker's exact deny-read profile; `unelevated` refused
to enforce it. Older failed lanes in the same epoch are excluded by each
attempt's start time, preventing cross-run attribution.

## 2026-09-22 probe

A short `gpt-5.6-luna` Codex CLI child emitted 14,504 input tokens (11,008
cached), 21 output tokens (9 reasoning), and no `total_tokens`. The collector
derived 14,525 and the archived ledger matched the raw terminal event exactly
with no errors. This checks the CLI transcript path used by native harness
workers, but not the harness worker discovery path. An in-chat collaboration
subagent completed separately; that tool did not expose a Codex CLI JSONL or
per-agent usage record to this collector, so its tokens were not measurable by
this ledger.

A second read-only `gpt-5.6-luna` CLI probe on 2026-09-24 requested a
250-350 word response. Its terminal event reported 14,566 input tokens
(11,008 cached), 440 output tokens (26 reasoning), and no `total_tokens`.
The ledger derived exactly 15,006 with no errors. Both live probes agree
with their raw terminal events; neither exercised native harness worker
discovery.
