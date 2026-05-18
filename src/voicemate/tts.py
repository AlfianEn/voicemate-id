"""Xiaomi MiMo text-to-speech client.

MiMo TTS uses the chat completions endpoint with audio modality.
The text to synthesize goes in an assistant message.
"""

from __future__ import annotations

from pathlib import Path

import httpx
import structlog

log = structlog.get_logger(__name__)

# Available voices on MiMo v2.5 TTS
AVAILABLE_VOICES = [
    "mimo_default", "冰糖", "茉莉", "苏打", "白桦",
    "Mia", "Chloe", "Milo", "Dean",
]


class MimoTTSClient:
    """Generate speech via MiMo TTS (chat completions + audio modality)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://token-plan-sgp.xiaomimimo.com/v1",
        model: str = "mimo-v2.5-tts",
        voice: str = "Mia",
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
        """Synthesize ``text`` into speech audio at ``out_path``.

        Uses the MiMo chat completions endpoint with ``modalities: ["text", "audio"]``.
        The text to speak must be in an ``assistant`` role message.
        """
        import base64

        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [
                {"role": "user", "content": ""},
                {"role": "assistant", "content": text},
            ],
            "modalities": ["text", "audio"],
            "audio": {"voice": self._voice, "format": fmt},
        }
        log.debug("tts.synthesize", model=self._model, voice=self._voice, chars=len(text))
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        audio_data = data["choices"][0]["message"]["audio"]["data"]
        audio_bytes = base64.b64decode(audio_data)
        out_path.write_bytes(audio_bytes)
        log.debug("tts.done", path=str(out_path), bytes=len(audio_bytes))
        return out_path
