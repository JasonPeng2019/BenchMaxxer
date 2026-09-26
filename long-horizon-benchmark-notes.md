# Long-Horizon Coding Benchmarks for Harness Evaluation — Working Notes

> 2026-09-25 protocol update: the user chose **uncapped** reportable runs.
> ROOT and worker token usage will be measured and compared after each run,
> not limited by a shared B. Older B/token-cap language below is historical
> planning context, not the active pilot protocol. See `AGENT_TODO.md` and
> `scripts/TOKEN_LEDGER_PLAN.md` for current run gates.

Eval design for testing a multi-agent harness + skill suite against raw coding-agent
CLIs on two ultra-long-horizon coding benchmarks: **SWE-Marathon** and **LHTB**.
The causal core uses the same model in both arms; a separate system-economics comparison
may use a cheaper model, but must not be described as a causal harness result.

> **Caveat on sources:** Both benchmarks were published in 2026 and post-date the
> assistant's training cutoff; figures are drawn from the papers, repos, and
> leaderboards cited in the References. Model names that appear in results (GPT-5.x,
> Gemini 3.1, Claude Opus 5, etc.) are reported as-is from those sources. Verify current
> numbers before relying on them — this space moves fast and both benchmarks are
> actively being hardened.

---

## 1. Goal / setup

Benchmark a **multi-agent harness + skill suite** against the **raw Codex CLI** on
long-horizon coding tasks. The active first experiment is a **hierarchical
compute-allocation** study in the **10M-token-per-task** neighborhood:

- **H-MH (treatment):** `gpt-5.6-terra` at `max` for ROOT and
  `gpt-5.6-terra` at `high` for every worker.
- **C-X (primary raw comparison, when triggered):** one raw `gpt-5.6-terra` agent at
  `xhigh`.
- **C-M (effort ablation, only if needed):** one raw `gpt-5.6-terra` agent at `max`.

The product question is whether a stronger ROOT can direct cheaper workers to reach a
better quality–token frontier than a single maximum-effort agent. This is the main
intended use of the harness. It deliberately changes **both** orchestration and the
allocation of reasoning effort, so it is not a harness-only causal test. A later,
separately labelled causal study may hold the model and effort constant in both arms.

The task thesis is that a good coding system can improve planning, recovery, verification,
and long-context execution — so the benchmarks are chosen because the *scaffolding* may
be the binding constraint, not just raw model capability.

Two design consequences that shape everything below:

- **The failure modes should be scaffold-addressable** — planning, self-verification,
  context/memory management, recovery, premature termination — rather than
  raw-capability-bound (novel algorithm design, research insight). Both SWE-Marathon and
  LHTB qualify.
- **Name the estimand correctly.** H-MH versus C-X estimates the end-to-end result of
  hierarchy plus asymmetric effort allocation against the original raw-xhigh setup. C-M is
  a conditional effort ablation, not the primary control. A harness-only claim requires a
  later study that holds model, reasoning effort, task, tools, network policy, continuation
  policy, and budget fixed.
- **Capability and efficiency belong in the same matrix.** The result should show whether
  the treatment reaches more correct end states *and* what tokens/cost it needed to do so,
  rather than treating a high score bought with arbitrary extra compute as a harness win.

---

## 2. SWE-Marathon (Abundant AI)

The best fit for the thesis, and one of the only benchmarks that reliably clears the
~10M-tokens/task bar.

- 20 ultra-long-horizon tasks, each with a bespoke executable environment, a
  human-written reference solution, and a **multi-layer verifier**.
- Logged agent attempts average **27.2M tokens/task** (right tail to ~877M); tasks run
  ~2–10 hours. Frontier agents solve **<30% pass@1**.
- Documented failure modes: **weak self-verification, self-reported infeasibility,
  premature termination** — essentially a spec sheet for what a good harness fixes.
- Flags **reward hacking in 13.8% of rollouts**; ships adversarial test-suite review +
  multi-layer checks to resist shortcuts.
- **Runs on Harbor** (`scripts/run-benchmark.sh`), explicitly designed to run trials
  with *any model or harness* — dropping in a same-model treatment arm is a first-class
  path.

**Why it fits:** the failure modes are scaffold-addressable, the verifiers are functional
(trustworthy deltas), and it's harness-swappable by design.

### Active first study: local two-task hierarchical-allocation screen

The first study is intentionally a **budget-limited external-reference screen**, not a
full paired causal matrix. It starts with the system configuration actually of interest
(H-MH) and uses the released Terra/xhigh results to decide whether the primary raw C-X run
is worth the additional subscription allowance. C-X is the local token-cap anchor for the
original raw-xhigh setup. C-M is reserved for diagnosing an apparent H-MH advantage that
could instead be explained by H-MH spending more tokens.

- **Pinned suite:** SWE-Marathon commit
  `f34867643bf07aec5208a861e667e01df0942099`, the revision in use for the public xhigh
  reference trials. Both selected tasks are CPU-only: 4 CPUs, 16 GB RAM, 20 GB storage,
  and no GPU.
- **BioFabric:** `biofabric-rust-rewrite`; native agent timeout 10 hours. Public
  `Codex / openai/gpt-5.6-terra / xhigh` is 0/8 passes, partial 0.963--0.980 (mean 0.973),
  26.53M--101.53M tokens, and 27--116 minutes per run (51 minutes mean). It is the
  near-completion, high-token persistence and verification case.
- **Find Network Alignments:** `find-network-alignments`; native agent timeout 8 hours.
  Public Terra/xhigh is 0/8 passes, partial 0.551--0.784 (mean 0.684), 20.81M--110.87M
  tokens, and 46--179 minutes per run (89 minutes mean). It is the CPU task where raw
  Terra/xhigh most clearly sustains multi-hour work.
- **First paid runs (H-MH-15):** run the full harness + complete skill suite once per task;
  configure ROOT as `gpt-5.6-terra` / `max` and every worker as
  `gpt-5.6-terra` / `high`. The 15-hour watchdog protects machine availability only. Do
  not run local raw Codex first.
- **Shared token ceiling:** before any paid task, freeze one per-task aggregate token budget
  **B**. It covers every ROOT and worker Codex invocation, not just the final ROOT
  transcript. Both C-X and any C-M ablation use the same B. The H-MH watchdog may remain
  15 hours and each raw watchdog 10 hours because coordination can add wall-clock latency;
  neither time limit is the primary compute budget. If a watchdog fires before pass or B,
  label that run time-censored and do not call the pair token-cap matched.
- **First diagnostic trigger:** for each task independently, run one fresh C-X-10 raw-Codex
  comparison only if the H-MH-15 result is materially unexpected after the pinned task hash
  and verifier are confirmed: a pass, a final partial score outside the released Terra/xhigh
  range above, or a predeclared token/budget-telemetry anomaly. Before launch, record the
  numerical definition of the anomaly and B in the manifest. C-X means raw
  `gpt-5.6-terra` / `xhigh`.
- **Effort-ablation trigger:** run one fresh C-M-10 raw Terra/max agent only if C-X is
  materially worse on the verifier result than H-MH **and** C-X has materially fewer
  aggregate tokens than H-MH. This asks whether the apparent H-MH advantage is simply
  additional max-effort compute. Record the numerical quality and token-difference
  thresholds before H-MH starts.
- **Interpretation:** an H-MH-15-only result is a descriptive product case study against
  external Terra/xhigh context. It cannot support a local "better for cheaper" claim. An
  H-MH/C-X pair at shared B is the small-N **system-level** quality–token comparison. C-M,
  if triggered, is an explanatory ablation; none of these establish a harness-only causal
  claim.

### Agreed first-run record (specification only; do not launch yet)

This is the complete current agreement for the first local SWE-Marathon screen. The runner
and token tooling are still unfinished; this section is a record of the intended experiment,
not authorization to run it.

| Task | Harness first run | Conditional raw sequence | Why this task | Token requirement |
|---|---|---|---|---|
| `biofabric-rust-rewrite` | One H-MH-15: full harness + complete skill suite; ROOT Terra/max, workers Terra/high; 15-hour watchdog | C-X-10 raw Terra/xhigh if H-MH passes, partial falls outside 0.963--0.980, or its first trigger fires. C-M-10 raw Terra/max only if C-X is worse and materially lower-token than H-MH. | Near-pass, sustained verification case | Preserve a distinct JSONL/usage record for ROOT and every worker; aggregate unique invocations to B and retain components, elapsed time, and verifier result. |
| `find-network-alignments` | One H-MH-15: full harness + complete skill suite; ROOT Terra/max, workers Terra/high; 15-hour watchdog | C-X-10 raw Terra/xhigh if H-MH passes, partial falls outside 0.551--0.784, or its first trigger fires. C-M-10 raw Terra/max only if C-X is worse and materially lower-token than H-MH. | CPU-only task where public Terra/xhigh sustained multi-hour work | Preserve the same per-process and aggregate token evidence. |

Both tasks use pinned SWE-Marathon revision `f34867643bf07aec5208a861e667e01df0942099` and
the shipped verifier. Before interpreting a run, confirm its task hash/verifier match that
revision. The host-side CLI remains authenticated by the existing ChatGPT subscription; no
credential may enter the task or verifier container.

**Token collection is mandatory for every run.** The token record is per task, not an
on-screen estimate: retain the native `codex exec --json` artifact for every process and
extract each terminal cumulative usage object. Keep provider-reported total tokens and the
component fields (`input`, `cached input`, `output`, and `reasoning`) separately; cached
input must not be added to input a second time. Save the run manifest (task, arm,
ROOT/worker role, effective model/effort, sandbox, watchdog, B, start/end, exit status),
final diff, and final verifier/partial result beside the token ledger. A local H-MH-only
outcome cannot establish token efficiency; only a matching local H-MH/C-X pair at B can be
described as a system-level token-and-quality comparison. C-M is an optional follow-up
ablation, not a required first comparison.

Together, the tasks test complementary allocation claims: BioFabric asks whether a
maximum-effort ROOT can direct high-effort verification into a pass, while Find Network
Alignments asks whether hierarchy can organize a multi-hour trajectory without drift.

---

## 3. LHTB (Long-Horizon-Terminal-Bench)

One of the best fits for *demonstrating harness value on a fixed model* — for a reason
unrelated to token count (dense partial-credit grading).

**What it is:** 46 containerized terminal tasks across nine domains (experiment
reproduction, software/reverse engineering, multimodal analysis, interactive games,
scientific computing, earth/energy, security/performance, robotics, EDA, APEX
professional workflows). Each task is a deliberately "broken" project the agent must
inspect, patch, validate, and iterate on. **Companion to Terminal-Bench 2.0; evaluated
with Harbor** (Terminus-2 harness by default; Codex for the GPT-5.3 run). Calibrated by
running DeepSeek-V4-Pro under **1.5-hour** budgets until tasks were "challenging but
still solvable in principle." Headline: strongest model (GPT-5.5) resolves only **15.2%**
at R≥0.95; **mean pass rate across models 4.3%**.

### Cost / horizon per task (90-min timeout)

Averages: **9.9M tokens, ~231 episodes, ~85 min, ~$10.2** per task. But it's
model-and-harness dependent and *straddles* 10M:

| Model | Tokens/task (M) | Episodes/task | Time/task (min) | Cost/task ($) |
|---|---|---|---|---|
| GPT-5.5 | 4.16 | 208 | 72.9 | 21.46 |
| MiniMax M3 | 20.20 | 314 | 90.0 | 6.13 |
| Kimi K2.7 Code | 8.54 | 183 | 85.4 | 8.31 |
| DeepSeek V4 Pro | 14.45 | 321 | 83.6 | 6.32 |
| Qwen3.7 Max | 6.13 | 218 | 83.5 | 7.78 |
| Doubao Seed 2.1 Pro | 5.80 | 183 | 91.7 | 5.16 |
| Gemini 3.1 Pro | 3.55 | 148 | 85.0 | 7.61 |
| GLM 5.1 | 5.84 | 120 | 92.6 | 5.13 |
| GPT-5.3 Codex | 4.57 | 299 | 80.7 | 8.20 |
| GLM 5.2 | 8.43 | 195 | 89.3 | 11.93 |
| Qwen3.6 Plus | 8.67 | 194 | 88.6 | 4.47 |
| Hy3 | 17.21 | 258 | 91.3 | 2.47 |
| GPT-5.4 | 10.90 | 302 | 79.3 | 27.57 |
| Kimi K2.6 | 10.27 | 188 | 92.5 | 9.94 |
| Grok 4.20 | 16.23 | 288 | 69.5 | 20.63 |
| **Average** | **9.66** | **228** | **85.1** | **10.21** |

### The token-floor tension (important)

On LHTB the horizon is pinned by **wall-clock** (90 min / ~228 episodes), not by tokens —
token count is *downstream* of how efficiently the harness+model spend that budget.
GPT-5.5 burns the fewest tokens precisely because it loops less; GPT-5.4 costs more than
the stronger GPT-5.5 because it runs more episodes (302 vs 208) doing redundant work.

**Consequence:** a hard 10M-token floor is in tension with what you're proving. A *good*
harness (less redundant exploration, better context compaction, no re-verify loops)
spends *fewer* tokens on the same task and could drop below the gate. The paper says as
much — the binding constraint is "budgeting a long horizon," and it expects gains from
reducing redundant exploration / preserving state / avoiding repeated verification loops
to exceed gains from better single-step reasoning. **Token count is a poor proxy for
horizon when harness efficiency is the variable under test.** (At a larger wall-clock
ceiling, cumulative token use will usually rise, but it should remain an outcome rather
than an eligibility gate.)

### Why LHTB fits the harness thesis: dense reward

Each task is decomposed into weighted subtasks with **continuous per-subtask scores**
(binary checks, thresholded/continuous metrics, and episode-aggregating scores), and the
reported reward `R = Σ wₖrₖ / Σ wₖ` captures *how far* an agent gets, not just whether it
finishes. On a fixed-model causal comparison, full passes may still be sparse; a
threshold-scored benchmark can show a wall of zeros, whereas LHTB's mean-reward axis is
exactly where a harness delta becomes visible.

Failure distribution backs this up: **79% of unresolved runs are timeouts still making
partial progress** (mean reward only 0.10–0.35); **near-misses (0.75 ≤ R < 0.95) occur
>2× as often as full passes**; ~19% are early exits, including **"false finishes"**
(high-reward voluntary stops that fail the hidden verifier — weak self-verification). All
signal a binary benchmark discards.

### Verifier integrity caveat

An audit of one 46-task sweep found **14 of 17 perfect scores were obtained by reading
the grader rather than solving the task**. Since patched (binary-feedback default,
isolated verifier); hardened runs must be reported separately from the pre-patch
snapshot. **Use the hardened config and audit trajectories** — same reward-hacking
caution as SWE-Marathon's 13.8%.

---

## 4. Extended-capability budgets: a 3× multiplier

Both SWE-Marathon and LHTB are open-source **Harbor task suites**, so the budget is a
config value, not baked into the task. A Harbor task is a directory with a `task.toml`
(metadata, timeouts, resource specs) plus `instruction.md`, an `environment/` (Docker),
and `tests/`.

### The budget rule

Keep every benchmark's native-budget track intact. For the extended-capability track,
use a **3× multiplier on that task's published wall-clock allowance** — not an arbitrary
24- or 48-hour cap. It gives a slower, process-heavy harness a meaningful recovery window
without changing the regime into an open-ended endurance test.

- **LHTB:** 90 min × 3 = **300 min / 5 h** per task. This is the primary extended protocol.
- **SWE-Marathon:** apply 3× to each task's native 2–10 h limit, yielding **6–30 h**. That
  is a future, much more expensive extended protocol; retain native per-task limits for
  the first SWE-Marathon study.

The active two-task H-MH screen in section 2 is a deliberate exception for cost control:
it uses a 10-hour watchdog for conditional raw C-X-10 (and C-M-10 only if its ablation
trigger fires) and a 15-hour allowance for initial harness H-MH-15 runs. Its primary
compute budget is the shared aggregate token ceiling B, not time. It is not a 3x result and
must not be pooled with the later formal
extended-capability track.

The cap is a ceiling, never a target: a verified pass ends the trial early.

### You have four budgets/policies, not one

Bumping only the wall-clock limit will silently get cut off:

1. **Wall-clock:** `timeout_sec` in the `[agent]` block of `task.toml`. For LHTB's
   extended protocol, set it to **18,000 seconds** (300 minutes), preferably via a
   job-level override rather than by editing every task.
2. **Turn / iteration cap:** e.g. Terminus-2 runs `max_turns: 500`. Leave this and the
   agent stops at turn 500 regardless of remaining clock. Raise every turn cap by the
   same 3× multiplier; fixed iteration caps otherwise silently cut off long unattended
   tasks.
3. **Token / dollar runaway guard:** set the same predeclared ceiling in every arm. It
   must be high enough not to be the expected binding limit at 3× time; it is a safety
   rail, not a target or a post-hoc per-arm adjustment.
4. **Continuation policy:** both arms must receive the same policy after an unverified
   early stop (see §5). This matters as much as the numerical caps.

The verifier's own scorer timeout is separate and can usually be left alone.

### LHTB-specific: `continue_until_timeout`

- Lives in the `[agent]` block of `task.toml`; set on **30 of 46 tasks**. When on, after
  the agent declares itself done the harness reruns the hidden verifier and, if not
  passed, **resumes the same session with the feedback**, repeating until timeout or pass.
- At the 5 h LHTB ceiling, an agent that "finishes" early but has not passed is given a
  bounded opportunity to inspect, verify, and repair its work under the benchmark's
  normal verifier signal — not human steering. The same behavior must apply in both
  experiment arms.
- **You need LHTB's harness patch** for the flag to do anything — stock upstream Harbor
  ignores it and those tasks run single-shot (and score lower).
- More runway also = more chance to find the grader-reading exploit → run the hardened
  isolated-verifier config.

### Caveats when you extend the budget

- **Calibration shift → not comparable to the published leaderboards.** LHTB was tuned to
  ~90 min and SWE-Marathon to 2–10 h. At 3× native budget, the difficulty profile still
  changes, so report it as a **modified 3× capability protocol**, not as an official
  "LHTB" or "SWE-Marathon" leaderboard score.
- **Reward-hacking risk grows** with time budget → hardened verifiers + trajectory audits.
- **Cost.** Wall-clock parallelizes across containers (Harbor runs on Modal / Daytona);
  **dollars and tokens do not**. A 5 h LHTB sweep is already 230 container-hours per arm
  and trial across 46 tasks; a 3× SWE-Marathon sweep is considerably larger. LHTB's
  cost-reward frontier already shows that higher spend does not imply higher score.
  **Pilot on a small, preregistered, difficulty- and domain-balanced slice first** before
  committing to full-suite trials.

---

## 5. One experiment: causal capability *and* token efficiency

The extended-capability question is not whether an agent can occupy an arbitrary number of
hours. It is whether a slower process-oriented harness uses its extra runway to converge,
rather than to loop, drift, or accumulate errors. The LHTB 300-minute protocol is long
enough to expose that distinction while remaining close to its original task regime.

### Experimental matrix

Run both tracks on the same preregistered tasks and trial indices:

| Track | Budget | Purpose |
|---|---:|---|
| Native | LHTB 90 min; SWE-Marathon task-native 2–10 h | Benchmark-calibrated efficiency baseline |
| Extended capability | 3× each task's native limit; LHTB = 300 min / 5 h | Eventual capability under a shared, process-tolerant ceiling |

Within each track, use a paired causal comparison:

- **Control:** raw Codex on `gpt-5.6-terra` / `xhigh`, with no suite instructions.
- **Treatment:** the harness + full skill suite on the identical model and reasoning
  effort.
- **Fixed conditions:** task image/base commit, tool access, network policy, model version,
  wall-clock limit, token/dollar runaway guard, task selection, and trial index.

The optional cross-model cheaper-system comparison belongs in a different table and is
never pooled into the causal harness estimate.

The active local two-task H-MH screen is outside this matrix: it compares Terra/max ROOT +
Terra/high workers with the existing eight-trial Terra/xhigh references first, then
conditionally launches local raw Terra/xhigh C-X-10 at B. Raw Terra/max C-M-10 is only an
effort ablation if C-X is worse and materially lower-token than H-MH. Keep its outcomes
separate from this eventual same-budget, paired causal estimate.

### Stop modes and a neutral capability ceiling

Measure two stop policies, applied identically to both arms:

1. **Autonomous stop:** let the agent decide it is done. This measures how much work is
   completed without a human nudge.
2. **Neutral capability ceiling:** end only on verifier pass or budget exhaustion. If an
   agent stops without a pass, resume its **same native session** with the same generic
   continuation instruction in both arms. Do not supply hidden subtask scores or
   arm-specific advice. On LHTB, use the hardened `continue_until_timeout` path where it
   is part of the benchmark configuration.

The second control should be named accurately as **raw Codex + neutral persistence shim**,
not as unmodified raw Codex. It is the mechanically neutral control required to test
eventual capability. The gap between the two stop policies quantifies reward that a human
"keep going" prompt would otherwise leave on the table.

### Pre-registered quality–cost claim

The causal result and the efficiency result are two views of the same trial trajectories.
For every run, record final reward/pass, cumulative input/cached-input/output tokens,
counterfactual API cost, wall-clock, turns, stops, resumes, and verifier/audit findings.

Call the paired suite **better for cheaper** only if it meets both conditions under the
same shared ceiling:

1. It has higher final verifier reward or pass rate (with a preregistered margin and
   confidence interval); and
2. It uses fewer tokens and lower counterfactual cost to reach the same preregistered
   quality threshold — e.g. `R ≥ 0.8`, `R ≥ 0.95`, and full pass.

Report reward-per-million-tokens and tokens-per-unit-reward as supporting measures, not
replacements for matched-quality thresholds. If the treatment is more correct but costs
more, report a capability win with an efficiency trade-off; do not claim it is cheaper.
If it is cheaper but less correct, report the inverse trade-off. Wall-clock time to each
threshold is a third axis and may legitimately be worse for the treatment.

### Reward trajectories and censoring

To see whether the harness is progressing rather than merely spending time, preserve
state snapshots at fixed checkpoints — for LHTB, 90, 180, and 300 minutes — and grade
cloned/isolated copies where task mechanics permit. Never reveal those intermediate grades
to either agent. Plot reward against both wall-clock and cumulative tokens/cost.

Runs that never reach a threshold are **right-censored** at the shared cap. Do not treat
their time-to-threshold or tokens-to-threshold as zero or omit them. Analyze treatment minus
control paired by task and trial, with task-level bootstrap confidence intervals.

---

## 6. Methodology cautions (harness-vs-harness)

- **Raw Codex is not a minimal baseline.** Native scaffolds (including Codex CLI)
  perform **~1.5–2× more tool calls** than a minimal mini-swe-agent scaffold, with
  sub-agent delegation, planning, and TODO-list ops available only on the native
  scaffolds — plus model-tuned editing primitives (`apply_patch` on GPT, `str_replace` on
  Claude) and model-specific system prompts. The causal result is therefore a comparison
  against an already-strong, model-tuned harness. **Add mini-swe-agent as a minimal third
  baseline** only if a floor as well as a native-CLI ceiling is useful.
- **Hold model + budget fixed; report quality, cost, and wall-clock, not just pass@1.** The framing
  to know is the **Binding Constraint Thesis** ("Stop Comparing LLM Agents Without
  Disclosing the Harness"): the execution harness is often a stronger determinant of
  performance than the model it wraps, and current protocols mis-credit harness gains to
  models. A shared runaway ceiling prevents unlimited spending, but matched-quality
  tokens-to-threshold and a quality–cost frontier are what establish that the scaffolding
  earns its keep. Princeton **HAL** (Holistic Agent Leaderboard, ICLR 2026)
  was the reference implementation of cost-controlled cross-benchmark eval (archived
  mid-2026; the cost-control idea is the durable part).
- **Verifier quality gates your signal.** Prefer execution/functional verifiers — and
  both benchmarks give you these. SWE-Marathon's multi-layer suite and LHTB's hidden
  rebuild-from-artifact checks are functional rather than LLM-judged, so small deltas
  aren't swamped by grader noise. (This is also why the reward-hacking audits matter: a
  functional verifier is still gameable if the grader is readable — see §3, §4.)
- **Audit trajectories for reward hacking.** A *more capable* orchestration layer can
  *increase* shortcut-taking; a clean-looking pass@1 can hide it (SWE-Marathon 13.8%;
  LHTB's grader-reading exploit).
- **Sample size / error bars.** SWE-Marathon is 20 tasks, LHTB 46. Use pass@k / mean@5 and
  partial-credit metrics; wide error bars at these sizes, so pilot before drawing strong
  conclusions.

---

## 7. Infra notes

- **Harbor is the common substrate.** SWE-Marathon and LHTB both run on Harbor, so
  standardizing on it lets you slot your harness in once and run both targets through the
  same plumbing — and keep budget/cost controls consistent. Harbor supports Claude Code,
  Codex, Gemini CLI, OpenHands, Aider, etc. as agents.
- **Parallelism** via Modal / Daytona (thousands of environments); wall-clock scales, cost
  does not.
- **Pilot first.** A 5 h LHTB sweep is already 230 container-hours per arm and trial;
  3× SWE-Marathon is larger still. Keep the pilot task slice and all caps preregistered.
- **Local-first exception for the active screen.** The published SWE-Marathon launcher uses
  Modal, but the active H-MH-15/C-X-10 screen uses a custom local runner. This saves Modal and
  API-key requirements, but it is not an official leaderboard reproduction. Pin the task
  revision and preserve the shipped verifier so the execution difference is explicit.

---

## 8. Setup & execution -- active local screen and later official route

The published SWE-Marathon script launches Harbor jobs on Modal. The active screen instead
uses a **local custom runner**: host-side Codex edits a dedicated task workspace while
Docker builds, tests, and verifies that workspace. This preserves the task image and
multi-layer verifier without requiring Modal or an API key. It is a local comparative
protocol, not an official SWE-Marathon leaderboard submission.

### Active local H-MH-15/C-X-10 setup

The ChatGPT subscription authenticates the **host-side Codex CLI**; it is independent of
execution isolation. Do not copy `auth.json` or any access token into a task or verifier
container. The run has three distinct boundaries:

```text
Host: Codex CLI + existing ChatGPT login + dedicated workspace-write sandbox
  -> edits only the run workspace
Local runner: owns Docker and exposes controlled task-test / verifier actions
Docker: credential-free task build/test environment and final no-network verifier
```

Do not give the agent unrestricted access to the host Docker daemon: Docker can bypass a
normal workspace-write boundary. The runner, not the agent, creates containers and mounts
only the current run workspace. This avoids fragile container-login handling and keeps
subscription credentials out of benchmark artifacts. The trade-off is that Codex runs in
its local workspace sandbox rather than inside the published Harbor agent container; use
the same arrangement for H-MH-15, C-X-10, and any conditional C-M-10.

1. Start Docker Desktop; confirm `codex login status` says ChatGPT and record
   `codex --version`.
2. Clone SWE-Marathon and check out `f34867643bf07aec5208a861e667e01df0942099`.
3. Build/run the BioFabric and Find Network Alignments oracles and shipped verifiers locally
   at zero model cost. Record each task hash and image digest; abort that task's
   public-reference comparison if either differs.
4. Complete and validate the token ledger through a non-reportable host-to-Docker smoke:
   prove that containers/artifacts contain no credentials; ROOT resolves to Terra/max;
   workers resolve to Terra/high; every process yields a distinct nonzero JSONL usage
   record; and aggregate accounting does not double-count a resumed or replayed process.
5. Freeze B, the two public xhigh references, the C-X trigger, and the C-M ablation
   thresholds. Then launch one H-MH-15 run per task. Launch C-X-10 and, only if warranted,
   C-M-10 according to those triggers.

### Later: official Harbor/Modal reproduction (not the active screen)

### 1. Install Harbor + prerequisites

```bash
uv tool install 'harbor[modal]==0.20.0'
# system: Docker running; Git LFS (for LHTB's large assets)
```

Version note: SWE-Marathon requires `0.20.0` (with the `modal` extra), which is also the
Harbor version LHTB's `continue_until_timeout` patch was cut against — so pinning
`0.20.0` keeps both consistent. LHTB's current README installs Harbor unpinned, so if its
repo has since moved to a newer Harbor and `0.20.0` chokes on its configs, run each
benchmark from its own version (`uvx harbor@<ver> ...` or a venv per repo) instead of one
global install. The LHTB oracle smoke test (step 2) tells you immediately whether
`0.20.0` is fine for it.

Authentication experiment — validate one real agent trial before scaling:

```bash
codex login              # use the supported headless/device-login path when available
claude setup-token       # use the provider-supported headless credential path when available
# Inspect the resulting Harbor job artifact: model identifier, auth route, and token fields.
```

### 2. Clone each and validate with the oracle

The oracle runs each task's shipped reference solution through the real verifier at $0
model cost — it confirms containers build and grading works, and surfaces broken tasks. Do
this before spending anything on agent runs.

```bash
# LHTB — local Docker, cheapest check, no API key, no Modal
git clone https://github.com/zli12321/LHTB && cd LHTB
git lfs install && git lfs pull
export DOCKER_DEFAULT_PLATFORM=linux/amd64        # Apple Silicon only
harbor run -c configs/examples/oracle_smoke.yaml

# SWE-Marathon — set up a Modal account first
git clone https://github.com/abundant-ai/swe-marathon && cd swe-marathon
#   oracle runs via each task's solve.sh — see scripts/run-benchmark.sh
```

### 3. Wire your harness in as an agent

Where the installed Harbor version ships them, `codex` and `claude-code` adapters are the
starting point for native-CLI baseline arms. Verify their exact model-selection and auth
semantics before calling either arm "raw." For the treatment, implement a custom agent
against Harbor's agent interface (roughly `setup(env)` → `run(instruction, env, context)`;
the Harbor Cookbook and AGENTS.md have the scaffolding) and select it with
`--agent <your-agent>`. The treatment and control must use the same model identifier,
reasoning effort, credential route, and benchmark-visible tool permissions.

### 4. Launch

```bash
# LHTB (local Docker; edit model_name / n_concurrent_trials / timeouts in the YAML)
harbor run -c configs/examples/full_benchmark.yaml

# SWE-Marathon (Modal compute; per scripts/run-benchmark.sh, with your agent + model)
```

Extended-capability budget: apply the **3× native-budget rule** to `timeout_sec` and every
turn cap together. For LHTB, that is `18000` seconds / 300 minutes; also confirm its
hardened `continue_until_timeout` patch is active. Retain each SWE-Marathon task's native
budget for the first study; a future 3× run means 6–30 h per task and should be a separate,
explicitly costed campaign.

### 5. Grade

LHTB grades subtask-by-subtask (dense partial reward) in its hardened verification path;
SWE-Marathon runs its multi-layer verifier in its Modal task environment. Grading may be
patch-based — the runner captures the agent's final diff and applies the held-out tests
to a clean container — which doubles as an escape hatch: if wiring the harness into the
container is fiddly, run it anywhere, then apply its final diff to the real container and
run the shipped verifier. That escape hatch is mainly useful for SWE-Marathon's
patch-based tasks; LHTB is stateful terminal work, so the natural path is running the agent
in the real local-Docker container.

## 9. Order of operations & first-run checklist

1. **Start Docker Desktop**; confirm `codex login status` says ChatGPT and record the
   installed Codex version.
2. **Clone the pinned suite**, build the BioFabric and Find Network Alignments local task
   images, and validate each oracle/verifier before spending model usage.
3. **Complete and validate the token ledger** with a non-reportable host-to-Docker smoke.
   Confirm no credentials enter a container or artifact; the ROOT/worker effective settings
   are Terra/max and Terra/high; and per-process plus aggregate token telemetry is present.
4. **Freeze the references and triggers:** public Terra/xhigh is 0/8 for both tasks;
   BioFabric partial range is 0.963--0.980 and Find Network Alignments is 0.551--0.784.
   Freeze B, the numerical telemetry-anomaly definition, and the C-M quality/token
   thresholds. H-MH-15 triggers C-X-10 only on a pass, a final partial score outside its
   range, or that anomaly, after task-hash verification.
5. **Run H-MH-15 once per task.** Archive each manifest, per-process JSONL/usage ledger,
   aggregate token record, final diff,
   reward/partial, verifier/audit output, tokens, and elapsed time. Do not run raw Codex first.
6. **Run C-X-10 only if triggered.** Use a new clean task workspace and the same B. Run
   C-M-10 only when its effort-ablation trigger fires. Report H-MH-15 alone as an
   external-reference case study and H-MH/C-X as a small-N, system-level quality–token
   comparison; neither establishes a harness-only causal effect.

The later LHTB and official Modal/Harbor studies remain valuable, but they are explicitly
out of scope until this low-budget local screen is complete.

---

## 10. Cost & token-efficiency instrumentation

The repository includes an **unfinished design draft** at
[`scripts/collect_codex_usage.py`](scripts/collect_codex_usage.py). Do not use it to launch
an experiment yet. Its current single-process wrapper/parser is not sufficient for H-MH:
it cannot establish effective per-role configuration, discover all ROOT/worker processes,
deduplicate restarts, or enforce/report an aggregate per-task cap.

Before a reportable agent run, complete the ledger as a **telemetry component**, not a second
scheduler or replacement harness. It must neither read/copy credentials nor start a second
agent process merely to measure the harness. Required behavior:

1. Preserve one raw `codex exec --json` artifact per unique ROOT/worker invocation, together
   with a role, parent/worker relation, effective model and effort, start/end, and exit status.
2. Select each invocation's final cumulative `turn.completed` usage rather than summing JSONL
   events. Preserve reported total, input, cached-input, output, and reasoning separately;
   cached input is a subset of input and is never added a second time.
3. Aggregate unique invocation records into one immutable per-task ledger. A resumed or
   replayed transcript must not be counted twice. When `total_tokens` is absent, label
   `input + output` as a derived comparison total and retain the raw fields. First validate
   on a subscription trace with nonzero reasoning whether `output_tokens` already includes
   `reasoning_output_tokens`; never add reasoning a second time by assumption.
4. Report consumption against B continuously enough for the native harness resource policy to
   stop launching further work. Record unavoidable in-flight overshoot rather than concealing
   it. Do not add an external scheduler, retry controller, or collaboration relay.
5. Emit a final manifest, aggregate `usage.json`, raw JSONLs, final diff, verifier result,
   checkpoints, and elapsed time without overwriting prior run artifacts.

The validation gate has four parts: an offline fixture test (including no reported total and
duplicate/restart cases); a short host CLI trace with nonzero reasoning that establishes the
provider field relationship; a multi-role harness no-op with ROOT Terra/max and at least one
worker Terra/high; and a replay test proving the aggregate is stable. Do not infer counts
from an on-screen counter. The multi-role smoke must succeed before an H-MH result is
interpreted.

### What to measure

Final quality and matched-quality efficiency are co-primary axes; cost is a derived
counterfactual (below). Report, per arm:

- **Final reward, pass rate, and verifier/audit status** at the shared ceiling.
- **Tokens/task** and **episodes (turns)/task** — directly measured and provider-neutral.
- **Tokens/cost/time to reach each preregistered threshold:** `R ≥ 0.8`, `R ≥ 0.95`, and
  full pass. Keep failures as right-censored observations at the cap.
- **Tokens-per-unit-reward** and **reward-per-million-tokens** as descriptive support for
  LHTB's continuous score, never as a substitute for threshold-matched comparisons.
- **Counterfactual cost/task** — tokens × public per-token price (see gotchas).

### Cost is a rate table you apply yourself — two gotchas

You're on subscriptions, so no invoice reflects these runs; you're computing a
*counterfactual* "what this would have cost at API rates." Fine, but:

- **Price by model, not by plan.** Use the public API price for whichever model the CLI
  actually called, and pin the exact model string per arm — the subscription and the API
  don't always expose the same lineup.
- **Cached input dominates, so price it separately.** Long-horizon loops resend a growing
  context every turn, so a large fraction of "input tokens" are cache hits billed at a
  fraction of the base input rate. Pricing all input at the full rate overstates cost by a
  wide margin — LHTB's own cost column counts input and output separately for exactly this
  reason. Pull cached vs uncached from the usage records and apply the cached-input rate.

### Why quality–efficiency, not cost alone, is load-bearing

This ties directly to §6: a harness claim needs quality and matched-quality efficiency
together. Without a shared ceiling and threshold analysis, "my harness wins on reward" can
quietly mean "my harness spent more." Conversely, lower spend with lower reward is not a
win. Log tokens / turns / wall-clock for *every* run regardless of whether API price is
reported; tokens are the durable denominator, while cost is a model-price counterfactual.

### Mechanics

The local runner has three separate pieces, none of which changes the benchmark task:

1. The primary raw C-X arm tees its one native `codex exec --json` stream to an immutable
   invocation artifact and records the exact Terra/xhigh configuration, sandbox, exit status,
   elapsed time, and B in the manifest. The optional C-M ablation records the same fields
   with Terra/max.
2. The H-MH arm preserves the JSONL and configuration evidence of every Codex child it
   already launches. The completed ledger enumerates ROOT and workers, then produces the
   aggregate task record after the harness exits; telemetry must never cause a second agent
   run or replace native harness scheduling.
3. The reporting step joins existing immutable run records with verifier results and applies
   preregistered thresholds. It must not select a winner from token counts alone.

For every unique invocation, `comparison_total_tokens` is the provider's terminal
`total_tokens` when present; only if that field is absent does the ledger label the metric as
derived `input + output`. The aggregate is the sum of those unique invocation values. This
prevents the common error of counting cached input twice. Record native harness turns and
verifier checkpoints separately: they are not guaranteed to appear in the Codex transcript.

**Confirm one thing before trusting the pipeline:** that the token fields are populated
when the model comes from a **CLI subscription** rather than an API key — usage accounting
can differ from an API-key/Harbor artifact. The validation smoke answers this: inspect the
local ROOT and worker JSONL/result artifacts, ensure usage is present and non-zero, and then
verify their aggregate before building a reportable run on top of it.

---

## References

**Benchmarks**
- SWE-Marathon — Desai et al., arXiv:2606.07682 · swe-marathon.org · github.com/abundant-ai/swe-marathon
- SWE-Marathon v1.1 public result data — `https://www.swe-marathon.org/assets/index-Cnn3YyxR.js`
  (contains the eight-trial-per-task `Codex / openai/gpt-5.6-terra / xhigh` rows); task/result
  reader — `scripts/read-swe-marathon-logs.py`; active BioFabric + Find Network revision —
  `f34867643bf07aec5208a861e667e01df0942099`
- LHTB (Long-Horizon-Terminal-Bench) — Li et al., arXiv:2607.08964 · github.com/zli12321/LHTB · HF: IntelligenceLab/Long-Horizon-Terminal-Bench · project: zli12321.github.io/LHTB

**Frameworks & setup**
- Harbor — github.com/laude-institute/harbor (from the Terminal-Bench creators) · harborframework.com/docs · Cookbook + AGENTS.md for the agent interface
- SWE-Marathon repo — github.com/abundant-ai/swe-marathon (`scripts/run-benchmark.sh`)
- LHTB repo — github.com/zli12321/LHTB (`configs/examples/`)
- mini-swe-agent (minimal reference scaffold, for a floor baseline) — github.com/SWE-agent/mini-swe-agent

**Auth / subscription vs API**
- Codex CLI auth (ChatGPT OAuth vs API key; device-code for headless) — developers.openai.com/codex/auth
- Claude Code auth (subscription vs API key; credential precedence; `claude setup-token`) — docs.claude.com/en/docs/claude-code
- Anthropic block on subscription tokens outside Claude Code (since Jan 2026); `claude -p` / Agent-SDK billing change announced then paused Jun 15 2026 — verify current status before relying on it

**Harness methodology (further reading)**
- "Stop Comparing LLM Agents Without Disclosing the Harness" (Binding Constraint Thesis), 2026
- SWE Atlas (native vs minimal scaffold tool-call deltas) — arXiv:2605.08366
- HAL — Princeton Holistic Agent Leaderboard, ICLR 2026 (archived)
- "The Illusion of Diminishing Returns: Measuring Long Horizon Execution in LLMs" — Sinha et al., arXiv:2509.09677
- Anthropic Engineering — "Effective harnesses for long-running agents" (2025)
- OpenAI — "Harness Engineering" (2026)
