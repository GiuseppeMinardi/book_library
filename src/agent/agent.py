from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.ollama import OllamaProvider

from ..models.agent import ClaudeAgentConfig, OllamaAgentConfig
from ..models.agent_models import AuthorInfo
from .prompts import AUTHOR_INFO_PROMPT, BOOK_SUMMARY_PROMPT

_ollama_config = OllamaAgentConfig()
_claude_config = ClaudeAgentConfig()

def _get_model(provider: str | None = None):
    match provider:
        case "anthropic":
            pydantic_provider = AnthropicProvider(
                api_key=_claude_config.api_key.get_secret_value()
                if _claude_config.api_key
                else None,
            )
            return AnthropicModel(
                model_name=_claude_config.model_name,
                provider=pydantic_provider,
            )
        case "ollama":
            pydantic_provider = OllamaProvider(base_url=_ollama_config.provider_url)
            return OpenAIChatModel(
                model_name=_ollama_config.model_name,
                provider=pydantic_provider,
            )
        case "openai":
            raise NotImplementedError("OpenAI provider not implemented yet.")
        case "gemini":
            raise NotImplementedError("Gemini provider not implemented yet.")
        case _:
            raise ValueError(f"Unsupported provider: {provider}")

def get_author_info_agent(provider: str | None = None) -> Agent[None, AuthorInfo]:
    return Agent(
        model=_get_model(provider),
        tools=[duckduckgo_search_tool()],
        system_prompt=AUTHOR_INFO_PROMPT,
        output_type=AuthorInfo,
    )


def get_book_summary_agent(provider: str | None = None) -> Agent[None, str]:
    return Agent(
        model=_get_model(provider),
        tools=[duckduckgo_search_tool()],
        system_prompt=BOOK_SUMMARY_PROMPT,
    )


author_info_agent: Agent[None, AuthorInfo] = get_author_info_agent(provider="anthropic")

book_summary_agent: Agent[None, str] = get_book_summary_agent(provider="anthropic")
