from abc import ABC, abstractmethod
from pathlib import Path

from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.ollama import OllamaProvider

from ..models.agent import AgentConfig

agent_config = AgentConfig()

class AgentGenerator(ABC):
    """
    An abstract base class for creating agents that interact with different AI models.

    Methods
    -------
    get_model() -> Union[AnthropicModel, OpenAIChatModel]
        Static method to retrieve the appropriate model based on the agent configuration.
    generate_agent(prompt_path: Path, **pydantic_agent_kwargs)
        Abstract method to be implemented by subclasses for generating agents.
    """

    @staticmethod
    def get_model():
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
        match agent_config.provider:
            case "anthropic":
                provider = AnthropicProvider(
                    api_key=agent_config.api_key.get_secret_value() if agent_config.api_key else None,
                    base_url=agent_config.provider_url
                )
                return AnthropicModel(
                    model_name=agent_config.model_name,
                    provider=provider,
                )
            case "ollama":

                provider = OllamaProvider(
                    base_url=agent_config.provider_url
                )
                return OpenAIChatModel(
                    model_name=agent_config.model_name,
                    provider=provider,
                )
            case _:
                raise ValueError(f"Unsupported provider: {agent_config.provider}")

    @abstractmethod
    def generate_agent(self, prompt_path: Path, **pydantic_agent_kwargs):
        """
        Generate an agent using the provided prompt file and additional keyword arguments.

        Parameters
        ----------
        prompt_path : Path
            The file path to the prompt used for generating the agent.
        **pydantic_agent_kwargs : dict
            Additional keyword arguments for configuring the agent.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """
        pass
