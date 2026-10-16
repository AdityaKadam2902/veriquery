.PHONY: setup lint typecheck test golden bench-smoke bench-dev bench-test figures docs up down

setup:
	uv sync --all-groups

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run mypy

# Coverage gate (>=90%) applies to verifier/ and executor/ per NFR-04.
test:
	uv run pytest tests/unit tests/property tests/integration \
	  --cov=veriquery.verifier --cov=veriquery.executor --cov-report=term-missing

golden:
	@echo "golden: no golden tests yet (arrive with T-104)"

bench-smoke:
	@echo "bench-smoke: not implemented yet (arrives with T-207)"

bench-dev:
	@echo "bench-dev: not implemented yet (arrives with T-406)"

# Guarded: the locked test split may only run after the analysis plan is frozen.
bench-test:
	@git rev-parse -q --verify refs/tags/test-lock >/dev/null || \
	  (echo "REFUSED: tag 'test-lock' not found. Freeze the test split and ANALYSIS_PLAN.md first." && exit 1)
	@echo "bench-test: not implemented yet (arrives with T-502)"

figures:
	@echo "figures: not implemented yet (arrives with T-702)"

docs:
	@echo "docs: not implemented yet"

up:
	docker compose up --build

down:
	docker compose down
