"""Anthropic Claude API adapter."""

import json
import time
from typing import Any

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from agentic_council.models.base import BaseLLM, LLMResponse, ModelConfig


class AnthropicAdapter(BaseLLM):
    """Adapter for Anthropic Claude models (used for Orchestrator)."""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.initialize()

    def initialize(self) -> None:
        """Initialize the Anthropic client."""
        self._client = anthropic.AsyncAnthropic(
            api_key=self.config.api_key
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a response using Claude.

        Args:
            prompt: The user message
            system_prompt: Optional system context
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            LLMResponse with Claude's response
        """
        start_time = time.perf_counter()

        # Build message payload
        messages = [{"role": "user", "content": prompt}]

        # Merge config with kwargs
        params = {
            "model": kwargs.get("model", self.config.model),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "messages": messages,
        }

        if system_prompt:
            params["system"] = system_prompt

        # Call the API
        response = await self._client.messages.create(**params)

        latency_ms = (time.perf_counter() - start_time) * 1000

        # Extract content
        content = ""
        if response.content:
            content = response.content[0].text

        return LLMResponse(
            content=content,
            model=response.model,
            provider="anthropic",
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            latency_ms=latency_ms,
            raw_response=response,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Generate a structured JSON response.

        Uses Claude's JSON mode via system prompt instructions.

        Args:
            prompt: The user message
            schema: JSON schema for expected output
            system_prompt: Optional additional system context
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response matching the schema
        """
        # Build schema-aware system prompt
        schema_instruction = f"""You must respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Respond ONLY with the JSON object, no additional text or markdown formatting."""

        full_system = schema_instruction
        if system_prompt:
            full_system = f"{system_prompt}\n\n{schema_instruction}"

        response = await self.generate(
            prompt=prompt,
            system_prompt=full_system,
            **kwargs
        )

        # Parse JSON response
        content = response.content.strip()

        # Handle markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])

        return json.loads(content)

    async def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_prompt: str | None = None,
        **kwargs: Any
    ) -> tuple[LLMResponse, list[dict[str, Any]]]:
        """Generate a response with tool use capability.

        Args:
            prompt: The user message
            tools: List of tool definitions
            system_prompt: Optional system context
            **kwargs: Additional parameters

        Returns:
            Tuple of (LLMResponse, list of tool calls)
        """
        start_time = time.perf_counter()

        messages = [{"role": "user", "content": prompt}]

        params = {
            "model": kwargs.get("model", self.config.model),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "messages": messages,
            "tools": tools,
        }

        if system_prompt:
            params["system"] = system_prompt

        response = await self._client.messages.create(**params)

        latency_ms = (time.perf_counter() - start_time) * 1000

        # Extract content and tool calls
        content = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        llm_response = LLMResponse(
            content=content,
            model=response.model,
            provider="anthropic",
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            latency_ms=latency_ms,
            raw_response=response,
        )

        return llm_response, tool_calls
