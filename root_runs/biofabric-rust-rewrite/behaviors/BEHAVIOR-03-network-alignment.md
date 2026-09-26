# BEHAVIOR-03 - Compatible network alignment

## Dictated outcome and source

The alignment plugin must load an alignment, merge two networks, classify merged
nodes and edges, compute supported evaluation scores, and emit reference-
compatible group, orphan, or cycle layouts. This is dictated by the task's
explicit inclusion of the network-alignment plugin, its fixed public alignment
surface, and visible alignment parity/analysis cases.

## Actors, triggers, and preconditions

A library caller or CLI user supplies two compatible network inputs and an
alignment mapping. Optional perfect/reference alignment data enables the
additional evaluation and node-group modes exposed by the fixed APIs. The mapping
and source files must be readable and syntactically valid for the selected
operation.

## Behavioral flow and decision rules

1. The alignment loader parses node mappings through the fixed alignment format
   contract.
2. Merge behavior produces a single network whose nodes retain graph origin and
   alignment status, and whose links retain compatible edge-type classification.
3. Score behavior computes the exposed topological and optional evaluation
   metrics (including EC, S3, ICS and, when perfect data is supplied, NC, NGS,
   LGS, and JS) using the reference-defined denominators and special cases.
4. Node grouping and Jaccard logic classify merged data under the requested
   perfect-alignment mode. Orphan and cycle processing identify the relevant
   links/nodes and produce compatible grouping/annotation information.
5. Alignment node and edge layout apply the requested group, orphan, or cycle
   mode and emit compatible row order, link order, labels, colors, and
   annotations.

## State, data, and observable effects

The mapping, merged-node identity/origin, node color, edge type, correctness
status, group tag/order, cycle position, orphan filtering result, metric values,
and final layout are observable state. Optional perfect-alignment input changes
only the evaluation/classification behavior for which the public contract calls;
it must not corrupt the base merged network.

## Edge, failure, and recovery behavior

The operation must handle unaligned nodes, partially mapped graphs, repeated or
invalid mapping content, zero-denominator score situations, disconnected pieces,
and alignment cycles according to the Java-compatible result. A malformed or
unavailable mapping fails through the fixed error contract. An absent optional
perfect alignment leaves optional evaluation unavailable rather than inventing
scores. Correcting the relevant input permits a retry without changing either
source network.

## Constraints and preserved behavior

Apply `SPEC.md`'s shared API, deterministic-parity, source/test restriction, and
offline rules. Alignment session output must integrate with the same session and
layout compatibility contract as BEHAVIOR-01 and BEHAVIOR-02. Any normalization
used by the task's comparison support is test mechanics, not permission to
weaken the underlying public alignment contract.

## Acceptance scenarios

- Given two networks and a valid mapping, merge results preserve compatible
  aligned and unaligned node/edge classifications and a usable merged network.
- Given the same merge, supported score calls produce reference-compatible
  metrics; optional perfect alignment enables the corresponding additional
  metrics and correctness/group behavior.
- Given inputs that select group, orphan, and cycle layout modes, each produces
  the reference-compatible row/column/group/annotation outcome, including
  cycle-related classifications.
- Given invalid mapping input or a partial alignment, the operation has the
  fixed compatible error or partial-result semantics and does not alter the
  source networks.

## Implementation freedom and unresolved decisions

Private merge representation, score calculation decomposition, and cycle-search
strategy are implementation freedom. There are no unresolved product decisions.
