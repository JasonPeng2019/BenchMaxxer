# Initial ROOT prompt — SWE-Marathon Find Network Alignments

Use this file as the initial prompt for the ROOT Codex session in this workspace.
Run it only after the operator has completed the separate host, Docker, isolation,
telemetry, uncapped-accounting, and explicit-authorization gates. This file does not
authorize a smoke test, provider invocation, Docker action, or benchmark trial by
itself.

## Task authority and boundaries

The task is SWE-Marathon `find-network-alignments`. Treat the task brief below and
the checked-out skeleton as the sole task authority. The pinned upstream
SWE-Marathon checkout is evidence only; do not modify it or inspect any verifier
implementation or held-out test.

Produce `/app/DM-HS.align` and `/app/y2kr-SC.align` for the supplied undirected
protein-interaction networks. Each file maps every node in the smaller graph to a
distinct node in the larger graph, one tab-separated pair per line with exact node
names. Completion requires S3 at least 0.32 for DM-HS and both S3 at least 0.55
and node correctness at least 0.30 for y2kr-SC. The task environment is offline;
the reference alignment is available only for the stated yeast node-correctness
metric. Do not rely on resources outside the task environment.

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
   - Invoke `$project-specification`, inspect the supplied network files and task
     boundary, and create the canonical package `SPEC.md` plus
     `behaviors/BEHAVIOR-*.md` in this ROOT workspace.
   - The package must define the alignment-file contract, injectivity, metric
     thresholds, offline limitation, and observable completion conditions. It is a
     behavior specification, not an implementation plan; do not begin task work in
     this step.

3. **Write the implementation plan with `$project-topology`.**
   - Invoke `$project-topology` after the specification is usable. Consume the
     specification and write the canonical `PLAN.md` plus `steps/STEP-*.md` package.
   - The plan must make the algorithmic work, output-file production, score
     validation, smallest sufficient harness-lane shape, and recovery path concrete.
     It must keep task outputs separate from ROOT workflow artifacts.
   - `PLAN.md` is the required planning artifact. Do **not** use Codex's `/plan`
     slash command as a replacement for `$project-topology`.

4. **Write `goal.md` from the completed plan.**
   - Create a top-level `goal.md` that refers explicitly to `PLAN.md` and contains:
     the end state, task boundaries, native-harness requirement, allowed evidence,
     verification conditions, uncapped token accounting/watchdog constraints, iteration policy, and
     blocked stop condition.
   - Its `## Goal text` section must be an exact, self-contained execution
     directive. It must state that the plan in `PLAN.md` is the implementation
     authority and that completion requires valid alignment outputs and score
     evidence rather than a self-report.

5. **Use the written goal as the execution directive.**
   - Before beginning task work or launching a harness lane, re-read `goal.md` in
     full. Treat its `## Goal text` as the active soft guardrail for the rest of
     this session; do not merely create the file and move on.
   - Execute `PLAN.md` through the native harness in accordance with that directive.
     Keep checking the plan, goal, task boundaries, and completion evidence at each
     material checkpoint. Do not claim completion merely because a plan or partial
     alignment exists.

## Run-wide constraints

- Keep Codex credentials on the host. Agent-facing Docker containers receive
  only the current task worktree, never credentials, the pinned benchmark
  checkout, or the source harness/workflow repos. The operator may mount the
  pinned verifier separately and read-only only after agent work is complete.
- For agent-visible container commands, use the host-side
  `python ../../scripts/docker_task_workspace.py --task find-network-alignments --worktree
  <current-lane-worktree> -- <command>` bridge. It pins the image and one mount;
  do not add verifier or solution mounts to a worker-facing container.
- ROOT alone has the approved host-command access needed for native harness
  Git worktree creation. Workers must retain the generated elevated Windows
  `worker-isolated` profile; never relax it to full access.
- Use the native harness; do not replace it with an external scheduler, retry loop,
  second agent runner, collaboration relay, or AI watcher.
- Preserve the distinct ROOT/worker JSONL and manifest evidence required by the
  token ledger. Count terminal cumulative usage once per invocation; cached input
  is a component of input, not an additive total.
- Runs are uncapped by user choice. The watchdog and task-image/verifier identities
  are operator-controlled constraints; preserve aggregate usage as an outcome.
  If a required environment or proof is not
  available, stop with the precise blocker rather than claiming a pass.
