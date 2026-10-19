# ADR-002: Own YAML catalog schema primary; importers secondary
Status: accepted (D-003)

## Context
The catalog defines what "correct" means. External formats are young or split: dbt now has a legacy spec (top-level `semantic_models:`) and a January 2026 "latest" spec (`semantic_model:` nested under models); Snowflake's current format is semantic view YAML; OKF is at v0.2 (see verification log V-20 to V-24).

## Options considered
- **A. Adopt dbt YAML natively.** Familiar, but two specs and no fields for our lifecycle and trap metadata.
- **B. Adopt OKF natively.** Standards-based, but v0.2 is young and its semantic-layer templates are deferred.
- **C. Own schema, with importers and exporters.** Full control over lifecycle (status, review dates, `not_to_be_confused_with`, allowed dimensions, checks); mapping effort.

## Decision
C. Own schema is primary. Importers (dbt legacy first, dbt latest second, Snowflake semantic view, OKF reader) write to a quarantine area and require review before use. Unsupported constructs are listed in `import_report.md`.

## Consequences
- Schema is versioned; a linter runs in CI.
- Import loses information in some cases; the report says where.
- Importers are Should-have and cut before core items (Section 14.3).
