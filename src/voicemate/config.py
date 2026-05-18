"""Configuration loaded from environment / .env file."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, validated on startup."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Telegram ---
    telegram_bot_token: str
    telegram_allowed_user_ids: str = ""

    # --- Xiaomi MiMo ---
    mimo_api_key: str
    mimo_base_url: str = "https://token-plan-sgp.xiaomimimo.com/v1"
    mimo_reasoning_model: str = "mimo-v2.5-pro"
    mimo_tts_model: str = "mimo-v2.5-tts"
    mimo_tts_voice: str = "Mia"

    # --- STT ---
    stt_provider: str = "openai"
    openai_api_key: str = ""
    openai_stt_model: str = "whisper-1"

    # --- Behavior ---
    log_level: str = "INFO"
    memory_budget_chars: int = 8000
    persona: str = Field(
        default=(
            "Kamu adalah VoiceMate ID, asisten suara berbahasa Indonesia. "
            "Jawaban singkat, jelas, dan ramah, maksimal 3-4 kalimat agar enak didengar. "
            "Hindari simbol markdown atau emoji."
        )
    )

    @property
    def allowed_user_ids(self) -> set[int]:
        raw = (self.telegram_allowed_user_ids or "").strip()
        if not raw:
            return set()
        return {int(x) for x in raw.split(",") if x.strip().isdigit()}


def load_settings() -> Settings:
    """Load and validate settings. Raises on missing required vars."""
    return Settings()  # type: ignore[call-arg]
