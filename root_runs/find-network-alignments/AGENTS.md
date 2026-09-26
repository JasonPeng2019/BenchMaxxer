# Repository instructions

These are portable starter instructions for the repository that contains this file.
Direct user instructions and more-specific repository instructions take precedence.

- Inspect relevant code, tests, and local guidance before editing.
- Make the smallest complete change; preserve unrelated user work.
- Use the repository's documented build, test, format, and dependency tools. Run
  proportionate checks, report their actual results, and never treat skipped or
  unavailable checks as a pass.
- Use a focused skill when its description matches the task. Use `project-topology`
  only to build a significant project execution plan, not for ordinary coding.
- Keep one writer for overlapping edits. Delegate only independently scoped work
  with explicit ownership, expected output, and completion conditions.
- Resolve exact targets before destructive actions. Do not discard work, mutate Git
  internals, commit, push, publish, or contact external parties without clear user authorization.

## SWE-Marathon ROOT-run workflow

For an explicitly authorized benchmark ROOT session, read and follow
`ROOT_RUN_PROMPT.md` before making task changes. It is the task-specific initial
prompt and requires this order: native harness setup, `$project-specification`,
`$project-topology`, creation of `goal.md`, then a full re-read of `goal.md`
before execution. Treat its `## Goal text` as the soft execution directive for the
remainder of the task; do not merely create the file and move on. `PLAN.md` is the
planning artifact; do not substitute Codex's `/plan` slash command for
`$project-topology`.

This workspace is a host-side ROOT workspace cloned from the agent-visible task
baseline. Do not modify the pinned upstream checkout under `benchmarks/`, read
verifier secrets, copy credentials, or launch Docker/provider work before the
operator has completed the separate experiment gates and explicitly authorized the
run.

For the reportable pilot, the user chose uncapped token usage. Preserve
per-process ROOT/worker usage and compare aggregate tokens after the run; do
not impose a token ceiling. ROOT alone may use approved host-command access to
operate the native harness. Every Codex worker must keep its generated
`worker-isolated` elevated Windows sandbox; never replace it with full host
access. Agent-facing Docker commands must go through
`../../scripts/docker_task_workspace.py` with exactly the current task lane worktree
mounted. Do not expose the benchmark verifier or oracle solution to a worker.
