from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.ollama import OllamaProvider

from ..models.agent import AgentConfig
from ..models.agent_models import AuthorInfo
from .prompts import AUTHOR_INFO_PROMPT, BOOK_SUMMARY_PROMPT

_agent_config = AgentConfig()

def _get_model():
    """
    Retrieve the appropriate model based on the agent configuration.

    Returns
    -------
    Union[AnthropicModel, OpenAIChatModel]
        The model instance corresponding to the configured provider.

    Raises
    ------
    ValueError
        If the provider specified in the configuration is unsupported.
    """
    match _agent_config.provider:
        case "anthropic":
            provider = AnthropicProvider(
                api_key=_agent_config.api_key.get_secret_value()
                if _agent_config.api_key
                else None,
            )
            return AnthropicModel(
                model_name=_agent_config.model_name,
                provider=provider,
            )
        case "ollama":
            provider = OllamaProvider(base_url=_agent_config.provider_url)
            return OpenAIChatModel(
                model_name=_agent_config.model_name,
                provider=provider,
            )
        case _:
            raise ValueError(f"Unsupported provider: {_agent_config.provider}")

_model = _get_model()

author_info_agent: Agent[None, AuthorInfo] = Agent(
    model=_get_model(),
    tools=[duckduckgo_search_tool()],
    system_prompt=AUTHOR_INFO_PROMPT,
    output_type=AuthorInfo,
)

book_summary_agent: Agent[None, str] = Agent(
    model=_model,
    tools=[duckduckgo_search_tool()],
    system_prompt=BOOK_SUMMARY_PROMPT,
)
