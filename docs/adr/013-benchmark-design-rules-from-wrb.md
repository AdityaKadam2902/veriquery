# ADR-013: Benchmark design rules adopted from WRB
Status: proposed (needs owner decision; recommendation: accept all)

## Context
WRB (arXiv 2608.09254) discloses weaknesses we can avoid by design: unbalanced family-disjoint splits, family-level intervals that include zero, a lexicon contaminated from the test split, an adversarial stratum that ranks nothing, denominator errors in scoring, no matched scaffold or ablation, single reviewer.

## Decision (rules)
1. **Stratified family split.** Assign template families to dev, validation and test per category so each category has several test families across at least two domains.
2. **Cluster-aware statistics.** Report a cluster bootstrap over families as co-primary with the paired task bootstrap; size the test split by families as well as questions.
3. **Lexicon guard.** CI fails if any ambiguity-gate synonym phrase occurs only in test questions.
4. **Discriminating adversarial category.** Category 7 is designed and checked on dev so that weak baselines fail it.
5. **Pinned denominators and a scoring-corrections log.** ANALYSIS_PLAN.md defines every metric with its denominator; corrections are logged with whether they moved a headline metric.
6. **Replay reproducibility.** Commit raw model outputs, a results file with input hashes and sealed costs; generate every number in the report, never type it. State the difference between replay and regeneration.
7. **Matched baseline and ablation.** B1+ is the matched baseline; add component ablations (gate, verifier, composer).
8. **Confidence signals** are trained and evaluated on pools that include cases where answering is wrong.
9. **Reviewers.** If no second person is available (D-020), report test-retest agreement and say it is not inter-annotator agreement.
10. **Audit-mode claim.** Pre-register the measure in ADR-004: share of wrong answers that pass rule-based checks and are caught by perturbation, with false-alarm rate.

## Consequences
- ANALYSIS_PLAN.md and the benchmark construction tasks (P4) incorporate these rules.
- Slightly more construction work (more families, a bootstrap by cluster); less risk of an indefensible result.
- Optional external check on WRB's dev and validation tasks after a license review (V-34).
