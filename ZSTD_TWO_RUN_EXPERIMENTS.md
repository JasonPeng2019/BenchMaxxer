# Two planned ZSTD benchmark runs

Status: experiment plan, not launch authorization or a change to an archived run. These are **two new runs total**; the completed ZSTD trials are not counted as either run.

## Shared comparison rules

- Use the same fresh ZSTD task baseline, pinned Docker image and verifier, continuous time limit, and scoring rules for both runs. Use separate source workspaces, harness configurations, runtime state, and result directories so concurrent runs cannot share or overwrite state. Preflight both configurations before launching either run.
- Pin `gpt-5.6-terra` and **Priority** service tier for ROOT and every model worker in both runs. Priority is a controlled setting here, not a cost-saving intervention. The earlier proposal to add a Standard-speed path is **not part of either run**.
- Both runs use the same **no-mandatory-skill-suite, optional-use harness base**. Give ROOT the task, a short contract, the harness entry points, and the native safety and review rules. Do not inject the full skill suite into either arm. Record any task-specific skill that ROOT nevertheless invokes so the comparison is transparent.
- Primary outcome: binary benchmark pass. Secondary outcomes: raw partial score, **uncached tokens** (input minus cached input, plus output, summed across ROOT and all workers), elapsed time, and any unknown-usage invocations. Include retries and failed calls. Do not substitute billed dollars or all-input token count for the agreed cost metric.
- Keep the benchmark task and test boundary unchanged. Only use public tests during development; evaluate the final frozen source with the same sealed verifier. Do not treat the published raw Terra/xhigh score distribution as a matched token-cost control: its per-run uncached-token counts are not recorded here.
- Give both runs the same predeclared time limit. A continuous five-hour limit matches the raw-xhigh benchmark protocol most closely; if choosing a shorter pilot, label both results as pilots rather than claiming a direct win over the original xhigh run.

## Run 1 — lean, optional-use harness

Give ROOT the ZSTD task and tell it the harness is available. Explain the bounded ways it can use the harness—as a coding worker, a fresh reviewer, or a test-design helper—but let ROOT decide whether and when those lanes are useful. Remove the **mandatory full skill-suite workflow** for this arm. Retain native safety, source custody, public-test, result-review, and shutdown rules; give ROOT a short task contract and the harness entry points it needs.

Start with Terra/**high** ROOT and Terra/**high** model workers, all on Priority. Run deterministic build and public-test commands without commissioning a model merely to execute them. This is the **lean control** for Run 2: record which harness roles ROOT actually used and how much each cost in uncached tokens. Do not add Run 2's formal no-progress record, prescribed fresh-stall-reviewer handoff, or role-specific effort mapping.

## Run 2 — xhigh ROOT with targeted max specialists

Use **the same lean, no-mandatory-skill-suite base as Run 1**. Run 2 adds three predeclared interventions: the no-progress record, a specific fresh-context reviewer at a genuine stall, and role-specific reasoning effort. It is a combined score/cost strategy test, not a clean ablation of each intervention.

### 1. Show no-progress evidence after each review

After every substantive worker or code review, give ROOT one compact, factual record with:

- the current source revision and the best-known source revision;
- a hash of the current source diff against the agreed task baseline, so an unchanged public result can be distinguished from an unchanged patch;
- the public-test command, pass/fail signature, and artifact reference for that source revision;
- the latest falsifiable hypothesis about the failing behavior, plus the prior hypothesis if it was just tested;
- uncached input and output tokens **by ROOT and worker invocation**, with in-flight or missing usage explicitly marked unknown rather than estimated.

Keep full transcripts and test output as evidence, but do **not** implement the earlier proposal for a broad, automatic changed-facts digest. This record may be a short fixed-format review artifact built from existing Git, public-test, and token-ledger evidence. After two consecutive reviews with the same unresolved failure signature and no improvement over the best public result, prompt ROOT to choose **one** of: a new falsifiable experiment, a fresh reviewer, or a different task area. The harness reports facts and the trigger; it does not accept code, schedule workers, or choose the next action.

### 2. Use a fresh-context reviewer at a genuine stall

When ROOT chooses review because a score-blocking failure is stalled, launch a fresh lane with a narrow task card. Supply the exact failing input and expected/actual behavior, source revision, relevant RFC 8878 invariant, and hypotheses already ruled out. Require either a discriminating test or a precise defect with a source location and explanation. Do not commission a general architecture review or repeat the same trace. ROOT decides whether to use the finding, owns integration, and runs the public checks.

### 3. Route effort to the active bottleneck

| Role in Run 2 | Terra effort | Assignment boundary |
| --- | --- | --- |
| ROOT manager and integrator | **xhigh** | Owns planning, lane selection, review, source custody, and final verification for the full run. |
| Routine coding or straightforward audit worker | **high** | Clear, bounded jobs with direct acceptance tests. |
| Active score-critical implementer | **max** | One precise hard algorithm task, such as compressed-block entropy, whose success could change the benchmark score. |
| Fresh stall reviewer | **max** | One specific failing case and ruled-out hypotheses; return a discriminating test or precise defect. |
| Focused repair worker | **max** | Patch a located, score-blocking defect and report the focused test and source revision. |
| Mechanical build, public-test execution, or evidence collection | **No model** | Run deterministic commands and report their output. |

The implementer, reviewer, and repair worker are **eligible** for max, not standing agents that must all be launched. ROOT chooses the active job from the evidence. Avoid multiple max agents investigating the same failure at once; if a reviewer identifies a defect, hand that finding to the repair worker instead of paying both to rediscover it. Record each max invocation and its result separately. If effort must change for a native worker, bootstrap a fresh, explicitly configured lane rather than silently changing a signed or resumed invocation. All model lanes remain on Priority.

This mapping is a hypothesis: xhigh ROOT may make better long-horizon decisions, high routine workers may avoid unnecessary reasoning, and max specialists may resolve benchmark-critical blockers. It does **not** guarantee fewer uncached tokens. In the prior high/high ZSTD pilot ROOT produced about 68% of **known total** tokens; that is not an uncached-token share, and xhigh ROOT plus max specialists could outweigh routine-worker savings. The original Standard-speed proposal is excluded because both runs are pinned to Priority.

## Interpretation

Compare both runs against each other on binary score first, then raw partial score, uncached tokens, and elapsed time under the shared protocol. Run 2 is a bundled treatment, so a win does not identify which addition caused it. Compare **score** against the published raw Terra/xhigh ZSTD outcomes, but do **not** claim lower uncached-token use than that raw xhigh run without its token ledger or a fresh matched raw control. Record any divergence in time limit, task baseline, verifier, or incomplete usage before interpreting the result. A max lane that is eligible but never launched is not counted as a max experiment.

Related notes: [harness score/cost ideas](HARNESS_BENCHMAXX_IDEAS.md) and [run manifest](RUN_MANIFEST.md). Official OpenAI Docs confirm that [GPT-5.6 Terra supports high, xhigh, and max](https://developers.openai.com/api/docs/models/gpt-5.6-terra), while [reasoning-effort guidance](https://developers.openai.com/api/docs/guides/reasoning) treats max as a setting to evaluate on the hardest work, not a demonstrated score/cost win for this task.
