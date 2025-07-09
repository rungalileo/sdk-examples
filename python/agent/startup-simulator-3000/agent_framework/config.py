from functools import lru_cache
import os
from typing import Optional, Any, Dict, List
from dotenv import load_dotenv
from dataclasses import dataclass, field
from .models import VerbosityLevel
from .llm.models import LLMConfig


class EnvironmentError(Exception):
    """Raised when required environment variables are missing"""

    pass


@dataclass
class AgentConfiguration:
    """Configuration for the agent framework"""

    llm_config: LLMConfig = field(
        default_factory=lambda: LLMConfig(model="gpt-4", temperature=0.1)
    )
    api_keys: Dict[str, str] = field(default_factory=dict)
    verbosity: VerbosityLevel = field(default=VerbosityLevel.LOW)
    metadata: Dict[str, Any] = field(default_factory=dict)
    enable_logging: bool = field(default=True)
    enable_tool_selection: bool = field(default=True)

    @staticmethod
    def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get an environment variable with an optional default"""
        return os.getenv(key, default)

    @classmethod
    def from_env(
        cls, required_keys: List[str], optional_keys: Optional[Dict[str, str]] = None
    ) -> "AgentConfiguration":
        """Create configuration from environment variables

        Args:
            required_keys: OPENAI_API_KEY, GALILEO_API_KEY, GALILEO_CONSOLE_URL
            optional_keys: Dict of optional key names to their default values
        """
        load_dotenv()

        # Load required API keys
        api_keys = {}
        for key_name in required_keys:
            env_value = os.getenv(f"{key_name.upper()}_API_KEY")
            if not env_value:
                raise EnvironmentError(
                    f"{key_name.upper()}_API_KEY environment variable is required. "
                    "Please set it in your .env file"
                )
            api_keys[key_name] = env_value

        # Load optional API keys
        if optional_keys:
            for key_name, default in optional_keys.items():
                env_value = os.getenv(f"{key_name.upper()}_API_KEY", default)
                if env_value:
                    api_keys[key_name] = env_value

        # Create configuration
        return cls(
            llm_config=LLMConfig(
                model=os.getenv("LLM_MODEL", "gpt-4"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            ),
            api_keys=api_keys,
            verbosity=VerbosityLevel(os.getenv("VERBOSITY", "low")),
            metadata={"env": os.getenv("ENVIRONMENT", "development")},
            enable_logging=os.getenv("ENABLE_LOGGING", "true").lower() == "true",
            enable_tool_selection=os.getenv("ENABLE_TOOL_SELECTION", "true").lower()
            == "true",
        )

    def with_overrides(self, **overrides) -> "AgentConfiguration":
        """Create new config with overridden values"""
        config_dict = self.__dict__.copy()
        config_dict.update(overrides)
        return AgentConfiguration(**config_dict)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AgentConfiguration":
        """Create configuration from dictionary - mainly used for testing"""
        if "api_keys" not in config_dict or "openai" not in config_dict["api_keys"]:
            raise ValueError("OpenAI API key must be provided in api_keys dictionary")

        llm_config = LLMConfig(
            model=config_dict.get("llm_model", "gpt-4"),
            temperature=config_dict.get("llm_temperature", 0.1),
            **config_dict.get("llm_settings", {}),
        )

        return cls(
            llm_config=llm_config,
            api_keys=config_dict["api_keys"],
            verbosity=VerbosityLevel(config_dict.get("verbosity", "low")),
            metadata=config_dict.get("metadata", {}),
            enable_logging=config_dict.get("enable_logging", True),
            enable_tool_selection=config_dict.get("enable_tool_selection", True),
        )
