"""Settings: secrets from environment or .env, never committed (invariant I7)."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    gemini_api_key: SecretStr | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    groq_api_key: SecretStr | None = Field(default=None, validation_alias="GROQ_API_KEY")
    hmac_key: SecretStr | None = Field(default=None, validation_alias="VERIQUERY_HMAC_KEY")
    llm_kill_switch: bool = Field(default=False, validation_alias="VERIQUERY_LLM_KILL_SWITCH")
    ollama_host: str = Field(
        default="http://localhost:11434", validation_alias="VERIQUERY_OLLAMA_HOST"
    )
    cache_dir: Path = Field(default=Path(".llm_cache"), validation_alias="VERIQUERY_CACHE_DIR")
