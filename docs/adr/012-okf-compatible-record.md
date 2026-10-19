# ADR-012: OKF-compatible verification record
Status: proposed (needs owner decision; recommendation B)

## Context
OKF v0.2 (Google Cloud) defines Attested Computation: typed parameters only, an executor receipt, a deterministic attester, `stale_after` gating. It defers receipt and verdict wire formats, attester interface and sandboxing, and semantic-layer templates. Our verification record (Section 7.7) and our verifier cover similar ground. Our catalog status maps one-to-one to OKF `status`.

## Options considered
- **A. Ignore OKF.** No work; no interoperability.
- **B. Keep our record native, add an OKF reader (already planned) and an export adapter that renders our record as an OKF-style receipt.** Small cost, interoperability, clear credit.
- **C. Make OKF the native format.** Couples us to a v0.2 spec that is still moving.

## Decision (recommended)
B, as a Should-have after the core, following the same logic as D-003. Not decided until the owner accepts.

## Consequences
- We avoid claiming the contract as ours and can offer fills for what OKF defers.
- Spec drift risk; pin the OKF version in importer and adapter tests.
