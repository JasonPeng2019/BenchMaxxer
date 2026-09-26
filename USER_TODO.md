# User TODO — local SWE-Marathon pilot

> 2026-09-25 update: this file preserves earlier planning notes. The user has
> since chosen uncapped runs with aggregate token measurement. `AGENT_TODO.md`
> is the current checklist; references to shared token ceiling B below are
> superseded.

> Historical setup notes. For the current implementation state and remaining
> gates, use `AGENT_TODO.md` and `root_runs/README.md`. In particular, the
> multi-process token ledger is now offline-tested, the ROOT workflow uses
> `project-specification` and `project-topology` with a soft `goal.md` directive
> rather than CLI `/goal`, and both ROOT workspaces have passed harness setup.
> Docker was rechecked on 2026-09-25: both task images were rebuilt and started
> offline, with 24.9 GiB free on the 40 GiB Docker disk afterward. The older
> image IDs below are historical and no longer present on this Engine; use the
> new IDs in `AGENT_TODO.md`. BioFabric's ROOT mount passes; Find's exact ROOT
> directory was subsequently shared in Docker Desktop File Sharing and its
> read-only, no-network mount now passes too.

This is the setup checklist for the agreed first experiment: two **harness + skill-suite**
runs on SWE-Marathon (`biofabric-rust-rewrite` and `find-network-alignments`). Each treatment
run is H-MH-15: `gpt-5.6-terra` at `max` for ROOT and `high` for every worker, with a
15-hour machine watchdog and one shared, aggregate per-task token ceiling **B**. The primary
conditional raw-Codex comparison is C-X-10: one raw `gpt-5.6-terra` / `xhigh` agent with the
same B and a 10-hour watchdog. C-M-10, raw Terra/max, is only a follow-up effort ablation.
Do **not** run either raw arm first.

## Already ready

- [~] Docker Desktop was working on its alternate VM backend. Recheck that the Engine responds
  before a smoke or a run; the latest capacity query could not reach the Docker named pipe.
- [x] This is a CPU-only study. A GPU is not required.
- [x] An OpenAI API key, Modal account, and Harbor are **not** required for this local pilot.
- [x] The Codex CLI stays on the Windows host and uses the ChatGPT subscription. It must not
  be installed, authenticated, or given host-Docker control inside a task container.
- [x] The benchmark checkout location is this repository's `benchmarks\\swe-marathon` folder.
- [x] Codex is currently authenticated through ChatGPT; Docker, Git, and Python are available.
- [x] SWE-Marathon is checked out cleanly at `f34867643bf07aec5208a861e667e01df0942099`.
- [x] A read-only, ephemeral Codex telemetry smoke check completed with a Terra/xhigh
  invocation and no tool calls. Its terminal JSONL usage was nonzero:
  `input_tokens=15455`, `cached_input_tokens=6912`, and `output_tokens=7`.
  This CLI event did **not** include `total_tokens`, so a completed collector must label any
  `input + output` fallback as derived and must not add cached input a second time.
  It validates subscription telemetry only; it does not yet validate H-MH role settings or
  multi-process aggregation.
- [x] The selected task environments were built from Docker's remote pinned-Git context, which
  preserves the benchmark's LF bytes. Docker VMM shares only this repository's `benchmarks`
  directory; it does not share the Codex credential location.
- [x] Oracle/verifier validation passed for both selected tasks in no-network containers:
  `find-network-alignments` earned reward `1` / partial score `1.0`; BioFabric earned reward
  `1` with 450 passing tests. Their retained setup artifacts are under
  `benchmarks/artifacts/setup/`.

### Frozen local setup identities

| Task | Pinned Git tree | Local image ID |
| --- | --- | --- |
| `biofabric-rust-rewrite` | `a13b1c68afbec2d8ed47815be359e72d2d49f70e` | `sha256:85c72483db17af4e147076e9d100c546a359e98ac77ed8cbac3a5578fb4e5515` |
| `find-network-alignments` | `a31ea5552a3e3404425594cfb2e01627953091ee` | `sha256:189b4a87742e7439be0981578b5166ee513d09930921f4b2e9c5b41e760aef0d` |

### Harness-ready task baselines

The image-extracted, agent-visible skeletons are separate clean Git repositories. They contain
neither a verifier secret nor a Codex credential and provide the future harness worktree bases:

| Task | Template path | Baseline commit |
| --- | --- | --- |
| `biofabric-rust-rewrite` | `benchmarks/task-templates/biofabric-rust-rewrite` | `934570e2c644a262a356314a61cf04bc9d2f99e5` |
| `find-network-alignments` | `benchmarks/task-templates/find-network-alignments` | `885b78c9b82f198d85f304bc243fd475f89d05e0` |

Two runner constraints are established:

1. Docker VMM needs the explicit, narrowly scoped `benchmarks` host-folder share already
   configured above; the agent itself must still have no Docker-daemon access.
2. Build task images from Docker's pinned remote-Git context (the `-lf` image tags above), not
   from the Windows checkout, because Windows line-ending conversion changes task bytes. When a
   verifier shell script is supplied from that host checkout, stream-normalize CRLF for that
   disposable container invocation without modifying the pinned checkout.

## Experiment specification now frozen in principle

- [x] **Treatment (H-MH):** Terra/max for ROOT and Terra/high for every worker. This is the
  product configuration under test: a stronger coordinator directing cheaper execution.
- [x] **Primary raw comparison (C-X):** raw Codex, Terra/xhigh, only when the H-MH diagnostic
  trigger fires. It is the local token-cap anchor for the original raw-xhigh setup.
- [x] **Effort ablation (C-M):** raw Codex, Terra/max, only if C-X is materially worse than
  H-MH and has materially fewer aggregate tokens. It distinguishes hierarchical allocation
  from simply buying more maximum-effort compute.
- [ ] Before spending on a task, choose and record aggregate per-task token ceiling **B** and
  the numerical definition of a telemetry anomaly that triggers C-X. Also preregister what
  “materially worse” and “materially fewer tokens” mean for the C-M ablation trigger.
- [ ] Treat either watchdog as a safety ceiling, not a matched budget. If a run reaches its
  watchdog before pass or B, record it as time-censored and do not call that pair token-cap
  matched.
- [ ] State results as a system-level hierarchy-plus-allocation comparison, never as a
  harness-only causal effect. An H-MH-only run cannot prove "better for cheaper."

## What you need to do

### 1. Keep the machine available for long runs

- [ ] Run on AC power and prevent Windows from sleeping while plugged in. Turning the display
  off is fine; sleeping, hibernating, signing out, or rebooting is not.
- [ ] Keep at least 100 GB of free disk space. Docker images, task worktrees, build caches,
  and retained artifacts can be substantial.
- [ ] Avoid starting other CPU- or disk-heavy work during a run.
- [ ] Recheck Docker resource capacity before a smoke: at least 4 available CPUs, 16 GiB RAM,
  and 20 GiB task storage. The latest `docker info` capacity check could not reach the named
  pipe, so it is not currently verified.

### 2. Confirm the host Codex subscription login

In PowerShell, run:

```powershell
codex login status
codex --version
```

- [ ] `codex login status` says the active method is **ChatGPT**, not API key.
- [ ] If it is signed out, run `codex login` and complete the browser flow. Do not create or
  provide an API key for this study.
- [ ] Never copy `~/.codex/auth.json`, a login token, or any Codex credential into Docker, a
  benchmark repository, a task workspace, or an artifact directory.

Codex CLI supports local ChatGPT-subscription sign-in; API-key sign-in is a separate,
usage-billed route. [Official OpenAI authentication documentation](https://learn.chatgpt.com/docs/auth)

### 3. Finish harness and skill-suite updates

- [ ] Update `harness-single` and `Codex_Claude_Setup` as intended.
- [ ] Finish making both repositories proper in-repo submodules. `.gitmodules` and both
  directories are staged/in progress, but the current terminal's `git submodule status` helper
  fails before reporting status because its Git-for-Windows helper cannot find `basename`/`sed`.
  Resolve that before relying on submodule reproducibility; do not overwrite the in-progress
  changes.
- [ ] Configure and prove the role split: ROOT explicitly gets Terra/max; every worker explicitly
  gets Terra/high. Record the resolved configuration/payload for every invocation so workers do
  not silently inherit ROOT/max.
- [ ] Update the harness prompt to name and require the Codex_Claude workflow's
  `project-spec` and `project-topology` skills. Those skills produce the project specification,
  topology, and implementation plan; do **not** use `/plan`.
- [ ] Only after those workflow artifacts are complete, set `/goal` to implement the produced
  plan with explicit scope, validation commands, checkpoints, and a verifiable completion
  condition. The installed Codex CLI reports the `goals` feature as stable.
- [ ] Tell me when those changes are ready for integration and explicitly authorize the
  non-reportable Codex smoke run. Until then, no Codex task run will start.

I will create a separate clean worktree for every agent run; do not use the harness repository
itself as a benchmark task workspace.

### 4. Complete and validate token accounting

- [ ] Finish `scripts/collect_codex_usage.py`; it remains an unfinished design draft and cannot
  run this experiment as-is. It currently handles one Codex process, not ROOT plus workers.
- [ ] Make it preserve a distinct immutable JSONL/manifest per ROOT and worker invocation,
  capture the effective role/model/effort, and aggregate only unique terminal usage records.
- [ ] Implement the shared token-cap ledger for B without adding a second scheduler, retry
  controller, or agent process around the native harness. Record any in-flight cap overshoot.
- [ ] Pass offline parser tests for reported totals, derived totals, and duplicate/restart cases.
- [ ] Run one short non-reportable host CLI trace with nonzero reasoning, then a non-reportable
  multi-role harness no-op; verify whether output already includes reasoning, nonzero
  subscription usage, ROOT Terra/max, workers Terra/high, aggregate stability, and no
  credentials in containers or artifacts.

### 5. Acknowledge the intended subscription use

- [ ] Confirm you are comfortable spending ChatGPT Codex allowance on the two non-reportable
  smoke checks followed by up to two 15-hour H-MH runs (one per task).
- [ ] The 10-hour raw C-X run is **not** part of the initial spend. It happens only for that
  task if the preregistered trigger fires: an H-MH pass, a final partial score outside the
  published Terra/xhigh reference range, or the recorded telemetry anomaly after task-hash
  verification. C-M adds one further run only if the preregistered C-X quality-and-token
  ablation trigger fires.

Subscription limits can still end a run early. That outcome is data and must be recorded; we
will not silently retry it as though it had the full budget.

## Things you do not need to set up yet

- No GPU.
- No OpenAI API key.
- No Modal, Harbor, or cloud account for this local SWE-Marathon screen.
- No Git LFS for the current SWE-Marathon step. It will be needed later for LHTB.
- Do not launch `scripts/collect_codex_usage.py` against a task yet. It is deliberately marked
  as an unfinished design draft, not an experiment runner. It must first become the validated
  multi-process telemetry ledger described above.
- Do not run a raw-Codex baseline first, and do not alter the harness or its skill suite while
  the protocol is being finalized.

## What I will do after the harness updates and smoke-test authorization

1. Recheck Docker capacity, task-image availability, and the shipped oracle/verifier at zero
   model cost.
2. Complete the credential-free host-to-Docker test bridge and validated multi-process token
   ledger, then perform the short, non-reportable H-MH smoke.
3. Freeze task hashes, image digests, B, public reference values, the C-X trigger, and the
   C-M ablation thresholds. Launch the actual H-MH tasks only after a separate explicit start
   instruction.

**Hard gate:** do not start any Codex smoke or benchmark-agent run until you say the harness
and `Codex_Claude_Setup` updates are complete and explicitly authorize testing.
