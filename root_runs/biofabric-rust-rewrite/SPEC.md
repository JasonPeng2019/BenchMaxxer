# BioFabric Rust rewrite specification

## Product intent and authority

The required outcome is a faithful Rust implementation of the BioFabric core
library and `biofabric` command-line tool, including its network-alignment
plugin. The governing authority is the task brief in `ROOT_RUN_PROMPT.md` and
the checked-out skeleton's fixed public surface and visible fixtures. The
reference Java behavior is the compatibility oracle; visible and held-out task
tests decide whether observable output has parity.

The task brief's explicit requirements take precedence over current stub
behavior. In this package, a *dictated requirement* is a task boundary or
observable compatibility outcome stated by that authority. A *necessary derived
behavior* is identified as such when it is needed to preserve a fixed API or
make parity observable. A *working assumption* is labeled and does not enlarge
the task. Algorithm, private-module, and data-structure choices remain
implementation freedom unless they alter the fixed public API or output.

## Current behavior and required change

The current workspace exposes the intended public Rust types, traits, methods,
CLI argument model, and visible parity tests, but most operational methods and
command handlers are stubs. The target replaces those stubs with behavior that
is compatible with BioFabric and its alignment plugin.

The following current boundaries must remain intact:

- Public types, traits, and method signatures are fixed; callers must not need
  an API migration.
- Task code may be implemented only in `crates/core/src/` and
  `crates/cli/src/`. Of the existing tests, only
  `crates/core/tests/parity_tests/runners.rs` may change. Other tests and all
  golden fixtures are protected evidence, not implementation inputs to alter.
- The final environment is offline. A successful rewrite must build and test
  from the locked task dependency set without fetching new network resources.

## Actors, boundaries, and non-goals

Library callers load or build networks, analyze them, compute layouts, work
with sessions, and use alignment results. CLI users invoke the supplied
`layout`, `info`, `convert`, `align`, `compare`, `extract`, `export-order`, and
`search` commands. The task test harness consumes serialized and textual
outputs.

In scope are the core model, supported file/session formats, layout and graph
analysis behavior, alignment loading/merging/scoring/layout behavior, and the
listed CLI workflows. The Rust public API and the command/flag contract already
represented in the skeleton are part of this product boundary.

Out of scope are changes to the public API, new user-facing commands or
formats, fixture rewrites, changing protected test expectations, accessing
held-out verifier behavior, and online service dependencies. Workflow planning
artifacts do not become library or CLI product behavior.

## Shared terminology and product rules

- A **network** contains named nodes, links, relation labels, isolated nodes,
  metadata, and where applicable shadow links. Directedness, bipartiteness,
  DAG status, adjacency, and duplicate handling are observable properties when
  exposed through the public API or a command.
- A **layout** assigns network nodes to rows and links to columns, retaining
  span, grouping, shadow, and annotation information required by the exported
  BioFabric representation. Ordering and serialized formatting are observable
  compatibility behavior, not cosmetic choices.
- A **session** combines a network with optional layout, annotations, display
  options, and alignment scores for BioFabric XML/session interchange.
- An **alignment** maps nodes of one input graph to another. A merged network
  preserves the graph origin and alignment classification needed for scores and
  alignment layouts.
- For valid inputs, every exposed result must match the reference's observable
  values, ordering, and emitted representation wherever the task compares it.
  This is a dictated parity rule. For malformed or unsupported inputs, the
  fixed public error/result interfaces must be used consistently with the
  reference rather than silently producing unrelated data or panicking.
- Determinism is a necessary derived behavior: repeated execution over the
  same input must not introduce avoidable ordering differences that invalidate
  parity.

## Behavior map and relationships

| Behavior | Dictated outcome | Depends on or interacts with |
| --- | --- | --- |
| [BEHAVIOR-01](behaviors/BEHAVIOR-01-network-data-and-interchange.md) | Callers can construct, import, query, and serialize compatible BioFabric network/session data. | Defines the shared network/session state used by all other behaviors. |
| [BEHAVIOR-02](behaviors/BEHAVIOR-02-layout-and-structural-analysis.md) | Callers receive compatible graph analysis and deterministic BioFabric layouts. | Consumes network data from BEHAVIOR-01; layout output is consumed by sessions and CLI workflows. |
| [BEHAVIOR-03](behaviors/BEHAVIOR-03-network-alignment.md) | Callers can load, merge, score, classify, and lay out aligned networks compatibly. | Consumes BEHAVIOR-01 data and BEHAVIOR-02 layout conventions. |
| [BEHAVIOR-04](behaviors/BEHAVIOR-04-command-line-workflows.md) | CLI users can perform the supported network and alignment workflows with compatible output. | Orchestrates the first three behaviors without changing their contracts. |

## Product-wide constraints and acceptance

The rewrite must preserve the fixed library and CLI contract and must not alter
protected tests or fixtures. Completion is observable only when the offline
workspace builds and `cargo test --workspace --no-fail-fast` can exercise the
implemented behavior, including byte-level parity where the reference fixtures
compare bytes. Focused visible tests may establish individual outcomes, but
they do not waive the final whole-workspace test condition.

The source restriction and offline constraint apply to every behavior. Any
allowed change to the parity runner must execute existing expectations against
the implementation; it must not weaken, skip, synthesize, or rewrite those
expectations.

## Assumptions and unresolved product decisions

Working assumption: when a detail is not explicit in a public signature or
visible fixture, the Java reference defines it. The earliest useful confirmation
is a focused comparison against existing visible behavior during implementation.

There are no unresolved product decisions: the task fixes the product boundary,
compatibility authority, and completion condition.
