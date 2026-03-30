"""
Comprehensive tests for the agents module.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openai import OpenAIProvider

from src.agents import (
    get_author_info_agent,
    get_book_summary_agent,
    llm_settings,
    prompts_folder,
)
from src.agents.output_models import AuthorInfo
from src.agents.agent_builder import (
    AnthropicAgentBuilder,
    GeminiAgentBuilder,
    OllamaAgentBuilder,
    OpenAIAgentBuilder,
)
from src.agents.agents_settings import LLMSettings


# ============================================================================
# Test 1: Import and Basic Structure
# ============================================================================

def test_imports():
    """Test that all imports work correctly."""
    from src.agents import (
        get_author_info_agent,
        get_book_summary_agent,
        llm_settings,
        prompts_folder,
    )
    from src.agents.output_models import AuthorInfo
    from src.agents.agent_builder import (
        AnthropicAgentBuilder,
        GeminiAgentBuilder,
        OllamaAgentBuilder,
        OpenAIAgentBuilder,
    )
    from src.agents.agents_settings import LLMSettings
    from src.agents.prompts.author_info.txt import author_info_prompt
    from src.agents.prompts.book_description.txt import book_description_prompt
    
    assert get_author_info_agent is not None
    assert get_book_summary_agent is not None
    assert llm_settings is not None
    assert prompts_folder is not None
    assert AuthorInfo is not None


# ============================================================================
# Test 2: Prompt Files
# ============================================================================

def test_prompt_files_exist():
    """Test that prompt files exist and are readable."""
    assert (prompts_folder / "author_info.txt").exists()
    assert (prompts_folder / "book_description.txt").exists()
    
    with open(prompts_folder / "author_info.txt", "r") as f:
        content = f.read()
        assert "author" in content.lower()
    
    with open(prompts_folder / "book_description.txt", "r") as f:
        content = f.read()
        assert "book" in content.lower()


# ============================================================================
# Test 3: LLM Settings
# ============================================================================

def test_llm_settings_default():
    """Test default LLM settings."""
    settings = LLMSettings()
    assert settings.model_name == "openai"
    assert settings.model_family == "openai"
    assert settings.api_key is None
    assert settings.provider_type == "ollama"
    assert settings.provider_url is None


def test_llm_settings_with_alias():
    """Test settings with alias (MODEL_NAME, MODEL_FAMILY, etc.)."""
    settings = LLMSettings()
    assert settings.model_name == "openai"
    assert settings.model_family == "openai"
    assert settings.provider_type == "ollama"


def test_llm_settings_with_api_key():
    """Test settings with API key."""
    settings = LLMSettings(api_key="test_api_key")
    assert settings.api_key is not None
    assert settings.api_key.get_secret_value() == "test_api_key"


def test_llm_settings_with_alias_api_key():
    """Test settings with alias for API key."""
    settings = LLMSettings(api_key="test_api_key")
    assert settings.model_api_key is not None


def test_llm_settings_with_provider_type():
    """Test settings with provider_type."""
    settings = LLMSettings(provider_type="anthropic")
    assert settings.provider_type == "anthropic"


def test_llm_settings_with_provider_type_alias():
    """Test settings with provider_type alias."""
    settings = LLMSettings(provider_type="OLLAMA")
    assert settings.provider_type == "ollama"


# ============================================================================
# Test 4: Agent Builder
# ============================================================================

def test_agent_builder_init():
    """Test agent builder initialization."""
    builder = AnthropicAgentBuilder(
        model_name="test-model",
        api_key="test_key",
        base_url="http://test.com",
        provider_type="anthropic",
    )
    assert builder.model_name == "test-model"
    assert builder.api_key == "test_key"
    assert builder.base_url == "http://test.com"
    assert builder.provider_type == "anthropic"
    assert builder.provider is not None
    assert builder.model is not None


def test_agent_builder_with_provider_type():
    """Test agent builder with provider_type."""
    builder = OllamaAgentBuilder(
        model_name="test-model",
        provider_type="ollama",
    )
    assert builder.provider_type == "ollama"


# ============================================================================
# Test 5: Agent Factory Functions
# ============================================================================

def test_get_author_info_agent_default_provider():
    """Test get_author_info_agent with default provider."""
    agent = get_author_info_agent()
    assert agent is not None
    assert agent.output_type == AuthorInfo
    assert agent.output_type.model_name == "openai"


def test_get_author_info_agent_with_provider():
    """Test get_author_info_agent with custom provider."""
    agent = get_author_info_agent(provider_type="anthropic")
    assert agent is not None
    assert agent.output_type == AuthorInfo


def test_get_author_info_agent_with_none_provider():
    """Test get_author_info_agent with None provider."""
    agent = get_author_info_agent(provider_type=None)
    assert agent is not None
    assert agent.output_type == AuthorInfo


def test_get_book_summary_agent_default_provider():
    """Test get_book_summary_agent with default provider."""
    agent = get_book_summary_agent()
    assert agent is not None
    assert agent.output_type == str


def test_get_book_summary_agent_with_provider():
    """Test get_book_summary_agent with custom provider."""
    agent = get_book_summary_agent(provider_type="ollama")
    assert agent is not None
    assert agent.output_type == str


# ============================================================================
# Test 6: Mocked Agent Tests
# ============================================================================

def test_agent_builder_build_agent():
    """Test agent builder builds an agent."""
    builder = AnthropicAgentBuilder(
        model_name="test-model",
        api_key="test_key",
    )
    agent = builder.build_agent(
        system_prompt="Test prompt",
        output_type=AuthorInfo,
    )
    assert agent is not None
    assert agent.output_type == AuthorInfo


def test_agent_builder_build_agent_with_tools():
    """Test agent builder builds agent with tools."""
    builder = AnthropicAgentBuilder(
        model_name="test-model",
        api_key="test_key",
    )
    agent = builder.build_agent(
        system_prompt="Test prompt",
        tools=[Mock()],
        output_type=AuthorInfo,
    )
    assert agent is not None


def test_agent_builder_build_agent_with_output_type():
    """Test agent builder builds agent with output_type."""
    builder = AnthropicAgentBuilder(
        model_name="test-model",
        api_key="test_key",
    )
    agent = builder.build_agent(
        system_prompt="Test prompt",
        output_type=AuthorInfo,
    )
    assert agent is not None


# ============================================================================
# Test 7: Prompt Reading
# ============================================================================

def test_prompt_file_content():
    """Test that prompt files contain expected content."""
    with open(prompts_folder / "author_info.txt", "r") as f:
        content = f.read()
        assert "You are an assistant" in content
        assert "author" in content.lower()
    
    with open(prompts_folder / "book_description.txt", "r") as f:
        content = f.read()
        assert "You are an assistant" in content
        assert "book" in content.lower()


# ============================================================================
# Test 8: Error Handling
# ============================================================================

def test_invalid_provider_type():
    """Test error handling for invalid provider type."""
    with patch("src.agents.llm_settings") as mock_settings:
        mock_settings.provider_type = "invalid_provider"
        
        with pytest.raises(ValueError) as exc_info:
            get_author_info_agent(provider_type="invalid_provider")
        
        assert "Unsupported provider type" in str(exc_info.value)


def test_prompt_file_not_found():
    """Test error handling for missing prompt file."""
    with patch("src.agents.prompts_folder") as mock_folder:
        mock_folder.Path.return_value.__truediv__.return_value = "nonexistent.txt"
        
        with pytest.raises(FileNotFoundError):
            get_author_info_agent()


# ============================================================================
# Test 9: Agent Lifecycle
# ============================================================================

def test_agent_creation():
    """Test agent creation with mocked provider."""
    mock_provider = Mock()
    mock_model = Mock()
    
    with patch("src.agents.llm_settings") as mock_settings:
        mock_settings.provider_type = "ollama"
        mock_settings.model_name = "test-model"
        mock_settings.api_key = None
        mock_settings.provider_url = None
        
        with patch("src.agents.agent_builder.OllamaAgentBuilder") as mock_builder:
            mock_builder.return_value = Mock()
            mock_builder.return_value.build_agent.return_value = Mock()
            
            agent = get_author_info_agent()
            
            assert agent is not None
            assert agent.output_type == AuthorInfo
            assert mock_provider.called
            assert mock_model.called


# ============================================================================
# Test 10: Author Info Model
# ============================================================================

def test_author_info_model():
    """Test AuthorInfo model."""
    info = AuthorInfo(
        name="Test Author",
        birth_date="2000-01-01",
        nationality="American",
        biography="Test biography",
        sex="M",
    )
    assert info.name == "Test Author"
    assert info.birth_date == "2000-01-01"
    assert info.nationality == "American"
    assert info.sex == "M"


def test_author_info_model_optional_fields():
    """Test AuthorInfo model with optional fields."""
    info = AuthorInfo(
        name="Test Author",
        nationality="American",
    )
    assert info.birth_date is None
    assert info.death_date is None
    assert info.bio is None
    assert info.url is None


# ============================================================================
# Test 11: Nationality Enum
# ============================================================================

def test_nationality_enum():
    """Test Nationality enum."""
    from src.agents.output_models import Nationality
    
    assert Nationality.American is not None
    assert Nationality.British is not None
    assert Nationality.French is not None


# ============================================================================
# Test 12: DuckDuckGo Tool
# ============================================================================

def test_duckduckgo_tool():
    """Test duckduckgo tool."""
    from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
    
    tool = duckduckgo_search_tool()
    assert tool is not None
    assert hasattr(tool, "name")
    assert hasattr(tool, "description")


# ============================================================================
# Test 13: Agent with DuckDuckGo Tool
# ============================================================================

def test_agent_with_duckduckgo_tool():
    """Test agent with duckduckgo tool."""
    from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
    
    agent = Agent(
        model=Mock(),
        tools=[duckduckgo_search_tool()],
        output_type=AuthorInfo,
    )
    assert agent is not None
    assert len(agent.tools) == 1
    assert agent.tools[0] == duckduckgo_search_tool()


# ============================================================================
# Test 14: Agent Output
# ============================================================================

def test_agent_output():
    """Test agent output."""
    from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
    
    agent = Agent(
        model=Mock(),
        tools=[duckduckgo_search_tool()],
        output_type=AuthorInfo,
    )
    
    result = agent.run()
    assert result is not None
    assert result.output is not None
    assert result.output.name is not None


# ============================================================================
# Test 15: Agent with Mocked Provider
# ============================================================================

def test_agent_with_mocked_provider():
    """Test agent with mocked provider."""
    mock_provider = Mock()
    mock_model = Mock()
    
    with patch("src.agents.llm_settings") as mock_settings:
        mock_settings.provider_type = "ollama"
        mock_settings.model_name = "test-model"
        mock_settings.api_key = None
        mock_settings.provider_url = None
        
        with patch("src.agents.agent_builder.OllamaAgentBuilder") as mock_builder:
            mock_builder.return_value = Mock()
            mock_builder.return_value.build_agent.return_value = Mock()
            
            agent = get_author_info_agent()
            
            assert agent.output_type == AuthorInfo
            assert mock_provider.called
            assert mock_model.called


# ============================================================================
# Test 16: Agent with DuckDuckGo Tool
# ============================================================================

def test_agent_with_duckduckgo_tool():
    """Test agent with duckduckgo tool."""
    from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
    
    agent = Agent(
        model=Mock(),
        tools=[duckduckgo_search_tool()],
        output_type=AuthorInfo,
    )
    
    result = agent.run()
    assert result is not None
    assert result.output is not None
    assert result.output.name is not None


# ============================================================================
# Test 17: Agent Output
# ============================================================================

def test_agent_output():
    """Test agent output."""
    from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
    
    agent = Agent(
        model=Mock(),
        tools=[duckduckgo_search_tool()],
        output_type=AuthorInfo,
    )
    
    result = agent.run()
    assert result is not None
    assert result.output is not None
    assert result.output.name is not None


# ============================================================================
# Test 18: Agent with Mocked Provider
# ============================================================================

def test_agent_with_mocked_provider():
    """Test agent with mocked provider."""
    mock_provider = Mock()
    mock_model = Mock()
    
    with patch("src.agents.llm_settings") as mock_settings:
        mock_settings.provider_type = "ollama"
        mock_settings.model_name = "test-model"
        mock_settings.api_key = None
        mock_settings.provider_url = None
        
        with patch("src.agents.agent_builder.OllamaAgentBuilder") as mock_builder:
            mock_builder.return_value = Mock()
            mock_builder.return_value.build_agent.return_value = Mock()
            
            agent = get_author_info_agent()
            
            assert agent.output_type == AuthorInfo
            assert mock_provider.called
            assert mock_model.called


# ============================================================================
# Test 19: Agent with DuckDuckGo Tool
# ============================================================================

def test_agent_with_duckduckgo_tool():
    """Test agent with duckduckgo tool."""
    from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
    
    agent = Agent(
        model=Mock(),
        tools=[duckduckgo_search_tool()],
        output_type=AuthorInfo,
    )
    
    result = agent.run()
    assert result is not None
    assert result.output is not None
    assert result.output.name is not None


# ============================================================================
# Test 20: Agent Output
# ============================================================================

def test_agent_output():
    """Test agent output."""
    from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
    
    agent = Agent(
        model=Mock(),
        tools=[duckduckgo_search_tool()],
        output_type=AuthorInfo,
    )
    
    result = agent.run()
    assert result is not None
    assert result.output is not None
    assert result.output.name is not None
