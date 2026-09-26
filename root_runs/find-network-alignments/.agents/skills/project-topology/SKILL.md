---
name: project-topology
description: Design a detailed, repository-grounded execution plan for a substantial project or change. Prefer project-specification first when dictated product behavior and acceptance are not yet clear; otherwise plan directly from the governing requirements. Use for a project plan, implementation plan, workflow, topology, or multi-stage delivery design. Produce a stable PLAN.md plus bounded STEP files with precise technical detail, focused verification, and the smallest useful coordination structure. Do not use for routine coding, diagnosis, or status reporting. This skill plans the work; it does not execute it.
disable-model-invocation: true
user-invocable: true
---

# Design a detailed project execution plan

Create a plan that another capable agent can execute without rediscovering the
important architecture, decisions, dependencies, or acceptance conditions. Depth
comes from technical specificity, not from the number of artifacts, roles, gates,
or records.

This is a planning skill. Inspect the project and write the requested plan, but do
not implement the planned product work or dispatch the workers described by it.
The sole dispatch exception is the read-only Bullshit Checker in Step 7.

## Multi-agent workspace orchestration

Prefer direct dispatch from one delivery owner to investigators, writers, reviewers,
and testers. A bounded lane lead may manage workers only when that lane has a stable
outcome, several internal tasks that genuinely need local sequencing or triage, and
a clear terminal result for the global owner. The runtime must actually support that
delegation. The global owner retains scope, cross-lane decisions, shared resources,
integration, live-operation authority, and final acceptance. A lane lead cannot
create another orchestration layer.

## Stable modular plan package

Every plan uses the predictable two-layer package defined in the
[Modular plan template](references/modular-plan-template.md): one root `PLAN.md`
and one or more outcome-based `STEP-*` files.

`PLAN.md` owns the finish line, current-to-target strategy, shared contracts and
decisions, execution shape, dependency graph, integration, whole-product
verification, and plan-wide risks. Each `STEP-*` file owns one bounded, independently
checkable implementation outcome and all detail local to it. A small plan still has at least
one step file; a large plan adds steps, not new document tiers.

The template is the sole authority for filenames, headings, deterministic ordering,
and stable step IDs. The structure exists for editability and navigation, not as a
conformance gate: harmless formatting drift never invalidates usable plan meaning,
product work, or behavioral evidence. When the interface cannot create files,
render the same file boundaries in the response.

Do not wrap the core package in another plan tier or auxiliary administrative
package unless a named external consumer requires it.

## Non-negotiable operating rules

### Validate requirement fit, not literal perfection

Development success means the requested behavior is implemented, supported by
sufficient evidence for the claim, and has no known material in-scope defect. It
does not mean every agent action, command, report, heading, optional check, or
unrelated repository surface is flawless.

Classify problems before deciding what they block:

- **Behavior-impacting defect:** required behavior is wrong or an in-scope
  regression exists. Block the affected step and consumers of its output.
- **Required-evidence gap:** a required claim cannot yet be decided. Hold that
  claim and its consumers, not unrelated completed work.
- **Prerequisite or authority gap:** an input needed by the next action is
  unavailable or permission for that action is missing. Hold only that action and
  its consumers until the gap is resolved.
- **Recoverable execution mistake:** a wrong path, command, fixture, edit, or
  assumption can be corrected locally. Retain valid work and continue.
- **Administrative or presentation defect:** a heading, summary, handoff, report,
  filename, missing duplicate record, or formatting issue is repaired only if a
  real consumer needs it. It is not a product failure and cannot overturn decisive
  behavioral evidence.
- **Unrelated or pre-existing failure:** disclose it and continue unless the
  planned work actually depends on it.
- **Live-safety condition:** stop or contain only the operation and shared resource
  that are threatened.

A nonzero command is an observed command result, not automatically a verdict on
the feature or entire run. Map the failure to the requirement, changed surface,
and downstream consumers it can invalidate.

An unsuccessful intermediate attempt, corrected edit, superseded test run, or
repaired tool invocation is execution history, not a defect in the final result.
After a correction, invalidate and rerun only evidence whose inputs changed; judge
the current product state rather than demanding a pristine first-pass history.

Reason separately about required behavior, the sufficiency of evidence for that
behavior, and any named repository or release gate. Do not collapse those questions
into one global pass/fail verdict. This separation guides decisions; it does not
require three reports or status fields.

Describe execution outcomes in ordinary language. Distinguish required behavior
that is established, required behavior or evidence that remains unresolved,
nonblocking limitations, and an operation that cannot safely proceed. Do not
require status tokens, completion forms, or an acceptance record to make those
distinctions.

If the repository or release process mandates a literal full gate, its failure can
block that gate's consumer or the release. It does not erase implemented behavior,
passing focused evidence, or completed independent steps.

Apply this same classification to review and test findings. Severity wording,
reviewer confidence, or consensus does not create authority. A true but out-of-scope
improvement remains nonblocking, and the delivery owner applies the smallest
correction that restores the required outcome.

### Preserve valid progress

A failure invalidates only the work and evidence that depend on the failed or
changed fact. Keep completed changes, accepted decisions, and passing checks whose
inputs remain valid. Do not restart a whole run, replay unrelated work, or reopen
accepted scope because a handoff, review note, plan section, or test report is
imperfect.

A full restart is justified only when a changed global input, corrupted shared
state, or invalid foundational assumption reaches the entire result. State that
dependency explicitly. Otherwise repair or replan only the unfinished or affected
portion.

### Keep one source of truth

Put each decision or fact in one authoritative place and reference it elsewhere.
Do not create parallel evidence ledgers, acceptance records, reviewer-approval
records, status histories, or copies of the same plan facts. Do not hash ordinary
files or repeat repository hashes. Use a revision, checksum, receipt, or immutable
record only when a named consumer needs identity, integrity, auditability, rollback,
or exact targeting.

### Make every piece of process earn its cost

Do not require a reviewer panel, consensus vote, fixed number of review rounds,
role registry, model map, module catalog, plan compiler, bespoke validator,
per-step recovery document, test matrix, harness, lock service, or separate report
unless the user, repository, regulator, runtime, or a concrete project risk requires
it. Existing mandatory controls remain binding only when they govern the planned
action or its release and have a real consumer; this skill does not invent new ones.

Do not add empty prose, placeholder rows, or inventories of `N/A` merely to make a
plan look complete. Keep the canonical files and core headings when authoring the
plan, but handle an absent special case with one useful sentence at most. Plan
quality is judged by whether its meaning lets the work be performed and verified
correctly; cosmetic conformance does not outrank that meaning.

## Build the plan

### 1. Establish the real assignment

State the requested outcome, user-visible or operational acceptance conditions,
non-goals, constraints, and authority boundary. Treat background documents as
context unless they actually govern the requested result. Surface contradictions
that would change the plan; do not silently merge them.

Ask a question only when the missing answer would materially change scope,
architecture, safety, authority, or the next safe action. Otherwise make the
smallest reasonable assumption, label it, and put its validation at the earliest
useful point in the plan.

If a `project-specification` package governs the work, read its
[spec-to-plan handoff](../project-specification/references/spec-to-plan-handoff.md).
Reference its product behaviors instead of copying or redefining them. A spec
behavior can require several small implementation steps; it is not a STEP size.
If the dictated behavior is too unclear to plan responsibly, recommend the
specification skill first. Do not make an optional specification artifact a gate
when the requirements are already clear.

### 2. Inspect enough of the project to plan concretely

Read applicable repository instructions and inspect the relevant source, tests,
configuration, schemas, generated artifacts, and operational tooling. Trace the
current call path or data flow far enough to identify the real change points and
shared contracts. Prefer current source and executable configuration over old
plans or history.

Do not pad the plan with an inventory of everything inspected. Record only findings
that affect the implementation, ordering, risk, or verification. For the detailed
inspection and writing standard, read
[Detailed planning guide](references/detailed-planning-guide.md), then author the
package with the [Modular plan template](references/modular-plan-template.md).

### 3. Choose the smallest sufficient execution shape

Planning detail and coordination complexity are independent. A single-owner plan
may be extremely detailed; a large file count does not require multiple agents.
Choose from these shapes:

| Shape | Use when | Required coordination |
| --- | --- | --- |
| Single owner | One capable executor can maintain the necessary context and safely implement and verify the result. This is the default. | Ordered implementation and verification only. |
| Single owner with focused support | One owner can deliver, but a bounded unknown or consequential risk benefits from a read-only investigation, design critique, or targeted independent check. | One concrete support question and one collection point. |
| Parallel delivery lanes | Two or more substantial deliverables have stable inputs, disjoint write ownership, and a clear integration order. | Frozen shared contracts, explicit lane boundaries, and one integration owner. |
| Staged coordination | Long dependency chains, live or scarce resources, migrations, rollout/rollback, or repeated cross-lane integration require durable stage boundaries. | Only the stages, decision points, and recovery controls demanded by those facts. No extra coordination package. |

Select multiple agents only when independent work, specialist judgment, isolation,
or wall-clock benefit exceeds coordination cost. Availability of agents, a request
for modular files, or the word “topology” is not sufficient.

If the plan uses any support lane, parallel writer, staged external operation, or
nontrivial recovery route, also read
[Coordination and recovery](references/coordination-and-recovery.md).

### 4. Decompose by executable outcomes

Organize work around independently usable and verifiable implementation outcomes
and dependency boundaries, not equal-sized chunks or arbitrary phases. Split a
proposed STEP when it contains several substantial outputs that can each be
completed, checked, and used or accepted separately, even if one owner would do
them serially. A STEP must not conceal serial assignments with separately
acceptable outputs or serve as a milestone for a whole subsystem. Keep tightly
coupled edits in one STEP when no meaningful intermediate result exists; do not
split by file, command, or worker count. Use the detailed planning guide to cover
the current constraints, concrete change points, implementation logic, dependencies,
verification, and only the migration or recovery mechanics the outcome needs.

Put each implementation block in one canonical `STEP-*` file using the template's
semantic sections. They are information homes, not report fields or acceptance
gates. Link shared context from `PLAN.md` instead of repeating it in every step.
The plan must be granular enough to implement, not merely a list such as "update
backend, add tests, review."

For each STEP, name a fast, repeatable check or smallest relevant test selection
that tests its local output. If the check must be added during the step, say what
it will exercise; do not invent a command. For live-only proof, name the fastest
local check and the later real proof boundary. The fast suite is available by step
completion, not a separate artifact or universal full-suite gate.

### 5. Design requirement-fit validation

Use the [detailed validation standard](references/detailed-planning-guide.md#design-requirement-fit-validation)
to map each material acceptance claim to sufficient, decisive evidence, specify
focused tests, and avoid duplicated checks or invented commands.

Keep behavioral evidence separate from any named exhaustive repository or release
gate. Apply the problem classification above to adverse results: a result affects
only the claims and consumers it can actually invalidate. Report shape, optional
signals, warnings, and unrelated repository failures are not development-success
conditions.

### 6. Make integration and recovery local

Name shared-contract changes before their consumers. Put serial integration in the
order the actual dependencies require. When parallel lanes are used, the integration
owner validates the combined result rather than accepting worker summaries as proof.

For each realistic failure, identify the smallest affected scope, the owner of the
repair decision, and the check that proves recovery. Administrative or tooling
failures block only their direct consumers. Batch compatible findings; do not
alternate review and repair after every individual note.
Findings are compatible when they share a correction objective, owner/source
context, and verification and invalidation boundary; keep unrelated repairs apart.

Give each STEP a fast lane for revisiting old work: retain the valid implementation,
workspace, and evidence; repair only the demonstrated defect; rerun its affected
fast tests and directly invalidated integration checks; then resume at the first
unresolved dependency. Do not rediscover or retest unaffected steps merely to
refresh a record. Use broader checks only when the changed dependency, unreliable
prior evidence, or a named release gate requires them.

Retries are based on progress, not a ritual count. Correct a narrow report or tool
error in place when cheap. If the same approach repeats without meaningful progress,
stop repeating it, diagnose the shared cause, and replan the remaining work with a
concretely different approach. Preserve all still-valid progress.

### 7. Complete the plan, then run the Bullshit Checker loop

Perform a final self-review against the user request and current project:

- every in-scope change is owned by a STEP, while already-correct preserved
  behavior has appropriate verification without a dummy implementation STEP;
- material current-state claims are grounded in inspected project sources;
- dependencies, shared seams, and integration order are explicit;
- parallel work is genuinely independent and serial work has a real dependency;
- the technical instructions are specific enough to act on;
- no STEP hides several independently acceptable outputs behind serial assignments;
- each STEP has a concrete fast check and a scoped re-entry route;
- verification can decide the claimed outcome;
- destructive, external, or live actions have appropriate authority and recovery;
- assumptions are visible at the point they matter; and
- every role, gate, artifact, rerun, and separate file has a concrete consumer or
  risk-based reason.

Once the plan is executable and its required coverage is sufficient, run the one
universally required planning review: a read-only **Bullshit Checker** focused only
on overcomplexity and ceremony.
Use one independent checker when the runtime provides one. If no independent
checker is available, ROOT performs the same critique as a deliberately separate
pass. This loop reviews the planning artifact; it does not execute product work,
run product tests, or become a lane in the authored plan.

Give the checker the current plan, the user request, and only the governing project
facts needed to distinguish required controls from invented process. Do not prepare
an evidence packet or custom report schema. Ask it to identify:

- roles, lanes, reviewers, gates, handoffs, waits, or approval steps without a
  concrete decision, consumer, risk, or authority boundary;
- duplicated requirements, evidence, acceptance statements, status, or reports;
- hashes, IDs, receipts, registries, ledgers, or immutable records without a named
  integrity, targeting, rollback, audit, or lifecycle need;
- repeated checks, broad reruns, matrices, environments, or review cycles that do
  not prove a distinct requirement or changed dependency;
- nominal fast lanes that still restart the plan or retest unaffected work;
- all-green or global pass/fail gates that let an unrelated, administrative, or
  corrected intermediate failure override current requirement-fit evidence;
- bespoke harnesses, compilers, validators, wrappers, templates, or coordination
  services whose cost exceeds their demonstrated payoff;
- arbitrary decomposition, extra mandatory files, placeholder sections, or
  task-card fields that make execution harder without improving correctness;
- serialization, retry loops, or full-run restarts where independent work or valid
  progress could be preserved; and
- administrative defects incorrectly treated as product failures or blockers.

The canonical `PLAN.md` plus `STEP-*` package is a user-required stability and
editability invariant, so its existence is not a valid overcomplexity criticism.
Empty sections, duplicated content, or needless splitting inside that package are
still valid targets for simplification.

A useful criticism identifies the challenged plan element, the coordination or
failure cost it adds, and the smallest simplification. These are decision criteria,
not required report fields: imperfect phrasing does not invalidate the checker pass
or force a rerun. ROOT asks for clarification only when a missing fact prevents
adjudication. The checker may not broaden scope, demand more reviewers or records,
remove required technical detail or verification, or treat plan length and
implementation granularity as ceremony by themselves.

ROOT adjudicates every criticism against the request, repository, runtime, and
actual risk:

- **Valid:** the challenged complexity is not required by a governing constraint
  and has no concrete consumer or risk-reduction payoff. Apply the smallest
  correction while preserving technical specificity, required evidence, authority,
  and recovery.
- **Invalid:** a binding requirement, named consumer, real dependency, or concrete
  risk justifies it. Keep it. A brief working reason is enough; do not create a
  disposition table or ask the checker to approve ROOT's decision.

Repeat the checker on the revised plan whenever ROOT accepts at least one valid
finding. Stop when a pass yields zero ROOT-validated findings. Candidate findings
that ROOT rejects do not keep the loop open, and the checker cannot veto delivery
or repeat a closed criticism unless the relevant plan or governing facts changed.
There is no fixed iteration count and no PASS/BLOCK record. The terminal condition
is ROOT's determination that no valid overcomplexity criticism remains.

The loop's terminal state does not belong in the plan package or an acceptance
record. Do not attach checker transcripts or iteration history. This is the only
universal independent plan review; do not add another by default.

## Output

Deliver the canonical modular package defined above. Do not add more plan artifacts
unless a real repository process or named consumer requires them.

Keep cross-step truth and the dependency graph in `PLAN.md`; keep outcome-specific
implementation detail and validation in its step file. Preserve technical depth:
name concrete change points, contracts, logic, state transitions, edge cases,
commands when confirmed, integration behavior, and local recovery. Modularity must
not turn the plan into shallow task titles or repeated boilerplate.

End with unresolved decisions only if they truly prevent a complete plan. Optional
refinements, formatting repairs, and unrelated failures are not blockers.
