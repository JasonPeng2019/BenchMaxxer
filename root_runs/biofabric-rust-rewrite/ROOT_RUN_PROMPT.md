# Initial ROOT prompt — SWE-Marathon BioFabric Rust rewrite

Use this file as the initial prompt for the ROOT Codex session in this workspace.
Run it only after the operator has completed the separate host, Docker, isolation,
telemetry, uncapped-accounting, and explicit-authorization gates. This file does not
authorize a smoke test, provider invocation, Docker action, or benchmark trial by
itself.

## Task authority and boundaries

The task is SWE-Marathon `biofabric-rust-rewrite`. Treat the task brief below and
the checked-out skeleton as the sole task authority. The pinned upstream
SWE-Marathon checkout is evidence only; do not modify it or inspect any verifier
implementation or held-out test.

Implement the `biofabric-core` Rust library and `biofabric` CLI as a faithful Rust
rewrite of BioFabric and its network-alignment plugin. The public types, traits,
and method signatures are fixed. Implement code in `crates/core/src/` and
`crates/cli/src/`; only `crates/core/tests/parity_tests/runners.rs` may be changed
among the existing tests. Do not change other test files, golden fixtures, or the
public API. Add private helpers, fields, or modules only when needed. The target is
byte-level parity with the Java reference under the task's visible and held-out
tests. The task environment is offline and its final scorer runs
`cargo test --workspace --no-fail-fast`.

## Required ordered workflow

1. **Set up the native harness before task work.**
   - Confirm that `harness-single/harness-config.json` names this exact absolute
     workspace as `root_workspace`, that no other live epoch is using the harness,
     and that the ROOT session resolves to `gpt-5.6-terra` / `high`.
   - From the repository's `harness-single` directory, run
     `python -m orchestrator_harness.operator_launch harness setup` and inspect its
     structured result. Do not bootstrap or launch a lane until setup succeeds.
   - Preserve the intended authority/isolation split: ROOT is Terra/high; every Codex worker
     bootstrap explicitly uses `--model gpt-5.6-terra`,
     `--provider-option reasoning_effort=high`, and
     `--provider-option service_tier=priority`. Do not let workers inherit ROOT
     defaults. Confirm those values in the signed invocation before launch.

2. **Write the task specification with `$project-specification`.**
   - Invoke `$project-specification`, inspect the code and visible tests, and create
     the canonical package `SPEC.md` plus `behaviors/BEHAVIOR-*.md` in this ROOT
     workspace.
   - The package must make the task boundary, fixed public API, permitted source
     areas, test-file restriction, parity requirement, offline constraint, and
     observable completion criteria explicit. It is a behavior specification, not
     an implementation plan; do not begin implementation in this step.

3. **Write the implementation plan with `$project-topology`.**
   - Invoke `$project-topology` after the specification is usable. Consume the
     specification and write the canonical `PLAN.md` plus `steps/STEP-*.md` package.
   - The plan must give concrete source/test touchpoints, a smallest sufficient
     harness-lane shape, verification steps, and a recovery path. It must respect
     the task's edit restrictions and keep task code separate from ROOT workflow
     artifacts.
   - `PLAN.md` is the required planning artifact. Do **not** use Codex's `/plan`
     slash command as a replacement for `$project-topology`.

4. **Write `goal.md` from the completed plan.**
   - Create a top-level `goal.md` that refers explicitly to `PLAN.md` and contains:
     the end state, task boundaries, native-harness requirement, allowed evidence,
     verification conditions, uncapped token accounting/watchdog constraints, iteration policy, and
     blocked stop condition.
   - Its `## Goal text` section must be an exact, self-contained execution
     directive. It must state that the plan in `PLAN.md` is the implementation
     authority and that completion requires evidence rather than a self-report.

5. **Use the written goal as the execution directive.**
   - Before beginning implementation or launching a harness lane, re-read
     `goal.md` in full. Treat its `## Goal text` as the active soft guardrail for
     the rest of this session; do not merely create the file and move on.
   - Execute `PLAN.md` through the native harness in accordance with that directive.
     Keep checking the plan, goal, task boundaries, and completion evidence at each
     material checkpoint. Do not claim completion merely because a plan or partial
     implementation exists.

## Run-wide constraints

- Keep Codex credentials on the host. Agent-facing Docker containers receive
  only the current task worktree, never credentials, the pinned benchmark
  checkout, or the source harness/workflow repos. The operator may mount the
  pinned verifier separately and read-only only after agent work is complete.
- Workers cannot access the Docker daemon. After each worker provider exits,
  ROOT runs compile/test checks against that lane using the host-side bridge:
  `python scripts/docker_task_workspace.py --task biofabric-rust-rewrite --worktree
  <current-lane-worktree> -- <command>` from the outer repository root.
  The bridge pins the image and mounts only that lane; never add verifier or
  solution mounts to an agent-visible container. Return actual build/test
  findings to the worker through a native lane resume when iteration is needed.
- ROOT alone has the approved host-command access needed for native harness
  Git worktree creation. Workers must retain the generated elevated Windows
  `worker-isolated` profile; never relax it to full access.
- Codex protects a worker worktree's Git metadata, so a sandboxed worker may
  edit task files but cannot create a Git commit. Do not ask the worker to
  retry `git add` or `git commit`. Have it finish its source edits and a truthful
  `RESULT.json`; after the provider exits, ROOT alone stages only the permitted
  task paths, reviews the exact staged diff, commits the lane branch with host
  access, and performs the native completion review/integration. A ROOT-owned
  commit is a custody step, not verification evidence or a task pass.
- Before a lane launch, use the pinned Docker bridge to verify that the mounted
  lane `Cargo.lock` equals the image's `/app/Cargo.lock` and that an offline
  `cargo fetch --locked` succeeds. Stop before model work if either check fails.
- Use the native harness; do not replace it with an external scheduler, retry loop,
  second agent runner, collaboration relay, or AI watcher.
- Preserve the distinct ROOT/worker JSONL and manifest evidence required by the
  token ledger. Count terminal cumulative usage once per invocation; cached input
  is a component of input, not an additive total.
- Runs are uncapped by user choice. The watchdog and task-image/verifier identities
  are operator-controlled constraints; preserve aggregate usage as an outcome.
  If a required environment or proof is not
  available, stop with the precise blocker rather than claiming a pass.
