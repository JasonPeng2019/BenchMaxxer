# Prepared ROOT workspaces

This directory contains one host-side ROOT workspace per selected benchmark task:

- `biofabric-rust-rewrite/` is cloned from the clean BioFabric agent-visible
  baseline at `934570e2c644a262a356314a61cf04bc9d2f99e5`.
- `find-network-alignments/` is cloned from the clean Find Network Alignments
  agent-visible baseline at `885b78c9b82f198d85f304bc243fd475f89d05e0`.
- `zstd-decoder/` is cloned from the clean, 13-file ZSTD agent-visible baseline
  at `c1c5a00cac9e58af70fb4289b9c0c49a67774f31`.

Each workspace contains the copied portable workflow files from
`Codex_Claude_Setup`: `.agent/`, `.agents/`, `.claude/`, `.codex/`,
`AGENTS.md`, `CLAUDE.md`, `.gitignore`, and `workspace-aid/`. The latter is
documentation required by the supplied workspace validator, not benchmark
runtime content. The source submodule remains the authoritative editable copy.

The `.agents/skills/` source and generated `.claude/skills/` mirror in both task
workspaces were synced to `Codex_Claude_Setup` revision
`30bdc088b3238f9e045bc9969f8b5cb0bb4981a0` and passed the supplied
workspace validator before harness integration. Re-sync from the source
submodule if that revision changes, then re-run `harness setup` for the selected
workspace to restore harness-owned Claude skills. The suite's validator expects
an unextended export and reports extra hooks/skills after harness integration;
that does not mean the installed source skills changed.

Both workspaces have since passed native `harness setup`. Their ROOT config
remained Terra/max, the harness hooks and operational skills were installed,
and their idle runtimes were cleanly shut down. `harness-config.json` currently
selects BioFabric for the first run. Both preflight runtimes are CLOSED; re-run
setup for the selected task before
starting an epoch; switch the one configured ROOT path only after shutdown.

As of 2026-09-25, the historical Terra/max statement above has been superseded:
both prepared workspace configs and ROOT prompts now require Terra/high for
ROOT, while each worker still requires explicit Terra/high at bootstrap. The
BioFabric benchmark attempt was cancelled and its runtime metadata remains
`SHUTTING_DOWN` despite no live run processes; do not reuse that runtime. The
next task was then undecided. ZSTD was selected afterward as described below.

The ZSTD workspace has the same pinned skill suite and Terra/high ROOT config;
its prompt requires explicit Terra/high for every worker. It passed portable
workspace validation and native harness setup. `harness-config.json` now
selects ZSTD; both unlaunched preflight lanes were retired and the latest
runtime is `CLOSED`. The image is built and pinned. After Docker Desktop File
Sharing was updated, the exact Terra/high lane passed the one-mount,
no-network bridge smoke. The supplied oracle earned reward 0 on the rebuilt
image (33/43 tests, partial 0.767), so the image is not oracle-validated.
The user accepted that risk and designated 0.767 as the local 100% comparison
reference, without changing official scoring; see `../RUN_MANIFEST.md` before
authorizing a run.
The intended ZSTD treatment is now an intentionally interrupted local pilot:
the machine may be powered off between clean ROOT session segments. Its
`ROOT_RESUME_PROMPT.md` and `../scripts/INTERRUPTED_ZSTD_RUN.md` define the
checkpoint/resume procedure. Count cumulative active time and all ROOT/worker
tokens; disclose offline gaps and do not present it as a continuous official
benchmark run. The harness treatment has a 10-hour cumulative active-time
limit, explicitly longer than the upstream task's five-hour timeout; any
conditional raw controls retain five continuous hours.

On this Windows host, both ROOT repositories also need local Git
`core.longpaths=true` for native lane worktree creation under the long path to
`root_runs/`; that local setting was applied during preflight.

The harness can use only one `root_workspace` at a time, and that workspace is
also the Git repository from which lane worktrees are created. Before activating
the harness, select the task workspace, point `harness-single/harness-config.json`
at its absolute path, and address the remaining protocol gates in
`../AGENT_TODO.md`.

For an authorized run, start the ROOT through
`../scripts/collect_codex_usage.py run` with the selected task workspace and
its `.harness-runtime` path. Use `--sandbox danger-full-access` for ROOT only,
as explicitly approved by the user; worker lanes retain their isolated native
Windows sandbox. Omit `--budget-tokens` for reportable runs: token use is
measured, not capped. Starting a ROOT CLI directly would omit ROOT JSONL capture.
The exact arguments and archive flow are in `../scripts/TOKEN_LEDGER_PLAN.md`.

Each task workspace also has a `ROOT_RUN_PROMPT.md`. It is the future ROOT
session's initial prompt: it requires harness setup, `$project-specification`,
`$project-topology`, and a plan-referencing `goal.md`. The prompt and `AGENTS.md`
require the ROOT to re-read that file and use it as the soft execution directive
for the remainder of the task. This is an intentional prompting guardrail, not an
activation of persisted Codex Goal state. This flow does not modify the pinned
upstream benchmark checkout.

Docker setup has since been checked separately: both pinned task images were
built and started in no-network containers, and a read-only mount of the
BioFabric ROOT workspace passed. After the Find ROOT workspace was added to
Docker Desktop File Sharing and Docker restarted, its read-only, no-network
mount passed too.
The authorized non-reportable `root-worker-elevated` preflight launched one
Terra/max ROOT and one Terra/high worker. Its immutable archive records 358,498
aggregate derived tokens and no ledger errors; no benchmark implementation was
started. Both task images were rebuilt from pinned LF context. BioFabric's
rebuilt-image oracle passed all 450 tests. Find's time-limited oracle twice
missed its primary S3=0.32 threshold (0.315106, then 0.318729), despite an
older-image pass; this remains an explicit run-readiness caveat. The
user chose to proceed with that documented risk, without changing the pinned
task or requiring a passing retry; no reportable run is authorized yet. The
operator-only `../scripts/docker_task_workspace.py` bridge passed one-mount,
no-network container smokes for both exact task lanes. See `../AGENT_TODO.md`
for current image IDs and remaining gates.
