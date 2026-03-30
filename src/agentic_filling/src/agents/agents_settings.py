from typing import Literal

from pydantic import AnyUrl, Field, SecretStr
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    model_name: str = Field(default=..., alias="MODEL_NAME")
    model_family: Literal["anthropic", "ollama", "openai", "gemini"] = Field(default="openai", alias="MODEL_FAMILY")
    api_key: SecretStr | None = Field(None, alias="MODEL_API_KEY")
    provider_url: AnyUrl | None = Field(None, alias="MODEL_PROVIDER_URL")
    provider_type: Literal["anthropic", "ollama", "openai", "gemini"] = Field(
        default="ollama", alias="MODEL_PROVIDER_TYPE"
    )
