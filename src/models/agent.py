from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClaudeAgentConfig(BaseSettings):
    model_name: str = Field(
        default="claude-instant",
        alias="CLAUDE_LLM_MODEL_NAME",
        description="Name of the AI model to be used by the agent.",
    )

    api_key: Optional[SecretStr] = Field(
        default=None,
        alias="CLAUDE_LLM_API_KEY",
        description="API key for accessing the AI model provider.",
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class OllamaAgentConfig(BaseSettings):
    model_name: str = Field(
        default="qwen3:4b",
        alias="OLLAMA_LLM_MODEL_NAME",
        description="Name of the AI model to be used by the agent.",
    )

    provider_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_LLM_PROVIDER_URL",
        description="Base URL of the AI model provider.",
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )