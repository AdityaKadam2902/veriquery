import pytest
from pydantic_settings import SettingsConfigDict

from veriquery.common.config import Settings


class IsolatedSettings(Settings):
    """Same settings, but never reads a developer's real .env file."""

    model_config = SettingsConfigDict(env_file=None, extra="ignore", populate_by_name=True)


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "abc123")
    monkeypatch.setenv("VERIQUERY_LLM_KILL_SWITCH", "true")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    settings = IsolatedSettings()
    assert settings.gemini_api_key is not None
    assert settings.gemini_api_key.get_secret_value() == "abc123"
    assert settings.llm_kill_switch is True
    assert settings.groq_api_key is None
    assert settings.ollama_host == "http://localhost:11434"


def test_secrets_never_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "abc123")
    assert "abc123" not in repr(IsolatedSettings())
