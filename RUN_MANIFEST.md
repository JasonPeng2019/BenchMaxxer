# Local SWE-Marathon pilot: pre-run manifest

Prepared 2026-09-25 before any reportable benchmark-agent run. Before launch,
freeze the outer source snapshot locally and record `git rev-parse HEAD` plus
the working-tree state with each eventual result. Nothing is pushed. This is a
local pilot, not an official Harbor/Modal SWE-Marathon reproduction.

## Superseding model-setting decision (2026-09-25)

After cancelling the BioFabric H-MH attempt, the user changed the **future**
harness treatment to H-H: ROOT `gpt-5.6-terra`/`high` and every Codex worker
`gpt-5.6-terra`/`high`. The old H-MH rules and run IDs below describe the
historical protocol and attempts; they do not authorize or configure another
max-effort ROOT run. At that point the next task had not been selected; the
subsequent ZSTD selection is recorded below. Do not apply the old task-specific
comparison triggers to ZSTD.

The prepared ROOT workspaces now have `model_reasoning_effort = "high"` in
`.codex/config.toml`, and their initial prompts require high for ROOT and
explicit high for each worker. Any future collector launch must also pass
`--model gpt-5.6-terra --reasoning-effort high`; its explicit CLI override is
part of the launch proof. The previous overlay hashes in the table below are
historical; the new config/prompt SHA-256 values are:

| Local file | Current SHA-256 |
| --- | --- |
| BioFabric `ROOT_RUN_PROMPT.md` | `612b33546e5665761e18694a1a058c76ef7b51f716bd6656c8536f437aecacb2` |
| BioFabric `.codex/config.toml` | `718e34023f5648d1c4d6eedf555802407a12002c896ee018bc3332ecc8d0651c` |
| Find `ROOT_RUN_PROMPT.md` | `4dab882bf872550af1a5ee4872112cfc5e8c82eb4c8b6787ec5aeec17e9ad563` |
| Find `.codex/config.toml` | `718e34023f5648d1c4d6eedf555802407a12002c896ee018bc3332ecc8d0651c` |

## ZSTD-decoder selection and setup (2026-09-25)

The user selected SWE-Marathon `zstd-decoder` for the next test, retaining the
H-H pairing: ROOT `gpt-5.6-terra`/`high`, every native Codex worker
`gpt-5.6-terra`/`high`, priority service tier, and **no token cap**. This is
setup authorization only, not authorization to launch the reportable agent or
score one. The task's original agent horizon is five hours
(`timeout_sec = 18000`). The user explicitly extends the **local harness**
treatment to 10 hours of cumulative active wall-clock time, so its initial
collector watchdog must be `--watchdog-hours 10`; this is a safety deadline,
not a matched token budget or an official task setting. Use a fresh run ID
such as `zstd-h-h-10-*` and an explicit ROOT `--reasoning-effort high`
override. Do not reuse the
cancelled BioFabric runtime.

**Interrupted-run amendment.** The user expects multiple planned machine
power-offs. The eventual H-H-10 treatment is therefore a single, explicitly
non-standard local trial with multiple ROOT Codex session segments, not a
continuous five-hour SWE-Marathon attempt. Launch with the collector's
`--interrupted-run`; after a clean pause, use its `resume` command with the
same `task.json` and the saved native session. Only active collector time
counts toward the cumulative 10-hour safety limit; report offline wall gaps
separately. ROOT must checkpoint, settle lanes, and shut down the native
harness before power-off. An abrupt outage or missing usage/cleanup proof is
not automatically a valid pause. The exact operator sequence and reporting
limits are in `scripts/INTERRUPTED_ZSTD_RUN.md`. This amendment does not
authorize launching the agent.

A separate, non-benchmark Luna/read-only CLI smoke exercised the installed
`codex exec resume` path once. Both segments emitted the same native thread ID;
the finalized ledger counted 27,219 aggregate tokens via cumulative-session
deltas, one resume, 11.907 active seconds, 5 paused wall seconds, and no ledger
errors. Evidence is under
`results/preflight_smoke_20260925/cli-resume-probe-20260925/` and its
`-ledger` archive. It proves CLI segment capture and accounting, **not** live
ZSTD agent performance, a native worker surviving reboot, or arbitrary
power-loss recovery.

| ZSTD input | Pinned identity |
| --- | --- |
| Agent-visible baseline, local template and ROOT HEAD | `c1c5a00cac9e58af70fb4289b9c0c49a67774f31` |
| SWE-Marathon task checkout | `f34867643bf07aec5208a861e667e01df0942099` |
| Workflow skill-suite source | `30bdc088b3238f9e045bc9969f8b5cb0bb4981a0` |
| Harness source HEAD at setup | `01bfcd14642c8b62b1c9ebd9d0bf03646abe8771` |
| Dockerfile SHA-256 | `4d7b58f3503559aef56046039e46830a8a06835a581584fb289fac185adfdc35` |
| Pinned image `swe-marathon-zstd-decoder:lf-20260925` | `sha256:3a43d4f3658c4a21115c518937b692692e9e721d3b6e4a3205972917b8bc2e8a` |
| Verifier `tests/test.sh` SHA-256 | `453aa960844288d914b2c2a094759ac761638ca8990a3a32c112e4c0a4d79bd8` |
| ROOT `AGENTS.md` SHA-256 | `ab8cd8b10a4ca0da99e57de90b01f3911229286816a3efe0340f47a241d8d178` |
| ROOT `ROOT_RUN_PROMPT.md` SHA-256 | `0e63423046c4bdb67973987bea07b5edca725b98d50fb349a90b24a1852b1f7a` |
| ROOT `ROOT_RESUME_PROMPT.md` SHA-256 | `0ae2e2d0eb79e900984750a7f3aace4d910ff0c639d5ae0c4f42e795caef03d6` |
| ROOT `RUN_CHECKPOINT.md` pre-run template SHA-256 | `731c8ec47856949542215cf4ea9f41d5e67d1aa9522c02af4eb12ec803b4cb65` |
| ROOT `.codex/config.toml` SHA-256 | `4be05fe7a14b7020642cb345f3320e7a6e3a412529be3f3d66946ccf918d4ded` |

The interrupted-run implementation snapshot is hash-pinned below; verify it
again immediately before launch because the outer working tree has unrelated
uncommitted state. The live `RUN_CHECKPOINT.md` is expected to change as ROOT
records progress.

**Launch authorization and preflight turn (2026-09-25).** The user explicitly
authorized starting the ZSTD H-H-10 harness run. The first collector turn,
`zstd-h-h-10-20260925t185204z`, exited after 10 seconds because its static
prompt omitted that authorization. It used 25,265 input and 233 output tokens,
did no harness setup or task work, and is preserved as an unscored launch
preflight. The prompt now carries the authorization for the fresh run ID
`zstd-h-h-10-20260925t185239z`; the hash above reflects that amendment.
That fresh run started at 2026-09-25 18:53:16 UTC with Terra/high ROOT,
priority tier, uncapped tokens, interrupted-run recording, and a 10-hour
cumulative active-time watchdog. ROOT's native setup succeeded, and its first
worker lane (`zstd-step01`, epoch `08b409d5140c4c8499f0da98062a5205`)
reached `running` with a signed Terra/high/priority invocation and generated
`worker-isolated` permissions. This records launch identity, not completion or
a verifier score; inspect the live task artifacts for subsequent state.

| Interrupted-run file | Prepared SHA-256 |
| --- | --- |
| `scripts/collect_codex_usage.py` | `9981a2276ea2952e248c32bd984ecfe94a657b4ab79426c71065038617195ecf` |
| `scripts/token_ledger.py` | `ba4a88db9f0fa0546f995cc2e1174883d0c4336f2a5f004c4f0fe7e978798655` |
| `scripts/docker_task_workspace.py` | `9f2286f4da714bb0b6509b36cf1e0e00fb022724772c30bc4a24378f12e82ca3` |
| `scripts/INTERRUPTED_ZSTD_RUN.md` | `7508508d68764e00cf929d2e1d29a25a6ff6a2d3701a0e658fc959323ea2b6a1` |

### Interrupted ZSTD resume amendment (2026-09-26)

The user authorized continuing the **same** paused task run
`zstd-h-h-10-20260925t185239z` after restarting Docker Desktop. The original
ROOT segment ended `PAUSE_READY` with native runtime `CLOSED` and monitor
`STOPPED`, but the STEP-02 worker suffered provider DNS/transport failures and
emitted no terminal usage. Its partial source edit was not integrated. The
original collector correctly refused resume because it could not distinguish
that terminated, unmetered worker from an active one.

The collector now accepts only a specific operator `usage-gaps.json` receipt
whose invocation ID and transcript SHA match, with the original native epoch
closed and lane retired. It leaves that worker's token amount **unknown**;
`known_total_tokens` is a lower bound and `token_total_is_exact` is false.
This preserves the run for implementation/scoring but disqualifies exact
token-matched comparisons. The ROOT transcript, worker transcript, native
records, and original launch/final manifests remain unchanged. All 29 offline
tests pass. Docker Desktop again exposes the pinned ZSTD image, and the
one-mount/no-network bridge returned `ZSTD_RESUME_DOCKER_OK` on an existing
retired lane worktree. The pause marker must be removed before ROOT resumes.

| Resume-amended file | SHA-256 |
| --- | --- |
| `scripts/collect_codex_usage.py` | `12a01b7b06cbe003212d3128aa467c0d14db6005f4eef7e186ef8de52ee5ecca` |
| `scripts/token_ledger.py` | `d84b55ba629b457dd04d93c8214d82447559c1b268be04072b540e013cb72e89` |
| `scripts/INTERRUPTED_ZSTD_RUN.md` | `5f6ba33de77018d387502fba91dbd29eb71012af3cfb6002cef8da084c7bf8ca` |
| ROOT `ROOT_RESUME_PROMPT.md` | `a5ad7262e055941d39d414aa747f2141455a877a99db1444e1c3d5cf1f7465fe` |
| `results/zstd-h-h-10-20260925t185239z/usage-gaps.json` | `09daabe3a618ee32546d1ea3b37254b35deaeda9619132df897fa39e8ed2f6c5` |

ROOT segment `0002` started at 2026-09-26 07:30:20 UTC in the original Codex
thread `01a0d9ea-2886-7943-8b6a-fdc9657b1238`, with the same Terra/high,
priority, ROOT host-access settings and `9.618524166666667` active watchdog
hours remaining. The host Codex CLI is now `0.157.1` (the first segment used
`0.156.1`), another disclosed pilot asymmetry. Native epoch
`b6f0fb9dd2c345d381c8058530f90bc2` opened and worker lane
`zstd-step02-resume` reached `running` with explicit Terra/high/priority and
generated `worker-isolated` permissions. The live snapshot has no accounting
errors and retains one unknown-usage prior worker; its current in-flight ROOT
and worker invocations are expected while the segment is active. No final
verifier score has been produced.

Only the 13 agent-visible environment files were copied into the template;
their SHA-256 values match the upstream environment. No `solution/`, verifier
`tests/`, raw `hidden/`, or credentials were copied into ROOT. The portable
workspace validator passed before harness integration. Native `harness setup`
returned `SETUP_OK`; an unlaunched ZSTD lane was bootstrapped with explicit
Terra/high, priority tier, and generated `worker-isolated` configuration.
The pinned Docker image built and a no-network image smoke passed. Docker
Desktop File Sharing now includes `root_runs/zstd-decoder`. A fresh no-model
preflight epoch `84aa505fc7724c0b97a6b5bde4c71131` bootstrapped the exact
Terra/high lane; the pinned one-mount, no-network Docker bridge returned
`ZSTD_BRIDGE_SMOKE_OK` against its lane worktree. No provider was launched.
The disposable lane was retired and `harness shutdown` returned `SHUTDOWN_OK`:
the ZSTD runtime is `CLOSED`, its monitor `STOPPED`, and no Docker container
remains. Use a new epoch for a reportable run.

The [public SWE-Marathon v1.1 dashboard](https://www.swe-marathon.org/)
reports eight raw Terra/xhigh ZSTD trials: 2/8 full passes, with individual
partial scores `1.000`, `1.000`, `0.744`, `0.721`, `0.581`, `0.581`, `0.581`,
and `0.512` (range `[0.512, 1.000]`). Its raw Terra/high ZSTD trials are
0/8 passes, with partial scores from `0.349` to `0.581`. These are uncalibrated
diagnostics from the public v1.1 leaderboard, not a local agent result.
The ZSTD protocol is frozen for a later, separately authorized launch:
run one fresh H-H-10 harness treatment first. Run one fresh C-X-5 raw
Terra/xhigh control only if H-H-10 earns a binary pass or a valid raw partial
strictly outside `[0.512, 1.000]`; missing or invalid scores do not trigger it.
Run one fresh C-M-5 raw Terra/max control only if the H-H/C-X pair has valid
final verifier and token records, C-X used at most 80% of H-H's aggregate
tokens, and C-X is materially worse: H-H passes while C-X fails, or H-H's raw
partial exceeds C-X's by at least 0.05. Do not trigger from time-censored
results. H-H has a 10-hour cumulative active-time watchdog across clean
segments; any raw control has a five-hour continuous safety watchdog. All
arms have no token cap, no best-of retries, and a fresh workspace. This
asymmetry limits interpretation of any H-H/raw comparison. Evaluate triggers
on the benchmark's **raw**
score, not the oracle-relative figure below. Report aggregate ROOT-plus-worker
tokens for H-H and ROOT tokens for raw controls. A local pair is a small-N
comparison, not a causal harness-only or token-budget-matched estimate.
These rules are preparation, not authorization to start a reportable run.

Operator-only oracle preflight on the rebuilt image: the supplied reference
solution built, passed all 6 public tests and 27/37 hidden tests: **33/43 in
total**, not 33/34. The verifier wrote reward `0` and `partial_score = 0.767`.
Evidence is in `results/preflight_smoke_20260925/zstd-oracle-20260925/`.
This image is **not oracle-validated**. The oracle container was removed after
capturing the metrics. The user chose to proceed with this documented risk.
For local comparison only, treat the oracle's `0.767` partial score as the
100% reference and report an agent's oracle-relative partial as
`agent_partial_score / 0.767` alongside its unmodified raw `partial_score`,
test counts, and binary reward. A result matching 0.767 is 100% of this local
reference, **not** an official full pass; values above 100% remain possible.
Do not alter the verifier, its thresholds, or the benchmark's score. This
choice does not by itself authorize launching a reportable agent run.

## Exact inputs

| Input | Pinned identity |
| --- | --- |
| SWE-Marathon checkout | `f34867643bf07aec5208a861e667e01df0942099` |
| BioFabric agent-visible base | `934570e2c644a262a356314a61cf04bc9d2f99e5` |
| Find Network Alignments agent-visible base | `885b78c9b82f198d85f304bc243fd475f89d05e0` |
| `harness-single` local commit | `3e7fdc9f7d89466d87343b248a827d68ddc1e0cd` |
| `Codex_Claude_Setup` commit | `30bdc088b3238f9e045bc9969f8b5cb0bb4981a0` |
| BioFabric verifier `test.sh` SHA-256 | `d861e3a455b0437177fe34d45e8aa19ae97b40a15f89d5066542cf7b5656ea6a` |
| Find verifier `test.sh` SHA-256 | `1fa278f16261c4e894e90eb3744ef5edcccf8d646bcc8a600dbb831b5fdafa7c` |
| BioFabric Docker image ID | `sha256:7371c89d8cda34360732ef8401ab301c78b72484dace66d4151e180d7fcd061c` |
| Find Docker image ID | `sha256:848b52ed2e1bae448d683769088b7c71bdfd782dce9b1f39578d766165bfa046` |
| Codex CLI at preflight | `0.156.1`, ChatGPT login |

The two `root_runs/` task repositories intentionally remain local workspaces,
not outer-repo source files. Their base commits are above; the portable skill
suite comes from the pinned `Codex_Claude_Setup` commit. Verify these local
overlay SHA-256 hashes before launching, since a hash detects drift but does
not reconstruct an omitted file:

| Local file | SHA-256 |
| --- | --- |
| BioFabric `AGENTS.md` | `2bec5ff304072759fd708a4c090f669a03ad172c5e803b16564266ecd696a07b` |
| BioFabric `ROOT_RUN_PROMPT.md` | `9dd7d7d0edc37e93cd62818f22ca5e656f85d4fb3e55121ddd0c62c9eeb53a05` |
| BioFabric `.codex/config.toml` | `ffaee480fc7ef3b37cefac7ab5208d2ca5b17e8099c7a8cfdd4989bf27a0ddb8` |
| Find `AGENTS.md` | `2bec5ff304072759fd708a4c090f669a03ad172c5e803b16564266ecd696a07b` |
| Find `ROOT_RUN_PROMPT.md` | `306862e8af23523f898f05d55134fcc1d0cf9d00c49b83b945b922438dcea71a` |
| Find `.codex/config.toml` | `ffaee480fc7ef3b37cefac7ab5208d2ca5b17e8099c7a8cfdd4989bf27a0ddb8` |

The source collector, token ledger, Docker bridge, and permission probe live in
this outer commit under `scripts/`. Preflight SHA-256 values and validation
evidence are in `results/preflight_smoke_20260925/PREFLIGHT_INVENTORY.md`.

## Frozen pilot rules

- Run sequentially, BioFabric then Find. H-MH-15 is the first reportable arm
  for each task: ROOT `gpt-5.6-terra`/`max`, workers
  `gpt-5.6-terra`/`high`, one fresh task workspace per run.
- No token cap. Record the aggregate of unique terminal ROOT and worker
  invocation input-plus-output token usage; cached input and reasoning output
  are subsets, not extra charges. An incomplete/invalid ledger makes a result
  uninterpretable until repaired. The 15-hour H-MH and 10-hour raw watchdogs
  are safety limits, not matched budgets. Mark expiry as time-censored.
- For each task independently, run one fresh C-X-10 raw
  `gpt-5.6-terra`/`xhigh` only if H-MH passes or its final verifier partial
  score is strictly outside the released raw range: BioFabric
  `[0.963, 0.980]`; Find `[0.551, 0.784]`. Invalid/missing scores do not
  trigger C-X; investigate them first.
- Run one fresh C-M-10 raw `gpt-5.6-terra`/`max` for a task only if its
  H-MH/C-X pair has valid final verifier and token records, C-X used at most
  80% of H-MH's aggregate tokens, **and** C-X quality is materially worse:
  H-MH passed while C-X failed, or H-MH's partial score exceeds C-X's by at
  least `0.05` on the 0-to-1 scale. Do not trigger from invalid or
  time-censored results.
- Do not retry or select the best of repeated runs. Report each attempt and
  its token total. H-MH alone is an external-reference case study; a local
  H-MH/C-X pair is a small-N hierarchy-plus-effort-allocation comparison, not
  a causal harness-only or token-budget-matched estimate.

BioFabric's rebuilt-image reference solution passed. Find's rebuilt-image
reference solution scored below its S3 pass threshold twice; an older image
passed once. The user accepted this documented, time-sensitive oracle-search
risk without changing the pinned task/verifier or requiring a lucky retry.
This does not make Find oracle-validated. Full harness discovery also has eight
M09 live-matrix failures from an absent `.agent-workspace/execute-matrix.py`;
focused launch/materialization, token-ledger, and Docker-bridge tests passed.

No reportable run is authorized by this manifest alone. Recheck exact IDs,
overlay hashes, runtime closure, power, and Docker availability immediately
before a separately authorized launch.

## 2026-09-25 BioFabric infrastructure-blocked attempt and repair

The first BioFabric H-MH launch, `biofabric-h-mh-15-20260925t084422z`, ended
BLOCKED without a verifier score. Its worker mounted a host `Cargo.lock` that
did not match the original image's `/app/Cargo.lock`, so offline Cargo stopped
before compilation. The sandbox also protected the worker worktree's Git
metadata; ROOT subsequently made the allowed source commit. Keep that attempt
and the original image ID above as historical evidence, not a scored result.

For a **new, clean-baseline BioFabric relaunch only**, the operator built
`swe-marathon-biofabric-rust-rewrite:host-lock-20260925` from the original
image with `scripts/Dockerfile.biofabric-host-lock` using
`docker build --provenance=false`. The new image ID is
`sha256:375a34a80ed17c7d577d7896edd346331bb4bda2e550868806b0e37d6554c9dc`.
Its `/app/Cargo.lock` and the host baseline both hash to
`3c0861070af5e72527b2ffcf3cc7436cae78d86e5a27398994babcb7dc014f71`.
The image fetched that lock's crates during construction, and the pinned
single-worktree Docker bridge subsequently passed an offline, no-network
`cargo test --workspace --no-run --locked --offline` on a clean starter lane.
`scripts/docker_task_workspace.py` pins this new image. No benchmark agent or
verifier was launched during the repair.

Codex's protected Git paths still prevent sandboxed workers from committing;
do not loosen their sandbox. ROOT must perform a narrow post-worker commit and
native review. Docker checks are ROOT-operated through the pinned bridge,
because workers cannot access the Docker daemon. The BioFabric ROOT overlay
files were amended accordingly; their new SHA-256 hashes are:

| Local file | SHA-256 for next BioFabric launch |
| --- | --- |
| BioFabric `AGENTS.md` | `27961f3c7186aa45597ee117a20efe1972f0b318434b05ea2943c11494f28053` |
| BioFabric `ROOT_RUN_PROMPT.md` | `187d782656c0737a58e045829894f8671950bccedf1279e9c79b44fbe6269db` |

The pinned verifier script had an LF-only operator copy under
`.harness-runtime/operator-only/`; `bash -n` passed without executing it.
A newly bootstrapped worker profile denied reads of that copy and host auth
and denied Docker access, while allowing its own `Cargo.lock` read. This
non-provider preflight epoch was closed after the check. The matching local
`harness-single` repair commit is
`01bfcd14642c8b62b1c9ebd9d0bf03646abe8771`.

The token collector now survives a Windows cp1252 stdout, and the ledger
handles repeated native `resume-lane` controllers appending to one transcript.
Its offline tests pass. The blocked attempt's archived, deduplicated usage is
`43,433,843` tokens (`26,310,556` ROOT plus `17,123,287` worker); ROOT's
in-chat sum of cumulative worker totals was not a valid token count.
No verifier score has been produced. The ROOT workspace now checks out fresh
branch `relaunch-biofabric-20260925` at baseline `934570e2`; the blocked
implementation remains on `main` at `0d6c659` and its generated SPEC/PLAN/goal
package was moved recoverably into the blocked run's result directory. Before
a new reportable attempt, freeze the updated source snapshot and rerun the
exact image/lock/runtime/power checks. Scoring remains paused pending the
user's direction.

### Relaunch preflight interruptions

On 2026-09-25, `biofabric-h-mh-15-20260925t132014z` exited before native
setup because its static prompt did not convey the user's new relaunch
authorization. Its separate ledger records 529,195 ROOT tokens and no worker.
`biofabric-h-mh-15-20260925t132411z` completed setup/specification but was
stopped before worker launch when ROOT inadvertently read the operator-only
verifier script while locating image evidence. That attempt is tainted and
unscored. Its generated specification files were archived with that attempt,
the operator-only verifier copy was removed from the ROOT workspace, and the
harness runtime was shut down. A fresh run must explicitly forbid traversal
of operator-only paths and start again from the unchanged task baseline.

### User-cancelled BioFabric relaunch

The clean relaunch `biofabric-h-mh-15-20260925t133258z` was stopped at the
user's request on 2026-09-25 around 16:30 UTC, before task completion or
verifier scoring. It is a cancelled, unscored attempt, not a failed benchmark
score. The exact collector process tree was terminated. The BioFabric harness
monitor reports `STOPPED`; no process command line references this run's epoch
`52e153e4d31f497ea801521e42586179`, and none of the epoch's recorded lane
controller process identities is alive. No container from the pinned BioFabric
image is running.

The harness shutdown could not certify cleanup of the already review-pending
STEP-02 lane: its last controller status was overwritten during shutdown with
`provider_state: starting`, no provider PID or process boundary, and
`cleanup_proven: false`. A lane-specific force-stop also returned
`FORCE_STOP_PROCESS_SURVIVED` despite the OS liveness checks above. The runtime
metadata remains `SHUTTING_DOWN`; do not reuse it for another run until this
proof/reconciliation issue is resolved and a fresh setup is performed. The
cancelled run's logs, task worktrees, and custody commits were preserved.

### Final interrupted ZSTD local pilot (2026-09-26)

Run `zstd-h-h-10-20260925t185239z` finished as an explicitly **partial**
Terra/high ROOT-plus-worker submission, not a full decoder and not a faithful
continuous SWE-Marathon trial. Its initial segment and three same-thread ROOT
continuations all used `gpt-5.6-terra`/`high`/priority. After a terminal ROOT
turn left an OPEN but quiescent review-pending lane, the collector gained the
explicit `--continue-open-runtime` path: it requires sealed ROOT usage, zero
in-flight invocations, and cleanup-proven exited review lanes. All 30 offline
collector/bridge tests passed. No new trial ID or epoch was substituted.

ROOT accepted STEP-03 only as a partial improvement and integrated
`src/zstd_decompress.c` in commit `7d2d8a1`; final checkpoint commit is
`a45b033`. A frozen validation lane matched the integrated commit and source
blob, and the public bridge passed 3/6 (`simple`, `img.png`, `repetitive`).
The remaining `audio.wav`, `img.bmp`, and `video.mp4` samples failed. Native
lanes were settled/retired, final scan found no active lanes or orphaned
leases, and the ZSTD runtime is `CLOSED`.

The operator-only verifier used the pinned image
`sha256:3a43d4f3658c4a21115c518937b692692e9e721d3b6e4a3205972917b8bc2e8a`
and pinned `tests/test.sh` hash
`453aa960844288d914b2c2a094759ac761638ca8990a3a32c112e4c0a4d79bd8`.
Its CRLF line endings were removed only in the Bash input stream, as in the
oracle preflight; the host script was not edited. The verifier built the
frozen source, confirmed Makefile integrity and no libzstd dependency, and
wrote `results/zstd-h-h-10-20260925t185239z/verifier-20260926/metrics.json`:
**3/6 public, 20/37 hidden, 23/43 total, raw `partial_score=0.535`, binary
reward `0`**. The saved verifier source artifact's SHA-256 matches the final
ROOT decoder source: `ecfa35295d06631ad2cb2c131a3e3677daeb155a37ee566853d5e516d7f20a18`.
Relative to the supplied oracle's 0.767 partial reference, this is 69.8%
locally; it is not an official pass. The exact disposable scoring container
was removed after the metrics and source artifacts were preserved.

The finalized archive is `results/zstd-h-h-10-20260925t185239z-ledger/`.
It reports 7,592.251 active seconds (2h 6m 32s) across four ROOT segments,
44,291 paused-wall seconds (12h 18m 11s), three ROOT resumes, no errors and
no in-flight calls. `known_total_tokens=102805139` is only a **lower bound**:
one earlier DNS-failed worker has unknown usage, so
`token_total_is_exact=false` and token-matched comparisons are invalid.
The run stopped voluntarily before the 10-hour cumulative ceiling. Its raw
0.535 partial falls inside the published Terra/xhigh ZSTD range
`[0.512, 1.000]`, and reward is 0; therefore the conditional C-X raw control
does not trigger. No raw control was launched.

### Fresh one-hour ZSTD H-H trial (2026-09-26)

**Excluded by user direction.** This run is preserved only as a negative
prompt-design example, not as a performance comparison or best-effort
one-hour result: its instructions let ROOT declare an intentionally partial
slice complete after 16 minutes. The follow-up run must target the entire
decoder and keep iterating while time remains.

At the user's request, a separate ZSTD Terra/high ROOT plus Terra/high worker
trial was started from the same 13 agent-visible baseline files in a fresh Git
repository at `root_runs/zstd-decoder/trial-1h-20260926/`. It was placed under
the already-shared ZSTD host directory solely for Docker Desktop file sharing;
its Git history contains only its own baseline and this trial, not the earlier
implementation. The prior ZSTD result was not used as an implementation input.
The prompt and `AGENTS.md` required harness setup, specification, topology,
and a plan scoped to what was achievable within one continuous hour. The
collector enforced `--watchdog-hours 1` with **no token cap**, explicit
Terra/high ROOT, Terra/high/priority worker, and ROOT-only host access. Its
bounded plan targeted raw/RLE and frame-validation behavior, expressly
deferring compressed blocks, entropy/sequences, and trained dictionaries.

An initial ID `zstd-h-h-1h-20260926-01` failed before Codex started because
Python could not resolve the npm `codex` shim as a native executable. No model
or worker task work occurred under that ID. The actual trial was relaunched
as `zstd-h-h-1h-20260926-02` with the installed native `codex.exe` on PATH;
the host CLI reported `0.155.0`, a disclosed version difference from the prior
interrupted pilot. The new run finished voluntarily after **961.719 seconds
(16m 1.719s)**, not at the one-hour watchdog. ROOT commit `8f0e6a3` contains
the partial decoder and `d2e7167` its handoff. One worker's protected Git
index lock prevented its own commit; ROOT reviewed and committed the source,
and native shutdown retired the rejected review lane. Runtime state is `CLOSED`.

The write-once ledger at `results/zstd-h-h-1h-20260926-02-ledger/` reports
**6,380,433 aggregate tokens** (4,180,127 ROOT; 2,200,306 worker), including
6,330,378 input, 6,109,696 cached input, and 50,055 output tokens. Thus
270,737 input-plus-output tokens were non-cached; cached input is a subset of
input, not extra tokens. It has zero errors, zero in-flight or unknown-usage
invocations, and `token_total_is_exact=true`.

The operator-only sealed verifier used pinned image
`sha256:3a43d4f3658c4a21115c518937b692692e9e721d3b6e4a3205972917b8bc2e8a`
and pinned `tests/test.sh` hash
`453aa960844288d914b2c2a094759ac761638ca8990a3a32c112e4c0a4d79bd8`.
It received a frozen copy of the committed candidate, with CRLF removed only
from the Bash input stream. Its Makefile and anti-libzstd checks passed. The
saved verifier source SHA-256
`5bec7d60e8beaf008d5aa4462bb311b84cc0846438cad07b4865515adcf87a5f`
matches ROOT's final source. Results at
`results/zstd-h-h-1h-20260926-02/verifier-20260926/` are **2/6 public,
5/37 hidden, 7/43 total, raw partial 0.163, binary reward 0**. Relative to
the supplied oracle's 0.767 partial reference, this is 21.3% locally, not an
official score adjustment. The exact disposable verifier container was removed
after artifacts were copied. This is a 16-minute early-finished trial under a
one-hour ceiling, not evidence of how the same agent would perform if it used
all 60 minutes.
