from pathlib import Path

from veriquery.agent.llm import DiskCache, Message, RawResponse, Usage
from veriquery.agent.llm.cache import build_request_record, cache_key


def _request(text: str = "hi") -> dict[str, object]:
    return build_request_record(
        provider="stub",
        model="m",
        messages=[Message(role="user", content=text)],
        schema_json={"type": "object"},
        temperature=0.0,
        seed=None,
    )


def _response(text: str = "{}") -> RawResponse:
    return RawResponse(
        text=text, usage=Usage(input_tokens=3, output_tokens=2), model_id="m", latency_ms=5.0
    )


def test_roundtrip_and_persistence(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    cache = DiskCache(path)
    req = _request()
    key = cache.put(req, _response("{}"))
    assert key == cache_key(req)
    assert DiskCache(path).get(key) == _response("{}")
    assert len(DiskCache(path)) == 1


def test_key_changes_with_every_field() -> None:
    base = _request("a")
    assert cache_key(base) != cache_key(_request("b"))
    changed = {**base, "temperature": 0.5}
    assert cache_key(base) != cache_key(changed)
    changed = {**base, "prompt_version": "v2"}
    assert cache_key(base) != cache_key(changed)


def test_tampered_entry_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    key = DiskCache(path).put(_request(), _response('{"a":1}'))
    path.write_text(path.read_text().replace('{\\"a\\":1}', '{\\"a\\":2}'))
    reloaded = DiskCache(path)
    assert reloaded.get(key) is None
    assert reloaded.rejected_entries == 1


def test_hmac_key_mismatch_rejects(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    key = DiskCache(path, hmac_key=b"k1").put(_request(), _response())
    assert DiskCache(path, hmac_key=b"k1").get(key) is not None
    other = DiskCache(path, hmac_key=b"k2")
    assert other.get(key) is None
    assert other.rejected_entries == 1


def test_garbage_lines_are_counted(tmp_path: Path) -> None:
    path = tmp_path / "c.jsonl"
    path.write_text("not json\n\n")
    assert DiskCache(path).rejected_entries == 1
