# STEP-06 - Operational fixed-command CLI workflows

## Outcome

Implement all existing command handlers so the `biofabric` binary composes the
completed core behavior for `layout`, `info`, `convert`, `align`, `compare`,
`extract`, `export-order`, and `search`. This independently advances
BEHAVIOR-04 without changing the fixed Clap-facing contract.

## Scope and touchpoints

Own `crates/cli/src/commands/**`. `crates/cli/src/main.rs` dispatch and
`crates/cli/src/args.rs` command/option definitions are protected fixed
interfaces; do not change them. Consume `FabricFactory`, the model, layout,
session, and alignment APIs from the integrated core. Do not edit the parity
runner or any existing test.

## Implementation

Make each handler a thin composition of the core APIs: preserve supplied
defaults and flag precedence, stdout/file choice, text/JSON shape, and error
exit behavior. Route `layout` and `align` through the completed layout/session
surfaces; route inspection/search/extraction through model/analysis; and route
conversion/order export through interchange. Avoid duplicating graph, layout,
or score calculations in CLI code and leave image/output modes at their
reference-defined behavior rather than inventing a renderer.

## Dependencies and integration

Consumes integrated STEP-02, STEP-03, and STEP-04. Its write path is disjoint
from STEP-05, allowing the two final lanes to run together. A core behavior
failure is returned to its owner; this lane repairs only handler composition,
formatting, and argument-to-core translation.

## Requirement-fit validation

The local claim is that the CLI package builds and its real command parser/
dispatch path can invoke each fixed handler. Where no existing CLI test isolates
a handler, add a narrow `#[cfg(test)]` case inside its owned command module using
the existing fixture input and a temporary output file; assert the relevant
artifact or error boundary without changing external test files. The final
integration gate and visible parity adapter establish broader core-output
compatibility; they do not replace CLI-specific behavior evidence.

### Fast test suite

ROOT runs both commands through the bridge after the provider exits:

- `cargo test -p biofabric` to compile and execute the CLI package's available
  tests; and
- `cargo run -p biofabric -- layout tests/parity/networks/sif/triangle.sif` to
  exercise the fixed parser, dispatcher, and a real handler over a visible
  input.

A change to a handler invalidates these checks and the focused command behavior
it serves, but does not by itself invalidate unrelated parity selectors.

## Failure scope and recovery

For a handler failure, retain integrated core code and resume this lane with the
failing command or compile result. For a core output mismatch reported through a
command, return the affected field to STEP-02, STEP-03, or STEP-04 and preserve
the handler. Rerun the package test/triangle-layout path after a local repair.

### Fast lane for revisiting old work

Repair the named handler, run `cargo test -p biofabric` and the triangle layout
invocation, then rerun only any direct command or final-gate selector whose
output that handler changes.
