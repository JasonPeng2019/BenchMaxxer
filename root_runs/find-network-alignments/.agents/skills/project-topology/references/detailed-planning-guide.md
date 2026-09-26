# Detailed planning guide

Use this guide to make a plan technically complete without turning it into a
compliance package. It supplies the reasoning and content standard; the
[modular plan template](modular-plan-template.md) supplies the stable file and
section structure. Combine related facts, keep irrelevant canonical sections
brief, and do not invent extra artifacts for concerns that have no bearing on
implementation or acceptance.

## Inspect the current system

Start from the smallest set of authoritative material that can establish how the
affected system works:

1. Read applicable repository instructions, the user’s source material, and the
   product or operational specification.
2. Locate the implementation entrypoints and trace the relevant call, event, data,
   or build path through the system.
3. Inspect nearby tests to learn existing behavior, fixtures, test boundaries, and
   the project’s normal verification commands.
4. Check configuration, schemas, migrations, generated sources, public types,
   dependency manifests, and deployment files only when the change can affect them.
5. Inspect current runtime or automation behavior before claiming it supplies a
   capability. A named script or directory is not proof that it performs the
   needed isolation, retry, rollout, or cleanup.
6. Use history only to resolve a specific ambiguity that current sources cannot
   answer.

The resulting plan should cite concrete paths and symbols where they help the
executor. It should not contain a research diary, a list of every file opened, or
copies of source text that the executor can read directly.

## Define the finish line

Translate the request into a compact implementation boundary:

When a `project-specification` package governs, link to its dictated outcomes and
acceptance instead of rewriting them. State only the implementation boundary,
technical constraints, authority, and unresolved decisions the plan must own.

- **Outcome:** the behavior, artifact, migration, or operational state that must
  exist when the work is complete.
- **Acceptance:** observable facts that distinguish complete from incomplete when
  no governing specification already owns them.
- **Non-goals:** plausible adjacent work that is intentionally outside this change.
- **Constraints:** compatibility, platform, performance, accessibility, security,
  data retention, tooling, timing, or organizational limits that actually apply.
- **Authority:** actions the executor may take and actions that still require a
  user or external decision.

Do not manufacture requirement IDs. Reuse `BEHAVIOR-*` IDs when a governing
specification supplies them; otherwise use labels only when a large plan needs stable
cross-references. Do not duplicate the same acceptance condition in a requirement
table, step table, evidence table, and review table; keep it once and link or refer
to it naturally.

Distinguish:

- **Observed:** established from current source, configuration, tests, or supplied
  material.
- **Assumed:** a reasonable working premise that the executor can validate early.
- **Unresolved:** a missing decision that changes the safe plan.

Ask about unresolved items only when their answer changes scope, architecture,
authority, or the next safe action. Avoid making the user decide implementation
details that repository inspection can settle.

## Map the affected architecture

Describe just enough current architecture to explain the proposed changes. Follow
the behavior across relevant boundaries:

- entrypoints and request/event sources;
- domain or business logic;
- state and persistence;
- public and internal interfaces;
- background jobs, queues, caches, or generated artifacts;
- UI state and user interaction;
- external services or live resources; and
- build, packaging, deployment, and observability paths.

For each material boundary whose behavior or contract can change, cover the
relevant owner, consumed and produced values, compatibility expectation, and
failure behavior. Omit dimensions that do not apply and untouched boundaries that
do not affect implementation. This prevents a locally plausible step from silently
breaking a downstream consumer without creating a boundary inventory.

Use a small table or flow only when it makes several dependencies clearer. Do not
draw a graph merely to prove that the plan is “topological.”

## Form implementation blocks

An implementation block is one substantial, independently usable and verifiable
output that an executor can finish without an arbitrary handoff. Boundaries should
follow behavior, ownership, and dependencies—not line count, file count, or equal
effort. A product behavior may require several blocks.

A strong block usually answers the relevant parts of this list:

- What behavior or capability is complete after this block?
- Which current path, component, or contract is changing?
- Which files, modules, classes, functions, schemas, configuration keys, or
  generated outputs are likely to change?
- What logic, state transition, data transformation, error handling, or fallback
  should be implemented?
- What remains compatible, and what consumers must change together?
- What inputs or prior decisions does the block require?
- Which later blocks consume its result?
- What focused check proves it?
- If it touches data or live state, how does rollout, rollback, retry, or cleanup
  work?

Write each block as one canonical `STEP-*` file using the
[modular plan template](modular-plan-template.md). The stable headings make the
plan easy to navigate and edit; they do not require boilerplate or repeated shared
context. A heading variation is a local formatting repair, while a missing
implementation dependency or undecidable acceptance claim is a substantive plan
gap. Keep that distinction explicit.

### Granularity test

A plan is too vague when the executor must still discover the core design. Replace
steps such as:

- “update the backend”;
- “wire up the UI”;
- “add validation”;
- “handle errors”; or
- “write tests”

with the actual integration points and behavior. For example, identify the handler
and service boundary, the request and response change, where validation runs, how
errors map to the public contract, which UI state consumes it, and which test
scenario observes the result.

A plan is too granular when it dictates obvious keystrokes, repeats source code,
assigns a separate step to each file, or freezes local implementation choices that
do not affect a contract, dependency, risk, or acceptance claim. Leave ordinary
coding judgment to the executor inside the stated behavioral boundary.

A plan is too coarse when one STEP contains several substantial outputs with
different completion points, proof, or downstream consumers. Ask whether an
intermediate output could be completed, checked, and used or accepted while the
remaining work is still unfinished. If yes, split there—even if the same executor
would perform both assignments serially. A shared implementation seam or test is
not by itself a reason to merge separately acceptable outputs. Conversely, keep
tightly coupled edits and their focused test together when no useful intermediate
result exists. One STEP should be a doable delivery unit, not a subsystem milestone.

## Apply relevant domain detail

Use these prompts selectively.

### APIs and service boundaries

- Specify endpoint, command, event, or public function changes.
- Describe request/response or message shapes, validation order, error mapping,
  idempotency, authentication/authorization, and compatibility.
- Name producers and consumers that must change together.
- Cover versioning or deprecation only if existing clients require it.

### Data and migrations

- State schema, constraint, index, serialization, or state-machine changes.
- Define migration order, old/new version coexistence, backfill or transformation,
  failure recovery, and rollback limits.
- Explain how partial progress is detected and safely resumed when that risk exists.
- Do not add snapshots, receipts, or hashes unless rollback, integrity, or audit
  actually consumes them.

### UI and interaction

- Identify the route, component, state owner, data dependency, and user action.
- Cover loading, empty, error, success, disabled, and retry states that the feature
  can actually reach.
- Preserve accessibility, keyboard behavior, responsive layout, and localization
  where the project or requested behavior requires them.
- State how the UI reflects authoritative server or local state and avoids stale or
  conflicting updates.

### Concurrency and background work

- Name the unit of concurrency, ordering guarantee, ownership of shared state, and
  duplicate or retry behavior.
- Describe cancellation, timeouts, cleanup, and idempotency when failures can leave
  partial work.
- Add locking or serialization only around a demonstrated shared mutation.

### Security and privacy

- Apply the actual trust boundary and threat model.
- Identify authentication, authorization, input handling, secret, data exposure,
  retention, and audit implications that fall inside scope.
- Do not turn every plan into a general hardening campaign. A real issue outside the
  governing scope may be noted without becoming a prerequisite.

### Performance and reliability

- Identify the concrete hot path, scale assumption, latency or resource budget, and
  measurement needed.
- Add caching, batching, retry, fallback, circuit breaking, or load testing only
  when a known requirement or observed risk warrants it.
- Avoid speculative infrastructure whose operation is more complex than the risk it
  is meant to reduce.

### Build, configuration, and deployment

- Name relevant flags, environment variables, manifests, generated outputs, CI
  jobs, release steps, and runtime dependencies.
- Distinguish source changes from generated or deployed projections.
- Define rollout order, compatibility window, observation, rollback, and cleanup
  for changes that cross a release boundary.

### Documentation

- Update user, operator, API, migration, or architecture documentation when its
  readers need the changed behavior.
- Do not create a changelog, report, handoff, or duplicate reference document solely
  because the plan has multiple steps.

## Order the work by real dependencies

Derive the sequence from consumed outputs:

1. Resolve a prerequisite only if a later step cannot proceed without it.
2. Define or update shared contracts before independent consumers implement against
   them.
3. Prefer an early executable path through the highest-risk shared seam when it can
   expose architectural mistakes cheaply.
4. Run independent implementation or verification work concurrently only after its
   inputs are stable.
5. Integrate in the order needed to keep the combined project buildable and
   diagnosable.
6. Place broad regression, rollout, or live checks after the smallest relevant
   integrated unit exists.

Distinguish a dependency from a preferred ordering. If two blocks do not consume
each other’s output and have safe write boundaries, say they may run in parallel.
If they share a contract or generated output, assign one owner or make the shared
change a serial predecessor.

## Design requirement-fit validation

Start with claims, not test categories. For each material behavior, determine the
cheapest observation that can distinguish success from failure.

Verification may include:

- existing unit, integration, end-to-end, contract, or snapshot tests;
- new focused tests for changed behavior and discovered regressions;
- type checking, linting, compilation, schema validation, or static analysis;
- manual or visual checks where automation cannot decide the claim;
- performance or load measurements tied to an explicit budget;
- migration dry runs, rollback checks, or data readback;
- security-specific checks tied to the actual trust boundary; and
- live-environment validation only for behavior that cannot be established
  elsewhere.

For each proposed new test, specify:

- the meaningful setup or precondition;
- the action or input;
- the important observable or assertion; and
- the regression or requirement it protects.

Use exact commands only after confirming them in repository tooling or docs. Separate
commands that can run independently, but do not invent a scheduling framework for
ordinary checks.

Each STEP names a **fast test suite**: the smallest independently runnable existing
test selection or concrete new focused test that can decide its local outcome. Name
the selector or confirmed command when known, the decisive assertion, and the
changed inputs that would require a rerun. A new test is implemented as part of
the STEP and is runnable by its completion. When automation cannot decide an
operational outcome locally, name the fastest repeatable check and its limitation,
then place the necessary live or integrated proof at its real boundary. A broad
suite is not a substitute for the local check. One decisive check can be enough;
do not build a runner solely for the label.

When an assertion fails, compare the governing requirement, observed product
behavior, and failing assertion before repairing the product. Classify it as a
product defect, an overstrong or incorrect oracle, or unresolved evidence. Ask
whether a plausible known-broken implementation could pass the proposed check;
if so, strengthen the check without expanding the requirement. Do not break correct
behavior to satisfy a bad test or weaken a valid requirement to obtain green.

Define sufficient evidence for each required behavior; do not make development
success depend on every available check, report, warning, or unrelated repository
surface being perfect. Apply the skill's
[requirement-fit classification](../SKILL.md#validate-requirement-fit-not-literal-perfection)
to adverse results and state which claim or consumer each result can actually
invalidate.

If a repository or release process requires an exhaustive gate, identify that gate
and its consumer separately from the behavioral evidence it consumes.

For costly, stateful, dependent, or repeated verification, schedule by real
resources: distinguish isolated local checks from shared-state and live/external
checks; run ready independent checks within actual capacity; refill capacity as
checks finish instead of imposing wave barriers. Ordinary failure holds only
dependent checks; independent coordinates may continue. Serialize shared state
or provider use only when a real conflict or limit requires it. Do not create a
mandatory matrix or scheduling ledger for ordinary focused checks.

### Avoid duplicated evidence

One test result may support several consumers. Refer to it; do not copy it into
separate evidence packets. Run a check again only when:

- a consumed input changed;
- the earlier environment or setup does not cover the required boundary;
- nondeterminism requires a justified sampling strategy;
- a release or policy explicitly requires a fresh run; or
- the prior result is missing or not trustworthy.

Do not rerun unaffected checks after a documentation or report correction. Do not
require every platform/environment combination when representative coverage proves
the claim, and do not use representative coverage when the contract is genuinely
platform-specific or exhaustive.

## Plan realistic risk and recovery

Include risks that can change the implementation or execution route. For each,
state the trigger or observation, impact, prevention or mitigation, and recovery
action. Name a separate owner only when responsibility differs from the delivery
owner. Avoid generic risk lists.

Useful categories include:

- incompatible interface or schema changes;
- partial migrations or rollout/version skew;
- shared-file or generated-output conflicts;
- data loss, duplicate effects, or unrecoverable external actions;
- weak or unavailable acceptance evidence;
- scarce environment or hardware access;
- security or privacy boundary mistakes; and
- integration behavior that local checks cannot observe.

A failed step should block only consumers of its missing result. Preserve independent
work and passing evidence. When the current approach stalls, change the assumption,
ownership, seam, oracle, or implementation strategy before retrying; a renamed copy
of the same plan is not a recovery.
