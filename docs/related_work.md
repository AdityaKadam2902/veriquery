# Related work and positioning (T-002)

Checked 2026-10-17. "Read" = primary source opened; "snippet" = only search excerpts seen; "cited" = known only through another paper. Nothing here is a claim that no other work exists: only that this review did not find it.

## Verdict

The architecture's core idea (LLM picks governed objects, deterministic code compiles and checks, system refuses when it cannot answer) is **established and already published several times in 2026**. Perturbed-database equivalence checking is also established (Zhong et al. 2020). What remains defensible is narrower: an **open, fully reproducible, multi-domain benchmark of trust failures**, a **measured audit verifier for third-party SQL**, and **risk-coverage analysis** on top. Rigor and reproducibility are the real differentiators, because the closest papers are single-domain, small, or only partly reproducible.

The Business Truth paper (WRB, Aug 2026) already offers a frozen, pre-registered benchmark with scored clarification, abstention, refusal, schema-drift and adversarial tasks, plus a deterministic rule-gated agent. VeriQuery is therefore best framed as **extending and stress-testing that line of work on real data, with a stronger verifier and harder adversaries**, and crediting it explicitly.

## Closest prior work

| Work | What it shows (from the source) | Overlap with us | Our delta |
|---|---|---|---|
| **dbt Labs, Semantic Layer vs Text-to-SQL, 2026 update** (blog, 7 Apr 2026; read) | ACME Insurance, 11 questions, 20 runs per model. Modeled config: Claude Sonnet 4.6 90.0% to 98.2%, GPT-5.3 Codex 84.1% to 100%. Unmodeled: text-to-SQL 64.5% vs semantic layer 72.7% overall. Out-of-scope questions score 0% for the semantic layer by construction ("failure looks like an error message"). | Semantic layer as the trusted path; refusal emerges implicitly | Eight trust-failure categories, scored refusal/clarification, three domains, about 240 questions |
| **PyDough** (Bodo; vendor blog read) | LLM writes PyDough, not SQL; deterministic compile. Vendor reports 100% on dbt's 11 questions over 220 runs on the unmodeled schema. Vendor claim, not independent. | "LLM never writes SQL" | We do not claim this; we benchmark it |
| **SPC: Bounded Semantic Planning and Deterministic Compilation**, arXiv 2608.16663, Aug 2026 (read in full) | Planner selects only governed identifiers; engine owns joins, roles, grain, SQL; static checker; refusal path. 38 paired ACME questions, 3 runs: solid success 37/38 vs 21/38 for direct SQL; 0 wrong-but-executed in 114 runs vs 29. Uses **counterfactual database instances** to separate grain-safe from fan-out queries. Authors state single domain, development on the benchmark, no held-out study, gain not attributable to compiler alone; public code excludes questions, gold labels, fixtures and harness. | Very close to B2 and to our fan-out perturbation | B2 is a reference implementation, not a novelty claim. Our delta is the public benchmark and harness, multiple domains, a dev/test split with frozen analysis plan, and measuring the verifier itself |
| **Business Truth, not SQL Accuracy** (Lee), arXiv 2608.09254, 10 Aug 2026 (read in full) | WarehouseReliabilityBench (WRB): 400 frozen tasks, two synthetic warehouses (e-commerce, SaaS), five categories (standard, ambiguous, unanswerable, schema drift, adversarial), about half with no correct SQL; family-disjoint 240/80/80 splits; pre-registered paired bootstrap and claim-verb rule; test split run once. QueryProof: deterministic state machine over a semantic layer and catalog, model called twice, static plus post-execution checks. On 80 test tasks: Business Truth Rate 0.537 vs 0.300 (32B direct), false success 0.351 vs 0.754 of returned answers, 0 wrong numbers on 24 answerable tasks. The post-execution checks were incomplete (wrong answers that passed them: 0.163 dev, 0.333 validation). Learned confidence and routing did not transfer. Authors disclose: one author and reviewer, test-split exposure through a contaminated lexicon, confounded headline (no matched scaffold), family-level bootstrap over 10 families includes zero, adversarial stratum ranks nothing (all systems 1.000), one model family, synthetic data only. Code: github.com/k-w-lee/query_proof | **Closest work to ours in thesis, benchmark design and protocol** | We differ in: audit mode (perturbation) for third-party SQL, real data (Olist, TPC-H), time-boundary, fan-out and metric-lifecycle categories, adversarial tasks designed to discriminate, a matched definition-aware baseline (B1+), several model families, cluster-aware statistics by design. Must credit WRB and report a metric mapping |
| **Semantic Layers for Reliable LLM-Powered Data Analytics**, arXiv 2604.25149, Apr 2026 (snippet) | Paired benchmark of accuracy and hallucination across three frontier models; adding the semantic document improves accuracy by 17 to 23 points. | Benchmark of semantic-layer benefit | Trust-failure categories and abstention, not accuracy gain alone |
| **OKF v0.2 Attested Computation** (Google Cloud spec; read) | Sanctioned computation as its own concept; agent supplies only typed parameter values; executor returns a receipt; deterministic attester compares what ran; failing attestation must not be displayed; `stale_after` gating. Spec defers receipt/verdict formats, attester interface and sandboxing, and semantic-layer templates. | Same contract as B2 plus our verification record | Make the record OKF-compatible and fill the deferred parts (ADR 001); do not claim the contract |
| **TrustSQL** (arXiv 2403.15879; cited via SPC) and **Reliable text-to-SQL with adaptive abstention** (SIGMOD 2025; cited) | Abstention as a first-class outcome; TrustSQL penalizes wrong answers more than abstention. | Abstention scoring | Not read. We add risk-coverage curves in the governed-metric setting; read both before claiming |
| **Zhong, Yu, Klein 2020, distilled test suites** (cited via SPC) | Execution accuracy on one database instance accepts wrong queries; multiple database instances separate them. | Foundation of our perturbation-based equivalence | We do not claim perturbation equivalence; we apply it to governed-metric equivalence for third-party SQL and measure precision and recall |
| **Anthropic, How Anthropic enables self-service data analytics with Claude** (3 Jun 2026; secondary blogs only) | Reported: structure and a semantic layer, not raw query access, moved accuracy; a mandatory SQL-review sub-agent added +6%. | Context | Re-read the primary post before citing numbers |
| **Snowflake Cortex Analyst; BIRD; Spider 2.0; Cube, Looker, Genie** | Not re-verified in this pass. | Context | Verify or drop figures before the report |

## What we can claim (proposed wording)

- **C1 Benchmark.** An open, reproducible benchmark with named trust-failure categories (ambiguity, stale or deprecated metrics, time boundaries, fan-out, adversarial pressure), scored refusal and clarification, multiple domains, a locked test split and a frozen analysis plan. *Not:* first benchmark with scored abstention, clarification and refusal (TrustSQL, WRB), first benchmark of semantic layers (dbt, 2604.25149).
- **C2 Audit verifier.** Perturbation-based equivalence of third-party SQL against governed metric definitions, with a labeled evaluation reporting precision, recall, false-alarm and UNMATCHED rates. *Not:* perturbation equivalence itself (Zhong 2020; SPC counterfactuals).
- **C3 Reference system (B2).** A reference implementation and control, not a novelty claim (PyDough, SPC, dbt, OKF).
- **C4 Abstention analysis.** Risk-coverage curves, AURC and coverage at fixed risk across systems and models, with paired uncertainty. *Not:* abstention scoring itself.
- **C5 Taxonomy and ecosystem.** Layer-attributed failure taxonomy, importers, MCP server, OKF-compatible record.

## Proposed changes to ARCHITECTURE.md section 2 (not applied; needs owner approval)

1. Replace the section 2.1 table with the rows above; correct the dbt figures (the 98.2%/90.0% pair is the modeled configuration; unmodeled overall is 72.7% vs 64.5%).
2. Section 2.2: reword as the C1 to C5 claims above; remove any implication that B2 or the verification record is new.
3. Section 2.3: add "State plainly that SPC, PyDough, OKF Attested Computation and dbt cover the typed-plan plus deterministic-compile pattern."
4. Make reproducibility an explicit design goal: every artifact (questions, gold labels, fixtures, harness, verdicts, run metadata including transmitted temperature and model snapshot) published, since the closest papers lack some of these.

## Reading list before positioning is frozen (blocks the final README and report, not coding)

1. TrustSQL (2403.15879) and Chen et al., adaptive abstention (SIGMOD 2025).
2. Rumiantsau and Fokeev (2604.25149), Kim et al. (2606.31041), SQLStructEval (2604.06736).
3. dbt-llm-sl-bench repository (August re-run) and the Anthropic June 2026 post.
4. WRB repository license (github.com/k-w-lee/query_proof) before any reuse of its tasks.

## Lessons from WRB proposed for our design (need ADR / owner approval)

1. **Stratify the family split.** WRB's test ambiguous stratum had two template families in one domain, because family-disjoint splitting put every "two defined metrics" family in dev. We assign families to splits per category so each category has several test families across at least two domains.
2. **Cluster-aware statistics from the start.** WRB's family-level bootstrap widened both intervals to include zero. Report a cluster bootstrap over families as co-primary, and size the test split by number of families, not just questions.
3. **Lexicon contamination guard.** Our deterministic ambiguity gate matches words against metric names and synonyms, like WRB's lexicon. Add a CI test that fails if any synonym phrase occurs only in test questions.
4. **Adversarial category must discriminate.** In WRB every system scored 1.000 on adversarial tasks, so the stratum ranked nothing. Design category 7 so weak baselines fail it.
5. **Pinned denominators and a scoring-corrections log.** Three of WRB's six scoring corrections were denominator errors. Define each metric with its denominator in ANALYSIS_PLAN.md and keep a corrections log. Map ours to WRB's: wrong-number rate to False Success Rate, coverage and answer accuracy as defined there, cost per correct answer.
5b. **Replay vs regeneration reproducibility.** Commit raw model outputs, a results file with input hashes, and sealed costs; generate every number in the report, never type it.
6. **Matched baseline and ablation.** WRB's headline compares a scaffolded 7B with an unscaffolded 32B and ran no component ablation. B1+ is our matched baseline; add a component ablation (gate, verifier, composer).
7. **Confidence signals must see wrong-to-answer cases.** WRB's fitted confidence model failed because it trained only on answerable questions. Include clarify/refuse cases in any abstention signal's training and evaluation pool.
8. **Be honest about reviewers.** WRB's second pass was test-retest by the same person. Our plan promises a second annotator for 20% of items; either find a real second person or report test-retest and say so.
9. **A sharp testable claim for audit mode (RQ4).** WRB measured that wrong answers still pass rule-based static and post-execution checks (0.163 dev, 0.333 validation). Pre-register: what share of such wrong answers does perturbation-based equivalence catch, and at what false-alarm rate?
10. **Optional external validity.** Run our systems on WRB's dev/validation tasks as an outside check, after a license review.