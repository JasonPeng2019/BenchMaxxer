# BioFabric Rust rewrite goal

## End state

The completed workspace is a faithful offline Rust rewrite of `biofabric-core`
and the fixed `biofabric` CLI, including network alignment. It satisfies the
product behaviors in `SPEC.md` and the repository execution design in
[`PLAN.md`](PLAN.md). Completion is established by current evidence from the
integrated implementation, not a worker or ROOT self-report.

## Task boundaries

- Keep every public type, trait, method signature, command, and flag fixed.
- Task-code changes are limited to `crates/core/src/`, `crates/cli/src/`, and
  the single permitted existing-test file
  `crates/core/tests/parity_tests/runners.rs`.
- Do not change any other existing test, fixture, golden output, dependency
  manifest/lockfile, or public API. Visible test data is read-only evidence.
- Do not inspect or modify `benchmarks/`, `results/`, or
  `.harness-runtime/operator-*`; do not access a verifier, held-out test, oracle
  solution, credentials, or prior-run artifact.

## Native harness and custody requirement

Execute `PLAN.md` through the native harness only. ROOT retains all lifecycle,
integration, Docker, Git custody, and completion-review authority. The ROOT
session must resolve to `gpt-5.6-terra` with `max` reasoning. Every worker
bootstrap must explicitly and visibly request `gpt-5.6-terra`,
`reasoning_effort=high`, and `service_tier=priority`, and retain its generated
`worker-isolated` Windows profile.

Before each lane launch, ROOT uses the pinned Docker bridge to verify the lane
`Cargo.lock` matches `/app/Cargo.lock` and that `cargo fetch --locked --offline`
succeeds. Workers do not use Docker or Git operations. They leave permitted
source edits and a truthful `RESULT.json`; after provider exit ROOT reviews,
stages, commits, and records native completion review for only the allowed
paths. A ROOT commit is custody, not test evidence.

## Allowed evidence and verification conditions

ROOT runs all agent-visible builds/tests only through the pinned bridge from the
outer repository root, mounting exactly the current lane worktree. Use the
bridge's own printed image identity and no verifier/solution mount. Run the
focused checks named in `PLAN.md` after the relevant lane exits and preserve
their actual results. Final completion requires successful bridge evidence for:

`cargo test --workspace --no-fail-fast`

No verifier run, verifier mount, scorer invocation, or benchmark reward is
authorized by this goal.

## Uncapped accounting and watchdog constraints

Token use is uncapped by user instruction. Preserve the distinct ROOT and worker
JSONL/manifest evidence required by the native token ledger, count terminal
cumulative usage once per invocation, and treat cached input as a component of
input rather than an additional total. Do not impose a token cap or bypass the
operator-controlled watchdog, task-image identity, or verifier-identity
constraints. Aggregate usage is an outcome to report after the run, not a reason
to curtail required work.

## Iteration policy

At each material checkpoint, compare the current state to `PLAN.md`, this goal,
the task boundary, and the required evidence. Classify a failed command by the
behavior and downstream consumer it can invalidate. Retain valid lane changes
and passing evidence; repair only the implicated owner/path through a native
lane resume or new bounded lane, rerun the focused selector and direct consumer,
then return to the first unresolved plan dependency. Do not rewrite fixtures,
repeat an unchanged approach without diagnosis, use an external scheduler, or
restart the whole run merely to obtain a clean history.

## Blocked stop condition

Stop and report the precise blocker—without claiming a pass—if native setup,
the required ROOT/worker model configuration, bridge lock/fetch preflight,
allowed-path custody, or required evidence is unavailable; if completion would
require forbidden verifier/benchmark access; or if a remaining product claim
cannot be established with the allowed environment. Preserve all valid work and
identify the smallest blocked dependency and its consumers.

## Goal text

Execute `PLAN.md` as the implementation authority for the BioFabric Rust
rewrite. Implement only the fixed `biofabric-core`/`biofabric` behavior in
`crates/core/src/` and `crates/cli/src/`, plus the sole allowed existing-test
adapter `crates/core/tests/parity_tests/runners.rs`; preserve public APIs,
protected tests, fixtures, golden outputs, manifests, and lockfile. Use only the
native harness: ROOT must run as `gpt-5.6-terra`/`max`; every worker bootstrap
must explicitly use `gpt-5.6-terra` with `reasoning_effort=high` and
`service_tier=priority` in its signed invocation and keep the generated
`worker-isolated` profile. Before launching each lane, ROOT must use the pinned
Docker bridge on that lane worktree to prove `Cargo.lock` equals
`/app/Cargo.lock` and that `cargo fetch --locked --offline` succeeds; stop that
lane if either check fails. Workers may edit only their assigned permitted paths
and leave a truthful `RESULT.json`; ROOT alone reviews, stages, commits, and
completion-reviews their work, and a commit is not evidence of correctness.

Run every agent-visible build/test through the pinned bridge with only the
current lane worktree mounted. Follow the focused checks, ownership boundaries,
integration order, and recovery rules in `PLAN.md`; retain valid work, repair
only the implicated behavior/path, and do not use an external scheduler or a
full restart for a local defect. The final completion claim requires actual
successful bridge evidence from `cargo test --workspace --no-fail-fast`, not a
self-report or a plan/commit. Preserve uncapped ROOT/worker token-ledger
evidence and watchdog constraints, counting terminal cumulative usage once per
invocation. Never inspect `benchmarks/`, `results/`, or
`.harness-runtime/operator-*`, and never run/mount a verifier or produce a
benchmark reward. If setup, model configuration, offline bridge preflight,
allowed-path custody, or required verification is unavailable, or if proof
would require forbidden benchmark access, stop with the exact blocker and the
smallest affected dependency rather than claiming completion.
