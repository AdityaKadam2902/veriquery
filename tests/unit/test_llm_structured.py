from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

import pytest
from pydantic import BaseModel

from veriquery.agent.llm import (
    DiskCache,
    LLMDisabled,
    Message,
    RawResponse,
    SchemaValidationFailure,
    StructuredLLM,
)
from veriquery.agent.llm.base import extract_json
from veriquery.agent.llm.stub import CallableProvider, ScriptedProvider


class Out(BaseModel):
    kind: Literal["plan", "clarify", "refuse"]
    reason: str


MSGS = [Message(role="system", content="s"), Message(role="user", content="q")]
OK = '{"kind":"plan","reason":"r"}'


def test_valid_first_try() -> None:
    llm = StructuredLLM(ScriptedProvider([OK]))
    result = llm.complete_structured(MSGS, Out, model="m")
    assert result.parsed == Out(kind="plan", reason="r")
    assert result.attempts == 1
    assert result.cache_hit is False
    assert result.transmitted == {"temperature": 0.0, "seed": None}


def test_fenced_and_prose_wrapped_json() -> None:
    assert extract_json('```json\n{"a":1}\n```') == '{"a":1}'
    assert extract_json('Sure! {"a":1} hope that helps') == '{"a":1}'
    llm = StructuredLLM(ScriptedProvider([f"```json\n{OK}\n```"]))
    assert llm.complete_structured(MSGS, Out, model="m").parsed.kind == "plan"


def test_repair_loop_then_success() -> None:
    provider = ScriptedProvider(["not json", '{"kind":"bogus","reason":"r"}', OK])
    result = StructuredLLM(provider).complete_structured(MSGS, Out, model="m")
    assert result.attempts == 3
    assert result.usage.input_tokens == 30
    last_call = provider.calls[-1]
    assert last_call[-2].role == "assistant"
    assert "invalid" in last_call[-1].content


def test_fails_after_max_repairs() -> None:
    provider = ScriptedProvider(["x", "y", "z"])
    with pytest.raises(SchemaValidationFailure) as info:
        StructuredLLM(provider).complete_structured(MSGS, Out, model="m")
    assert info.value.attempts == 3
    assert info.value.last_text == "z"


def test_cache_hit_works_offline(tmp_path: Path) -> None:
    cache = DiskCache(tmp_path / "c.jsonl")
    first = StructuredLLM(ScriptedProvider([OK]), cache).complete_structured(MSGS, Out, model="m")
    assert first.cache_hit is False

    offline = ScriptedProvider([])  # raises if it is ever called
    second = StructuredLLM(offline, DiskCache(tmp_path / "c.jsonl"))
    result = second.complete_structured(MSGS, Out, model="m")
    assert result.cache_hit is True
    assert result.parsed == first.parsed
    assert offline.calls == []


def test_provider_name_is_part_of_the_cache_key(tmp_path: Path) -> None:
    cache = DiskCache(tmp_path / "c.jsonl")
    StructuredLLM(ScriptedProvider([OK]), cache).complete_structured(MSGS, Out, model="m")
    other = StructuredLLM(CallableProvider(lambda _: OK), cache)
    assert other.complete_structured(MSGS, Out, model="m").cache_hit is False


def test_kill_switch_blocks_miss_but_allows_hit(tmp_path: Path) -> None:
    cache = DiskCache(tmp_path / "c.jsonl")
    StructuredLLM(ScriptedProvider([OK]), cache).complete_structured(MSGS, Out, model="m")
    killed = StructuredLLM(ScriptedProvider([]), cache, kill_switch=True)
    assert killed.complete_structured(MSGS, Out, model="m").cache_hit is True
    other = [Message(role="user", content="different")]
    with pytest.raises(LLMDisabled):
        killed.complete_structured(other, Out, model="m")


def test_provider_receives_schema_and_params() -> None:
    seen: dict[str, Any] = {}

    class Spy:
        name = "spy"

        def generate(
            self,
            messages: Sequence[Message],
            *,
            model: str,
            temperature: float,
            seed: int | None,
            json_schema: dict[str, Any] | None,
        ) -> RawResponse:
            seen.update(model=model, temperature=temperature, seed=seed, schema=json_schema)
            return RawResponse(text=OK, model_id=model, latency_ms=1.0)

    StructuredLLM(Spy()).complete_structured(MSGS, Out, model="m", seed=7)
    assert seen["seed"] == 7
    assert seen["schema"]["properties"]["kind"]["enum"] == ["plan", "clarify", "refuse"]
