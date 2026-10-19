# ADR-007: Provider-agnostic LLM client with disk cache
Status: accepted (D-017; resolves D-007 except M2)

## Context
Zero budget (owner decision: free tiers only), reproducibility needs, and quota limits measured on the owner's accounts on 2026-10-17 (verification log section 6): Groq open models 30 RPM, 1K RPD, 8K TPM, 200K TPD; Gemma 4 26B/31B on AI Studio 30 RPM, 16K TPM, 14.4K RPD; Gemini 3.5 Flash-Lite and 3.1 Flash-Lite 15 RPM, 250K TPM, 500 RPD; other Gemini Flash models 20 RPD; Pro models not on the free tier.

## Options considered
- **A. One vendor SDK.** Simple; locks the benchmark to one provider.
- **B. Third-party abstraction library.** Less code; extra dependency and opaque behavior.
- **C. Thin own client** (pydantic structured output, provider adapters, disk cache).

## Decision
C. Interface returns a typed result with `parsed`, `raw_text`, token usage, `model_id`, latency, `cache_hit`. Disk cache keyed by content hash and integrity-checked. Structured output is always validated with pydantic with a repair loop (at most 2 retries). Models: **M1 (primary, 3 seeds): Gemma 4 31B on AI Studio; M3: gemini-3.5-flash-lite; M4 (dev only): small local Ollama model; M2 (smaller open-weight): decided at T-006 from measured local speed.** Groq is for small side experiments only (200K TPD is about 100 calls per day).

## Consequences
- Record model id and snapshot, requested and transmitted temperature, and the quota pages at run time with every result (SPC and WRB both lost this provenance).
- V-16: Gemma 4 JSON-schema support through the Gemini API is unverified; first T-006 smoke test.
- V-17: free-tier Gemini content may be used by Google; send public or synthetic data only and disclose that test questions may leak into future training data.
- Provider kill switch environment variable disables all LLM calls.
