from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class OllamaEmbeddingSettings(BaseSettings):
    model_name: str = Field(..., alias="OLLAMA_EMBEDDING_MODEL_NAME", description="Name of the Ollama embedding model to use.")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )