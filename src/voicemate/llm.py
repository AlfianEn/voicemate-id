"""Xiaomi MiMo reasoning client (OpenAI-compatible chat completions)."""

from __future__ import annotations

from dataclasses import dataclass

import structlog
from openai import AsyncOpenAI

log = structlog.get_logger(__name__)


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str


class MimoReasoningClient:
    """Thin wrapper over the MiMo OpenAI-compatible chat endpoint."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xiaomimimo.com/v1",
        model: str = "mimo-reasoning",
    ) -> None:
        if not api_key:
            raise ValueError("MIMO_API_KEY is required.")
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def reply(self, messages: list[ChatMessage], *, max_tokens: int = 512) -> str:
        log.debug("llm.reply", model=self._model, messages=len(messages))
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        choice = resp.choices[0]
        text = (choice.message.content or "").strip()
        return text
