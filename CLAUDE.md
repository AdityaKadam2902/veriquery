# Project: VeriQuery
Source of truth: docs/ARCHITECTURE.md (v2.1). Do not redesign finalized decisions (Sec 18.1).
Workflow: pick a task ID from Sec 14, meet its acceptance criteria, write tests first or with the code.
Commands: `make setup | lint | typecheck | test | golden | bench-smoke`.
Standards: Python 3.11, uv, ruff, mypy --strict, pytest (90% coverage on verifier/ and executor/).
Never: write SQL from user text, run the locked test split early, commit secrets or raw third-party data, execute untrusted SQL outside the sandbox, return raw rows from audit mode, feed query results back into an LLM prompt in B2.
Style: concise; targeted diffs, not whole-file rewrites; ask only when blocked.
Always: update STATUS.md at session end; log unverified external facts in docs/verification_log.md.
