"""Typed values and errors for the LLM client (Architecture 7.13)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound=BaseModel)


class Message(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: Literal["system", "user", "assistant"]
    content: str


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0

    def __add__(self, other: Usage) -> Usage:
        return Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
        )


class RawResponse(BaseModel):
    """One provider call. `transmitted` records what was actually sent (temperature, seed)."""

    text: str
    usage: Usage = Field(default_factory=Usage)
    model_id: str
    latency_ms: float
    transmitted: dict[str, Any] = Field(default_factory=dict)


@dataclass(frozen=True)
class LLMResult(Generic[T]):
    """Result of a structured call. `latency_ms` and `usage` sum all attempts.

    On a cache hit, latency is the originally measured latency, not the (near zero) replay time.
    """

    parsed: T
    raw_text: str
    usage: Usage
    model_id: str
    latency_ms: float
    cache_hit: bool
    attempts: int
    transmitted: dict[str, Any] = field(default_factory=dict)


class LLMError(Exception):
    """Base class for LLM client errors."""


class ProviderError(LLMError):
    def __init__(self, provider: str, status_code: int, detail: str) -> None:
        super().__init__(f"{provider} error {status_code}: {detail}")
        self.provider = provider
        self.status_code = status_code
        self.detail = detail


class SchemaValidationFailure(LLMError):
    def __init__(self, attempts: int, last_text: str, errors: list[str]) -> None:
        super().__init__(f"output failed schema validation after {attempts} attempts")
        self.attempts = attempts
        self.last_text = last_text
        self.errors = errors


class LLMDisabled(LLMError):
    """The kill switch is on and the request is not in the cache."""
