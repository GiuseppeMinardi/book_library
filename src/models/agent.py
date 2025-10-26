from enum import Enum
from typing import Literal, Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AvaiableProviders(str, Enum):
    """Avaiable AI model providers."""

    openai = "openai"
    ollama = "ollama"
    anthropic = "anthropic"
    gemini = "gemini"


class AgentConfig(BaseSettings):
    """Configuration settings for the AI agent."""

    # Provide sensible defaults so the application can be imported in dev
    # environments where env vars may not be set. These can still be
    # overridden via environment variables (aliases shown).
    model_name: str = Field(
        "claude-instant",
        alias="LLM_MODEL_NAME",
        description="Name of the AI model to be used by the agent.",
    )

    # Make provider_url optional and default to a common local Ollama URL.
    provider_url: Optional[str] = Field(
        "http://localhost:11434",
        alias="LLM_PROVIDER_URL",
        description="Base URL of the AI model provider.",
    )

    api_key: Optional[SecretStr] = Field(
        None,
        alias="LLM_API_KEY",
        description="API key for accessing the AI model provider.",
    )

    provider: Literal["openai", "ollama", "gemini", "anthropic"] = Field(
        default="ollama",
        alias="LLM_PROVIDER",
        description="The AI model provider to be used.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )