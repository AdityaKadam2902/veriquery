"""Provider protocol and the structured-output client with cache and repair loop."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any, Protocol

from pydantic import BaseModel, ValidationError

from veriquery.agent.llm.cache import DiskCache, build_request_record, cache_key
from veriquery.agent.llm.types import (
    LLMDisabled,
    LLMResult,
    Message,
    RawResponse,
    SchemaValidationFailure,
    T,
    Usage,
)
from veriquery.common.hashing import canonical_json


class Provider(Protocol):
    name: str

    def generate(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        seed: int | None,
        json_schema: dict[str, Any] | None,
    ) -> RawResponse: ...


def schema_instruction(json_schema: dict[str, Any] | None) -> str:
    """Prompt text asking for a single JSON object; used by every provider for consistency."""
    if json_schema is None:
        return ""
    return (
        "Respond with a single JSON object that matches this JSON Schema, and nothing else "
        "(no prose, no code fences):\n" + canonical_json(json_schema)
    )


_FENCE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.DOTALL)


def extract_json(text: str) -> str:
    """Strip code fences and surrounding prose; return the outermost {...} if present."""
    stripped = text.strip()
    match = _FENCE.match(stripped)
    if match:
        stripped = match.group(1)
    start, end = stripped.find("{"), stripped.rfind("}")
    if start != -1 and end > start:
        return stripped[start : end + 1]
    return stripped


class StructuredLLM:
    """`complete_structured` with caching, kill switch and up to `max_repairs` repair retries."""

    def __init__(
        self,
        provider: Provider,
        cache: DiskCache | None = None,
        *,
        max_repairs: int = 2,
        kill_switch: bool = False,
    ) -> None:
        self._provider = provider
        self._cache = cache
        self._max_repairs = max_repairs
        self._kill_switch = kill_switch

    def _call(
        self,
        messages: Sequence[Message],
        schema_json: dict[str, Any],
        *,
        model: str,
        temperature: float,
        seed: int | None,
        prompt_version: str,
        catalog_version: str,
    ) -> tuple[RawResponse, bool]:
        request = build_request_record(
            provider=self._provider.name,
            model=model,
            messages=messages,
            schema_json=schema_json,
            temperature=temperature,
            seed=seed,
            prompt_version=prompt_version,
            catalog_version=catalog_version,
        )
        if self._cache is not None:
            hit = self._cache.get(cache_key(request))
            if hit is not None:
                return hit, True
        if self._kill_switch:
            raise LLMDisabled("LLM calls are disabled and this request is not cached")
        raw = self._provider.generate(
            messages,
            model=model,
            temperature=temperature,
            seed=seed,
            json_schema=schema_json,
        )
        if self._cache is not None:
            self._cache.put(request, raw)
        return raw, False

    def complete_structured(
        self,
        messages: Sequence[Message],
        schema: type[T],
        *,
        model: str,
        temperature: float = 0.0,
        seed: int | None = None,
        prompt_version: str = "",
        catalog_version: str = "",
    ) -> LLMResult[T]:
        schema_json = schema.model_json_schema()
        convo = list(messages)
        usage = Usage()
        latency = 0.0
        all_hits = True
        errors: list[str] = []
        last_text = ""
        for attempt in range(1, self._max_repairs + 2):
            raw, hit = self._call(
                convo,
                schema_json,
                model=model,
                temperature=temperature,
                seed=seed,
                prompt_version=prompt_version,
                catalog_version=catalog_version,
            )
            usage = usage + raw.usage
            latency += raw.latency_ms
            all_hits = all_hits and hit
            last_text = raw.text
            try:
                parsed = schema.model_validate_json(extract_json(raw.text))
            except ValidationError as exc:
                summary = "; ".join(
                    f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()
                )[:500]
                errors.append(summary)
                convo = [
                    *convo,
                    Message(role="assistant", content=raw.text),
                    Message(
                        role="user",
                        content=(
                            f"Your previous reply was invalid ({summary}). "
                            "Reply again with only a JSON object matching the schema."
                        ),
                    ),
                ]
                continue
            return LLMResult(
                parsed=parsed,
                raw_text=raw.text,
                usage=usage,
                model_id=raw.model_id,
                latency_ms=latency,
                cache_hit=all_hits,
                attempts=attempt,
                transmitted=raw.transmitted,
            )
        raise SchemaValidationFailure(len(errors), last_text, errors)


__all__ = ["BaseModel", "Provider", "StructuredLLM", "extract_json", "schema_instruction"]
