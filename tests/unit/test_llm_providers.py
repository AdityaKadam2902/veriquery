import json
from typing import Any

import httpx
import pytest

from veriquery.agent.llm import Message, ProviderError
from veriquery.agent.llm.gemini import GeminiConfig, GeminiProvider
from veriquery.agent.llm.ollama import OllamaProvider

MSGS = [Message(role="system", content="SYS"), Message(role="user", content="Q")]
SCHEMA: dict[str, Any] = {"type": "object", "properties": {"a": {"type": "string"}}}
SECRET = "super-secret-key"  # noqa: S105


def _gemini(handler: Any, config: GeminiConfig | None = None) -> GeminiProvider:
    return GeminiProvider(
        SECRET, config=config, client=httpx.Client(transport=httpx.MockTransport(handler))
    )


def test_gemini_request_and_parsing() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["headers"] = dict(request.headers)
        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": "hidden", "thought": True}, {"text": '{"a":"x"}'}]
                        }
                    }
                ],
                "usageMetadata": {
                    "promptTokenCount": 12,
                    "candidatesTokenCount": 5,
                    "thoughtsTokenCount": 3,
                },
                "modelVersion": "gemma-test-001",
            },
        )

    raw = _gemini(handler).generate(
        MSGS, model="gemma-test", temperature=0.0, seed=3, json_schema=SCHEMA
    )
    assert raw.text == '{"a":"x"}'
    assert (raw.usage.input_tokens, raw.usage.output_tokens) == (12, 8)
    assert raw.model_id == "gemma-test-001"
    assert captured["headers"]["x-goog-api-key"] == SECRET
    assert SECRET not in captured["url"]
    assert captured["url"].endswith("/models/gemma-test:generateContent")
    body = captured["body"]
    assert "SYS" in body["systemInstruction"]["parts"][0]["text"]
    assert body["generationConfig"] == {
        "temperature": 0.0,
        "seed": 3,
        "responseMimeType": "application/json",
    }
    assert raw.transmitted == body["generationConfig"]


def test_gemini_without_system_instruction_and_mime() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "{}"}]}}]})

    config = GeminiConfig(use_system_instruction=False, json_mode="prompt")
    _gemini(handler, config).generate(
        MSGS, model="m", temperature=0.0, seed=None, json_schema=SCHEMA
    )
    body = captured["body"]
    assert "systemInstruction" not in body
    assert body["contents"][0]["parts"][0]["text"].startswith("SYS")
    assert "responseMimeType" not in body["generationConfig"]
    assert "seed" not in body["generationConfig"]


def test_gemini_error_does_not_leak_key() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="JSON mode is not enabled for this model")

    with pytest.raises(ProviderError) as info:
        _gemini(handler).generate(MSGS, model="m", temperature=0.0, seed=None, json_schema=None)
    assert info.value.status_code == 400
    assert SECRET not in str(info.value)


def test_gemini_no_candidates() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"promptFeedback": {"blockReason": "SAFETY"}})

    with pytest.raises(ProviderError, match="no candidates"):
        _gemini(handler).generate(MSGS, model="m", temperature=0.0, seed=None, json_schema=None)


def test_ollama_request_and_parsing() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "model": "llama3.2:3b",
                "message": {"role": "assistant", "content": '{"a":"y"}'},
                "prompt_eval_count": 20,
                "eval_count": 7,
            },
        )

    provider = OllamaProvider(client=httpx.Client(transport=httpx.MockTransport(handler)))
    raw = provider.generate(MSGS, model="llama3.2:3b", temperature=0.0, seed=1, json_schema=SCHEMA)
    assert captured["url"].endswith("/api/chat")
    assert captured["body"]["format"] == SCHEMA
    assert captured["body"]["stream"] is False
    assert captured["body"]["options"] == {"temperature": 0.0, "seed": 1}
    assert raw.text == '{"a":"y"}'
    assert (raw.usage.input_tokens, raw.usage.output_tokens) == (20, 7)


def test_ollama_unreachable_is_provider_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    provider = OllamaProvider(client=httpx.Client(transport=httpx.MockTransport(handler)))
    with pytest.raises(ProviderError, match="cannot reach Ollama"):
        provider.generate(MSGS, model="m", temperature=0.0, seed=None, json_schema=None)
