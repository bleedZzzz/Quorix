"""LLM provider interface and implementations."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.config.settings import settings


class LLMProvider(ABC):
    """Abstract interface for LLM operations."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Generate text completion."""
        pass

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate JSON structured response."""
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens."""
        pass


class MockLLMProvider(LLMProvider):
    """Mock/Fallback LLM for development and testing without paid API keys."""

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        return (
            "[Quorix Research Synthesis]\n\n"
            "Based on the provided literature evidence, the query was analyzed thoroughly.\n"
            "Key finding: The investigated papers demonstrate consistent empirical support.\n"
            "Claim 1: The retrieved methodology aligns with established literature benchmarks [1].\n"
            "Claim 2: Further investigation into theoretical boundary cases remains an open direction [2]."
        )

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        # Simple heuristic response matching typical structured prompts (intent, claims, gaps)
        return {
            "intent": "factual_inquiry",
            "rewritten_query": prompt,
            "entities": ["neural architecture", "transformer", "attention mechanism"],
            "constraints": {},
            "claims": [
                {
                    "text": "The retrieved methodology aligns with established literature benchmarks.",
                    "verification_state": "verified",
                    "confidence": 0.95,
                }
            ],
            "is_sufficient": True,
            "relevance_grade": "HIGH_RELEVANCE",
        }

    async def stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        text = await self.generate(prompt, system_prompt, temperature, max_tokens)
        for word in text.split(" "):
            yield word + " "


class OpenAILLMProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        sys = system_prompt or "You are a JSON assistant. Respond with valid JSON only."
        if not sys.endswith("Respond with valid JSON only."):
            sys += " Respond with valid JSON only."

        raw = await self.generate(prompt=prompt, system_prompt=sys, temperature=0.0)
        # Strip potential markdown formatting
        cleaned = raw.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())

    async def stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=60.0) as client, client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    payload = json.loads(line[6:])
                    delta = payload["choices"][0].get("delta", {}).get("content", "")
                    if delta:
                        yield delta


def get_llm_provider(policy: str = "default") -> LLMProvider:
    """Factory to get the appropriate LLM provider based on environment and policy."""
    if settings.openai_api_key:
        model = "gpt-4o-mini" if policy == "fast" else "gpt-4o"
        return OpenAILLMProvider(api_key=settings.openai_api_key, model=model)
    return MockLLMProvider()
