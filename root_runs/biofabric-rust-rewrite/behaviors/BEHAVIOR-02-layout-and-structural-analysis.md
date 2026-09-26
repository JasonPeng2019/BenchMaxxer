# BEHAVIOR-02 - Compatible layout and structural analysis

## Dictated outcome and source

Library callers must receive reference-compatible graph-analysis results and
BioFabric layouts for the fixed default, similarity, hierarchy, cluster,
control-top, set, and World Bank layout surface. This is dictated by the fixed
analysis/layout APIs and the visible parity configurations that compare node
order, link order, and session output.

## Actors, triggers, and preconditions

A caller supplies a compatible network and, when required by a selected layout,
layout parameters, a fixed node/link order, node attributes, cluster/control
information, or a progress monitor. The input must satisfy a selected algorithm's
reference-defined preconditions (for example, directed structure where a
hierarchical or control-top operation requires it).

## Behavioral flow and decision rules

1. Structural analysis exposes traversal, connected components, neighborhoods,
   degree ordering, shortest paths, DAG levels, topological order, and cycle
   detection according to the reference's treatment of direction, links, and
   isolated nodes.
2. A node layout determines the compatible row order. A corresponding edge
   layout assigns compatible columns, link groups, spans, shadows, and
   annotations to form a `NetworkLayout`.
3. Default layouts use their defined starting and grouping rules. Similarity,
   hierarchical, clustered, control-top, set, and World Bank variants apply the
   supplied mode and parameter values rather than silently falling back to an
   unrelated layout.
4. Fixed node or link order inputs take precedence where the public API selects
   fixed-order layout behavior. Layout extraction compresses the retained
   submodel while preserving the reference-defined relationship of rows,
   columns, and links.

## State, data, and observable effects

The observable layout includes node rows, link columns, regular/shadow state,
link-group membership/order, no-shadow and full spans, row/column counts, and
node/link annotations. These values feed order files and BioFabric sessions;
their ordering and formatting are compatibility behavior. Analysis results are
observable through their public return values and CLI consumers.

## Edge, failure, and recovery behavior

Valid edge cases include empty or one-node networks, disconnected components,
self-links, cycles, directed DAGs, and graphs whose supplied order or attributes
select a specialized mode. Algorithms must preserve the reference behavior for
these cases, including any reference-defined inability to produce a DAG-only
result. Missing required specialized inputs or invalid order data use the fixed
error/result behavior rather than producing an arbitrary ordering. The caller
may supply a valid parameter/input and retry.

## Constraints and preserved behavior

Apply the shared rules in `SPEC.md`, especially fixed APIs, deterministic parity,
protected golden fixtures, and offline operation. Progress/cancellation hooks
remain usable through the fixed monitor interfaces; an implementation may choose
private iteration mechanics but must not change their observable contract.

## Acceptance scenarios

- Given the visible graphs, structural analysis returns reference-compatible
  components, degrees, neighborhoods, cycle/DAG findings, and topological
  results, including isolated and self-linked nodes.
- Given each supported layout configuration and its required input data, the
  resulting row and column ordering, shadows, groups, spans, and annotations
  match the reference-observed layout representation.
- Given shadow-disabled, fixed-order, clustered, control-top, set, hierarchy,
  and similarity variations, only the reference-prescribed variation changes;
  the underlying network data remains intact.
- Given a valid submodel selection from a layout, the extracted network and
  compressed layout retain the compatible surviving rows and columns.

## Implementation freedom and unresolved decisions

Traversal algorithms, sorting internals, and private layout helpers are
implementation freedom, subject to observable parity. There are no unresolved
product decisions.
