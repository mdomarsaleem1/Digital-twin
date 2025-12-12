"""Google Gemini API adapter."""

import json
import time
from typing import Any

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from agentic_council.models.base import BaseLLM, LLMResponse, ModelConfig


class GeminiAdapter(BaseLLM):
    """Adapter for Google Gemini models (used for Specialists and Devil's Advocate)."""

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.initialize()

    def initialize(self) -> None:
        """Initialize the Gemini client."""
        genai.configure(api_key=self.config.api_key)

        # Create generation config
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
        )

        self._client = genai.GenerativeModel(
            model_name=self.config.model,
            generation_config=generation_config,
        )
        self._generation_config = generation_config

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
        """Generate a response using Gemini.

        Args:
            prompt: The user message
            system_prompt: Optional system context (prepended to prompt)
            **kwargs: Additional parameters

        Returns:
            LLMResponse with Gemini's response
        """
        start_time = time.perf_counter()

        # Gemini handles system prompts differently - we prepend it
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"

        # Override generation config if needed
        gen_config = None
        if "temperature" in kwargs or "max_tokens" in kwargs:
            gen_config = genai.types.GenerationConfig(
                max_output_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
            )

        # Generate response (async)
        response = await self._client.generate_content_async(
            full_prompt,
            generation_config=gen_config,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        # Extract content and usage
        content = ""
        if response.text:
            content = response.text

        # Gemini provides token counts in usage_metadata
        usage = {"input_tokens": 0, "output_tokens": 0}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage["input_tokens"] = getattr(response.usage_metadata, "prompt_token_count", 0)
            usage["output_tokens"] = getattr(response.usage_metadata, "candidates_token_count", 0)

        return LLMResponse(
            content=content,
            model=self.config.model,
            provider="google",
            usage=usage,
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

        Uses Gemini's JSON mode capabilities.

        Args:
            prompt: The user message
            schema: JSON schema for expected output
            system_prompt: Optional additional system context
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response matching the schema
        """
        # Build schema-aware prompt
        schema_instruction = f"""You must respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Respond ONLY with the JSON object, no additional text, markdown, or code blocks."""

        full_system = schema_instruction
        if system_prompt:
            full_system = f"{system_prompt}\n\n{schema_instruction}"

        # Use JSON response mode if available (Gemini 1.5+)
        gen_config = genai.types.GenerationConfig(
            max_output_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
            response_mime_type="application/json",
        )

        full_prompt = f"{full_system}\n\n---\n\n{prompt}"

        response = await self._client.generate_content_async(
            full_prompt,
            generation_config=gen_config,
        )

        # Parse JSON response
        content = response.text.strip()

        # Handle markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])

        return json.loads(content)

    async def generate_chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a response in a multi-turn chat context.

        Args:
            messages: List of {"role": "user"|"assistant", "content": str}
            system_prompt: Optional system context
            **kwargs: Additional parameters

        Returns:
            LLMResponse with Gemini's response
        """
        start_time = time.perf_counter()

        # Convert to Gemini's history format
        history = []
        for msg in messages[:-1]:  # All but the last message
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})

        # Start chat with history
        chat = self._client.start_chat(history=history)

        # Get the last message as the prompt
        last_message = messages[-1]["content"]
        if system_prompt:
            last_message = f"{system_prompt}\n\n{last_message}"

        # Generate response
        response = await chat.send_message_async(last_message)

        latency_ms = (time.perf_counter() - start_time) * 1000

        content = response.text if response.text else ""

        usage = {"input_tokens": 0, "output_tokens": 0}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage["input_tokens"] = getattr(response.usage_metadata, "prompt_token_count", 0)
            usage["output_tokens"] = getattr(response.usage_metadata, "candidates_token_count", 0)

        return LLMResponse(
            content=content,
            model=self.config.model,
            provider="google",
            usage=usage,
            latency_ms=latency_ms,
            raw_response=response,
        )
