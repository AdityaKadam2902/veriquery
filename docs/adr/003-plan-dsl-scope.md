# ADR-003: Narrow typed plan DSL
Status: accepted

## Context
In B2 the LLM never writes SQL or final numbers (D-005). The size of the plan language sets coverage and attack surface.

## Options considered
- **A. Free-form SQL from the LLM.** Maximum coverage, no determinism (this is the B0/B1 baseline).
- **B. Rich plan language with joins and route selection** (as in SPC, arXiv 2608.16663). Higher coverage; needs a join-path engine, route registry and grain lowering.
- **C. Narrow DSL over governed metrics whose SQL templates already encode joins and grain.**

## Decision
C, as specified in Section 7.2: one metric, optional ratio denominator (both `ratio_compatible`), half-open time range, at most 2 `group_by`, at most 5 filters, comparison (`prior_period`, `prior_year`) computed by the compiler, `top_n` of 1 to 50. Output is a discriminated union `Plan | Clarify | Refuse` with fixed refusal reason codes. Any other shape must become `Clarify` or `Refuse(no_metric)`.

## Consequences
- Coverage is lower and measured, not hidden (coverage and unnecessary-refusal rates are reported).
- Coverage grows by adding metrics and operators through PRs with golden tests.
- Joins and grain correctness live in reviewed catalog templates plus verifier checks V09 and V12.
