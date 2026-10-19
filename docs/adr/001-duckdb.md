# ADR-001: DuckDB as the analytical engine
Status: accepted (D-002)

## Context
We need an embedded, zero-setup, fast engine that makes the benchmark reproducible on a laptop, supports read-only connections, and can be locked down for untrusted SQL (audit mode).

## Options considered
- **A. DuckDB.** Embedded, columnar, fast analytics, single-file databases, read-only mode, configuration lock, Python API. Weaker native resource isolation than a server with cgroups.
- **B. SQLite.** Ubiquitous and simple, but weak analytical features and slower on larger scans. (SPC, arXiv 2608.16663, used a SQLite port.)
- **C. PostgreSQL in a container.** Rich isolation and roles, but setup cost and slower reproduction for users.

## Decision
DuckDB, with `sqlglot` using the `duckdb` dialect. (WRB, arXiv 2608.09254, also uses DuckDB, which eases cross-comparison.)

## Consequences
- Executor: `read_only=True`, per-query timeout, row cap. Lockdown settings (`enable_external_access=false`, `lock_configuration`, extension autoload/autoinstall off, `memory_limit`, `threads`) are specified in ADR-009; exact setting names are verified at T-311.
- Windows has no cgroups or `ulimit`; the portable sandbox for audit execution is a Docker container.
- Data loaders (for example TPC-H generation) may need DuckDB extensions installed. Loaders run outside the sandbox and never inside the executor. To confirm at T-101.
- Third-party SQL written for other dialects may fail to parse: verdict `ERROR` or `UNMATCHED`, documented.
