# BEHAVIOR-04 - Compatible command-line workflows

## Dictated outcome and source

The `biofabric` CLI must make the fixed command and flag surface operational:
`layout`, `info`, `convert`, `align`, `compare`, `extract`, `export-order`, and
`search`. This is dictated by the task's required CLI rewrite and the fixed
argument definitions. The CLI is a consumer of the core behaviors, not a
separate alternate data model.

## Actors, triggers, and preconditions

A command-line user invokes one of the supplied commands with its required
paths/arguments and optional flags. Inputs must be readable and valid for the
selected format/operation. Output may be written to the selected path or, where
the fixed command permits, standard output.

## Behavioral flow and decision rules

- `layout` loads a network, honors layout/shadow/group/order/attribute options,
  computes the selected layout, and emits its compatible output form.
- `info`, `compare`, and `search` load compatible network data and present the
  selected structural, neighborhood, matching, relation, degree, or JSON/text
  result without changing the input.
- `convert` loads a supported input and writes the requested compatible format,
  observing shadow and output-path options.
- `extract` returns the requested node-list or hop-neighborhood subnetwork in
  the selected compatible format.
- `export-order` emits the requested node or link ordering from a compatible
  layout/session input.
- `align` loads both networks and a mapping, applies the selected alignment
  layout, optionally reports scores/evaluation output, and writes or prints its
  compatible result.

Each command follows the defaults, flag precedence, output mode, and error
behavior represented by its fixed argument contract and the reference.

## State, data, and observable effects

The command's observable effects are its output bytes/text/JSON/session files,
exit success or failure, and any requested written artifact. Input network files
are read-only from the command user's perspective. Command output must preserve
the model/layout/alignment semantics of BEHAVIOR-01 through BEHAVIOR-03.

## Edge, failure, and recovery behavior

Missing paths, unsupported output modes, malformed data, absent requested nodes,
invalid regexes, incompatible flags, or output I/O failures report a compatible
command failure and do not claim success. Empty searches, isolated nodes, and
valid no-result/zero-score cases retain the reference-defined normal output
semantics. A user can correct arguments or data and rerun the command.

## Constraints and preserved behavior

The fixed Clap-facing command and option names/types are protected by the public
contract. No new command or online behavior is required. CLI output participates
in the shared deterministic parity requirement and must not bypass the core
library's error/data rules.

## Acceptance scenarios

- Given valid inputs and default options, every listed command completes its
  documented core workflow and emits the reference-compatible result.
- Given explicit supported options, the selected layout, output format,
  filtering, comparison, extraction, score, and text/JSON behavior changes only
  as the fixed command contract specifies.
- Given an invalid path, incompatible/malformed input, bad search expression, or
  missing requested entity, the command reports a compatible failure instead of
  producing unrelated output.
- Given CLI output that represents a network, layout, session, or alignment, it
  remains consumable by the corresponding fixed core interchange behavior.

## Implementation freedom and unresolved decisions

Handler organization, formatting helpers, and private CLI control flow are
implementation freedom unless visible output or the fixed command contract
changes. There are no unresolved product decisions.
