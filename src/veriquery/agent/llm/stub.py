"""Scripted providers for tests and offline development. No network, no keys."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from veriquery.agent.llm.types import LLMError, Message, RawResponse, Usage


class ScriptedProvider:
    """Returns the given texts in order; records every call."""

    name = "stub"

    def __init__(self, responses: Sequence[str]) -> None:
        self._responses = list(responses)
        self.calls: list[list[Message]] = []

    def generate(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        seed: int | None,
        json_schema: dict[str, Any] | None,
    ) -> RawResponse:
        self.calls.append(list(messages))
        if len(self.calls) > len(self._responses):
            raise LLMError("ScriptedProvider has no more scripted responses")
        text = self._responses[len(self.calls) - 1]
        return RawResponse(
            text=text,
            usage=Usage(input_tokens=10, output_tokens=len(text) // 4 + 1),
            model_id=model,
            latency_ms=1.0,
            transmitted={"temperature": temperature, "seed": seed},
        )


class CallableProvider:
    """Responds with `fn(messages)`; useful for rule-based fake models."""

    name = "stub-fn"

    def __init__(self, fn: Callable[[Sequence[Message]], str]) -> None:
        self._fn = fn

    def generate(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        seed: int | None,
        json_schema: dict[str, Any] | None,
    ) -> RawResponse:
        text = self._fn(messages)
        return RawResponse(
            text=text,
            usage=Usage(input_tokens=10, output_tokens=len(text) // 4 + 1),
            model_id=model,
            latency_ms=1.0,
            transmitted={"temperature": temperature, "seed": seed},
        )
