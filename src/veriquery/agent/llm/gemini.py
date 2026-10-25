"""Google AI Studio (Gemini API) adapter over plain REST.

Gemma models on this API have historically differed from Gemini (system instructions and JSON
mode may be rejected), so both are switchable. Which combination works for the chosen model is
established by `scripts/smoke_llm.py` (verification log V-16). Native JSON-schema enforcement is
not used here; the schema is described in the prompt and validated by the client (ADR-007).
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

import httpx
from pydantic import SecretStr

from veriquery.agent.llm.base import schema_instruction
from veriquery.agent.llm.types import Message, ProviderError, RawResponse, Usage


@dataclass(frozen=True)
class GeminiConfig:
    use_system_instruction: bool = True
    json_mode: Literal["mime", "prompt"] = "mime"  # "mime" sends responseMimeType=application/json
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    timeout_s: float = 120.0


class GeminiProvider:
    name = "gemini"

    def __init__(
        self,
        api_key: SecretStr | str,
        *,
        config: GeminiConfig | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._key = api_key if isinstance(api_key, SecretStr) else SecretStr(api_key)
        self._config = config or GeminiConfig()
        self._client = client or httpx.Client(timeout=self._config.timeout_s)

    def _build_body(
        self,
        messages: Sequence[Message],
        temperature: float,
        seed: int | None,
        json_schema: dict[str, Any] | None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        system_parts = [m.content for m in messages if m.role == "system"]
        instruction = schema_instruction(json_schema)
        if instruction:
            system_parts.append(instruction)
        system_text = "\n\n".join(system_parts)
        contents: list[dict[str, Any]] = [
            {"role": "model" if m.role == "assistant" else "user", "parts": [{"text": m.content}]}
            for m in messages
            if m.role != "system"
        ]
        body: dict[str, Any] = {}
        if system_text:
            if self._config.use_system_instruction:
                body["systemInstruction"] = {"parts": [{"text": system_text}]}
            elif contents and contents[0]["role"] == "user":
                first = contents[0]["parts"][0]["text"]
                contents[0]["parts"][0]["text"] = f"{system_text}\n\n{first}"
            else:
                contents.insert(0, {"role": "user", "parts": [{"text": system_text}]})
        body["contents"] = contents
        generation: dict[str, Any] = {"temperature": temperature}
        if seed is not None:
            generation["seed"] = seed
        if self._config.json_mode == "mime" and json_schema is not None:
            generation["responseMimeType"] = "application/json"
        body["generationConfig"] = generation
        return body, dict(generation)

    def generate(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        seed: int | None,
        json_schema: dict[str, Any] | None,
    ) -> RawResponse:
        body, transmitted = self._build_body(messages, temperature, seed, json_schema)
        url = f"{self._config.base_url}/models/{model}:generateContent"
        started = time.perf_counter()
        response = self._client.post(
            url,
            json=body,
            headers={"x-goog-api-key": self._key.get_secret_value()},
        )
        latency_ms = (time.perf_counter() - started) * 1000.0
        if response.status_code >= 400:
            raise ProviderError(self.name, response.status_code, response.text[:500])
        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            reason = data.get("promptFeedback") or data
            raise ProviderError(
                self.name, response.status_code, f"no candidates: {str(reason)[:300]}"
            )
        parts = (candidates[0].get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        meta = data.get("usageMetadata") or {}
        usage = Usage(
            input_tokens=int(meta.get("promptTokenCount", 0)),
            output_tokens=int(meta.get("candidatesTokenCount", 0))
            + int(meta.get("thoughtsTokenCount", 0)),
        )
        return RawResponse(
            text=text,
            usage=usage,
            model_id=str(data.get("modelVersion") or model),
            latency_ms=latency_ms,
            transmitted=transmitted,
        )
