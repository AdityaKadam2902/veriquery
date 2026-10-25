# LLM setup and smoke test (T-006)

Keys live in `.env` only (copy `.env.example`). Never paste keys into chat, commits or command lines.

## 1. Gemini / Gemma (AI Studio)
```bash
uv sync --all-groups
uv run python scripts/list_models.py gemma        # find the exact Gemma 4 model ids
uv run python scripts/smoke_llm.py --provider gemini --model <id>
```
Verification log V-16: Gemma may reject system instructions or JSON mode. If pass 1 reports an error, try in this order and keep the first combination that gives `schema_validity_rate` 1.0 (or close):
```bash
... --provider gemini --model <id> --no-system-instruction
... --provider gemini --model <id> --json-mode prompt
... --provider gemini --model <id> --no-system-instruction --json-mode prompt
```
Default pacing is 2.5 s between live calls (30 RPM limit for Gemma). Raise `--sleep` if you see 429 errors.

## 2. Ollama (local, M4 and maybe M2)
Install Ollama, then: `ollama pull llama3.2:3b` (about 2 GB, fits 16 GB RAM) and run
`uv run python scripts/smoke_llm.py --provider ollama --model llama3.2:3b`.
Report `mean_latency_ms` and the GPU shown in Task Manager (Performance, GPU); that decides M2/M4.

## 3. Pass criteria for T-006
- Pass 1 live on two providers returns valid structured output for most of the 8 questions.
- Pass 2 is 100% cache hits with identical output (`replay_all_cache_hits` and `replay_identical` true), also with the network off.

Send me the JSON summary printed by each run (it contains no secrets).
