"""Factory for creating model adapters."""

import os
from pathlib import Path
from typing import Any

import yaml

from agentic_council.models.base import BaseLLM, ModelConfig, ModelProvider
from agentic_council.models.anthropic_adapter import AnthropicAdapter
from agentic_council.models.gemini_adapter import GeminiAdapter


class ModelFactory:
    """Factory for creating and managing LLM adapters."""

    _adapters: dict[str, type[BaseLLM]] = {
        ModelProvider.ANTHROPIC: AnthropicAdapter,
        ModelProvider.GOOGLE: GeminiAdapter,
    }

    _instances: dict[str, BaseLLM] = {}

    @classmethod
    def create(
        cls,
        provider: str | ModelProvider,
        model: str,
        api_key: str | None = None,
        **kwargs: Any
    ) -> BaseLLM:
        """Create a new LLM adapter instance.

        Args:
            provider: The model provider (anthropic, google, openai)
            model: The specific model name
            api_key: API key (or use environment variable)
            **kwargs: Additional config parameters

        Returns:
            Configured LLM adapter

        Raises:
            ValueError: If provider is not supported
        """
        if isinstance(provider, str):
            provider = ModelProvider(provider.lower())

        if provider not in cls._adapters:
            raise ValueError(f"Unsupported provider: {provider}")

        # Get API key from environment if not provided
        if api_key is None:
            env_var = {
                ModelProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
                ModelProvider.GOOGLE: "GOOGLE_API_KEY",
                ModelProvider.OPENAI: "OPENAI_API_KEY",
            }.get(provider)

            if env_var:
                api_key = os.getenv(env_var)

        config = ModelConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            max_tokens=kwargs.get("max_tokens", 2048),
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 1.0),
            extra_params=kwargs,
        )

        adapter_class = cls._adapters[provider]
        return adapter_class(config)

    @classmethod
    def get_or_create(
        cls,
        role: str,
        provider: str | ModelProvider,
        model: str,
        **kwargs: Any
    ) -> BaseLLM:
        """Get an existing adapter or create a new one.

        Uses caching to avoid creating multiple adapters for the same role.

        Args:
            role: The role identifier (e.g., "orchestrator", "finance")
            provider: The model provider
            model: The model name
            **kwargs: Additional config parameters

        Returns:
            LLM adapter for the role
        """
        cache_key = f"{role}:{provider}:{model}"

        if cache_key not in cls._instances:
            cls._instances[cache_key] = cls.create(provider, model, **kwargs)

        return cls._instances[cache_key]

    @classmethod
    def from_config_file(cls, config_path: str | Path) -> dict[str, BaseLLM]:
        """Create adapters from a YAML configuration file.

        Args:
            config_path: Path to the models.yaml config file

        Returns:
            Dictionary mapping role names to LLM adapters
        """
        config_path = Path(config_path)

        with open(config_path) as f:
            config = yaml.safe_load(f)

        adapters = {}

        # Create orchestrator adapter
        if "orchestrator" in config:
            orch_config = config["orchestrator"]
            adapters["orchestrator"] = cls.create(
                provider=orch_config["provider"],
                model=orch_config["model"],
                max_tokens=orch_config.get("max_tokens", 4096),
                temperature=orch_config.get("temperature", 0.7),
            )

        # Create specialist adapter (shared by all specialists)
        if "specialists" in config:
            spec_config = config["specialists"]
            adapters["specialists"] = cls.create(
                provider=spec_config["provider"],
                model=spec_config["model"],
                max_tokens=spec_config.get("max_tokens", 2048),
                temperature=spec_config.get("temperature", 0.6),
            )

        # Create devil's advocate adapter
        if "devils_advocate" in config:
            da_config = config["devils_advocate"]
            adapters["devils_advocate"] = cls.create(
                provider=da_config["provider"],
                model=da_config["model"],
                max_tokens=da_config.get("max_tokens", 3072),
                temperature=da_config.get("temperature", 0.8),
            )

        return adapters

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the adapter instance cache."""
        cls._instances.clear()

    @classmethod
    def register_adapter(
        cls,
        provider: ModelProvider,
        adapter_class: type[BaseLLM]
    ) -> None:
        """Register a new adapter class for a provider.

        Args:
            provider: The provider identifier
            adapter_class: The adapter class to register
        """
        cls._adapters[provider] = adapter_class
