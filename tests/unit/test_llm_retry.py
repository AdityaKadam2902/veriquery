from collections.abc import Sequence
from typing import Any

import pytest

from veriquery.agent.llm import Message, ProviderError, RawResponse
from veriquery.agent.llm.retry import RetryingProvider

MSGS = [Message(role="user", content="q")]


class Flaky:
    name = "flaky"

    def __init__(self, failures: list[int]) -> None:
        self._failures = list(failures)
        self.calls = 0

    def generate(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        seed: int | None,
        json_schema: dict[str, Any] | None,
    ) -> RawResponse:
        self.calls += 1
        if self._failures:
            raise ProviderError("flaky", self._failures.pop(0), "boom")
        return RawResponse(text="{}", model_id=model, latency_ms=1.0)


def _call(provider: RetryingProvider) -> RawResponse:
    return provider.generate(MSGS, model="m", temperature=0.0, seed=None, json_schema=None)


def test_retries_then_succeeds_with_growing_capped_delays() -> None:
    delays: list[float] = []
    inner = Flaky([503, 500, 429])
    provider = RetryingProvider(
        inner,
        max_attempts=5,
        base_delay_s=2.0,
        max_delay_s=3.0,
        sleep=delays.append,
        jitter=lambda: 1.0,
    )
    assert _call(provider).text == "{}"
    assert inner.calls == 4
    assert provider.retries == 3
    assert delays == [2.0, 3.0, 3.0]


def test_client_errors_are_not_retried() -> None:
    inner = Flaky([400])
    provider = RetryingProvider(inner, sleep=lambda _: None)
    with pytest.raises(ProviderError) as info:
        _call(provider)
    assert info.value.status_code == 400
    assert inner.calls == 1


def test_gives_up_after_max_attempts() -> None:
    inner = Flaky([503, 503, 503])
    provider = RetryingProvider(inner, max_attempts=3, sleep=lambda _: None)
    with pytest.raises(ProviderError):
        _call(provider)
    assert inner.calls == 3
    assert provider.retries == 2


def test_name_follows_inner_provider() -> None:
    assert RetryingProvider(Flaky([])).name == "flaky"
