"""Speech-to-text adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import structlog
from openai import AsyncOpenAI

log = structlog.get_logger(__name__)


class SpeechToText(Protocol):
    async def transcribe(self, audio_path: Path) -> str: ...


class OpenAIWhisperSTT:
    """Speech-to-text via the OpenAI Whisper API."""

    def __init__(self, api_key: str, model: str = "whisper-1") -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for the openai STT provider.")
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def transcribe(self, audio_path: Path) -> str:
        log.debug("stt.transcribe", path=str(audio_path), model=self._model)
        with audio_path.open("rb") as f:
            resp = await self._client.audio.transcriptions.create(
                model=self._model,
                file=f,
                language="id",
                response_format="text",
            )
        # response_format="text" returns a plain string in the SDK
        text = resp if isinstance(resp, str) else getattr(resp, "text", str(resp))
        return text.strip()


def build_stt(provider: str, *, openai_api_key: str, openai_model: str) -> SpeechToText:
    provider = provider.lower().strip()
    if provider == "openai":
        return OpenAIWhisperSTT(api_key=openai_api_key, model=openai_model)
    raise ValueError(f"Unsupported STT provider: {provider!r}")
