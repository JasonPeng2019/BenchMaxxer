# STEP-01 - Usable network and graph foundation

## Outcome

Implement the fixed model, selection, worker-monitor, and graph-analysis
behavior so that later format, layout, alignment, and CLI work consumes a
coherent `Network` rather than stubs. This directly advances BEHAVIOR-01 and
BEHAVIOR-02 and is independently useful to library callers.

## Scope and touchpoints

Own `crates/core/src/model/**`, `crates/core/src/analysis/**`, and
`crates/core/src/worker.rs`. The fixed interface boundary is re-exported by
`crates/core/src/model/mod.rs` and `crates/core/src/lib.rs`; do not alter its
public signatures. Consumers are
the I/O factory/parsers, all layout algorithms, alignment merge/scoring, the
CLI handlers, and the existing `analysis_tests.rs`/parity infrastructure.

## Implementation

Complete model construction and mutation semantics, preserving insertion/order
meaning supplied by `IndexMap`/`IndexSet`; link endpoint and shadow behavior;
duplicate and self-link behavior; and network metadata/derived-index updates.
Implement node/link/annotation/selection helpers using the existing fields and
error/panic contract documented by their APIs—do not replace them with a new
model representation.

Implement traversal, components, neighborhoods, degree ordering, shortest path,
topological ordering/DAG levels, and directed-cycle detection in
`analysis/`. Match the reference's treatment of direction, shadows, isolated
nodes, and deterministic tie order as established by the existing fixtures.
Honor the existing progress-monitor cancellation interface for long loops.

## Dependencies and integration

This lane starts only after the shared bridge lock/fetch preflight in `PLAN.md`.
It produces the stable core value/graph contract used by STEP-02 through
STEP-04. It owns no I/O, layout, alignment, CLI, or existing-test source; report
instead of editing any such file.

## Requirement-fit validation

The required evidence is that the library compiles with completed fixed model and
analysis surfaces and that their direct unit behavior is exercised where existing
in-source tests cover it. Use focused implementation tests inside the owned
source modules only when an existing source-level assertion cannot distinguish a
critical graph rule; do not modify protected integration tests.

### Fast test suite

ROOT runs `cargo test -p biofabric-core --lib` through the bridge on the lane
after the worker exits. It must compile the completed model/analysis consumers
and pass the direct unit tests, including existing cycle-relation/model checks.
Any changed model or graph rule invalidates this result; unrelated later CLI or
fixture formatting changes do not.

## Failure scope and recovery

If the fast suite or a later consumer finds a model/graph defect, retain the
accepted lane state and resume this lane with the smallest failing model or
analysis selector. Rerun the fast suite and only direct consumers whose behavior
uses that changed semantic (normally STEP-02, STEP-03, and STEP-04); do not
restart independently valid CLI or fixture work.

### Fast lane for revisiting old work

Re-enter at the named public method and failing graph case, retain the rest of
the foundation, rerun `cargo test -p biofabric-core --lib`, and then rerun the
specific direct consumer test that exposed the issue.
