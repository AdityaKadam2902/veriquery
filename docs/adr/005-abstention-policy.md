# ADR-005: Abstention policy
Status: accepted

## Context
A system that refuses everything has zero wrong numbers and no value, so abstention must be measured with coverage. WRB reports that a fitted confidence model lost to a hand-weighted heuristic because it was trained only on answerable questions, and that thresholds tuned on validation did not transfer.

## Options considered
- **A. LLM self-reported confidence.** Cheap, poorly calibrated, not auditable.
- **B. Rule-based tiering over observable signals.** Auditable; coarse.
- **C. Learned model over signals.** Can rank better; risks overfitting the answered pool.

## Decision
Deterministic gates first (ambiguity gate before any LLM call; refusal when retrieval finds no metric above threshold). Then B: policy tiers answer, answer with warning, clarify, refuse, from signals (retrieval margin, repair retries, verifier warnings, `self_inconsistency`, optional agreement across k=3 plans). C is an upgrade only if it beats B on held-out template families (leave-one-family-out), fit on the dev split only, trained and evaluated on pools that include cases where answering is wrong. Baselines use agreement across k=3 sampled SQL executions as their confidence signal.

## Consequences
- Report risk-coverage curves, AURC, coverage at 1% and 5% risk, and unnecessary clarify/refuse rates.
- Thresholds are chosen on a validation family set separate from test; the test split is run once per the frozen analysis plan.
- Fail closed: any failed check or budget breach refuses with a reason code.
