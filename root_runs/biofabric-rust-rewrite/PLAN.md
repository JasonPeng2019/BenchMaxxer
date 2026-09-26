# BioFabric Rust rewrite execution plan

## Outcome and boundaries

Deliver the implementation described by [SPEC.md](SPEC.md), advancing
BEHAVIOR-01 through BEHAVIOR-04 without changing their product meaning. The
work is a faithful offline Rust implementation of the fixed BioFabric library,
CLI, and alignment surface—not a redesign of its API, fixtures, or reference
oracle.

Implementation writes are limited to `crates/core/src/`, `crates/cli/src/`, and
the single permitted existing-test adapter
`crates/core/tests/parity_tests/runners.rs`. `SPEC.md`, this plan package, and
`goal.md` are ROOT workflow artifacts and are not task-code change targets for
workers. No task work may inspect benchmark/verifier material or change goldens,
protected tests, dependency manifests, or public signatures. Visible goldens are
read-only compatibility evidence.

Observed: the workspace exposes all major public types and command arguments,
but most implementations are stubs. Observed: the root task prompt names
`cargo test --workspace --no-fail-fast` as the final gate and requires all
agent-visible checks to use the pinned Docker bridge. Assumption: visible
fixtures and fixed signatures give enough oracle coverage to implement each
layer before full parity integration. The Java reference resolves any remaining
format/order detail; no product decision is outstanding.

## Current system and target design

The current call path is intentionally skeletal:

`CLI arguments or caller -> model/I/O -> analysis/layout or alignment ->
NetworkLayout/session/output`.

`crates/core/src/model/` provides `Network`, `Link`, `Node`, annotations, and
selection state. `analysis/` is its graph-algorithm consumer. `io/` imports and
writes network/order/session data and is routed by `FabricFactory`. `layout/`
converts a network and `LayoutParams` into row/column-oriented `NetworkLayout`.
`alignment/` merges two networks and applies scoring and alignment-specific
layouts. `crates/cli/src/main.rs` dispatches the existing arguments to eight
stubbed command handlers. The parity macros already describe fixture scenarios,
but their only allowed implementation adapter, `runners.rs`, is stubbed.

The target keeps those boundaries and implements the data flow in dependency
order. First make model/graph state reliable; then make interchange and layout
behavior independently usable. Alignment consumes those stable forms. Finally,
the CLI and parity runner become thin adapters over the completed core rather
than reimplementing graph behavior.

## Shared decisions and contracts

- Preserve every existing public type, trait, method signature, CLI command,
  and argument name. Private helpers are allowed only inside permitted source
  areas; `Cargo.toml` and `Cargo.lock` stay unchanged.
- Treat node/link ordering, shadow state, link grouping, XML/NOA/EDA formatting,
  and score edge cases as observable compatibility contracts. Keep deterministic
  iteration at serialization and ordering boundaries; do not rely on incidental
  hash iteration.
- Model mutation must keep any derived graph state (such as adjacency and
  metadata) coherent for the existing public methods. I/O, layout, alignment,
  and CLI code must propagate the existing typed errors rather than masking a
  failed parse or writing partial success.
- `runners.rs` may translate `ParityConfig` into real library calls and format
  their results, but it must consume existing fixtures/assertions unchanged. It
  cannot turn a missing capability into a skipped or synthesized passing case.
- ROOT owns all native-harness lifecycle, Git custody, integration, and Docker
  evidence. Before every worker launch, ROOT must run the pinned bridge against
  that lane worktree to byte-compare `Cargo.lock` with `/app/Cargo.lock` and run
  `cargo fetch --locked --offline`; either failure blocks that lane before model
  work. After a provider exits, ROOT reviews its allowed-path diff, stages and
  commits only permitted source paths, then records native completion review.
- Every compile/test command is run by ROOT through
  `python scripts/docker_task_workspace.py --task biofabric-rust-rewrite
  --worktree <lane-worktree> -- <command>` from the outer repository root. The
  bridge's printed image identity is the only image identity used as evidence.
  Workers do not use Docker. No verifier mount, scorer, reward, or external
  scheduler is part of this plan.

## Step map and execution order

This uses staged native lanes because the model layer is a real prerequisite,
while I/O and layout have disjoint source ownership once that layer is stable.
The alignment and CLI layers consume both outputs, so serializing those joins
reduces false parity diagnoses. ROOT is the single integration owner.

| Step | Produces | Depends on |
| --- | --- | --- |
| [STEP-01](steps/STEP-01-network-and-graph-foundation.md) | Usable network/model and graph primitives for BEHAVIOR-01 and BEHAVIOR-02. | Native lane preflight only. |
| [STEP-02](steps/STEP-02-network-interchange.md) | Compatible format, order, attribute, annotation, and session interchange for BEHAVIOR-01. | STEP-01; may run in parallel with STEP-03. |
| [STEP-03](steps/STEP-03-core-layouts.md) | Compatible generic/default/specialized layouts for BEHAVIOR-02. | STEP-01; may run in parallel with STEP-02. |
| [STEP-04](steps/STEP-04-alignment-engine.md) | Compatible merging, scoring, grouping, and alignment layouts for BEHAVIOR-03. | Integrated STEP-02 and STEP-03. |
| [STEP-05](steps/STEP-05-visible-parity-adapter.md) | Genuine visible-parity execution for BEHAVIOR-01 through BEHAVIOR-03. | Integrated STEP-02 through STEP-04; may run in parallel with STEP-06. |
| [STEP-06](steps/STEP-06-cli-workflows.md) | Operational fixed-command CLI workflows for BEHAVIOR-04. | Integrated STEP-02 through STEP-04; may run in parallel with STEP-05. |

Each step gets one direct native worker lane with the step's write boundary.
STEP-02 and STEP-03 may run together because their owned paths are respectively
`crates/core/src/io/**` and `crates/core/src/layout/**`, and they consume the
unchanged public model interfaces from STEP-01. STEP-05 and STEP-06 may run
together because their owned paths are respectively the sole permitted
`runners.rs` adapter and `crates/cli/src/commands/**`; both consume the stable
integrated core. A worker may not change another lane's files to resolve a
problem; it returns that conflict to ROOT for serial resolution. Every bootstrap explicitly selects
`gpt-5.6-terra`, `reasoning_effort=high`, and `service_tier=priority` in its
signed invocation, retains the generated `worker-isolated` profile, and writes
a truthful `RESULT.json` rather than attempting Git operations.

## Integration and whole-product validation

ROOT first integrates and tests STEP-01. It then launches STEP-02 and STEP-03
from that integrated base, reviews both disjoint diffs, and joins them before
running `cargo test -p biofabric-core --test pipeline_stub` through the bridge;
that smoke test observes the real load/layout/extract seam. STEP-04 follows the
joined core and is checked with its focused analysis selectors. STEP-05 and
STEP-06 then run from the integrated core in parallel, enabling respectively
the existing parity macros and the command handlers.

Focused command results establish local claims only. After STEP-05, STEP-06,
and any targeted repairs, ROOT runs through the bridge on the actual integrated
lane:

`cargo test --workspace --no-fail-fast`

That named task gate consumes the final completion claim. It does not authorize
verifier access or a benchmark reward. If it exposes a parity failure, ROOT maps
the failure to the step and owned source path it actually implicates, resumes or
creates only that native lane with the focused failing selector, retains
unaffected integrated commits and evidence, then reruns the affected selector
and any direct consumer. A generic whole-workspace retry or a generic integration
writer is not a recovery strategy.

## Risks, assumptions, and unresolved decisions

The principal risk is subtle reference ordering/serialization behavior, not API
design. Address it at each layer through the existing fixture selectors and
preserve the first failing byte/field as the diagnostic target; do not rewrite a
fixture. A Docker lock mismatch or failed offline fetch is a prerequisite gap,
not a source defect: stop that lane and report the exact bridge evidence. A
native launch/configuration mismatch—including an invocation that does not show
the required worker model/options or the ROOT Terra/max assignment—also stops
before task code work. No unresolved design decision prevents execution.
