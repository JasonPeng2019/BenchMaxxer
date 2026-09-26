# STEP-04 - Compatible alignment engine and layouts

## Outcome

Implement alignment parsing consumption, merge classification, scoring, group/
Jaccard/cycle/orphan analysis, and the three fixed alignment layout modes. This
directly advances BEHAVIOR-03 and produces core behavior that the `align` CLI
and alignment parity runner can use without bespoke logic.

## Scope and touchpoints

Own `crates/core/src/alignment/**`: `types.rs`, `loader.rs`, `merge.rs`,
`scoring.rs`, `groups.rs`, `jaccard.rs`, `cycle.rs`, `cycle_relation.rs`,
`orphan.rs`, and `layout.rs`. Consume, but do not alter, the `io::align`
mapping format from STEP-02 and `layout` structures/traits from STEP-03.
Protected interfaces include `MergedNetwork`, `AlignmentScores`, `NodeGroupMap`,
`AlignmentCycles`, `OrphanFilter`, `AlignmentLayoutMode`, and their existing
public methods/fields.

## Implementation

Use the fixed alignment mapping to construct merged IDs, node colors, edge
types, perfect-alignment correctness, and deterministic merged-network order.
Implement the exposed metrics with reference-compatible numerator, denominator,
and empty/partial-mapping behavior. Build group ordering, Jaccard correctness,
cycle paths/positions, and orphan context from that same classification rather
than reclassifying independently in each layout.

Implement group, orphan, and cycle node/edge layouts through the existing layout
traits, including their reference-specific group order, relation labels, colors,
annotations, shadow handling, and cycle bounds. Propagate fixed parse/layout
errors and progress cancellation rather than replacing them with default values.

## Dependencies and integration

Start only after ROOT integrates STEP-02 and STEP-03, because it consumes both
the real alignment input semantics and layout representation. It owns no CLI or
parity-runner code. STEP-05 and STEP-06 consume its completed library calls; a
malformed alignment input issue routes to STEP-02, while a shared layout
representation issue routes to STEP-03.

## Requirement-fit validation

Use existing `analysis_tests.rs` score cases for metric behavior and the existing
alignment/cycle parity cases, once the runner is available, for row/column and
annotation compatibility. A score-only pass does not establish alignment layout
parity, so retain the later parity selector as the direct consumer check.

### Fast test suite

ROOT runs `cargo test -p biofabric-core --test analysis_tests -- align_score_`
through the bridge after the worker exits. This selector exercises the existing
EC/S3/ICS and optional-evaluation score cases against fixture networks. If a
cycle/group layout implementation changed, also run the focused
`analysis_tests` selector that names the affected cycle or node-group case;
full alignment parity is verified after STEP-05.

## Failure scope and recovery

Resume this lane for a merge/classification/metric/layout mismatch, retaining
STEP-02/STEP-03 and unrelated alignment work. Rerun the failing analysis selector
and the direct parity selector after STEP-05 only when its consumed alignment
output changed; do not reset the full workspace.

### Fast lane for revisiting old work

Repair the named alignment source path, run its focused `analysis_tests`
selector, then rerun the specific alignment parity selector once the runner
consumer is integrated.
