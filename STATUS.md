# STATUS (updated: 2026-10-17)
**Phase:** P0  **Current task(s):** T-005 done; T-006 next (T-001 to T-004 done; ADR-012 and ADR-013 awaiting owner)
## Done (since last update)
- T-005: SPEC.md (one page) and README skeleton
- T-004: ADRs 001-013 written (docs/adr/); Section 2 of ARCHITECTURE.md rewritten (v2.2) per approved ADR-011
- T-002: docs/related_work.md drafted. Finding: typed-plan + deterministic-compile is already published (SPC, PyDough, dbt, OKF); positioning narrowed to benchmark, audit verifier, abstention analysis, reproducibility
- T-001: repo scaffold, tooling config, Makefile, pre-commit, CI skeleton, smoke test
- T-003: licenses, providers, importer formats, OKF version verified; see docs/verification_log.md (budget resolved: free tiers only, Gemma 4 31B as M1; see section 6)
## Next (max 5, with task IDs)
- T-006 API keys, Ollama, stub LLM client with cache smoke test
## Blockers / questions
- Owner to accept or change ADR-012 (OKF-compatible record, recommendation B) and ADR-013 (WRB-derived benchmark rules, recommend accept all)
- Owner to check GPU (Task Manager, Performance, GPU); 16 GB RAM known
- D-007 M2 model: decide at T-006 from hardware
- V-16: Gemma 4 structured-output support untested (first T-006 smoke test)
## Decisions made (link ADRs)
- ADR-001 to ADR-010 accepted (architecture decisions D-002, D-003, D-005, D-013, D-017, D-023 to D-026)
- ADR-011 positioning accepted (owner, 2026-10-17)
- Budget: free tiers only; D-007 resolved except M2 (ADR-007)
- D-019: no fixed weekly hours; owner will give as many as possible, dates tracked as actuals
- Proposed, awaiting owner: ADR-012, ADR-013
## Parking lot (out-of-scope ideas)
- LICENSE file (Apache-2.0 full text) before first public release (NFR-08)
## Metrics snapshot (dev): wrong-number rate / coverage per system
- n/a