# BEHAVIOR-01 - Compatible network data and interchange

## Dictated outcome and source

Library callers must be able to create and query BioFabric networks, import
supported network/alignment-adjacent data, and write compatible representations
through the fixed public APIs. This is dictated by the task's required
`biofabric-core` Rust rewrite and the fixed model, I/O, session, color,
annotation, attribute, and order interfaces. It supports all downstream
layouts, analysis, alignment, and CLI commands.

Necessary derived behavior is stable identity and ordering for nodes and links:
formats, layouts, and parity comparisons need a consistent representation of
the same input. Internal indexing and parser organization remain implementation
freedom.

## Actors, triggers, and preconditions

An application or CLI handler supplies a network directly or selects a supported
SIF, GW, JSON, or BioFabric XML/session input; it may also supply node/link
order, attribute, or annotation data where the fixed API accepts it. A caller
may request a write to SIF, GW, JSON, or session output. Inputs must be readable
and have the format implied by their extension or explicitly selected format.

## Behavioral flow and decision rules

1. Construction and import create nodes, relations, links, metadata, and lone
   nodes according to the supplied representation, using the fixed model API.
2. Network queries expose membership, counts, links, neighborhoods, relation
   types, attributes, classifications, and selections consistently with that
   data.
3. Shadow-link generation, de-duplication, adjacency rebuilding, directed/DAG/
   bipartite detection, comparison, and subnetwork extraction retain the
   reference-defined meaning of regular links, shadows, self-links, and
   isolated nodes.
4. An export or session save emits the compatible textual/serialized form.
   A session round trip preserves the network plus the optional layout,
   annotations, display options, and scores it represents.
5. File-factory format detection routes a supported input or output to the
   corresponding compatible behavior without exposing an alternate format
   contract.

## State, data, and observable effects

Node IDs, names, attribute values, link endpoints, relation labels, link shadow
state, and network metadata are product-significant. Node and link order is also
observable whenever it appears in an order file, layout, or serialized session.
Attribute and annotation tables preserve their named row/column meaning and
colors. A `Session` visibly distinguishes a bare network from one with layout
or alignment information.

## Edge, failure, and recovery behavior

Inputs may include isolated nodes, duplicate links, self-links, multiple
relations, directed structures, invalid formatting, missing files, or an
unsupported extension. Valid special cases retain their reference meaning;
invalid or unsupported inputs return the applicable fixed parse/I/O error path.
No partial or fabricated network becomes a successful import result. A caller
can correct the source or select a supported format and retry.

## Constraints and preserved behavior

Apply the shared API, parity, source-area, protected-test, and offline rules in
`SPEC.md`. The implementation must not add an incompatible format or change a
public data type merely to simplify serialization. Exact Java-compatible output
is required wherever the task's fixtures observe it.

## Acceptance scenarios

- Given a valid network with normal, isolated, self, and multi-relation links,
  import and model queries expose the same nodes, link categories, and
  structural properties as the reference.
- Given a network in each supported input representation, loading then writing
  its relevant compatible output preserves the reference-defined data and
  ordering.
- Given attributes, annotations, order files, and a session containing layout
  state, the corresponding public operations preserve their visible values
  through the supported round trip.
- Given malformed content, a missing path, or an unsupported format, the call
  fails through the fixed error contract instead of succeeding with unrelated
  data.

## Implementation freedom and unresolved decisions

Parser structure, private caching, and serialization helpers are implementation
freedom. The Java reference resolves format details not made explicit by the
visible contract. There are no unresolved product decisions.
