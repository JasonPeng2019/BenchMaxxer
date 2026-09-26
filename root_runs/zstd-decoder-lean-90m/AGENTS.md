# ZSTD decoder pilot: lean optional-use harness

Read `ROOT_RUN_PROMPT.md` before task work. Implement the complete RFC 8878
Zstandard decoder, not a planned subset. The run has a continuous 90-minute
wall-clock limit from ROOT launch, including setup, coding, testing, and
shutdown; there is no token cap. Scope the implementation to finish as much
of the full task as possible within that limit. Do not stop early merely
because one milestone or public sample passes. Report remaining gaps honestly.

The native harness is available for optional coding, fresh review, or test
design lanes. ROOT decides if and when those lanes improve the task. There is
no mandatory project-specification, project-topology, goal-file, or full
skill-suite workflow in this arm. If any task-specific skill is used, record
its name in the final report. Keep planning light, but preserve explicit
interfaces and source ownership for any delegated work.

Stay in this fresh task repository. Outside it, access only the named
`../../harness-lean-zstd` harness documentation and commands and the pinned
Docker bridge. Do not inspect any other run, solution, verifier, hidden test,
encrypted asset, credential, or benchmark implementation. Use only the
agent-visible source, RFC, samples, and public tests. The operator runs the
sealed verifier only after the source is frozen.

ROOT alone may operate the pinned no-network task-copy Docker bridge, review source,
commit accepted changes, and shut down the native harness. Every worker must
be Terra/high/priority in its generated `worker-isolated` sandbox. Read the
harness `AGENTS.md`, `QUICK_RULES.md`, and `QUICK_START.md` before using it.
Run native `scan --no-write` after bootstrap and before launch. A successful
`resume-lane` only prepares an invocation: explicitly run `lane launch` and
verify a recorded process identity before waiting or notifying. A running
lifecycle with `launch_pending: true` is not a launched worker.

Do not alter `src/Makefile`, tests, samples, RFC, or harness code; do not
invoke/copy libzstd or another decompressor. Private helpers under `src/`
are allowed if the unchanged Makefile builds the final program. The public
`test.sh` has host CRLF line endings; feed a CRLF-normalized stream to Bash
without changing that protected file. Report exact public-test evidence,
source revision, worker usage, unsupported behavior, and clean shutdown.
