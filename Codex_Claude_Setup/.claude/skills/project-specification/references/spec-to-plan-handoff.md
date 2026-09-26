# Specification-to-plan handoff

Read this reference only when an implementation plan will consume a
`project-specification` package. The handoff preserves one source of truth while
turning dictated behavior into repository work.

## Keep artifact authority separate

The specification owns:

- dictated product outcomes and boundaries;
- actors, workflows, product rules, state meaning, and observable effects;
- protected existing behavior and compatibility commitments;
- product constraints, non-goals, and acceptance scenarios; and
- product assumptions and unresolved product decisions.

The implementation plan owns:

- repository-grounded current and target architecture;
- concrete change points, internal contracts, and technical decisions;
- implementation steps, dependencies, ordering, and agent ownership;
- test design, confirmed commands, integration, rollout, and recovery; and
- sufficient development evidence for the specification's acceptance scenarios.

Do not copy specification prose or acceptance scenarios into the plan. Reference
the governing `BEHAVIOR-*` ID, file, or section and describe only the implementation
consequence. A plan may introduce necessary technical prerequisites, but it may not
promote them into new product requirements.

## Decide whether the specification is usable

A plan can proceed when the material dictated behaviors are sufficiently decidable
to choose an implementation route. It does not require a formatting-perfect or
administratively approved specification.

Before planning, resolve or isolate only:

- contradictory dictated behaviors that demand incompatible implementations;
- a missing product decision that materially changes the valid implementation;
- acceptance that cannot distinguish required behavior; or
- an ambiguous behavior identity or broken reference that prevents knowing which
  requirement governs the work.

A labeled working assumption, local wording problem, optional recommendation,
missing cosmetic detail, or irrelevant source failure does not block planning.
Carry the assumption to the earliest useful validation point and repair references
locally.

## Map behavior to implementation blocks

The root `PLAN.md` step map is the single required-change-to-work coverage index.
For each `STEP-*` block, identify the `BEHAVIOR-*` outcomes it directly advances.
A shared technical prerequisite is justified by the dependency edges from its
consuming steps; do not list every distant behavior on its row. The mapping must
establish both directions:

- every dictated behavior needing a change is advanced by at least one
  implementation step; already-correct behavior to preserve may instead have an
  integration check without a dummy implementation step; and
- every implementation step is justified by a specified behavior or a necessary
  technical prerequisite for one.

Do not create a second traceability matrix, requirement ledger, or acceptance map.
A `BEHAVIOR-*` is a product slice, not a STEP size. Split work when a substantial
output can be completed, checked, and used or accepted independently, even if the
same owner performs the assignments serially. When several steps jointly deliver
a behavior, the root step map shows the join; explain it further only if the
dependency is not obvious. Each step names only its local
contribution. One step may advance several behaviors only when their implementation
is one inseparable technical outcome with one coherent verification and repair
boundary;
reference their IDs without copying their text.

Behavior order does not automatically dictate implementation order. Derive step
order from technical dependencies, stable contracts, risk, and integration needs.

## Translate acceptance into development evidence

For every material specification acceptance scenario, the plan identifies the
least expensive decisive technical evidence. This may be an existing or new unit,
integration, contract, end-to-end, manual, migration, performance, security, or
live-environment check according to the behavior and risk.

The plan owns test setup, repository commands, fixtures, implementation assertions,
and environment needs. The specification continues to own the observable product
result. Link the two; do not rewrite either into a duplicate evidence record.

A single check may support several behaviors. Reuse the result instead of requiring
one execution or report per behavior. An adverse result invalidates only the
behaviors and implementation conclusions it can actually reach.

## Attach agent ownership to real work

Agent subroles are execution assignments, not product structure. Use them only when
specialist judgment, safe isolation, independent work, or meaningful wall-clock
benefit justifies delegation.

For delegated work, the plan maps the owner or lane directly to its `STEP-*` blocks
or bounded investigation and makes the outcome, write boundary, accepted inputs,
integration point, and return decision clear enough to execute. State single-owner
delivery once rather than repeating the same owner on every step.

Do not create free-standing role modules, a role registry, or one worker per
behavior. Behavior slices express product meaning; implementation blocks express
delivery outcomes; agent assignments express temporary execution ownership.

## Handle specification changes locally

When a specification fact changes:

1. identify the affected behavior IDs and shared rules;
2. invalidate only plan decisions, steps, and evidence that consume those facts;
3. update the root coverage and dependency mapping where necessary;
4. preserve unaffected implementation design and passing evidence; and
5. rerun only checks whose inputs or required outcomes changed.

Do not regenerate the whole plan, renumber stable behaviors or steps, or replay
unrelated work merely to restore a clean-looking history.

## Completion boundary

Specification fidelity, plan coverage, and implementation proof are related but
separate questions:

- specification fidelity asks whether dictated product meaning is captured;
- plan coverage asks whether the repository work owns every specified behavior;
  and
- implementation proof asks whether the current product satisfies that behavior.

Do not collapse them into one global status or require three reports. Use the
distinction to decide the smallest affected scope when something is missing or
wrong.
