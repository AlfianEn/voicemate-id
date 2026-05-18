"""Smoke tests for Settings."""

from __future__ import annotations

import pytest

from voicemate.config import Settings


def test_settings_load_minimal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("MIMO_API_KEY", "test-mimo-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.delenv("TELEGRAM_ALLOWED_USER_IDS", raising=False)

    s = Settings(_env_file=None)  # type: ignore[call-arg]

    assert s.telegram_bot_token == "test-token"
    assert s.mimo_api_key == "test-mimo-key"
    assert s.allowed_user_ids == set()
    assert s.mimo_reasoning_model == "mimo-reasoning"
    assert s.mimo_tts_model == "mimo-v2.5-tts"


def test_allowed_user_ids_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x")
    monkeypatch.setenv("MIMO_API_KEY", "y")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_IDS", "111, 222 ,abc, 333")

    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.allowed_user_ids == {111, 222, 333}
