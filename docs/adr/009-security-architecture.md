# ADR-009: Security architecture and trust boundaries
Status: accepted (D-023, D-024, D-026); detailed trust-boundary document and invariant tests at T-310

## Context
The LLM output, user input, third-party SQL, imported catalogs and MCP clients are all untrusted. Audit mode executes untrusted SQL.

## Options considered
- **A. Rely on LLM guardrails or prompting.** Not enforceable.
- **B. Static allow-lists only.** Misses runtime behavior.
- **C. Defense in depth with deny-by-default,** typed plans, sandboxed read-only execution, output provenance and evaluation.

## Decision
C. Principles: the LLM is untrusted; least capability; allow-lists and deny by default; defense in depth; fail closed; auditability (Section 13). Invariants I1 to I8, each with an automated test:
- I1 only a validated typed plan through the compiler reaches the executor (B2).
- I2 result text never re-enters an LLM prompt (B2).
- I3 every executed statement is compiler-generated or a single audit-verified SELECT on allow-listed objects inside the sandbox.
- I4 audit mode never returns raw rows.
- I5 read-only connection, external access disabled, configuration locked, resource limits.
- I6 every response carries a verification record.
- I7 secrets never appear in logs, prompts, records or errors.
- I8 sensitive columns are never selectable; small groups suppressed when policy is on.
Audit execution runs in a Docker container (portable sandbox). Plain-Python mode applies the DuckDB lockdown and timeouts only and documents the gap.

## Consequences
- Security is evaluated, not only designed: attack-success rate on category 7b, an injection corpus of 60+ cases, SQL fuzzing.
- WRB's adversarial stratum scored 1.000 for every system and ranked nothing; category 7 must be built so weak baselines fail it (ADR-013).
- OWASP LLM category names and security tool choices are verified in P3 (verification log section 5).
