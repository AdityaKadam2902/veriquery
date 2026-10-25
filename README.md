# VeriQuery

Open-source toolkit and public benchmark for measuring and enforcing the **numerical trustworthiness** of AI data agents, with an audit verifier that checks any agent's SQL against governed metric definitions.

> **Status: under construction (Phase 0 complete, Phase 1 starting).** No results exist yet. Nothing below is a claim until it is measured. Source of truth: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). One-page summary: [`SPEC.md`](SPEC.md).

## 1. The problem
TODO (T-703): one failing example, a plausible wrong number from a free-form text-to-SQL agent and the governed answer.

## 2. What VeriQuery provides
- **C1** reproducible, multi-domain benchmark of trust failures
- **C2** audit verifier for third-party SQL (perturbed-execution equivalence)
- **C3** reference attested agent (B2), a control rather than a novelty claim
- **C4** abstention analysis (risk-coverage)
- **C5** failure taxonomy, importers, MCP server

## 3. Related work and honest framing
The typed-plan plus deterministic-compile pattern is established (dbt, PyDough, SPC, OKF Attested Computation). The closest work is WRB (arXiv 2608.09254), which we credit and extend. See [`docs/related_work.md`](docs/related_work.md) and [ADR-011](docs/adr/011-positioning.md).

## 4. Headline results
TODO (T-701): table with confidence intervals after the frozen-plan test run. Empty until then.

## 5. Quickstart
TODO (T-606): Docker and plain Python in 10 minutes.

## 6. How it works
TODO: diagram of the attested flow and the audit flow (Architecture 6.3, 6.4).

## 7. Audit mode example
TODO (T-309).

## 8. Benchmark and how to run it
TODO (P4): dataset card, license notes (Olist is CC BY-NC-SA 4.0 and is not redistributed; TPC-H is "derived from" with a non-comparability disclaimer), `make bench-dev`, locked test split.

## 9. Catalog format and importers
TODO (P1, P5): YAML schema; importers for dbt (legacy and latest), Snowflake semantic views, OKF v0.2.

## 10. Limitations and threats to validity
The benchmark measures agreement with organizational definitions, not absolute truth. The HMAC verification record is tamper-evident only. Audit equivalence is evidence, not proof. Full list: Architecture 10.9 (TODO: copy into report).

## 11. Roadmap
See Architecture Section 14.

## 12. Citing, license, contributing
Code license Apache-2.0 (D-015; LICENSE file added before first release). Citation file: TODO (T-702). Contributions: TODO.

## Development
```bash
make setup lint typecheck test
```