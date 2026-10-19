# ADR-008: Verification record signing
Status: accepted (D-013)

## Context
Every answer, clarification and refusal carries a verification record (Section 7.7). Signing makes tampering detectable but must not be oversold.

## Options considered
- **A. No signature.** Simplest; no integrity signal.
- **B. HMAC-SHA256 with a local secret.** Simple, tamper-evident; not a trust anchor between parties.
- **C. ed25519 public-key signatures.** Third-party verifiable; key management burden.
- **D. Transparency log or keyless signing.** Strongest story; heavy for a reference tool.

## Decision
B first, with key id, rotation, nonce and timestamp in each record. C is a could-have.

## Consequences
- README states plainly that HMAC is tamper-evident only, and avoids the word "attested" for anything beyond what is implemented.
- Record fields: see Section 7.7. Whether to align the record with OKF Attested Computation is ADR-012 (proposed).
