# STEP-02 - Compatible network and session interchange

## Outcome

Implement the complete fixed I/O path so callers can load/write supported
network data, orders, attributes, annotations, colors/display options, and
BioFabric sessions using the usable model from STEP-01. This directly advances
BEHAVIOR-01 and supplies input/session behavior to later layout, alignment, and
CLI work.

## Scope and touchpoints

Own `crates/core/src/io/**`, including `sif.rs`, `gw.rs`, `json.rs`, `xml.rs`,
`factory.rs`, `session.rs`, `align.rs`, `order.rs`, `attribute.rs`,
`annotation.rs`, `color.rs`, and `display_options.rs`. `FabricFactory` is the
single format-routing seam. The fixed `Network`, `Session`, `ParseError`,
`ImportStats`, `AlignmentMap`, and public parser/writer signatures are protected
consumer contracts.

## Implementation

Implement parsing/writing for SIF, GW, JSON, alignment, node/link orders, and
BioFabric XML/session data with their reference-defined validation, ordering,
and error semantics. Route only supported extensions through `FabricFactory`.
Preserve session layout/display/alignment state and raw plugin data needed for
round-trip fidelity. Complete attribute/annotation tables and the color/display
helpers consumed by session/layout serialization.

Keep parser state local until a valid result can be returned, use the existing
`ParseError` variants for malformed/unsupported sources, and preserve model
insertion ordering rather than relying on unordered maps at an output boundary.
Do not change fixture files or add alternate file-format contracts.

## Dependencies and integration

Consumes STEP-01's model behavior. Its source path is disjoint from STEP-03,
so ROOT may launch both lanes concurrently after STEP-01 is integrated. It
provides all format/order/session inputs to STEP-04 and STEP-05. If a layout
consumer reveals an I/O semantic ambiguity, return it to ROOT rather than
editing `layout/**`.

## Requirement-fit validation

Use the visible parity input files and fixed parser APIs to establish that valid
network/session data can be represented and malformed input reaches the fixed
error boundary. Preserve exact serializer/order behavior for the later parity
adapter; a generic deserialization round trip is not sufficient evidence by
itself.

### Fast test suite

ROOT runs `cargo test -p biofabric-core --lib` through the bridge on this lane.
The worker should add only narrowly scoped source-module tests when needed to
decide a parser or round-trip rule that the current direct tests do not isolate.
After STEP-02 joins STEP-03, ROOT additionally runs the shared
`cargo test -p biofabric-core --test pipeline_stub` seam check; its SIF load is
the direct I/O consumer. Parser/session changes invalidate those two checks, not
alignment-only tests.

## Failure scope and recovery

An input/serialization failure holds only I/O-dependent consumers. Resume this
lane with the failing format and preserve other parser implementations and
passing source tests; after repair rerun the format-local fast check and the
pipeline seam if it consumes that format.

### Fast lane for revisiting old work

Repair the named parser/writer/factory route, rerun `cargo test -p
biofabric-core --lib`, and rerun `pipeline_stub` only when SIF/network-session
flow or its consumed serialization changed.
