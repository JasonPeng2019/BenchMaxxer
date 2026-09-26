# STEP-03 - Compatible core layout algorithms

## Outcome

Implement generic layout plumbing, default ordering/edge placement, and all
fixed specialized layout algorithms so a `Network` yields a compatible
`NetworkLayout`. This directly advances BEHAVIOR-02 and provides the layout
contract needed by sessions, alignment, CLI, and parity runners.

## Scope and touchpoints

Own `crates/core/src/layout/**`: `traits.rs`, `build_data.rs`, `result.rs`,
`link_group.rs`, `default.rs`, `similarity.rs`, `hierarchy.rs`, `cluster.rs`,
`control_top.rs`, `set.rs`, and `world_bank.rs`. Do not change model, parser,
alignment, CLI, or test files. The protected seams are `LayoutParams`,
`NodeLayout`, `EdgeLayout`, `NetworkLayoutAlgorithm`, `TwoPhaseLayout`,
`LayoutBuildData`, and the public `NetworkLayout`/node/link layout fields.

## Implementation

Complete the two-phase row/column pipeline first: parameter handling, row maps,
link-group indexing/sort keys, regular/shadow column assignment, spans, and
annotations. Build default layout on that canonical representation so fixed node
or link order and group mode have one implementation path.

Implement similarity, hierarchy, cluster, control-top, set, and World Bank
variants through the fixed traits and their supplied parameters. Preserve the
reference's tie-breaking, directed/DAG preconditions, group placement, control
and target ordering, shadow behavior, and annotation ranges. `NetworkLayout`
extraction must compress retained rows/columns while preserving surviving link
semantics. Do not create a second layout data type or duplicate graph logic that
belongs to STEP-01.

## Dependencies and integration

Consumes STEP-01. It may run beside STEP-02 because its write boundary is
disjoint and the public attribute/order types already exist; ROOT joins both
before the pipeline smoke test. STEP-04 consumes its layout values/types and
STEP-05/STEP-06 turn them into parity and CLI outputs.

## Requirement-fit validation

The local claim is that every fixed layout surface compiles against the stable
model and produces structurally valid `NetworkLayout` values. The joined I/O+
layout claim is exercised by the pipeline test. Exact NOA/EDA/BIF order remains
the later parity evidence once STEP-05 makes the existing adapter genuine.

### Fast test suite

ROOT runs `cargo test -p biofabric-core --lib` through the bridge for the lane's
direct layout/unit checks. Once STEP-02 is integrated, ROOT runs
`cargo test -p biofabric-core --test pipeline_stub`; it decisively checks SIF
loading, default node/edge layout, row count, links, and extraction together.
Any change to layout order, shadow/column assignment, or the consumed model/I/O
path invalidates the appropriate one of those checks.

## Failure scope and recovery

If a specialized fixture differs, resume this lane at the selected algorithm or
shared column/group helper and rerun its smallest source test plus the direct
pipeline/parity selector that identified it. Keep successful independent layout
variants and STEP-02's I/O result; do not rerun alignment until its consumed
layout contract changed.

### Fast lane for revisiting old work

Retain the integrated base, repair the implicated `layout/**` method, run the
library suite, then rerun the failing layout/pipeline selector and only the
alignment or CLI selector that consumes the changed layout field.
