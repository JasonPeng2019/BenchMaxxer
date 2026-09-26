# Agent TODO — Local SWE-Marathon H-MH Pilot

This is the original checklist for the local two-task pilot. A BioFabric run
was later authorized and cancelled without scoring; the current decision below
supersedes its old model pairing and task order.

## Current decision after the cancelled BioFabric attempt

The H-MH model pairing and task order below are historical. The selected
`zstd-decoder` Terra/high ROOT-plus-worker pilot has now run and been scored
locally as a deliberately interrupted, non-standard trial. Its raw partial
was 0.535 (23/43), binary reward 0; see `RUN_MANIFEST.md`. The cancelled
BioFabric runtime remains quarantined in `SHUTTING_DOWN`.

- [x] Create and commit a clean ZSTD agent-visible baseline, clone a fresh
  ROOT workspace, copy the current skill suite, and validate the workspace.
- [x] Set explicit high effort in ROOT config and worker bootstrap; run native
  harness setup and bootstrap one unlaunched, isolated preflight lane.
- [x] Build and pin the ZSTD image; add the one-mount/no-network Docker bridge
  entry and pass its offline tests.
- [x] Add `root_runs/zstd-decoder` to Docker Desktop File Sharing, apply/restart,
  then pass the exact lane bridge smoke (`ZSTD_BRIDGE_SMOKE_OK`).
- [x] Proceed with the documented oracle risk: supplied oracle reward `0`,
  `partial_score 0.767`, 33/43 tests (not 33/34). Use 0.767 as the local 100%
  reference while preserving raw scores; do not call the image oracle-validated.
- [x] Close the first unlaunched preflight lane/runtime; the runtime is `CLOSED`
  and its monitor `STOPPED` after lane force-stop and shutdown.
- [x] Use a fresh no-model preflight epoch to pass the exact lane bridge
  smoke, then close it; runtime `CLOSED`, monitor `STOPPED`.
- [x] Freeze the ZSTD H-H-10 protocol and conditional five-hour raw controls in
  `RUN_MANIFEST.md`, using raw verifier scores for triggers.
- [x] Prepare the deliberately interrupted H-H-10 treatment: same native ROOT
  session and task ID across clean segments, cumulative active-time watchdog,
  pause checkpoint/runbook, and offline-tested aggregate ROOT token ledger.
- [x] Record a local hash snapshot of the amended collector, Docker bridge,
  prompts, and runbook in `RUN_MANIFEST.md`. Recheck hashes and record the
  outer Git HEAD/dirty state immediately before launch; do not silently treat
  the unrelated dirty worktree as a clean commit.
- [x] User authorized the ZSTD H-H-10 launch on 2026-09-25. Pass
  `--reasoning-effort high` and `--watchdog-hours 10` to the ROOT collector;
  verify every worker invocation also resolves to high. Keep token use uncapped.
- [x] Resume and finish the same ZSTD run, freeze its partial decoder, run the
  pinned operator-only verifier, and finalize the cumulative ROOT-plus-worker
  ledger. Raw C-X is not triggered by the valid 0.535 partial and reward 0.

## Hard gate

- [x] Run only the authorized non-reportable Codex preflights while completing
  integration. Do not start H-MH-15, C-X-10, or C-M-10 without separate
  reportable-run authorization.
- [ ] Do not run raw Codex first. The first reportable runs are H-MH-15; C-X-10
  and C-M-10 are conditional follow-ups only.
- [ ] Keep all Codex credentials on the host. Do not copy authentication files,
  tokens, the harness source, or the workflow-suite source into a task workspace,
  Docker container, verifier artifact, or benchmark checkout.

## 1. Establish the ROOT workspace

- [x] Prepare task-specific host-side ROOT workspaces under `root_runs/`: one
  each for `biofabric-rust-rewrite` and `find-network-alignments`. Each is the
  Git repository from which that task's harness lane worktrees will be created.
- [x] Preserve `Codex_Claude_Setup` as the source submodule. Merge its runtime
  files into the ROOT workspace rather than moving the submodule itself:
  `.agent/`, `.agents/`, `.claude/`, `.codex/`, `AGENTS.md`, and `CLAUDE.md`.
  Include `workspace-aid/` as well: it is documentation, but the supplied
  workspace validator requires its README as part of a complete import.
- [x] Merge existing ROOT-workspace instructions/configuration deliberately; do
  not overwrite project-specific rules blindly.
- [x] Treat `.agents/skills/` as the editable source and `.claude/skills/` as the
  generated mirror. The source/mirror pair was copied together and must be
  resynchronized with the supplied helper after any source change; do not
  hand-edit the mirror.
- [x] Change `harness-single/harness-config.json` from its stale external
  `Orchestrator-Harness-2` path to the first ROOT-workspace path, BioFabric.
  Switch it to Find Network Alignments only between closed runtimes.
- [x] Run `harness setup` for each prepared ROOT workspace. Both preserved the
  Terra/max ROOT config and merged harness-owned hooks and operational skills.
  Both idle runtimes were then shut down; re-run setup for the selected task
  before a live epoch.

## 2. Make the ROOT workflow explicit

- [x] Update the ROOT prompt/instructions to require the actual skill names:
  `project-specification` followed by `project-topology`. (`project-spec` in
  earlier notes is not the installed skill name; add an intentional alias only
  if one is genuinely required.)
- [x] Require those skills to create the project specification and implementation
  plan before execution.
- [x] After the artifacts are complete, require the ROOT prompt and `AGENTS.md`
  to re-read `goal.md` and use its `## Goal text` as the soft execution directive
  for the approved plan, with explicit scope, checkpoints, validation commands,
  and a verifiable completion condition. This is a prompting guardrail, not
  persisted Codex Goal state. Do not use `/plan` as the substitute workflow.
- [x] Keep the native harness as the execution mechanism. Do not add a parallel
  runner, scheduler, retry controller, collaboration relay, or AI watcher.

## 3. Prove model, effort, and isolation settings

- [x] Configure and retain proof that ROOT runs `gpt-5.6-terra` at `max`.
  The shipped Codex ROOT payload currently defaults to `gpt-5.4` / `medium`, so
  the experiment setting must not rely on that payload default.
- [x] Configure every Codex worker lane as `gpt-5.6-terra` at `high`, with an
  explicit service tier. Preserve the exact resolved launch configuration for
  each worker; do not allow workers to inherit ROOT/max silently.
- [x] Use ROOT-only `danger-full-access` with explicit user approval. The
  workspace sandbox denied `.git` writes and blocked native bootstrap. The
  non-reportable ROOT/max preflight then launched a worker successfully.
- [x] Enforce a worker-only `worker-isolated` permission profile with exact
  read denials for host Codex auth, benchmark checkout/verifier, harness source,
  workflow-suite source, and results. The native
  Windows `elevated` sandbox is explicitly selected; `unelevated` refused this
  deny-read profile. A generated lane profile probe showed the worker task
  readable, auth/verifier unreadable, and Docker daemon denied. The actual
  elevated Codex worker then completed the no-op lane under this launch vector.
  The earlier `:workspace` profile was insufficient: it allowed auth and
  verifier reads until the explicit deny profile was installed. A sibling-ROOT
  deny was removed after its inherited Windows ACL blocked a later sandbox in
  that task; the two exact root ACL entries from preflight were cleared, and
  both roots now have no explicit sandbox-user deny ACEs.
- [ ] Keep the role structure clear: ROOT is the host-side coordinator; workers
  edit separate clean worktrees derived from the selected task templates; Docker
  builds, tests, and verifies only the mounted task workspace.

## 4. Complete token accounting without replacing the harness

- [x] Finish `scripts/collect_codex_usage.py` as an offline-tested telemetry
  component with ROOT capture and native harness worker discovery.
- [x] Preserve one archived JSONL, manifest, role, parent/worker relationship,
  effective model/effort/tier, start/end time, and exit status for every unique
  ROOT and worker invocation. Final artifacts are written once with hashes.
- [x] Extract each invocation's final cumulative `turn.completed` usage record;
  use provider-reported `total_tokens` when present, otherwise label
  `input_tokens + output_tokens` as derived. Keep cached input separate because
  it is a subset of input, not an additional total.
- [x] Deduplicate exact replayed transcripts, subtract prior same-thread
  cumulative usage on resume, and aggregate unique charged invocation records.
- [x] Make the token ceiling optional. The user explicitly chose **no token
  cap** for reportable runs: omit `--budget-tokens`; the native launch gate is
  not installed, while ROOT/worker usage is still archived and compared.
  The cap code remains available only for diagnostic experiments.
- [x] Pass offline tests for reported totals, derived totals, replay/resume,
  missing or malformed usage, terminal selection, launch-gate decisions, and
  write-once finalization.

## 5. Finish operational and protocol prerequisites

- [x] Recheck Docker Desktop/Engine availability and capacity before a smoke:
  on 2026-09-25 the Linux Engine had 6 CPUs and 16.64 GiB RAM. Docker Desktop
  was configured for a 40 GiB disk; after both pinned task images were built,
  the container filesystem had 24.9 GiB free. A no-network container's cgroup
  enforced the intended 4-CPU and 16-GiB limits. Recheck before each live run.
- [ ] Keep the host on AC power, prevent sleep/hibernate/sign-out/reboot during
  runs, retain at least 100 GB free disk, and avoid competing CPU/disk-heavy work.
  On 2026-09-25, C: had 383.6 GiB free, but the active Balanced plan's AC
  sleep-after setting was 600 seconds. The collector now temporarily inhibits
  Windows idle sleep during a run and releases the request afterward; this was
  verified locally. No machine-wide power setting was changed. Confirm AC and
  avoid reboot/sign-out immediately before a reportable run.
- [x] Reconfirm `codex login status` uses the ChatGPT subscription and record
  `codex --version`; do not introduce an API key for this pilot.
  Last checked 2026-09-25: ChatGPT login, `codex-cli 0.156.1`; recheck before
  any provider run.
- [x] Rebuild and retain both task images from the pinned SWE-Marathon
  `f34867643bf07aec5208a861e667e01df0942099` remote-Git context rather
  than the Windows checkout, preserving the LF-byte constraint. Current local
  IDs: BioFabric `sha256:7371c89d8cda34360732ef8401ab301c78b72484dace66d4151e180d7fcd061c`;
  Find `sha256:848b52ed2e1bae448d683769088b7c71bdfd782dce9b1f39578d766165bfa046`.
  Both images started successfully in no-network, resource-limited containers.
  These replace the unavailable older local image IDs recorded in `USER_TODO.md`;
  re-freeze IDs/digests in the final protocol manifest before a reportable run.
- [x] Record the user's decision to proceed with Find Network Alignments under
  a documented oracle-reliability risk, without requiring a passing local
  oracle first. This does **not** make the image oracle-validated or authorize
  a reportable run. BioFabric's rebuilt-image oracle
  passed all 450 tests / reward 1. Find's first rebuilt-image oracle returned
  reward 0 / partial 0.976694 (primary S3 0.315106 vs target 0.32); a
  sequential repeat returned reward 0 / primary S3 0.318729. Both yeast
  alignments passed and the verifier itself ran. The 600-second parallel
  search is timing-sensitive; an older-image oracle had passed once. Do not
  change the pinned task, oracle, or thresholds to hide this variability. In
  reporting, preserve both failures and the older pass; do not cherry-pick a
  passing retry or describe the rebuilt image as reference-solution validated.
- [x] Complete the agent-facing host-to-Docker bridge. The operator-only
  `scripts/docker_task_workspace.py` pins each image, validates an exact task
  lane worktree, and uses one bind mount, no network, 4 CPUs, and 16 GiB RAM.
  Unit tests and live no-op container smokes passed for both tasks: task files
  were visible while credentials, `/tests/test.sh`, and `/solution/solve.sh`
  were absent. The separate operator-side oracle/verifier check is never
  exposed to a worker.
- [x] Implement or explicitly configure the 15-hour H-MH and 10-hour raw
  watchdogs before a paid task. The collector now enforces `--watchdog-hours`,
  inhibits Windows idle sleep during the run, stops a process tree at expiry,
  and requests native harness shutdown for detached lanes. Nineteen offline
  ledger/watchdog tests pass; a live ROOT-plus-worker smoke proved the timer
  stays alive through a detached worker. Forced live expiry has not been tried.
- [x] Pin the pilot's outer source snapshot in a local, unpushed commit,
  including `.gitmodules`, current harness/workflow gitlinks, the collector,
  Docker bridge, token ledger, `RUN_MANIFEST.md`, and this checklist. The
  benchmark checkout, task workspaces, personal notes, and result archives
  remain local and outside the outer Git snapshot; task/workspace identities
  and overlay hashes are frozen in `RUN_MANIFEST.md`.

## 6. Validate before paid work

- [x] Run the offline ledger/parser and native launch-gate tests.
- [ ] Account for the unrelated upstream live-matrix test gap. A full harness
  discovery ran 326 tests: 8 failed/errored because its M09 test module calls
  an absent, untracked `.agent-workspace/execute-matrix.py` entrypoint.
  The 55 focused adapter/materialization tests, 19 ledger/watchdog tests, and
  2 Docker-bridge tests pass. Do not report the full harness suite as green;
  decide whether this M09-only entrypoint is required for the pilot or fix it
  separately before requiring a whole-repo green run.
- [x] After explicit authorization, run one short non-reportable host CLI trace
  with nonzero reasoning and validate the subscription JSONL field relationship.
  The 2026-09-22 Luna probe used ChatGPT login and reported 14,504 input,
  11,008 cached input, 21 output, and 9 reasoning output tokens; no reported
  total was present, so the ledger correctly derived 14,525 input + output.
- [x] After explicit authorization, run one non-reportable multi-role harness
  no-op. Verify ROOT Terra/max, worker Terra/high, distinct nonzero per-process
  usage, stable aggregation under replay, preserved role/configuration evidence,
  and absence of credentials from Docker/artifacts. The successful
  `root-worker-elevated` rehearsal recorded ROOT/max 36,275 and worker/high
  322,223 derived tokens, 358,498 total, with no ledger errors. The worker
  wrote a valid preflight RESULT.json and no benchmark implementation. The
  archive is in `results/preflight_smoke_20260925/root-worker-elevated-archive`.
  Earlier failed attempts are retained separately and excluded by run time.
- [ ] Resolve any failure in this validation before interpreting or launching an
  H-MH result.

## 7. Freeze the pilot protocol before H-MH-15

- [x] Record the user's uncapped-run choice: no shared **B**; compare measured
  aggregate usage ex post. Never describe H-MH/C-X as token-budget matched.
- [x] Keep C-X-10 conditional, as confirmed by the user: run it for a task
  only if H-MH passes or its partial score falls outside the published raw
  range below. An invalid token ledger is a run-integrity failure to repair,
  not a reason to launch raw as a substitute.
- [x] Pre-register the C-M-10 trigger: C-X has a valid, non-time-censored
  result with at most 80% of H-MH's aggregate tokens, and is materially worse
  on verifier quality (H-MH pass versus C-X fail, or H-MH partial minus C-X
  partial at least 0.05). See `RUN_MANIFEST.md` for the complete rule.
- [x] Record that the 15-hour H-MH and 10-hour raw watchdogs are safety
  ceilings, not matched compute budgets. Expiration before a pass is
  time-censoring; never describe an uncapped comparison as token-cap matched.
- [x] Freeze the published raw Terra/xhigh reference ranges from the working
  notes for the conditional C-X trigger:
  - BioFabric: partial score 0.963–0.980.
  - Find Network Alignments: partial score 0.551–0.784.
- [x] Ensure every report describes any uncapped local H-MH/C-X pair
  as a small-N system-level hierarchy-plus-allocation comparison—not a causal
  harness-only result. H-MH alone is only an external-reference case study.

## 8. Run order after separate authorization

1. Recheck Docker capacity, task image availability, task hashes, and the shipped
   oracle/verifier at zero model cost.
2. Complete the two authorized non-reportable validation checks above.
3. Freeze the manifest fields, uncapped token-accounting choice, triggers,
   thresholds, image/task identities,
   and public reference values.
4. Run one H-MH-15 treatment on `biofabric-rust-rewrite` and one on
   `find-network-alignments`, each in a new clean task workspace.
5. Run C-X-10 for a task only if its pre-registered pass/out-of-range trigger
   fires.
6. Run C-M-10 only if its separate pre-registered quality-and-token trigger fires.

## Later, out of scope for this pilot

- [ ] Official Harbor/Modal SWE-Marathon reproduction.
- [ ] LHTB setup, including Git LFS, hardened verifier configuration, Harbor's
  `continue_until_timeout` support, and the formal native/3x capability tracks.
- [ ] A same-model, same-effort, same-budget paired study that can isolate a
  causal harness effect from the hierarchy/effort-allocation system effect.
