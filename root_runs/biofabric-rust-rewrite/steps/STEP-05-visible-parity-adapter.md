# STEP-05 - Genuine visible-parity adapter

## Outcome

Replace the permitted parity-runner stubs with an adapter that invokes the
completed core implementation and performs the existing visible comparisons.
This yields direct integrated evidence for BEHAVIOR-01 through BEHAVIOR-03
without changing protected test sources or fixtures.

## Scope and touchpoints

Own only `crates/core/tests/parity_tests/runners.rs`. The fixed
`ParityConfig` in `main.rs`, macros/common helpers, all test modules, and all
fixtures are protected evidence. Consume the stable I/O, layout, and alignment
APIs from STEP-02 through STEP-04; do not alter them to make an adapter compile.

## Implementation

Implement configuration parsing, input loading, layout selection, fixed
NOA/EDA handling, analysis/submodel helpers, and NOA/EDA/BIF formatting by
calling the real core behavior. Preserve the existing macro/config semantics
and normalization logic; do not weaken an assertion, skip a missing capability,
or synthesize a passing output. The runner remains an adapter rather than a
second reference implementation.

## Dependencies and integration

Consumes integrated STEP-02, STEP-03, and STEP-04. Its write path is disjoint
from STEP-06, so ROOT may launch both final lanes together. A core output
mismatch is returned to the owning core step; the runner lane only repairs
translation, configuration, or formatting defects local to `runners.rs`.

## Requirement-fit validation

The existing parity macros are the decisive local evidence because they compare
the runner's real outputs with protected fixtures. Default and alignment
selectors cover distinct core paths; passing one does not silently waive the
other or the final workspace gate.

### Fast test suite

ROOT runs both commands through the bridge after the provider exits:

- `cargo test -p biofabric-core --test parity_tests -- default` for the default
  NOA/EDA/BIF adapter path; and
- `cargo test -p biofabric-core --test parity_tests -- alignment` for the
  alignment adapter path.

For a specialized failure, use the exact existing test name as the fast
selector. A runner/core output change invalidates the corresponding selector,
not unrelated CLI build evidence.

## Failure scope and recovery

For a configuration/formatting adapter defect, retain the integrated core and
resume this lane with the failing selector. For a core output mismatch, return
the expected/actual field to STEP-02, STEP-03, or STEP-04 and preserve the
runner. Rerun only the affected parity selector after repair.

### Fast lane for revisiting old work

Repair the implicated `runners.rs` path, run its exact parity selector, and
then rerun only final-gate checks that consume the changed output.
