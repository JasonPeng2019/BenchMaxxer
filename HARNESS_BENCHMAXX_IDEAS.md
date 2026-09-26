# Harness score/cost ideas

Status: ideas for a **new** experiment, not changes to the completed ZSTD run or to the live harness. Updated 2026-09-26.

## Objective and evidence

Optimize binary benchmark passes and useful partial progress per total cost, counting ROOT and every worker. Keep the task image, verifier, time limit, model, service tier, and scoring rules explicit. A single favorable run is a case study, not evidence of a repeatable win.

The interrupted ZSTD Terra/high ROOT-plus-worker pilot scored 23/43 tests, raw partial 0.535, binary reward 0. Its ledger records 102,805,139 **known** tokens: 69,572,689 ROOT and 33,232,450 worker tokens. One DNS-failed worker has unknown usage, so this total is a lower bound. Nineteen STEP-03 worker invocations culminated in a 3/6 visible-suite result. The published v1.1 raw Terra/xhigh ZSTD reference has 2/8 full passes and partial scores from 0.512 to 1.000. These runs have different time and interruption protocols and do not establish a harness advantage or disadvantage.

Sources: [final ZSTD record](RUN_MANIFEST.md#final-interrupted-zstd-local-pilot-2026-09-26), [usage ledger](results/zstd-h-h-10-20260925t185239z-ledger/usage.json), [run checkpoint](root_runs/zstd-decoder/RUN_CHECKPOINT.md), [raw reference](RUN_MANIFEST.md#interrupted-zstd-resume-amendment-2026-09-26).

## Best changes while keeping ROOT and coding workers at high

1. **Try Standard speed in a fresh run.** The completed run selected `priority` for ROOT and workers. Current OpenAI Docs say GPT-5.6 Fast/Priority costs 2x Standard API token rates or 2.5x Standard Codex credits with ChatGPT billing. Verify the actual account billing route and that Standard fits the fixed time limit. The Codex adapter currently requires a `service_tier` and forwards it; the ROOT collector also requires `--service-tier`. Add and preflight an explicit Standard path for both, without changing the archived run. [Speed documentation](https://learn.chatgpt.com/docs/agent-configuration/speed).
2. **Show no-progress evidence after each review.** Produce a compact, factual record of current/best source revision, source-diff hash, public-test signature, last hypothesis, and cost by invocation. After two unchanged outcomes on the same failure, prompt ROOT to choose a new falsifiable experiment, a fresh reviewer, or a different task area. The harness must not make the acceptance or scheduling decision itself.
3. **Give ROOT a bounded evidence digest.** Keep full transcripts, but present changed facts and short references instead of repeatedly rereading broad logs and skill material. ROOT produced about 68% of known ZSTD tokens. Measure savings in billed input/cache/output and effect on quality; do not equate token count with price.
4. **Use a fresh-context reviewer at a genuine stall.** Give the reviewer a specific failing input, source revision, RFC invariant, and prior ruled-out hypotheses. Require a discriminating test or precise defect. Do not commission another general review or repeat the same trace. ROOT retains integration and test authority.
5. **Ablate the mandatory full project skill suite, not the harness.** Use a short task contract and plan, but require native harness setup and at least one fresh validation worker that audits actual source/public evidence. ROOT must review the finding and rerun deterministic checks. The optional-only 90-minute pilot stopped without a worker, so it is not a useful harness treatment. Keep native safety and result-review rules; treat skill-suite removal as the experimental difference, not worker-free execution.

## Best changes when lowering some reasoning effort

1. **Eliminate model work for mechanical testing.** ROOT invokes the existing deterministic build/public bridge and receives a bounded pass/fail summary. A separate model-based tester is warranted only for designing a new discriminating test, not for running commands.
2. **Set effort per lane by difficulty.** Keep hard coding and hard failure diagnosis at high or above; use medium/low only for narrowly scoped read-only inventory or straightforward audits. Current native bootstrap already records explicit worker effort, while native resume preserves it. Escalating an existing high lane to xhigh/max requires a fresh, separately bound lane or an explicitly designed harness change; do not silently mutate its signed invocation.
3. **Add an escalation trigger and a known-good checkpoint.** A lower-effort result must identify a source revision, focused test, and remaining failure. If it is inconclusive or regresses, preserve the last passing revision and route the exact blocker to a stronger specialist. Keep enough time/cost allowance for final integration and verification.
4. **Lower ROOT effort last.** ROOT accounted for most known tokens, so lowering it has upside, but it owns source custody, lane decisions, and integration. First test compact context and selective worker effort; then compare a medium ROOT with the same deterministic guardrails against a high ROOT.

## Role mapping to challenge raw Terra/xhigh at lower cost

| Role | Initial effort | Why | Escalation |
| --- | --- | --- | --- |
| ROOT manager, integration, benchmark boundary | **high** | Long-running custody, task selection, review, and final checks consumed most known tokens in ZSTD. Entire-run xhigh/max ROOT may erase worker savings. | Consult a bounded xhigh specialist for a hard technical decision; measure a separate xhigh-ROOT arm only if high ROOT repeatedly makes wrong decisions. |
| Hard algorithm implementer (e.g., FSE/Huffman/dictionaries) | **xhigh** | This role directly touches the benchmark-critical defect that high workers did not solve in ZSTD. Concentrate extra reasoning where a correct patch can change the verifier score. | One bounded max diagnosis or implementation attempt after a documented xhigh stall. |
| Ordinary implementation worker | **high** | Frame parsing, interfaces, routine extensions, and focused fixes have clearer acceptance tests. | Promote only the specific hard blocker to xhigh. |
| Independent reviewer/debugger | **high** for routine review; **xhigh** for a fresh hard-bug hypothesis | A second context is useful at a stall, but general reviews add cost without necessarily advancing code. | **max** only for a precise, score-blocking issue with prior high/xhigh hypotheses ruled out. |
| Tester and evidence collector | **No model** for build/run/diff; **high** only to design a novel test | The executable test is deterministic and should be run once per meaningful change. | xhigh only if test interpretation itself is technically hard. |
| Planner/spec writer | **high**, brief | The benchmark already supplies a detailed task and constraints. | No standing max planner. |

**Max is an exception, not a permanent role.** Reserve it for the narrowest unsolved, benchmark-critical algorithm or architecture question, with a source snapshot and a concrete requested output. Higher effort can improve complex reasoning but generally increases time and tokens; it has no demonstrated score/cost payoff for this harness yet. [OpenAI Docs on subagent effort](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Allocate xhigh to the person or agent actually solving the bottleneck, regardless of title. If ROOT itself is doing the difficult algorithm diagnosis, compare an xhigh ROOT arm or consult an xhigh specialist; paying both to repeat the same diagnosis is unlikely to help. The current collector fixes ROOT effort for a run, and native lane resume preserves worker effort, so a phase-specific effort switch needs an explicit new invocation design with intact accounting.

### Recommended starting configuration

- Run ROOT at **high** for ordinary coordination, source custody, and integration; run ordinary coding and focused review at **high**. ROOT consumed about 68% of known ZSTD tokens, so making it xhigh or max for the entire run is a cost-risk hypothesis, not the default.
- Assign **xhigh** to the single active owner of the score-critical implementation or diagnosis. In ZSTD, that means compressed-block entropy and later dictionary behavior. The 19 high-effort STEP-03 invocations make this the strongest place to test extra reasoning. If ROOT owns that technical work, shift the xhigh allocation to ROOT for a separately measured arm rather than duplicating the investigation.
- Keep **max** as one short rescue invocation for a precisely stated blocker after an xhigh attempt has produced no improvement. Supply the failing case, current source revision, prior traces, and required output. Do not maintain a standing max ROOT, planner, tester, or generic reviewer. Execute existing build and public-test commands without a model agent.

The comparison target depends on the raw control: if raw xhigh passes, the harness must also pass at lower total cost; if raw xhigh fails, compare partial score and cost while reporting that both binary rewards are zero. The repository has published raw-xhigh ZSTD outcomes but no matched local raw-xhigh cost record, so collect a fresh control before claiming a cheaper win.

## Experiment to decide whether it wins

Run a fresh raw Terra/xhigh control and a fresh lean-harness arm on the same pinned task and verifier, with the same continuous five-hour limit and Standard tier. For the lean arm, start with high ROOT, xhigh only for the hardest coding lane, high ordinary workers, deterministic testing, and no standing max agent. Use a predeclared total cost ceiling below the measured raw xhigh cost; count ROOT, all workers, retries, cached input, long-context premiums, and unknown usage separately. Measure binary pass first, then raw partial, actual billed cost, elapsed time, and cost to a predeclared quality threshold. A max specialist can be a separately recorded rescue variant, not silently added to the base arm. Repeat on more than one task/seed before claiming a general win.
