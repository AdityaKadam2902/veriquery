# ADR-007: Provider-agnostic LLM client with disk cache
Status: accepted (D-017; resolves D-007, M2 provisional)

## Context
Zero budget (owner decision: free tiers only), reproducibility needs, and quota limits measured on the owner's accounts on 2026-10-17 (verification log section 6): Groq open models 30 RPM, 1K RPD, 8K TPM, 200K TPD; Gemma 4 26B/31B on AI Studio 30 RPM, 16K TPM, 14.4K RPD; Gemini 3.5 Flash-Lite and 3.1 Flash-Lite 15 RPM, 250K TPM, 500 RPD; other Gemini Flash models 20 RPD; Pro models not on the free tier.

## Options considered
- **A. One vendor SDK.** Simple; locks the benchmark to one provider.
- **B. Third-party abstraction library.** Less code; extra dependency and opaque behavior.
- **C. Thin own client** (pydantic structured output, provider adapters, disk cache).

## Decision
C. Interface returns a typed result with `parsed`, `raw_text`, token usage, `model_id`, latency, `cache_hit`. Disk cache keyed by content hash and integrity-checked. Structured output is always validated with pydantic with a repair loop (at most 2 retries). Models: **M1 (primary, 3 seeds): gemma-4-31b-it on AI Studio; M3: gemini-3.5-flash-lite; M4 (dev only): llama3.2:3b via Ollama; M2 (smaller open-weight): provisionally llama3.2:3b via Ollama (3.4 s per call measured), to be confirmed on the dev split (not at floor) and locked before the test split is tagged.** Groq is for small side experiments only (200K TPD is about 100 calls per day).

## Consequences
- Record model id and snapshot, requested and transmitted temperature, and the quota pages at run time with every result (SPC and WRB both lost this provenance).
- V-16 resolved (verification log section 8): gemma-4-31b-it and gemma-4-26b-a4b-it both return schema-valid JSON on the first try with system instruction plus JSON mime mode (8/8 each; small sample, re-measure at scale).
- Free-tier 5xx bursts occur: all provider calls go through a retry wrapper (backoff with jitter on 429/500/502/503/504); failures are never cached; infrastructure-failure rate is reported per run.
- Latency is 18 to 30 s per call, so the harness runs several concurrent workers within RPM/TPM limits (T-201).
- V-17: free-tier Gemini content may be used by Google; send public or synthetic data only and disclose that test questions may leak into future training data.
- Provider kill switch environment variable disables all LLM calls.