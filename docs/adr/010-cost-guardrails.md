# ADR-010: Cost guardrails and budget policy
Status: accepted (D-025)

## Context
Free tiers have hard daily limits (ADR-007). Denial-of-wallet and quota exhaustion must never produce an unverified guess.

## Options considered
- **A. Best effort, no limits.** Risks quota exhaustion mid-run and silent degradation.
- **B. Hard guardrails with a circuit breaker that fails closed.**

## Decision
B. Budget defaults (Section 7.12.3): max 6000 input and 800 output tokens per request, 2 retries, per-client daily request caps, audit time budget 3000 ms, persisted budget state across restarts. A circuit breaker on 429s, quota exhaustion or budget exceeded degrades to cached results or a refusal with reason `capacity`. A kill switch disables LLM calls. Cost levers in order: deterministic gates before the LLM, compact prompts, two caches (LLM-call and plan-to-result), one structured call with at most 2 retries, optional model tiering as an ablation only.

## Consequences
- The harness respects RPM, TPM and RPD per provider, batches within limits and is resumable.
- Cost per correct answer is reported with a pinned denominator in ANALYSIS_PLAN.md (cost on answerable tasks divided by correct returned answers, as WRB defines it), alongside cost per question and a cost-quality Pareto plot. Free-tier runs report estimated list-price cost from a dated `pricing.yaml`.
