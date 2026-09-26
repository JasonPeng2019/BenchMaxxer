# Stable modular specification template

This template fixes where specification information lives so a detailed product
definition remains predictable, modular, and easy to revise. It does not turn
Markdown conformance into product acceptance.

## Fixed package

Every substantial project specification has this core package:

```text
<spec-directory>/
|-- SPEC.md
`-- behaviors/
    |-- BEHAVIOR-01-<outcome-slug>.md
    `-- BEHAVIOR-02-<outcome-slug>.md
```

`SPEC.md` owns cross-behavior product truth. Each `BEHAVIOR-*` file owns one
coherent user-visible or operational outcome. Do not add companion files for
requirement status, acceptance approval, review disposition, evidence, source
hashes, or validation output. Add another artifact only when a named external
consumer needs an independently maintained deliverable.

The initial author should use the canonical headings below. Later agents read them
semantically: a harmless rename, ordering difference, typo, or misplaced fact is a
local editing issue, not proof that the specification or product failed. Missing or
contradictory meaning that changes product behavior is substantive.

## Deterministic behavior rules

1. Create one `SPEC.md` and at least one `BEHAVIOR-*` file.
2. Make each behavior file one coherent outcome for a user, operator, caller, or
   downstream system—not one code component, agent role, document topic, or phase.
3. Keep terminology, global invariants, source precedence, and rules consumed by
   several behaviors in `SPEC.md`; link to them from behavior files.
4. During initial authoring, number behaviors in the order users or systems
   encounter them when that order is meaningful. Otherwise order prerequisites
   before consumers, then break ties by first appearance in the governing request
   and lexical outcome slug.
5. Use lowercase hyphenated slugs that describe the completed behavioral outcome.
6. After publication, keep existing behavior IDs stable. Give added behavior the
   next unused ID and express new ordering or interaction in the behavior map rather
   than renumbering unaffected files.
7. Put each product fact in one authoritative location. Other files reference that
   location rather than paraphrasing it into a second requirement.

## Canonical `SPEC.md`

```markdown
# <Product or change> specification

## Product intent and authority

<The product outcome, why it matters, governing user request and source material,
and any real precedence among those sources. Explain how dictated requirements,
necessary derived behavior, assumptions, recommendations, and implementation
freedom are distinguished. Do not copy entire source documents.>

## Current behavior and required change

<The relevant existing user-visible or operational behavior; protected invariants
and compatibility commitments; what changes; what remains unchanged; and the
intended current-to-target behavioral delta. For greenfield work, state the target
baseline without inventing legacy behavior.>

## Actors, boundaries, and non-goals

<Actors and external systems; in-scope journeys and operational outcomes; authority,
platform, policy, timing, or product constraints that actually govern behavior;
and plausible adjacent work that is intentionally outside the product boundary.>

## Shared terminology and product rules

<Domain terms, shared state meanings, global invariants, permissions, precedence,
cross-behavior business rules, and externally meaningful contracts used by more
than one behavior. Keep local rules in their behavior file.>

## Behavior map and relationships

| Behavior | Dictated outcome | Depends on or interacts with |
| --- | --- | --- |
| [BEHAVIOR-01](behaviors/BEHAVIOR-01-<slug>.md) | <observable product outcome> | <real prerequisite or interaction> |

<Use one row per behavior. This is the navigation and relationship index, not a
second requirement description or acceptance ledger.>

## Product-wide constraints and acceptance

<Only constraints and end-to-end acceptance that genuinely span several behaviors:
for example accessibility, security, privacy, compatibility, performance,
reliability, lifecycle, or a complete cross-behavior journey. Refer to local
acceptance scenarios instead of copying them.>

## Assumptions and unresolved product decisions

<Labeled working assumptions and only decisions that materially change dictated
behavior, scope, compatibility, safety, or authority. State the affected behaviors
and earliest useful resolution point. If no special item remains, say so briefly.>
```

## Canonical `behaviors/BEHAVIOR-<NN>-<outcome-slug>.md`

```markdown
# BEHAVIOR-<NN> - <Completed user-visible or operational outcome>

## Dictated outcome and source

<What must be observably true, who benefits or relies on it, and which governing
request or shared rule dictates it. Distinguish explicit requirements from any
necessary derived behavior or working assumption without creating a provenance
ledger.>

## Actors, triggers, and preconditions

<Relevant actors and external systems; event or user action that starts the
behavior; required state, permissions, inputs, or prior outcomes; and conditions
under which the behavior does not apply.>

## Behavioral flow and decision rules

<The normal observable flow, branches, ordering, business rules, calculations,
defaults, precedence, idempotency, and repeated-action behavior needed to remove
product ambiguity. Use a short sequence or decision table only when it clarifies
real branching.>

## State, data, and observable effects

<Product-significant state transitions; data meaning, ownership, lifetime, and
visibility; inputs and outputs; side effects; synchronization expectations; and
what each actor can observe. Avoid dictating internal storage or code design unless
it is a governing constraint.>

## Edge, failure, and recovery behavior

<Material invalid, empty, partial, duplicate, concurrent, unavailable, timeout,
cancellation, retry, and recovery cases. Specify the user-visible or operational
result, retained state, and allowed next action where those cases can occur. Omit
irrelevant theoretical cases.>

## Constraints and preserved behavior

<Behavior-local compatibility, authorization, privacy, security, accessibility,
localization, performance, reliability, platform, or lifecycle requirements that
actually apply; plus existing behavior that must remain unchanged. Reference
product-wide rules rather than duplicating them.>

## Acceptance scenarios

<Concrete scenarios that distinguish correct from incorrect behavior. For each
material scenario, make the meaningful precondition, action or event, and
observable result clear. Include negative and boundary scenarios when they define
the product contract. Do not prescribe implementation tests or commands here.>

## Implementation freedom and unresolved decisions

<Choices intentionally left to implementation; optional recommendations that are
not acceptance requirements; labeled assumptions; and only unresolved product
decisions that can change this behavior. A brief statement is enough when no
special decision remains.>
```

## Interpretation

The headings are stable information homes, not completion forms. A section may be
brief when the behavior genuinely has little to say there. Do not manufacture edge
cases, constraints, or unresolved decisions to fill the template. Conversely, do
not omit material dictated behavior merely to shorten the specification.

The specification defines product meaning; it does not prove implementation.
Planning and development validation later determine how the repository changes and
whether the resulting product satisfies these behaviors.
