# Verification log

Unverified external facts and how they were checked. Every [VERIFY] item from the architecture
is resolved here (T-003).

| Date | Item | Status | Source / note |
|---|---|---|---|
| 2026-10-17 | CI action pins: actions/checkout v7.0.1, astral-sh/setup-uv v10.2.0 | partial | SHAs read via `git ls-remote` tags. Release age (>= 2 weeks rule) NOT yet checked. |
| 2026-10-17 | pre-commit hook revs (ruff-pre-commit v0.9.10, pre-commit-hooks v5.0.0) | unverified | Written from memory; run `pre-commit autoupdate` and review. |
