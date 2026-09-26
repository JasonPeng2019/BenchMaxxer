# Interrupted ZSTD pilot: operator runbook

This is an intentionally **non-standard local pilot**, not a continuous or
official SWE-Marathon trial. The user expects multiple planned machine
power-offs. Preserve one task run ID, one Codex ROOT session, the same pinned
task/image/model, and all native worker evidence across segments. There is no
token cap. The harness safety limit is **10 hours of cumulative active collector time**;
powered-off gaps are excluded and disclosed. Never describe this as a
continuous five-hour attempt or compare its wall time directly with the
published trials. The upstream task's own timeout remains five hours; this
extended harness run is intentionally non-standard. Conditional raw controls
retain their five-hour continuous safety limit.

## Initial launch (only after separate user authorization)

From the outer repository, use an unused `zstd-h-h-10-*` ID:

```powershell
python scripts/collect_codex_usage.py run `
  --run-id zstd-h-h-10-<unique-id> --task zstd-decoder --arm harness `
  --cwd root_runs/zstd-decoder `
  --prompt-file root_runs/zstd-decoder/ROOT_RUN_PROMPT.md `
  --results-dir results --model gpt-5.6-terra `
  --reasoning-effort high --service-tier priority `
  --sandbox danger-full-access --watchdog-hours 10 `
  --harness-runtime root_runs/zstd-decoder/.harness-runtime `
  --interrupted-run
```

The collector writes `results/<run-id>/task.json`, the first ROOT JSONL, and
its immutable launch/final manifests. ROOT uses the native harness directly;
the collector does not start or schedule worker lanes.

## Planned power-off pause

1. Tell the operator **before** shutting down. The operator places
   `root_runs/zstd-decoder/OPERATOR_PAUSE_REQUEST.md` with the request time and
   reason. ROOT checks for it before new lanes or major phases. This is a
   prompting signal, not a hard preemption or a guarantee of immediate pause.
2. Wait for ROOT to finish/settle active native lanes, update
   `RUN_CHECKPOINT.md`, shut down the harness with cleanup proof, and exit its
   Codex turn with `PAUSE_READY`. Do not power off while the collector or a
   worker is still active.
3. Confirm the collector wrote the segment's `manifest.json`, the native
   runtime is `CLOSED`, the monitor is `STOPPED`, no lane is active, and
   `snapshot --task-file results/<run-id>/task.json` has no errors. Record
   actual wall stop time. Only then turn off the machine.

If ROOT cannot reach a clean boundary, do **not** pretend the pause was clean.
An abrupt outage can leave a missing final manifest, live/ambiguous lane
metadata, or unreported in-flight tokens. The resume command fails closed in
those cases; a separate evidence review is required before any continuation
could be counted. Do not force-stop by broad process name or erase worktrees.

## Continue after reboot

Verify Docker is running, the pinned image identity and host path are intact,
and the prior segment is sealed. Remove the exact pause-request file only
after its checkpoint is captured. The collector refuses a resume unless the
task was marked `planned_resume`, the prior ROOT transcript contains a native
session ID and countable terminal usage, and the harness runtime is `CLOSED`.
If a terminated worker lacks terminal usage after an external failure, keep
its transcript and native records untouched. A specific `usage-gaps.json`
receipt may acknowledge the unknown amount only when its transcript hash
matches and the original epoch is closed with that lane retired. The ledger
then reports known tokens as a **lower bound**, not an exact aggregate. This
does not waive a live worker, missing ROOT usage, or a changed transcript.
Then use:

```powershell
python scripts/collect_codex_usage.py resume `
  --task-file results/<run-id>/task.json `
  --prompt-file root_runs/zstd-decoder/ROOT_RESUME_PROMPT.md
```

This executes `codex exec resume` for the saved session with the original
Terra/high, priority, ROOT host-access settings. It writes a new numbered
`segments/0002`, `0003`, etc. under the **same** task run. The active-time
watchdog receives only the unused portion of the original 10 hours. ROOT
reopens a fresh native harness epoch and continues from `goal.md`, `PLAN.md`,
and `RUN_CHECKPOINT.md`; it must not create a fresh task trial.

If a ROOT turn instead ends with terminal, countable usage while the native
epoch remains **OPEN**, do not pretend it was a clean power-off pause. A
same-thread continuation may use `resume --continue-open-runtime` only when
the collector finds no in-flight usage and every non-retired lane is
`review_pending` with controller/provider exited and cleanup proven. This
keeps its isolated worktree and epoch intact; the continuation prompt must
explicitly say not to run fresh `harness setup`. The flag does not waive a
running worker or ambiguous cleanup state.

## Final evidence and interpretation

After the last segment and all worker processes finish, inspect `snapshot`,
then call `finalize --task-file results/<run-id>/task.json --output
results/<run-id>-ledger`. The ledger includes all ROOT segments and native
worker attempts, charging only cumulative-session deltas. Report raw verifier
reward/partial, the separate oracle-relative partial (`raw_partial / 0.767`),
aggregate tokens, ROOT resume count, active elapsed time, paused wall time,
and any recovery gaps. If `unknown_usage_invocations` is nonzero, report that
count and `token_total_is_exact = false`; do not use the lower bound for
token-matched comparisons. A valid local score after clean pauses is meaningful
partial evidence of implementation ability, **not** a faithful SWE-Marathon
score or a controlled speed comparison. If token/cleanup evidence is incomplete,
label it approximate or invalid; never silently promote it to a clean result.
