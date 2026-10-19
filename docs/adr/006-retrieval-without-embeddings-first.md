# ADR-006: Lexical retrieval first, embeddings only if needed
Status: accepted

## Context
The agent needs the top metric cards in the prompt. The catalog is small and curated (about 24 metrics at first).

## Options considered
- **A. Lexical ranking** over `title`, `synonyms`, `description`, plus one hop over `not_to_be_confused_with`.
- **B. Embeddings.** Better recall on paraphrase; adds a model dependency and nondeterminism risk.
- **C. LLM-based routing.** Costs a call and is harder to audit.

## Decision
A, top-k 5 by default. Add embeddings only if dev-set retrieval recall at k=5 is below 95%.

## Consequences
- Deterministic and cheap; retrieval recall is measured on dev.
- The ambiguity gate matches question words against metric names and synonyms, like WRB's lexicon. Synonyms must never be written from test questions; a CI test fails if any synonym phrase occurs only in test questions (ADR-013).
