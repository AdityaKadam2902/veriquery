# ADR-004: Audit equivalence by normalization plus perturbed execution
Status: accepted

## Context
Audit mode must say whether arbitrary SQL from another agent matches a governed definition, and explain why not. Execution on one database instance can accept different queries that happen to agree (Zhong et al. 2020 distilled test suites; SPC's counterfactual instances address the same problem).

## Options considered
- **A. Structural AST comparison only.** Cheap; misses semantically equal rewrites and says little about differences.
- **B. Execution on the real data only.** Accepts queries that agree by coincidence.
- **C. Structural comparison, then execution on the real data and K perturbed copies.** Catches fan-out, boundary and null-handling differences; not a proof.
- **D. Formal equivalence solver.** Strong guarantees; poor support for realistic SQL; high effort.

## Decision
C, as in Section 7.5.3: safety parse, normalize, infer candidate metric, structural compare, then K=8 perturbed copies (row subsampling, duplicate-row injection, NULL injection in non-key columns, value jitter, boundary-timestamp shifts), early exit on first difference, K adaptive within a time budget. Verdicts: `EQUIVALENT`, `DIFFERENT_DEFINITION`, `UNMATCHED`, `UNSAFE`, `ERROR`. Complex SQL (window functions, recursive CTEs, correlated subqueries) returns `UNMATCHED`.

## Consequences
- We do not claim perturbation equivalence is new; the contribution is its application to governed definitions for third-party SQL, and its measurement.
- The verifier is evaluated on a labeled set (about 150 items) for precision, recall, false-alarm and UNMATCHED rates.
- RQ4 includes a pre-registered measure motivated by WRB (arXiv 2608.09254): what share of wrong answers that pass rule-based static and post-execution checks does perturbation catch, and at what false-alarm rate (see ADR-013).
- Execution only inside the sandbox (ADR-009) and never returns raw rows (I4).
