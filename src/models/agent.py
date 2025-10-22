from enum import Enum
from typing import Literal, Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AvaiableProviders(str, Enum):
    """Avaiable AI model providers."""



class AgentConfig(BaseSettings):
    """Configuration settings for the AI agent."""

    model_name: str = Field(
        ...,
        alias="LLM_MODEL_NAME",
        description="Name of the AI model to be used by the agent."
    )
    provider_url: str = Field(
        ...,
        alias="LLM_PROVIDER_URL",
        description="Base URL of the AI model provider."
    )
    api_key: Optional[SecretStr] = Field(
        ...,
        alias="LLM_API_KEY",
        description="API key for accessing the AI model provider."
    )

    provider: Literal["openai", "ollama", "gemini", "anthropic",] = Field(
        default="ollama",
        alias="LLM_PROVIDER",
        description="The AI model provider to be used."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )