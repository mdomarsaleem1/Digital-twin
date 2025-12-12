"""Base classes for LLM model adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class ModelProvider(str, Enum):
    """Supported model providers."""
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENAI = "openai"


@dataclass
class ModelConfig:
    """Configuration for an LLM model."""
    provider: ModelProvider
    model: str
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 1.0
    api_key: str | None = None
    extra_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Standardized response from any LLM."""
    content: str
    model: str
    provider: str
    usage: dict[str, int]
    latency_ms: float
    raw_response: Any = None

    @property
    def input_tokens(self) -> int:
        return self.usage.get("input_tokens", 0)

    @property
    def output_tokens(self) -> int:
        return self.usage.get("output_tokens", 0)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class BaseLLM(ABC):
    """Abstract base class for LLM adapters."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self._client: Any = None

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            prompt: The user prompt/message
            system_prompt: Optional system prompt for context
            **kwargs: Additional model-specific parameters

        Returns:
            LLMResponse with the generated content
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Generate a structured response matching the schema.

        Args:
            prompt: The user prompt/message
            schema: JSON schema for the expected response
            system_prompt: Optional system prompt for context
            **kwargs: Additional model-specific parameters

        Returns:
            Parsed response matching the schema
        """
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the client connection."""
        pass

    @property
    def is_initialized(self) -> bool:
        """Check if the client is initialized."""
        return self._client is not None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.config.model}, provider={self.config.provider})"
