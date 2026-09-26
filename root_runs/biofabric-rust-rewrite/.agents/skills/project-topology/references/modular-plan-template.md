# Stable modular plan template

This template fixes where plan information lives so plans remain predictable,
modular, and easy to edit. It does not turn Markdown conformance into a development
gate.

## Fixed package

Every project-topology plan has exactly this core package:

```text
<plan-directory>/
|-- PLAN.md
`-- steps/
    |-- STEP-01-<outcome-slug>.md
    `-- STEP-02-<outcome-slug>.md
```

`PLAN.md` owns cross-step truth. Each `STEP-*` file owns one bounded, executable
outcome.
Do not add companion files for requirements, evidence, reviews, acceptance, status,
handoffs, hashes, or validation. Add another artifact only when the user, repository,
regulator, or a named downstream consumer requires it.

The initial author should use the canonical headings below. Later agents must read
them semantically: a harmless rename, ordering difference, typo, or misplaced fact
is a local editing issue, not evidence that the plan or implemented product failed.
Only missing meaning that prevents implementation, dependency reasoning, or
requirement-fit validation is substantive.

## Deterministic step rules

1. Create one `PLAN.md` and at least one `STEP-*` file.
2. Make each step one independently usable, verifiable implementation outcome,
   not one file, role, command, review, report, administrative action, or whole
   subsystem milestone. Split substantial outputs that can be completed and
   accepted separately, even if one owner performs them serially. Do not split
   tightly coupled edits with no meaningful intermediate result.
3. Give a shared foundation its own step only when it produces a usable and
   verifiable result, typically consumed by multiple later outcomes.
4. During initial authoring, number steps in dependency order. Break ties by their
   first position in the end-to-end product flow, then by lexical outcome slug.
5. Use lowercase hyphenated slugs that describe the completed outcome.
6. After the plan is published, keep existing step IDs stable. Assign the next
   unused ID to added work and express any new predecessor relationship in the step
   map rather than renumbering unaffected files.
7. Keep each shared fact in `PLAN.md` once. Step files link to or name that source
   instead of copying it.

## Canonical `PLAN.md`

```markdown
# <Project or change> execution plan

## Outcome and boundaries

<The requested result or, when a specification governs, links to its outcome and
acceptance without copying them. State the implementation boundary, non-goals,
real constraints, and authority limits. Distinguish inspected facts, working
assumptions, and decisions that are genuinely unresolved.>

## Current system and target design

<The relevant current call, data, state, build, or operational flow; the target
flow; concrete change points; and why this is the smallest complete design. Name
paths, symbols, interfaces, schemas, and confirmed commands where they help an
executor act without rediscovery.>

## Shared decisions and contracts

<Cross-step interfaces, data shapes, state rules, compatibility choices, error
semantics, and design decisions. Keep each shared fact here once. If the plan has
no cross-step contract, say that briefly rather than inventing one.>

## Step map and execution order

<The selected execution shape and its short justification. Single owner is the
default. Name delegated ownership or write boundaries only when delegation is
actually planned. If work will run concurrently, name the planned lanes and the
shared boundary that makes them safe; do not enumerate every theoretically
compatible pair of steps.>

| Step | Produces | Depends on |
| --- | --- | --- |
| [STEP-01](steps/STEP-01-<slug>.md) | <usable outcome; directly advanced BEHAVIOR-* IDs if a spec exists> | <real prerequisite> |

<Use one row per step. When a spec governs, this is also the single coverage index
for required changes: map each changed behavior and each necessary prerequisite.
Already-correct behavior to preserve can be verified at integration without a
dummy implementation step. Explain a multi-step join only when it is not obvious.
For a shared prerequisite, consuming rows' dependency cells show why it exists;
do not list every distant behavior. Do not repeat implementation detail or
validation here.>

## Integration and whole-product validation

<How step outputs join; integration order; the combined behaviors that must be
observed; and the focused, relevant, or whole-product evidence sufficient for the
requested result. Identify a mandatory repository or release gate and its consumer
separately from behavioral proof when they are not equivalent. Refer to step-local
checks instead of copying them here.>

## Risks, assumptions, and unresolved decisions

<Only items that can change implementation, ordering, authority, shared state,
acceptance, or recovery. State the smallest affected scope and earliest useful
resolution point. If there is no special plan-wide item, one sentence is enough.>
```

## Canonical `steps/STEP-<NN>-<outcome-slug>.md`

```markdown
# STEP-<NN> - <Completed implementation outcome>

## Outcome

<The one independently usable and checkable output when this step is finished,
why it is needed, and which part of the root outcome it advances. If this names
several separately acceptable outputs, split the step.>

## Scope and touchpoints

<Relevant current behavior and concrete files, components, symbols, interfaces,
schemas, configuration, generated outputs, or operational surfaces. Identify a
protected surface only when an executor could plausibly change it by mistake.>

## Implementation

<The actionable design: logic and control flow, data or state transitions,
interface changes, validation and error behavior, compatibility, important edge
cases, and any migration, rollout, cleanup, or documentation work this outcome
actually requires. Leave choices local when they do not affect a contract,
dependency, risk, or acceptance condition.>

## Dependencies and integration

<Inputs consumed from earlier steps or external decisions; the exact usable output
this step produces; downstream consumers; and ownership or write boundaries when
relevant. Keep plan-wide lane grouping in `PLAN.md`.>

## Requirement-fit validation

<The material behavior claims and sufficient evidence for each. Refer to root
acceptance rather than copying it. Distinguish the local fast check below from
combined, live, or release proof only when those boundaries are required.>

### Fast test suite

<Name the smallest independently runnable test selection for this step's outcome,
its decisive assertion, and the inputs that would invalidate its result. State a
confirmed selector or command when known; if a test must be added in this step,
describe it concretely. For a live-only outcome, name the fastest repeatable local
check, its limit, and the real proof boundary. Do not substitute a whole-project
suite or create an extra suite artifact just for this heading.>

## Failure scope and recovery

<Only realistic failures needing more than the fast lane below, such as live-state
containment, migration rollback, or a changed architecture. Name the affected
consumers and route; otherwise rely on the fast lane without a second procedure.>

### Fast lane for revisiting old work

<Where to re-enter after a bounded defect in this step, what valid output and
passing evidence to retain, the narrow repair, and which fast tests and direct
integration consumers to rerun. Do not replay unaffected steps or old suites.
If no special route is needed, state the affected fast selection and direct
consumers in one sentence.>
```

## Execution interpretation

This template organizes authoring; it does not decide product success. Apply the
skill's [requirement-fit rules](../SKILL.md#validate-requirement-fit-not-literal-perfection):
corrected mistakes and format drift do not invalidate behavior, and only evidence
whose inputs changed needs to be rerun. Do not create a status or acceptance record.
