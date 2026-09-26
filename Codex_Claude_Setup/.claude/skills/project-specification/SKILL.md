---
name: project-specification
description: Turn a broad product idea, change request, or mixed source material into a detailed, deterministic specification of dictated product boundaries and behavior. Use when actors, workflows, state rules, edge and failure behavior, preserved behavior, constraints, and acceptance scenarios must be explicit before implementation planning. This is the recommended precursor to project-topology when the input is not already implementation-ready. Produce a stable SPEC.md plus BEHAVIOR-* package; do not design repository implementation steps or execute the product work.
---

# Specify dictated product behavior

Create an implementation-ready product specification that preserves what the user
actually wants and gives a later planner enough behavioral precision to design the
work without rediscovering product intent. Depth comes from explicit behavior,
boundaries, rules, state, edge cases, and observable acceptance—not from more
reports, approvals, or administrative records.

This is a specification skill, not an implementation-planning or delivery skill.
It may inspect an existing product to establish current behavior and protected
invariants, but it does not choose repository change points, create implementation
steps, assign delivery agents, or execute the change. Follow it with
`project-topology` when an implementation plan is needed.

## Stable modular specification package

Every substantial specification uses the two-layer package defined in the
[modular specification template](references/modular-spec-template.md): one root
`SPEC.md` and one or more outcome-based `BEHAVIOR-*` files.

`SPEC.md` owns product-wide intent, source authority, current-to-target boundaries,
actors, terminology, shared rules, cross-behavior interactions, product-wide
acceptance, and unresolved product decisions. Each `BEHAVIOR-*` file owns one
coherent user-visible or operational outcome and all dictated behavior local to it.
These are behavior slices, not code modules, agent roles, or implementation phases.

The template is the sole authority for filenames, canonical headings,
deterministic ordering, and stable behavior IDs. That structure makes a large
specification navigable and editable; it is not a product-success gate. Harmless
heading, ordering, naming, or formatting drift is a local repair when the meaning
remains clear.

Do not add companion requirement tables, acceptance ledgers, review records,
evidence packets, status histories, source hashes, or approval forms. Add an
artifact only when a named external consumer genuinely needs a separate lifecycle.

## Preserve requirement authority

Keep these categories distinct in ordinary language:

- **Dictated requirement:** behavior, boundary, or constraint explicitly required
  by the user or a governing source.
- **Necessary derived behavior:** behavior logically required to make a dictated
  requirement coherent, safe, or observable. Explain the dependency.
- **Working assumption:** a reasonable premise not dictated by the source. Label it
  and identify the earliest useful way to confirm it.
- **Optional recommendation:** a possible improvement that is not required for the
  requested product outcome.
- **Implementation freedom:** a design choice the specification intentionally
  leaves to the implementation planner or executor.

Do not silently promote an assumption, common convention, reviewer preference, or
optional enhancement into a product requirement. Do not weaken an explicit
requirement merely because a simpler implementation would be convenient.

When sources conflict, apply any authority or precedence stated by the user,
repository, contract, or governing policy. If no precedence resolves a conflict
and the choice materially changes product behavior, surface that decision instead
of inventing an answer. Resolve ordinary wording differences from context.

For a change to an existing product, distinguish behavior intentionally changed
from behavior that must remain compatible. Observed current behavior is not
automatically a requirement, but a relied-upon behavior or explicit compatibility
promise must not disappear accidentally.

## Validate behavioral sufficiency, not document perfection

A usable specification makes every material dictated outcome sufficiently explicit
that a capable planner can identify the implementation work and decisive
acceptance evidence without guessing the product design. It need not exhaust every
conceivable scenario, prescribe internal implementation, or have flawless prose.

Classify issues by what they can invalidate:

- **Product-fidelity defect:** dictated behavior is omitted, contradicted, or
  materially distorted. Hold that behavior and consumers that depend on it.
- **Behavioral-decidability gap:** a material outcome lacks enough rules or
  observable acceptance to distinguish correct from incorrect. Hold that claim,
  not unrelated specified behavior.
- **Unresolved product decision:** a missing choice materially changes scope,
  user-visible behavior, compatibility, safety, or the product contract. Ask for
  the decision or keep only its consumers unresolved.
- **Working uncertainty:** a labeled assumption can be checked during planning or
  implementation without changing the core product decision. Keep it visible and
  continue.
- **Structural reference defect:** an ambiguous behavior identity, broken package
  link, or orphaned file impairs navigation. Repair that reference locally; it does
  not erase valid behavioral content.
- **Presentation defect:** formatting, heading wording, ordering, or prose polish
  is nonblocking when the intended meaning remains usable.
- **Unrelated failure or optional enhancement:** disclose it when useful, but it
  does not expand required scope or block the specification.

After any correction, reconsider only behaviors and conclusions that consumed the
changed fact. A corrected intermediate draft, failed command, or repaired link does
not require a pristine restart.

## Build the specification

### 1. Establish sources, authority, and requested outcome

Identify the user request, supplied source material, governing product or policy
documents, and relevant existing-product behavior. State the intended product
outcome and the authority boundary. Treat background material as context unless it
actually governs the requested behavior.

Ask a question only when the answer materially changes product behavior, scope,
compatibility, safety, or authority. Otherwise make the smallest reasonable
assumption, label it, and place confirmation at the earliest useful point.

### 2. Inspect the existing product when the specification changes one

Inspect enough current source, interfaces, schemas, tests, configuration, user
flows, and operational behavior to distinguish the baseline from the requested
change. Follow the relevant end-to-end path and identify relied-upon behavior,
shared state, external contracts, and failure behavior that the change may affect.

Do not turn the specification into a repository inventory or implementation plan.
Record current facts only when they establish a product boundary, protected
behavior, terminology, constraint, or target behavioral delta.

### 3. Define product boundaries and behavior slices

Read the [detailed specification guide](references/detailed-specification-guide.md)
and use it to establish actors, flows, domain rules, states, inputs and outputs,
failure behavior, constraints, non-goals, and acceptance scenarios relevant to the
request.

Divide the product into coherent behavioral outcomes. A behavior slice should be
meaningful to a user, operator, caller, or downstream system and independently
explainable without an arbitrary handoff. Do not slice by code directory, agent
role, equal size, or document convenience.

### 4. Author the canonical package

Use the [modular specification template](references/modular-spec-template.md).
Put cross-behavior truth in `SPEC.md`; put outcome-local detail in its canonical
`BEHAVIOR-*` file. Reference shared rules instead of copying them.

For each behavior, make the relevant dictated flow, decision rules, state changes,
data meaning, edge and failure behavior, preserved behavior, constraints, and
acceptance scenarios concrete. Leave internal architecture and coding choices open
unless the user or governing source actually constrains them.

### 5. Check behavioral coverage and coherence

Before structural checking, review the specification against the source request:

- every dictated outcome is owned by a behavior file;
- product boundaries and non-goals prevent plausible scope drift;
- current behavior to preserve or replace is explicit where it matters;
- shared terms, state, and rules do not conflict across behaviors;
- alternate, failure, and recovery behavior is defined where it changes the
  product contract;
- acceptance scenarios can decide each material outcome;
- assumptions, derived behavior, recommendations, and implementation freedom are
  not disguised as dictated requirements; and
- unresolved decisions are limited to choices that truly require external product
  authority.

This is a semantic review, not a form to complete. Irrelevant domain prompts and
cosmetic differences do not create gaps.

### 6. Run the structural checker as a local diagnostic

When the package is written to files and Python is available, run the bundled
`scripts/check_spec_structure.py` against the specification directory. It checks
only package usability: the root file, behavior identities, root-to-behavior links,
orphans, and relative file targets.

The checker does not judge product completeness, prose, exact headings, optional
sections, or requirement quality. A diagnostic affects only the ambiguous or
broken reference it identifies. Correct it in place when useful; do not restart
specification work, discard valid behavior, or create a checker report. If the
script is unavailable, inspect the same structural facts directly.

### 7. Run the Specification Fidelity Checker loop

Once the package is detailed enough to plan from, perform one independent,
read-only fidelity critique when the runtime provides an independent checker. If
not, ROOT performs the critique as a deliberately separate pass. Give it the
current specification and the governing request or source material—no evidence
packet or custom report schema.

The checker looks only for material specification problems:

- dictated behavior or a product boundary omitted, weakened, or contradicted;
- protected current behavior changed without authority;
- an assumption, recommendation, or implementation preference presented as a
  dictated requirement;
- conflicting behavior, terminology, state, or acceptance across files;
- a material flow, edge, failure, permission, or state transition left ambiguous;
- acceptance scenarios unable to distinguish the required result; or
- duplicated behavioral truth likely to drift between authoritative locations.

A useful criticism identifies the source behavior at risk and the smallest
correction, but those are decision criteria rather than mandatory report fields.
ROOT adjudicates every criticism:

- **Valid:** source-grounded product meaning is missing, conflicting, invented, or
  undecidable. Apply the smallest correction that restores fidelity.
- **Invalid:** the criticism is stylistic, optional, implementation-prescriptive,
  outside governing scope, or already answered clearly enough. Keep the current
  specification. A brief working reason is enough.

Repeat the checker only when ROOT accepts at least one valid fidelity finding.
Stop when a pass yields zero ROOT-valid findings. Rejected findings do not keep the
loop open; the checker cannot veto delivery or reopen a closed criticism without a
relevant source or specification change. Do not attach transcripts, verdict
records, iteration histories, or approval artifacts to the specification.

## Hand off to implementation planning

When a plan is requested, read
[Spec-to-plan handoff](references/spec-to-plan-handoff.md). The specification owns
dictated product behavior; the implementation plan owns repository change design,
step ordering, agent ownership, technical verification, integration, and recovery.
The plan references specification behavior IDs and anchors rather than restating
their requirements or acceptance scenarios.
A `BEHAVIOR-*` slice defines product meaning, not the size of an implementation
STEP. One behavior may need several separately usable and checkable steps; do not
merge those outputs into a milestone just to keep a one-to-one mapping.

## Output

Deliver the canonical `SPEC.md` plus `BEHAVIOR-*` package. Preserve behavioral
depth and stable information ownership. Do not add a separate summary, requirement
database, validation report, or review record unless a named external consumer
requires it.

End with genuinely unresolved product decisions only. Formatting repairs,
optional enhancements, implementation choices, and unrelated repository failures
are not unresolved product requirements.
