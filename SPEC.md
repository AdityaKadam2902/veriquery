# VeriQuery SPEC (one page)

Source of truth: `docs/ARCHITECTURE.md` v2.2. If this page disagrees, the architecture wins.

## Problem
AI data agents answer business questions with SQL and return plausible, confident, wrong numbers: wrong definition, silent join fan-out, time-boundary errors, stale or deprecated metrics, unneeded answers to ambiguous or unanswerable questions, or compliance under pressure. Users cannot tell, and execution-match benchmarks do not score it.

## What VeriQuery is
An open-source toolkit and public benchmark that measures and enforces the numerical trustworthiness of data agents. It is not a new idea for governed-metric agents (dbt, PyDough, SPC, OKF, WRB exist); see `docs/related_work.md` and ADR-011.

## Contributions
- **C1** Reproducible multi-domain benchmark of trust failures (about 240 questions, 8 categories, stratified family-disjoint dev/test split, locked test tag, frozen analysis plan).
- **C2** Audit verifier for third-party SQL: normalization plus perturbed-execution equivalence against governed metrics, with measured precision, recall, false-alarm and UNMATCHED rates.
- **C3** B2 reference system: LLM emits a typed Plan, Clarify or Refuse; deterministic compiler, read-only DuckDB executor, verifier, templated composer. Control, not a novelty claim.
- **C4** Abstention analysis: risk-coverage curves, AURC, coverage at 1% and 5% risk, with cluster-aware uncertainty.
- **C5** Failure taxonomy by pipeline layer, importers (dbt, Cortex, OKF), MCP server.

## Systems compared
B0 schema-only text-to-SQL; B1 plus metric docs; **B1+ (primary baseline)** plus retries and 3-sample voting; **B2** attested agent; B3 audit gate over B1+ output.

## Hypotheses (may be partly false; report honestly)
H1 B2 has a lower wrong-number rate than B1+, especially in categories 3, 4, 5, 7. H2 the coverage cost is quantifiable and partly recoverable. H3 audit mode catches a substantial share of wrong numbers at a low false-alarm rate. H4 benefits hold across model strengths.

## Scope
In: single-turn questions with at most one clarification; read-only analytics; TPC-H, Olist (Must), saas_synth (Should); governed YAML catalog; plan DSL; verifier (attested and audit); benchmark and harness; API, UI, MCP; importers; technical report.
Out: general BI, multi-turn dialogue, multilingual input, training or fine-tuning, multi-tenancy and RBAC, streaming data, domain advice.

## Fixed constraints
- Python 3.11+, uv, ruff, mypy `--strict`, pytest (90% coverage on `verifier/` and `executor/`), DuckDB (ADR-001).
- In B2 the LLM never writes SQL or final numbers; query results never re-enter an LLM prompt (I1, I2).
- Untrusted SQL runs only in a sandbox; audit mode never returns raw rows (I3, I4).
- Time ranges are half-open with an explicit `as_of` (D-009).
- No test-split run before the analysis plan is frozen and `test-lock` is tagged (D-011).
- Free-tier LLMs only; budget and circuit breaker fail closed (ADR-007, ADR-010).

## Definition of success
Gates G1 to G3 and the v1.0 checklist in architecture Sections 14 and 15. Minimum credible result: public benchmark and harness, measured audit verifier, frozen-plan results on the test split with intervals, and a report that states where B2 and the verifier fail, even if H1 is not supported.