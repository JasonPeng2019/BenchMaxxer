# Detailed specification guide

Use this guide to turn broad intent into precise product behavior without turning
the specification into an implementation plan or compliance dossier. Apply only
the domain prompts that can affect the requested outcome. The
[modular specification template](modular-spec-template.md) defines where the
resulting information lives.

## Establish governing intent

Start from the smallest authoritative set of inputs that establishes what the
product must do:

1. Read the current user request and any supplied product, policy, contract, or
   operational source material.
2. Identify stated precedence, mandatory constraints, and decisions the user has
   explicitly left open.
3. Separate background explanation from language that actually dictates behavior.
4. Surface genuine contradictions that change the product instead of blending them
   into a vague compromise.
5. Use repository history only when current product behavior or source material
   cannot resolve a material ambiguity.

Do not copy sources into the specification or create a provenance record for every
sentence. Cite or link a governing section when it prevents later ambiguity. The
specification should make product meaning usable, not preserve a research diary.

### Keep requirement classes visible

Use ordinary language to preserve the difference between:

- an explicit user or governing-source requirement;
- behavior necessarily derived from that requirement;
- an observed current behavior or compatibility dependency;
- a working assumption;
- an optional recommendation; and
- an internal implementation choice.

A derived behavior needs a real dependency. For example, an explicit requirement
that a retried payment must never charge twice necessarily implies an observable
idempotency rule. It does not automatically dictate a particular database,
locking strategy, or queue.

Do not turn conventional polish into dictated scope. Features such as analytics,
notifications, administration, export, configurability, or broad platform support
remain optional unless the requested outcome or governing environment actually
requires them.

## Establish current and target behavior

For a change to an existing product, inspect the relevant end-to-end behavior far
enough to answer:

- What can each actor do or observe today?
- Which inputs, states, and external systems participate?
- Which current behaviors are explicitly changing?
- Which compatibility promises or relied-upon behaviors must remain?
- Which current defects or ambiguities are part of the requested change?
- Which adjacent behavior is outside scope even if it could be improved?

Use current source, tests, schemas, configuration, and executable behavior as
evidence of the baseline, but do not assume every implementation accident is a
product requirement. Preserve behavior because a governing source or real consumer
requires it, not merely because it exists.

Write the target as a behavioral delta: what becomes possible, impossible,
different, or newly guaranteed. Avoid implementation language such as class names,
internal functions, table layouts, or framework choices unless they form part of a
public contract or explicit constraint.

## Define product boundaries

A useful boundary identifies:

- actors, callers, operators, and external systems inside the behavior;
- the journeys, events, and operational outcomes being specified;
- authority and permission limits;
- data, platform, compatibility, policy, timing, and lifecycle constraints that
  actually govern the product;
- plausible non-goals that an implementer might otherwise infer; and
- decisions that remain implementation freedom.

Do not add a generic non-goal inventory. Include a non-goal only when it prevents a
credible misunderstanding or unintended expansion.

## Form coherent behavior slices

A behavior slice is a complete observable outcome, not a code module. Good
boundaries usually follow an actor goal, system response, lifecycle transition, or
operational capability.

A behavior is too broad when it contains several outcomes with independent actors,
rules, or acceptance. It is too narrow when it describes one screen control, API
call, field, validation message, or internal operation that has no independently
meaningful outcome.

Strong behavior slices usually answer the relevant parts of these questions:

- Who or what initiates the behavior, and why?
- What preconditions and permissions apply?
- What normal sequence is observable?
- Which rules choose among branches?
- What state or externally meaningful data changes?
- What can each participant observe afterward?
- What happens for invalid, repeated, partial, concurrent, unavailable, or
  cancelled execution where applicable?
- Which existing behavior or compatibility promise must remain?
- What scenarios decisively distinguish correct from incorrect behavior?

Keep shared terminology and invariants in `SPEC.md`. Keep the complete local flow
in one behavior file rather than splitting happy path, errors, and acceptance into
separate artifacts.

## Detail flows and decision rules

Describe behavior at the level necessary to remove product ambiguity. Depending on
the outcome, this may include:

- trigger and preconditions;
- ordered actor and system actions;
- validation order when it changes what an actor sees;
- defaults, precedence, calculations, limits, and rounding;
- branching conditions and resulting behavior;
- repeated-action, duplicate, idempotency, and ordering rules;
- cancellation, timeout, retry, and resume behavior;
- authoritative state and conflict resolution;
- user-visible messages or error categories when wording or distinction matters;
- terminal states and permitted next actions; and
- side effects, notifications, audit consequences, or external effects when
  required by the product.

Use a sequence, state table, or decision table only when several transitions or
branches are clearer in that form. Do not create diagrams or tables merely to make
the specification appear formal.

### State and data semantics

Specify data by product meaning rather than storage design:

- identity and ownership;
- required, optional, defaulted, or derived values;
- allowed ranges, units, precision, formats, and normalization;
- visibility and mutability;
- source of truth and synchronization expectation;
- lifecycle, retention, deletion, and recovery behavior;
- uniqueness and duplicate meaning;
- partial or historical state; and
- externally meaningful compatibility or migration semantics.

Define schemas or message shapes when they are themselves a public or cross-system
contract. Leave indexes, tables, caches, internal events, and serialization choices
to planning unless explicitly constrained.

## Apply relevant domain detail

Use these prompts selectively. Absence of an irrelevant prompt is not a defect.

### User interface and interaction

- Entry route, initiating action, and actors allowed to perform it.
- Information hierarchy and product-significant content.
- Loading, empty, partial, success, error, disabled, stale, and retry states that
  can actually occur.
- Navigation, dismissal, interruption, back/forward behavior, and state restoration.
- Keyboard, focus, screen-reader, responsive, localization, and reduced-motion
  behavior where the product or applicable standard requires it.
- Optimistic or delayed updates and reconciliation with authoritative state.

Do not prescribe pixel values, component libraries, or styling implementation
unless supplied design material or a governing design system makes them required.

### APIs, commands, events, and integrations

- Caller and ownership boundary.
- Inputs, outputs, validation, defaults, and error distinctions.
- Authentication and authorization behavior.
- Idempotency, ordering, retries, timeouts, cancellation, and partial failure.
- Versioning, compatibility, deprecation, and consumer transition when applicable.
- Observable side effects and delivery guarantees.

Do not choose internal endpoints, handlers, transport libraries, or deployment
topology unless the contract dictates them.

### Data and lifecycle behavior

- Creation, transition, archival, deletion, restoration, and expiration rules.
- Concurrent changes and conflict outcomes.
- Import, export, migration, coexistence, and rollback semantics visible to
  consumers.
- Partial processing, resumability, duplicates, and reconciliation.
- Retention, privacy, residency, and audit behavior when governed.

### Background and asynchronous behavior

- Initiation, progress visibility, completion, and failure notification.
- Ordering and concurrency guarantees.
- Duplicate submission and retry outcome.
- Cancellation, timeout, abandonment, cleanup, and resume behavior.
- Behavior across restarts or dependency outages when product-significant.

### Security, privacy, and abuse boundaries

- Trust boundary, actor identity, and authorization decision.
- Sensitive input, output, storage, transmission, and disclosure behavior.
- Consent, retention, deletion, and audit obligations.
- Rate, abuse, enumeration, replay, or privilege concerns tied to the actual
  product behavior.

Do not turn the specification into a general hardening campaign. Record only
requirements supported by the real threat model or governing source.

### Performance, availability, and reliability

- User-visible latency, throughput, scale, or resource limits that actually matter.
- Availability and degraded-mode behavior.
- Consistency, freshness, durability, recovery, and data-loss tolerance.
- Fallback behavior and observable consequences.

Use measurable budgets when supplied or necessary to distinguish acceptable
behavior. Do not invent arbitrary numbers solely to make a requirement measurable.

### Operational and release behavior

- Feature availability, rollout population, configuration, and compatibility
  window when product-significant.
- Operator-visible health, progress, failure, containment, and recovery.
- Irreversible actions, rollback limits, and post-action verification.
- Documentation or communication that users or operators require to use the
  changed behavior safely.

## Write decisive acceptance scenarios

Acceptance belongs to the behavior it decides. For every material rule or outcome,
include enough scenarios to distinguish success from failure. A useful scenario
makes clear:

- the meaningful initial state and actor;
- the trigger, input, or action;
- relevant branch or boundary condition; and
- the observable product result, state, or external effect.

Cover normal behavior plus negative, boundary, recovery, permission, concurrency,
or compatibility cases only when they define the contract. Several requirements
may share one end-to-end scenario; refer to it instead of duplicating it.

Acceptance scenarios are behavioral oracles, not implementation test cases. Do not
name repository commands, test files, mocks, frameworks, or internal assertions.
The later plan translates these scenarios into technical evidence.

Avoid subjective outcomes such as “works correctly,” “is intuitive,” “is fast,” or
“handles errors gracefully” unless the specification defines observable meaning.

## Preserve implementation freedom

A detailed specification should be strict about dictated behavior and deliberately
open about internal means. State implementation freedom when a planner might
otherwise mistake an example or current implementation for a requirement.

Implementation freedom may include internal architecture, algorithms, data
structures, storage layout, libraries, naming, file organization, job topology, or
test framework. It does not include violating product behavior, public contracts,
compatibility, safety, or governing constraints.

Do not provide pseudocode or a repository change list unless the behavior itself is
algorithmically defined or the user explicitly requires a technical design as part
of the product contract.

## Handle uncertainty without stalling

Ask the user only when a missing choice can produce materially different valid
products. Otherwise choose the narrowest reasonable assumption and label it.

A specification may be usable with working assumptions. It is not usable where an
unresolved choice makes a material behavior contradictory or impossible to decide.
Hold only affected behaviors; continue specifying independent outcomes.

When new source information arrives, update the authoritative behavior and only
the cross-behavior conclusions that consume it. Do not rewrite unaffected files or
renumber stable behavior IDs merely to make revision history look clean.

## Final substance test

The specification is sufficiently detailed when a capable implementation planner
can, without inventing product intent:

- explain the product boundary and current-to-target behavior;
- identify every material dictated outcome;
- trace shared rules and behavior interactions;
- distinguish requirements, derived necessities, assumptions, recommendations,
  and implementation freedom;
- design implementation work for the full normal and material exceptional flows;
- choose decisive technical evidence for each acceptance scenario; and
- identify the few product decisions that genuinely remain external.

More prose is not automatically more detail. Prefer explicit rules, transitions,
and observable examples over repeated summaries or generic completeness language.
