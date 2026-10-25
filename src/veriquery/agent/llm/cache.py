"""Append-only JSONL disk cache with per-entry integrity check.

Each line stores the full request for auditability. The digest is an HMAC-SHA256 when a key is
given, otherwise a plain SHA-256 (corruption detection only). Entries that fail the digest or
whose key does not match their request are ignored and counted in `rejected_entries`.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from veriquery.agent.llm.types import Message, RawResponse
from veriquery.common.hashing import canonical_json, hmac_sha256_hex, sha256_hex


def build_request_record(
    *,
    provider: str,
    model: str,
    messages: Sequence[Message],
    schema_json: dict[str, Any] | None,
    temperature: float,
    seed: int | None,
    prompt_version: str = "",
    catalog_version: str = "",
) -> dict[str, Any]:
    return {
        "provider": provider,
        "model": model,
        "messages": [m.model_dump() for m in messages],
        "schema": schema_json,
        "temperature": temperature,
        "seed": seed,
        "prompt_version": prompt_version,
        "catalog_version": catalog_version,
    }


def cache_key(request: dict[str, Any]) -> str:
    return sha256_hex(canonical_json(request))


class DiskCache:
    def __init__(self, path: Path, hmac_key: bytes | None = None) -> None:
        self._path = path
        self._hmac_key = hmac_key
        self._entries: dict[str, RawResponse] = {}
        self.rejected_entries = 0
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            self._load()

    def _digest(self, body: dict[str, Any]) -> str:
        text = canonical_json(body)
        if self._hmac_key is not None:
            return hmac_sha256_hex(self._hmac_key, text)
        return sha256_hex(text)

    def _load(self) -> None:
        with self._path.open(encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    body = {
                        "key": entry["key"],
                        "request": entry["request"],
                        "response": entry["response"],
                    }
                    if entry["digest"] != self._digest(body) or entry["key"] != cache_key(
                        entry["request"]
                    ):
                        raise ValueError("integrity check failed")
                    self._entries[entry["key"]] = RawResponse.model_validate(entry["response"])
                except (ValueError, KeyError, TypeError):
                    self.rejected_entries += 1

    def get(self, key: str) -> RawResponse | None:
        return self._entries.get(key)

    def put(self, request: dict[str, Any], response: RawResponse) -> str:
        key = cache_key(request)
        body = {"key": key, "request": request, "response": response.model_dump()}
        entry = {
            **body,
            "created_at": datetime.now(UTC).isoformat(),
            "digest": self._digest(body),
        }
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(canonical_json(entry) + "\n")
        self._entries[key] = response
        return key

    def __len__(self) -> int:
        return len(self._entries)
