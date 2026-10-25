"""Local Ollama adapter. Uses native JSON-schema constrained output via `format`
(Ollama 0.5 or newer; verification log V-13)."""

from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any

import httpx

from veriquery.agent.llm.base import schema_instruction
from veriquery.agent.llm.types import Message, ProviderError, RawResponse, Usage


class OllamaProvider:
    name = "ollama"

    def __init__(
        self,
        host: str = "http://localhost:11434",
        *,
        timeout_s: float = 600.0,
        client: httpx.Client | None = None,
    ) -> None:
        self._host = host.rstrip("/")
        self._client = client or httpx.Client(timeout=timeout_s)

    def generate(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        seed: int | None,
        json_schema: dict[str, Any] | None,
    ) -> RawResponse:
        msgs = [m.model_dump() for m in messages]
        instruction = schema_instruction(json_schema)
        if instruction:
            msgs.insert(0, {"role": "system", "content": instruction})
        options: dict[str, Any] = {"temperature": temperature}
        if seed is not None:
            options["seed"] = seed
        payload: dict[str, Any] = {
            "model": model,
            "messages": msgs,
            "stream": False,
            "options": options,
        }
        if json_schema is not None:
            payload["format"] = json_schema
        started = time.perf_counter()
        try:
            response = self._client.post(f"{self._host}/api/chat", json=payload)
        except httpx.ConnectError as exc:
            raise ProviderError(
                self.name, 0, f"cannot reach Ollama at {self._host}: {exc}"
            ) from exc
        latency_ms = (time.perf_counter() - started) * 1000.0
        if response.status_code >= 400:
            raise ProviderError(self.name, response.status_code, response.text[:500])
        data = response.json()
        return RawResponse(
            text=str((data.get("message") or {}).get("content", "")),
            usage=Usage(
                input_tokens=int(data.get("prompt_eval_count", 0)),
                output_tokens=int(data.get("eval_count", 0)),
            ),
            model_id=str(data.get("model") or model),
            latency_ms=latency_ms,
            transmitted=dict(options),
        )
