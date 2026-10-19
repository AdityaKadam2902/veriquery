# ADR-011: Positioning after the prior-art review
Status: accepted (owner approved the Section 2 rewrite on 2026-10-17)

## Context
T-002 found that the typed-plan plus deterministic-compile pattern is already published (dbt, PyDough, SPC arXiv 2608.16663, OKF Attested Computation), that perturbed-database equivalence is established (Zhong et al. 2020), that abstention scoring is established (TrustSQL), and that WRB (arXiv 2608.09254) already offers a frozen, pre-registered benchmark with scored clarification, abstention, refusal, schema-drift and adversarial tasks. See `docs/related_work.md`.

## Options considered
- **A. Keep the v2.1 framing.** Overstates novelty; fails honest-framing rules.
- **B. Narrow to claims we can defend** and credit prior work explicitly.
- **C. Abandon the project.** Unwarranted: reproducible multi-domain evaluation and a measured audit verifier remain open.

## Decision
B. Claims are C1 to C5 as worded in Section 2.2. B2 is a reference system and control. WRB is credited and a metric mapping (wrong-number rate to False Success Rate, coverage, answer accuracy, cost per correct answer) is reported.

## Consequences
- README, report and posts follow Section 2.3.
- Reproducibility is a design goal: publish questions, gold labels, fixtures, harness, raw model outputs, verdicts and run metadata.
- Risk: the contribution is narrower and more rigor-dependent. Mitigation: the measured audit verifier, real-data categories (time, fan-out, lifecycle), a discriminating adversarial category, and cluster-aware statistics.
