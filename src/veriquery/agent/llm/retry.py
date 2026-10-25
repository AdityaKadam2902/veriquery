"""Retry with exponential backoff and jitter for transient provider errors.

Retries only server-side or rate-limit statuses; client errors (400, 401, 403, 404) are raised
immediately. Failures are never written to the cache. Retry-After and quota-aware pacing arrive
with the full rate limiter (T-201).
"""

from __future__ import annotations

import random
import time
from collections.abc import Callable, Sequence
from typing import Any

from veriquery.agent.llm.base import Provider
from veriquery.agent.llm.types import Message, ProviderError, RawResponse

RETRYABLE = frozenset({429, 500, 502, 503, 504})


class RetryingProvider:
    def __init__(
        self,
        inner: Provider,
        *,
        max_attempts: int = 4,
        base_delay_s: float = 2.0,
        max_delay_s: float = 60.0,
        retry_statuses: frozenset[int] = RETRYABLE,
        sleep: Callable[[float], None] = time.sleep,
        jitter: Callable[[], float] = random.random,
    ) -> None:
        self._inner = inner
        self.name = inner.name
        self._max_attempts = max_attempts
        self._base = base_delay_s
        self._cap = max_delay_s
        self._statuses = retry_statuses
        self._sleep = sleep
        self._jitter = jitter
        self.retries = 0

    def generate(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        seed: int | None,
        json_schema: dict[str, Any] | None,
    ) -> RawResponse:
        attempt = 1
        while True:
            try:
                return self._inner.generate(
                    messages,
                    model=model,
                    temperature=temperature,
                    seed=seed,
                    json_schema=json_schema,
                )
            except ProviderError as exc:
                if exc.status_code not in self._statuses or attempt >= self._max_attempts:
                    raise
                delay = min(self._cap, self._base * 2 ** (attempt - 1))
                self._sleep(delay * (0.5 + self._jitter() / 2))
                self.retries += 1
                attempt += 1
