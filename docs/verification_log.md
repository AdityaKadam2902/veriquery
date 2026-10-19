# Verification log

Every external fact the architecture marked [VERIFY], with how and when it was checked.
Status: `confirmed` (primary source read), `partial` (secondary source or ambiguous), `open` (needs a login or later task).
Checked 2026-10-17 (T-003).

## 1. Licenses and terms

| ID | Item | Status | Finding | Source |
|---|---|---|---|---|
| V-01 | Olist license | confirmed | CC BY-NC-SA 4.0 (Kaggle dataset page). Matches §8.2 belief. NonCommercial + ShareAlike: any redistributed derived data must stay CC BY-NC-SA. | kaggle.com/datasets/olistbr/brazilian-ecommerce |
| V-02 | Olist redistribution plan | decision | Keep §8.2: no raw redistribution, download script only. Questions and ground-truth values derived from Olist carry CC BY-NC-SA terms; dataset card must say so. Per-file licensing (§17) stands. | derived from V-01 |
| V-03 | TPC-H terms | confirmed | Non-official use is allowed as a "derived" benchmark: name must be prefixed "Derived from"; no TPC primary/optional metrics; must carry a non-comparability disclaimer; no comparison with official TPC results. Our metrics (wrong-number rate, coverage) are not TPC metrics. | tpc.org Fair Use Quick Reference v1.0.0 |
| V-04 | TPC-H wording to use | decision | "TPC-H-derived schema and data" everywhere; add the disclaimer sentence from the Fair Use doc to the dataset card. | derived from V-03 |

## 2. LLM providers and models (D-007)

| ID | Item | Status | Finding | Source |
|---|---|---|---|---|
| V-10 | Groq free limits (open models) | confirmed (user console, 2026-10-17) | Rate-limits page lists openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.8-27b at 30 RPM, 1K RPD, **8K TPM, 200K TPD**. Page header mixes "Free Plan / Developer Plan" labels and says the shown limits are Developer base limits; a second site reports the same numbers as Free. Confirm in console Limits page. Limits are per organization, not per key. Cached tokens do not count. | console.groq.com/docs/rate-limits; benchlm.ai/free-tier/groq |
| V-11 | Groq older models | partial | llama-3.1-8b-instant (14.4K RPD) and llama-3.3-70b-versatile appear in secondary articles but are not listed on the current rate-limits page. Do not rely on them. | same |
| V-12 | Gemini free tier | confirmed (user AI Studio, 2026-10-17) | Free-tier text models (standard): gemini-3.8-flash, 3.6-flash, 3.5-flash-lite, 3.1-flash-lite, 3-flash-preview, 2.5-pro/flash/flash-lite. gemini-4-argon and 3.1-pro-preview are NOT on the free tier. Free-tier content may be used to improve Google products. Exact RPM/TPM/RPD are no longer in the docs; visible only per project in AI Studio (aistudio.google.com/rate-limit). RPD resets midnight Pacific. | ai.google.dev/gemini-api/docs/pricing, /rate-limits (updated 2026-10-15) |
| V-13 | Ollama structured output | confirmed | JSON-schema constrained output via `format` (Ollama >= 0.5.0), supported in the Python library. Candidate dev models: llama3.2:3b, llama3.1:8b, qwen3:8b. Reasoning models cannot return thinking + structured output in one call. Exact local model chosen at T-006 from hardware. | ollama.com structured outputs blog |
| V-14 | Proposed D-007 | superseded by section 6 | M1 openai/gpt-oss-120b (Groq); M2 openai/gpt-oss-20b (Groq) or qwen/qwen3.8-27b; M3 gemini-3.5-flash-lite (or 3.8-flash, per AI Studio limits); M4 Ollama small model. **Blocked on V-15.** | |
| V-15 | **Budget conflict with §10.6** | resolved: free-only, see section 6 | §10.6 plans ~8,800 calls. At an assumed ~2K tokens per call (estimate, replace with measured values at T-006/T-207), M1 alone is ~5,300 calls = ~10.6M tokens; at 200K TPD that is ~53 days on one Groq model, and 8K TPM allows only ~4 calls/min. The free tier cannot carry the full plan on schedule. Options: (a) Groq Developer plan (card on file; Groq states ~10x limits) for M1; (b) split load across Groq models and Gemini free tier (limits per V-12); (c) cut B1+ votes or run fewer seeds; (d) Gemini Batch (paid). Pick one before T-006. | computed |

## 3. Importer formats (FR-15, §7.9)

| ID | Item | Status | Finding | Source |
|---|---|---|---|---|
| V-20 | dbt MetricFlow YAML | confirmed | Two specs. **Legacy**: top-level `semantic_models:` + measures + `metrics:` (dbt Core 1.6-1.11). **Latest** (Jan 2026): `semantic_model:` block nested under a model, simple metrics replace measures, cross-model metrics in top-level `metrics:`; supported on dbt platform, Fusion, Core 1.12. Cross-project refs not supported in latest. Metric types: simple, ratio, derived, cumulative, conversion. | docs.getdbt.com (latest-metrics-spec, semantic-model-properties, metric-properties) |
| V-21 | dbt importer scope | proposal | Support the legacy spec first (largest installed base), latest spec second. Report unsupported types in import_report.md as already designed. Field-level mapping to be written when T-5xx starts. | |
| V-22 | Snowflake semantic YAML | partial | Current recommended format is the **semantic view YAML**: `tables` (dimensions, facts, table-scoped metrics, time dimensions), `relationships`, view-level derived `metrics`, `verified_queries`, optional variables/materializations. Legacy stage-based semantic model YAML still works. Exact field names not yet read; fetch the spec page when building the importer. | docs.snowflake.com semantic-view-yaml-spec |
| V-23 | OKF version and owner | confirmed | OKF is Google Cloud's spec, **v0.2** (released 2026-07-24/25; v0.1 about six weeks earlier). Spec: GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md. Only `type` is required. Optional families: `sources` (+credibility signals), `generated`, `verified` (trust tiers), `status` (draft/stable/deprecated), `stale_after`, and the `Attested Computation` type. Bundles may declare `okf_version` in root index.md. Third-party tools show higher numbers (e.g. a Dart package v0.4.2); that is the package version, not the spec. | SPEC.md on GitHub; docs.rs/okf-core; pub.dev/okf |
| V-24 | OKF status mapping | confirmed | Our catalog status (draft/stable/deprecated) maps 1:1 to OKF `status`; our review dates map to `stale_after`/`verified`. §7.9 mapping holds. | SPEC.md section 5 |

## 4. Positioning impact (feeds T-002 and §2)

**OKF v0.2 "Attested Computation" (SPEC section 10) is close prior art for the B2 design and the verification record:** a sanctioned computation as its own concept, the agent may only supply typed parameter values (never author the computation), an executor returns a receipt, a deterministic no-LLM attester re-derives the binding and compares it to what actually ran, failing attestations must not be displayed, and `stale_after` gates staleness. The spec explicitly defers: receipt/verdict wire formats, the attester ABI and sandboxing, attestation caching, and semantic-layer templates (Looker, dbt) where comparison moves from SQL equality to model-and-binding equality.

Consequences (decisions for you, not yet applied to the architecture):
1. D-001 must name OKF Attested Computation as prior art; "typed plan + deterministic compiler + attester" is not new on its own.
2. What remains ours: the benchmark and abstention analysis, the failure taxonomy, and audit mode for arbitrary third-party SQL using perturbation equivalence (OKF's attester is SQL/binding equality).
3. Opportunity: make the verification record and our attester interface OKF-compatible, filling the gaps OKF deferred. Needs an ADR.

## 5. Deferred [VERIFY] items (not needed before their tasks)

| Item (architecture line) | Needed by | Note |
|---|---|---|
| Prior-art figures, line 65 | T-002 | dbt benchmark, Cortex verified queries, PyDough, Spider 2.0, plus OKF (section 4 above) |
| Olist column names, line 362 | T-101 | schema assertions at load time |
| Hugging Face dataset license constraints, line 864 | T-704 | after V-01/V-02 |
| Security tool choices, line 1073; OWASP LLM Top 10 names, line 1076 | P3 security work | check current OWASP list then |
| DuckDB lockdown setting names, line 1036 | T-311 | read DuckDB docs when implementing |
| Zenodo DOI, arXiv endorsement, line 1250 | T-702 | |
| Free hosting options, line 1215 | T-606 | |
| CI action pins | before first public push | checkout v7.0.1 and setup-uv v10.2.0 pinned by SHA from `git ls-remote`; release age (two-week rule) not checked; pre-commit hook revs written from memory, run `pre-commit autoupdate` and review |

Note: the Olist and TPC-H facts above were read from the dataset page and the TPC Fair Use document directly; the Groq and Gemini facts come from the vendors' current docs (Gemini docs dated 2026-10-15). Re-check provider limits at the start of each benchmark run.

## 6. Resolution from the owner's own consoles (2026-10-17)

Decision: **free tiers only**. OKF is to be named as prior art (D-001 wording); making the verification record OKF-compatible is decided in ADR 001 (T-004).

**Measured limits (owner's accounts, free tier)**

| Provider / model | RPM | TPM | RPD | TPD |
|---|---|---|---|---|
| Groq openai/gpt-oss-120b, gpt-oss-20b, qwen/qwen3.8-27b | 30 | 8K | 1K | 200K |
| Groq openai/gpt-oss-safeguard-20b | 3 | 2K | 1K | 200K |
| Groq allam-2-7b (Arabic-focused) | 30 | 6K | 7K | 500K |
| Gemini 3.5 Flash-Lite, 3.1 Flash-Lite | 15 | 250K | 500 | not shown |
| Gemini 3.8 / 3.7 / 3.6 / 3 Flash, 2.5 Flash | 5 | 250K | 20 | not shown |
| Gemini 2.5 Flash-Lite | 10 | 250K | 20 | not shown |
| **Gemma 4 26B and 31B (AI Studio)** | **30** | **16K** | **14.4K** | not shown |
| Gemini 2.5 Pro, 3.1 Pro, 4 Argon | 0 | 0 | 0 | not available on free |

**Budget math** (assumed ~2K tokens per call; replace with measured values at T-006/T-207)
- Groq gpt-oss: 200K TPD is about 100 calls/day. Unusable for primary runs. Reserve for small side experiments only.
- Gemma 4 31B: ~5,300 calls is ~10.6M tokens. TPM 16K allows ~8 calls/min, so ~11 hours of pure run time; RPD 14.4K is not binding. Fits in a few days.
- gemini-3.5-flash-lite: ~1,750 calls at 500 RPD is ~4 days.

**D-007 (resolved except M2)**
- M1 (primary, 3 seeds): Gemma 4 31B via AI Studio.
- M3: gemini-3.5-flash-lite.
- M4 (dev only): small local Ollama model.
- M2 (smaller open-weight): default is a local Ollama model sized to the owner's hardware, decided at T-006 (may coincide with M4). Gemma 4 26B is a weak size contrast to 31B.

**New risks**
- V-16: structured JSON output support for Gemma 4 through the Gemini API is NOT verified. First T-006 smoke test. Fallback: schema in the prompt + pydantic validation + repair loop (already in the design).
- V-17: Gemini free-tier content may be used to improve Google products. Send only public or synthetic data. Test-split questions sent to the free tier may enter future training data; state this on the dataset card (affects future contamination, not current results).
- V-18: Google states limits are not guaranteed and can change. Re-read the quota pages at the start of every benchmark run and log them with the results.

## 7. Prior-art review (T-002, 2026-10-17)

| ID | Item | Status | Finding |
|---|---|---|---|
| V-30 | dbt benchmark figures | confirmed (blog read) | 11 questions, 20 runs, ACME Insurance. 90.0% to 98.2% (Sonnet 4.6) and 84.1% to 100% (GPT-5.3 Codex) are the MODELED configuration; unmodeled overall is 72.7% (semantic layer) vs 64.5% (text-to-SQL). The architecture section 2.1 omits this distinction. |
| V-31 | PyDough 100% claim | partial | Confirmed as a vendor (Bodo) blog claim: 100% over 220 runs on the unmodeled schema. Not independently verified. |
| V-32 | Closest 2026 papers | partial | SPC (2608.16663) and Business Truth / WRB (2608.09254) read in full; 2604.25149 snippet only. See docs/related_work.md. |
| V-33 | Cortex Analyst accuracy claim, BIRD, Spider 2.0 figures | open | Not re-verified; drop or verify before the report. |
| V-34 | WRB repository license | open | github.com/k-w-lee/query_proof: license not checked. Needed before reusing any WRB tasks. |
| V-35 | Owner hardware for local models | recorded | HP Pavilion laptop, 16 GB RAM, GPU unknown (check Task Manager, Performance, GPU). Local model choice (M2/M4) is decided at T-006 from measured tokens per second. |