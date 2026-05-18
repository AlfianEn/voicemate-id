"""Xiaomi MiMo text-to-speech client."""

from __future__ import annotations

from pathlib import Path

import httpx
import structlog

log = structlog.get_logger(__name__)


class MimoTTSClient:
    """Generate Indonesian speech via the MiMo TTS endpoint.

    Uses the OpenAI-compatible /audio/speech endpoint shape, which the MiMo
    platform exposes for its TTS models.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.xiaomimimo.com/v1",
        model: str = "mimo-v2.5-tts",
        voice: str = "zh_female_xiaoyu",
        timeout: float = 60.0,
    ) -> None:
        if not api_key:
            raise ValueError("MIMO_API_KEY is required for TTS.")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._voice = voice
        self._timeout = timeout

    async def synthesize(self, text: str, out_path: Path, *, fmt: str = "mp3") -> Path:
        """Synthesize ``text`` and write the audio bytes to ``out_path``."""
        url = f"{self._base_url}/audio/speech"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "voice": self._voice,
            "input": text,
            "response_format": fmt,
        }
        log.debug("tts.synthesize", model=self._model, voice=self._voice, chars=len(text))
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            out_path.write_bytes(resp.content)
        return out_path
