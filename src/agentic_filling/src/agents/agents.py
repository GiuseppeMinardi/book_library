from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

from .agent_builder import (
    AnthropicAgentBuilder,
    GeminiAgentBuilder,
    OllamaAgentBuilder,
    OpenAIAgentBuilder,
)
from .agents_settings import LLMSettings
from .output_models import AuthorInfo

llm_settings = LLMSettings()
prompts_folder = Path(__file__).parent / "prompts"

match llm_settings.provider_type:
    case "anthropic":
        agent_builder = AnthropicAgentBuilder(
            model_name=llm_settings.model_name,
            api_key=llm_settings.api_key.get_secret_value()
            if llm_settings.api_key
            else None,
        )
    case "ollama":
        agent_builder = OllamaAgentBuilder(
            model_name=llm_settings.model_name,
            base_url=llm_settings.provider_url.geturl()
            if llm_settings.provider_url
            else None,
            provider_type=llm_settings.provider_type,
        )
    case "openai":
        agent_builder = OpenAIAgentBuilder(
            model_name=llm_settings.model_name,
            api_key=llm_settings.api_key.get_secret_value()
            if llm_settings.api_key
            else None,
        )
    case "gemini":
        agent_builder = GeminiAgentBuilder(
            model_name=llm_settings.model_name,
            api_key=llm_settings.api_key.get_secret_value()
            if llm_settings.api_key
            else None,
        )
    case _:
        raise ValueError(f"Unsupported provider type: {llm_settings.provider_type}")

def get_author_info_agent(provider_type: str | None = None) -> Agent[None, AuthorInfo]:
    if provider_type is None:
        provider_type = llm_settings.provider_type
    prompt = prompts_folder / "author_info.txt"

    with prompt.open() as f:
        author_info_prompt = f.read()
    
    return agent_builder.build_agent(
        system_prompt=author_info_prompt,
        provider_type=provider_type,
        tools=[duckduckgo_search_tool()],
        output_type=AuthorInfo,
    )

def get_book_summary_agent(provider_type: str | None = None) -> Agent[None, str]:
    if provider_type is None:
        provider_type = llm_settings.provider_type
    prompt = prompts_folder / "book_description.txt"

    with prompt.open() as f:
        book_summary_prompt = f.read()
    return agent_builder.build_agent(
        system_prompt=book_summary_prompt,
        provider_type=provider_type,
        tools=[duckduckgo_search_tool()],
        output_type=str,
    )