from abc import ABC, abstractmethod

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openai import OpenAIProvider


class AgentBuilder(ABC):
    """Template agent for the pydantic_ai Agent class. This is not meant to be used directly, but rather to be subclassed for specific llm providers."""

    def __init__(
        self, model_name: str, api_key: str | None = None, base_url: str | None = None, provider_type: str | None = None
    ):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.provider_type: str = provider_type
        self.provider = self._set_provider()
        self.model = self._set_model()

    @abstractmethod
    def _set_provider(self):
        pass

    @abstractmethod
    def _set_model(self):
        pass

    def build_agent(
        self,
        system_prompt: str,
        tools: list | None = None,
        output_type: type | None = None,
    ) -> Agent:
        return Agent(
            model=self.model,
            tools=tools or [],
            system_prompt=system_prompt,
            output_type=output_type,
        )


class AnthropicAgentBuilder(AgentBuilder):
    def _set_provider(self):
        return AnthropicProvider(
            api_key=self.api_key,
        )

    def _set_model(self):
        return AnthropicModel(
            model_name=self.model_name,
            provider=self.provider,
        )


class OllamaAgentBuilder(AgentBuilder):
    def _set_provider(self):
        return OllamaProvider(base_url=self.base_url)

    def _set_model(self):
        match self.provider_type:
            case "openai":
                return OpenAIChatModel(
                    model_name=self.model_name,
                    provider=self.provider,
                )
            case "gemini":
                return GeminiModel(
                    model_name=self.model_name,
                    provider=self.provider,
                )
            case "anthropic":
                return AnthropicModel(
                    model_name=self.model_name,
                    provider=self.provider,
                )
            case _:
                raise ValueError(f"Unsupported provider type: {self.provider_type}")


class OpenAIAgentBuilder(AgentBuilder):
    def _set_provider(self):
        return OpenAIProvider(api_key=self.api_key)

    def _set_model(self):
        return OpenAIChatModel(
            model_name=self.model_name,
            provider=self.provider,
        )

class GeminiAgentBuilder(AgentBuilder):
    def _set_provider(self):
        return GoogleProvider(api_key=self.api_key)

    def _set_model(self):
        return GeminiModel(
            model_name=self.model_name,
            provider=self.provider,
        )
    
