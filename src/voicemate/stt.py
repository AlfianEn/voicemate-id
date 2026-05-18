"""Speech-to-text adapters."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Protocol

import httpx
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
        log.debug("stt.transcribe.openai", path=str(audio_path), model=self._model)
        with audio_path.open("rb") as f:
            resp = await self._client.audio.transcriptions.create(
                model=self._model,
                file=f,
                language="id",
                response_format="text",
            )
        text = resp if isinstance(resp, str) else getattr(resp, "text", str(resp))
        return text.strip()


class MimoOmniSTT:
    """Speech-to-text via Xiaomi MiMo v2 Omni multimodal model.

    Sends audio as base64 input_audio to the chat completions endpoint.
    The omni model can listen to audio and transcribe it.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://token-plan-sgp.xiaomimimo.com/v1",
        model: str = "mimo-v2-omni",
        timeout: float = 60.0,
    ) -> None:
        if not api_key:
            raise ValueError("MIMO_API_KEY is required for the omni STT provider.")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    async def transcribe(self, audio_path: Path) -> str:
        log.debug("stt.transcribe.mimo_omni", path=str(audio_path), model=self._model)
        audio_bytes = audio_path.read_bytes()
        audio_b64 = base64.b64encode(audio_bytes).decode()

        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        # Detect format from extension
        fmt = audio_path.suffix.lstrip(".").lower()
        if fmt in ("ogg", "oga"):
            fmt = "ogg"
        elif fmt in ("mp3", "mp4"):
            fmt = "mp3"
        elif fmt in ("wav", "wave"):
            fmt = "wav"
        else:
            fmt = "ogg"  # Telegram voice notes are ogg

        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Transkripsikan audio ini ke teks Bahasa Indonesia. "
                                "Hanya keluarkan teks hasil transkripsi, tanpa penjelasan."
                            ),
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {"data": audio_b64, "format": fmt},
                        },
                    ],
                }
            ],
            "max_tokens": 500,
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        if "error" in data:
            raise RuntimeError(f"MiMo omni STT error: {data['error']}")

        text = data["choices"][0]["message"]["content"].strip()
        log.debug("stt.result.mimo_omni", chars=len(text))
        return text


def build_stt(
    provider: str,
    *,
    openai_api_key: str = "",
    openai_model: str = "whisper-1",
    mimo_api_key: str = "",
    mimo_base_url: str = "https://token-plan-sgp.xiaomimimo.com/v1",
) -> SpeechToText:
    provider = provider.lower().strip()
    if provider == "openai":
        return OpenAIWhisperSTT(api_key=openai_api_key, model=openai_model)
    if provider == "mimo-omni":
        return MimoOmniSTT(api_key=mimo_api_key, base_url=mimo_base_url)
    raise ValueError(f"Unsupported STT provider: {provider!r}")
